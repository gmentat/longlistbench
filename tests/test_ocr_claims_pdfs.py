import unittest
import tempfile
from pathlib import Path

from benchmarks.ocr_claims_pdfs import build_arg_parser, collect_pdf_files


class OcrCliTests(unittest.TestCase):
    def test_default_ocr_engine_is_gemini(self) -> None:
        parser = build_arg_parser()
        args = parser.parse_args([])
        self.assertEqual(args.ocr_engine, "gemini")

    def test_collect_pdf_files_supports_custom_recursive_suite_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case_dir = root / "multihop_012_001"
            case_dir.mkdir()
            (case_dir / "loss_run_summary.pdf").write_bytes(b"%PDF-1.4\n")
            (case_dir / "driver_roster.pdf").write_bytes(b"%PDF-1.4\n")
            (root / "top_level.pdf").write_bytes(b"%PDF-1.4\n")

            pdfs = collect_pdf_files(root, file_name=None, recursive=True, tiers=None, limit=0)

            self.assertEqual(
                [path.name for path in pdfs],
                ["top_level.pdf", "driver_roster.pdf", "loss_run_summary.pdf"],
            )


if __name__ == "__main__":
    unittest.main()
