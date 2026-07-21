import json
from dataclasses import asdict
from pathlib import Path

from benchmarks.core_operations import generate_driver_mvr as driver_mvr
from benchmarks.core_operations import generate_ifta_multisection as ifta
from benchmarks.core_operations import generate_loss_runs as loss_runs
from benchmarks.core_operations import render_operational_tables as operational_tables


DATA_DIR = Path("data")


def test_driver_mvr_sparse_reports_match_ground_truth() -> None:
    for sample_id in driver_mvr.SAMPLE_IDS:
        released = json.loads(
            (DATA_DIR / "ground_truth" / f"{sample_id}.json").read_text(
                encoding="utf-8"
            )
        )
        rows, reports = driver_mvr.sparse_ground_truth(
            driver_mvr.make_driver_rows(sample_id)
        )
        assert rows == released
        html = driver_mvr.html_document(
            sample_id,
            driver_mvr.COMPANIES[sample_id],
            rows,
            reports,
        )

        assert len(reports) == driver_mvr.REPORT_COUNT
        assert driver_mvr.report_indices(len(rows))[0] == 0
        assert driver_mvr.report_indices(len(rows))[-1] == len(rows) - 1
        assert sum(row["accidents_last_5_years"] is not None for row in rows) == 8
        assert sum(row["mvr_violations"] is not None for row in rows) == 8
        assert html.count("Certified Employer Driving Record") == 8
        assert "1&nbsp;&nbsp;of&nbsp;&nbsp;2" not in html
        assert "1&nbsp;&nbsp;of&nbsp;&nbsp;4" not in html
        for row in rows:
            roster_cells = (
                f"<td>{driver_mvr.h(row['name'])}</td>"
                f"<td>{driver_mvr.h(row['state_licensed'])}</td>"
                f"<td>{driver_mvr.h(row['license_number'])}</td>"
                f"<td>{driver_mvr.h(row['date_of_birth'])}</td>"
                f"<td>{driver_mvr.h(row['date_hired'])}</td>"
                f"<td class='center'>{driver_mvr.h(row['years_experienced'])}</td>"
                f"<td>{driver_mvr.h(row['mvr_run_date'])}</td>"
                f"<td class='center'>{driver_mvr.h(row['license_class'])}</td>"
            )
            assert roster_cells in html
        for report in reports:
            assert report["license_number"] in html
            assert report["accidents_last_5_years"] in html
            assert report["mvr_violations"] in html


def test_ifta_multisection_generation_matches_release_ground_truth() -> None:
    cases = (
        ("ifta_multisection_return_001", 9301, 10),
        ("ifta_multisection_return_002", 9402, 14),
    )
    for sample_id, seed, returns in cases:
        generated = [asdict(record) for record in ifta.make_records(seed, returns)]
        released = json.loads(
            (DATA_DIR / "ground_truth" / f"{sample_id}.json").read_text(encoding="utf-8")
        )
        assert generated == released


def test_loss_run_generation_matches_release_ground_truth() -> None:
    for sample_number in range(1, 4):
        sample_id = f"loss_run_external_{sample_number:03d}"
        _sections, generated = loss_runs.build_sections(
            sample_number,
            86000 + sample_number * 977,
        )
        released = json.loads(
            (DATA_DIR / "ground_truth" / f"{sample_id}.json").read_text(encoding="utf-8")
        )
        assert generated == released


def test_operational_table_rewrite_is_idempotent() -> None:
    rows = json.loads(
        (DATA_DIR / "ground_truth" / "ifta_tax_inquiry_001.json").read_text(
            encoding="utf-8"
        )
    )
    assert operational_tables.rewrite_tax_inquiry_rows(rows) == rows


def test_public_generators_cover_every_core_operations_document(tmp_path) -> None:
    manifest = json.loads((DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
    released_ids = {
        instance["id"]
        for instance in manifest["instances"]
        if instance["hf_config"] == "core_operations"
    }
    rendered_ids = {
        document["sample_id"]
        for document in operational_tables.build_documents(tmp_path / "rendered")
    }
    generated_ids = (
        set(driver_mvr.SAMPLE_IDS)
        | {"ifta_multisection_return_001", "ifta_multisection_return_002"}
        | {f"loss_run_external_{index:03d}" for index in range(1, 4)}
        | rendered_ids
    )

    assert len(released_ids) == 26
    assert generated_ids == released_ids


def test_public_generators_do_not_reference_private_paths() -> None:
    generator_dir = Path("benchmarks/core_operations")
    forbidden = ("/Users/", "/home/", "production_references", "REFERENCE_DIR")
    for path in generator_dir.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert all(value not in source for value in forbidden), path
