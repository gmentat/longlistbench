import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.validate_html_table_occupancy import (
    SparseColumnFinding,
    find_page_scaffold_mismatches,
    find_sparse_columns,
    is_expected_sparse_column,
)


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


class RenderedHtmlIntegrityTests(unittest.TestCase):
    def test_tables_have_no_unexpected_structurally_empty_columns(self) -> None:
        findings = find_sparse_columns(DATA_DIR / "html")
        unexpected = [finding for finding in findings if not is_expected_sparse_column(finding)]
        self.assertEqual(unexpected, [])

    def test_explicit_html_pages_match_recorded_pdf_page_counts(self) -> None:
        self.assertEqual(find_page_scaffold_mismatches(DATA_DIR), [])

    def test_flowing_policy_sections_do_not_claim_one_to_one_pdf_pages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            dataset = Path(directory)
            (dataset / "html").mkdir()
            (dataset / "metadata").mkdir()
            (dataset / "html/policy.html").write_text(
                '<section class="page"><h1>Policy Form</h1></section>',
                encoding="utf-8",
            )
            (dataset / "metadata/policy.json").write_text(
                json.dumps({"pdf_page_count": 4, "html_pagination_mode": "flowing_sections"}),
                encoding="utf-8",
            )

            self.assertEqual(find_page_scaffold_mismatches(dataset), [])

    def test_group_context_columns_are_expected_to_be_sparse(self) -> None:
        finding = SparseColumnFinding(
            sample_id="ifta_return_schedule_001",
            page=1,
            title="Return Schedule",
            section="Schedule",
            header="Schedule",
            empty_rate=0.9,
            row_count=20,
        )

        self.assertTrue(is_expected_sparse_column(finding))


if __name__ == "__main__":
    unittest.main()
