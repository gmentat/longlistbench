from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[1] / "data"

CANONICAL_STRESSORS = [
    "page_breaks",
    "split_records",
    "multi_row",
    "duplicates",
    "large_doc",
    "multiple_tables",
    "multi_column",
    "merged_cells",
    "ocr_condition",
    "ocr_layout_condition",
    "long_range_evidence",
    "cross_section_join",
    "repeated_keys",
    "heterogeneous_record_list",
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _html(sample_id: str) -> str:
    return (DATA_DIR / "html" / f"{sample_id}.html").read_text(encoding="utf-8")


def _ground_truth_records(sample_id: str) -> list[dict[str, Any]]:
    ground_truth = _load_json(DATA_DIR / "ground_truth" / f"{sample_id}.json")
    if isinstance(ground_truth, list):
        return ground_truth
    if isinstance(ground_truth, dict):
        for key in ("records", "incidents"):
            rows = ground_truth.get(key)
            if isinstance(rows, list):
                return rows
    return []


def _has_stressor_evidence(instance: dict[str, Any], stressor: str) -> tuple[bool, str]:
    sample_id = instance["id"]
    html = _html(sample_id)
    html_lower = html.lower()
    records = _ground_truth_records(sample_id)
    page_count = int(instance.get("pdf_page_count") or instance.get("pages_estimate") or 0)
    target_count = int(instance.get("num_target_records") or len(records))

    if stressor == "page_breaks":
        return page_count > 1, f"{page_count} PDF pages"

    if stressor == "split_records":
        table_count = len(re.findall(r"<table\b", html, flags=re.IGNORECASE))
        block_markers = len(re.findall(r"<br\s*/?>|continuation", html_lower))
        ok = page_count > 1 and (table_count > 1 or block_markers > 0)
        return ok, f"{page_count} pages; {table_count} tables; {block_markers} split-block markers"

    if stressor == "multi_row":
        markers = [
            'class="desc"',
            "class='note'",
            'class="note"',
            "continuation",
            "section-note",
            "clause-heading",
            "detail-grid",
            "<br>",
        ]
        hits = [marker for marker in markers if marker in html_lower]
        return bool(hits), f"multi-row markers: {hits[:5]}"

    if stressor == "duplicates":
        markers = [
            "prior term",
            "prior-term",
            "archive",
            "archived",
            "revised run",
            "summary cards",
            "summary card",
            "not target records",
            "inactive or non-target",
            "no-claims",
        ]
        hits = [marker for marker in markers if marker in html_lower]
        return bool(hits), f"duplicate/distractor markers: {hits[:6]}"

    if stressor == "large_doc":
        # 2.0 includes both very high row-count docs and moderately large
        # production-like packets where page count is the stressor.
        ok = target_count >= 500 or page_count >= 50 or (target_count >= 300 and page_count >= 40)
        return ok, f"{target_count} records; {page_count} pages"

    if stressor == "multiple_tables":
        table_count = len(re.findall(r"<table\b", html, flags=re.IGNORECASE))
        return table_count > 1, f"{table_count} HTML tables"

    if stressor == "multi_column":
        markers = ["column-count", "two-column", "two-col"]
        hits = [marker for marker in markers if marker in html_lower]
        return bool(hits), f"column markers: {hits}"

    if stressor == "merged_cells":
        merged_count = len(re.findall(r"\b(?:colspan|rowspan)\s*=", html, flags=re.IGNORECASE))
        return merged_count > 0, f"{merged_count} colspan/rowspan attributes"

    if stressor == "ocr_condition":
        transcript = DATA_DIR / "transcripts" / "ocr_gemini" / f"{sample_id}.md"
        ok = transcript.exists() and transcript.stat().st_size > 0 and "ocr" in instance.get("transcripts_available", [])
        size = transcript.stat().st_size if transcript.exists() else 0
        return ok, f"OCR transcript bytes: {size}"

    if stressor == "ocr_layout_condition":
        transcript = DATA_DIR / "transcripts" / "ocr_gemini" / f"{sample_id}.md"
        table_count = len(re.findall(r"<table\b", html, flags=re.IGNORECASE))
        ok = transcript.exists() and transcript.stat().st_size > 0 and table_count > 1
        return ok, f"OCR transcript present; {table_count} source tables"

    if stressor == "long_range_evidence":
        gap = int(instance.get("minimum_gap_pages_between_primary_and_last_evidence") or 0)
        evidence_sections = instance.get("evidence_map") or []
        return gap >= 20 and len(evidence_sections) >= 2, f"gap={gap}; sections={len(evidence_sections)}"

    if stressor == "cross_section_join":
        required_fields = {"return_id", "jurisdiction", "total_miles", "tax_due_refund"}
        joined_rows = [row for row in records if required_fields <= set(row)]
        return bool(joined_rows), f"{len(joined_rows)} rows contain fields from separate sections"

    if stressor == "repeated_keys":
        jurisdictions = [str(row.get("jurisdiction")) for row in records if row.get("jurisdiction")]
        repeated = len(jurisdictions) - len(set(jurisdictions))
        return repeated > 0, f"{repeated} repeated jurisdiction keys"

    if stressor == "heterogeneous_record_list":
        record_types = sorted({str(row.get("record_type")) for row in records if row.get("record_type")})
        return len(record_types) > 1, f"{len(record_types)} record types"

    return False, f"unknown stressor: {stressor}"


def test_every_declared_complexity_stressor_has_artifact_coverage() -> None:
    manifest = _load_json(DATA_DIR / "manifest.json")
    instances = manifest["instances"]
    stressors = list(manifest["complexity_stressors"])

    assert set(stressors) == set(CANONICAL_STRESSORS)

    failures: list[str] = []
    coverage_counts: Counter[str] = Counter()
    for stressor in stressors:
        labeled = [instance for instance in instances if stressor in instance.get("problems", [])]
        assert labeled, f"{stressor} is declared but not assigned to any document"

        for instance in labeled:
            ok, evidence = _has_stressor_evidence(instance, stressor)
            if ok:
                coverage_counts[stressor] += 1
            else:
                failures.append(f"{instance['id']} lacks evidence for {stressor}: {evidence}")

    assert not failures
    assert all(coverage_counts[stressor] > 0 for stressor in stressors)


def test_manifest_alias_and_instance_metadata_paths_are_current() -> None:
    manifest = _load_json(DATA_DIR / "manifest.json")
    assert manifest == _load_json(DATA_DIR / "metadata.json")

    for instance in manifest["instances"]:
        sample_id = instance["id"]
        relative_path = Path("metadata") / f"{sample_id}.json"
        assert instance["files"]["metadata"] == relative_path.as_posix()

        metadata_path = DATA_DIR / relative_path
        assert metadata_path.is_file()
        sample_metadata = _load_json(metadata_path)
        assert sample_metadata["id"] == sample_id
        assert sample_metadata["files"]["metadata"] == relative_path.as_posix()
