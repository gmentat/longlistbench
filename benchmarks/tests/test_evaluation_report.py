import hashlib
import json

from benchmarks import evaluate_models
from benchmarks.evaluate_models import EvaluationResult


def test_evaluation_report_includes_manifest_provenance(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    manifest = {"instances": []}
    manifest_bytes = json.dumps(manifest).encode("utf-8")
    (data_dir / "manifest.json").write_bytes(manifest_bytes)
    monkeypatch.setattr(evaluate_models, "default_dataset_dir", lambda: data_dir)

    result = EvaluationResult(
        model="codex_gpt55",
        sample="sample_001",
        tier="core_operations",
        format="production_like_pdf",
        transcript="ocr",
        metrics={
            "f1": 1.0,
            "recall": 1.0,
            "precision": 1.0,
            "found": 1,
            "total_gold_field_pairs": 1,
            "total_pred_field_pairs": 1,
            "ground_truth_count": 1,
            "predicted_count": 1,
        },
        extraction_time=0.0,
    )

    evaluate_models.generate_report([result], tmp_path, evaluation_mode="offline_replay")

    report = json.loads((tmp_path / "evaluation_report.json").read_text())
    report_md = (tmp_path / "evaluation_report.md").read_text()
    assert report["dataset"]["manifest_sha256"] == hashlib.sha256(manifest_bytes).hexdigest()
    assert report["dataset"]["manifest_path"].endswith("manifest.json")
    assert "git_sha" in report["dataset"]
    assert report["evaluation_mode"] == "offline_replay"
    assert "Evaluation mode: `offline_replay`" in report_md
    assert " N/A | N/A |" in report_md
