import hashlib
import json

from benchmarks.ocr_claims_pdfs import (
    ocr_user_prompt,
    refresh_organized_manifest_transcripts,
)


def test_layout_table_mode_forbids_csv_normalization():
    prompt = ocr_user_prompt("layout")

    assert "Do not convert tables to CSV" in prompt
    assert "preserve the visible table layout" in prompt


def test_csv_table_mode_keeps_existing_prompt_contract():
    prompt = ocr_user_prompt("csv")

    assert "Format tables as CSV" in prompt


def test_refresh_updates_sizes_and_only_marks_regenerated_samples(tmp_path):
    dataset = tmp_path / "data"
    for directory in ["pdfs", "html", "ground_truth", "transcripts/ocr_gemini", "metadata"]:
        (dataset / directory).mkdir(parents=True, exist_ok=True)

    instances = []
    for sample_id in ["regenerated", "unchanged"]:
        (dataset / "pdfs" / f"{sample_id}.pdf").write_bytes(b"pdf")
        (dataset / "html" / f"{sample_id}.html").write_text("html", encoding="utf-8")
        (dataset / "ground_truth" / f"{sample_id}.json").write_text("[]\n", encoding="utf-8")
        (dataset / "transcripts" / "ocr_gemini" / f"{sample_id}.md").write_text(
            "# Page 1\n", encoding="utf-8"
        )
        metadata = {
            "id": sample_id,
            "files": {},
            "artifacts": {},
            "layout_revision": {"ocr_status": "stale_until_regenerated_from_pdf"},
        }
        (dataset / "metadata" / f"{sample_id}.json").write_text(
            json.dumps(metadata), encoding="utf-8"
        )
        instances.append(metadata)

    manifest = {"instances": instances}
    (dataset / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (dataset / "metadata.json").write_text(json.dumps(manifest), encoding="utf-8")

    refresh_organized_manifest_transcripts(dataset, {"regenerated"})

    refreshed = json.loads((dataset / "manifest.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in refreshed["instances"]}
    assert (
        by_id["regenerated"]["layout_revision"]["ocr_status"]
        == "regenerated_from_current_pdf"
    )
    assert "ocr_regenerated_at" in by_id["regenerated"]["layout_revision"]
    assert (
        by_id["unchanged"]["layout_revision"]["ocr_status"]
        == "stale_until_regenerated_from_pdf"
    )
    assert by_id["regenerated"]["ocr_md_size_bytes"] == len("# Page 1\n")
    assert by_id["regenerated"]["files"]["pdf_size_bytes"] == len(b"pdf")
    assert by_id["regenerated"]["artifacts"] == {
        "pdf_sha256": hashlib.sha256(b"pdf").hexdigest(),
        "html_sha256": hashlib.sha256(b"html").hexdigest(),
        "ground_truth_sha256": hashlib.sha256(b"[]\n").hexdigest(),
        "ocr_sha256": hashlib.sha256(b"# Page 1\n").hexdigest(),
    }
