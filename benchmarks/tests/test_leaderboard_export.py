import json
from pathlib import Path
from unittest.mock import patch

import pytest

from benchmarks import export_leaderboard_space


def _write_run(
    results_dir: Path,
    run_dir: str,
    key: str,
    *,
    manifest: str,
    samples: int = 32,
    rows: int = 29_599,
) -> None:
    target = results_dir / run_dir
    target.mkdir(parents=True)
    report = {
        "dataset": {"manifest_sha256": manifest},
        "model_stats": {key: {"total_samples": samples, "total_rows": rows}},
    }
    metadata = {
        "requested_model": key,
        "effort": "xhigh",
        "cli_version_observed_at_metadata_write": "test-cli",
        "generated_at": "2026-07-21T00:00:00+00:00",
    }
    (target / "evaluation_report.json").write_text(json.dumps(report), encoding="utf-8")
    (target / "run_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")


def test_load_runs_rejects_mixed_dataset_manifests(tmp_path: Path) -> None:
    runs = (
        ("run-a", "model_a", "Harness A", "Model A"),
        ("run-b", "model_b", "Harness B", "Model B"),
    )
    _write_run(tmp_path, "run-a", "model_a", manifest="a" * 64)
    _write_run(tmp_path, "run-b", "model_b", manifest="b" * 64)

    with patch.object(export_leaderboard_space, "RUNS", runs):
        with pytest.raises(ValueError, match="targets a different dataset"):
            export_leaderboard_space.load_runs(tmp_path)


def test_prepare_output_requires_explicit_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "space"
    output.mkdir()
    stale = output / "stale.txt"
    stale.write_text("stale", encoding="utf-8")

    with pytest.raises(FileExistsError, match="pass --overwrite"):
        export_leaderboard_space.prepare_output(output, overwrite=False)

    export_leaderboard_space.prepare_output(output, overwrite=True)
    assert output.is_dir()
    assert list(output.iterdir()) == []
