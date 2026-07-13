import unittest
from pathlib import Path

from benchmarks.validate_html_table_occupancy import (
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


if __name__ == "__main__":
    unittest.main()
