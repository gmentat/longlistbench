import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.generate_multihop_benchmark import (
    MULTIHOP_CASE_CONFIGS,
    generate_multihop_suite,
)


class MultiHopBenchmarkTests(unittest.TestCase):
    def test_generate_multihop_suite_writes_single_document_crosspage_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            metadata = generate_multihop_suite(out_dir, render_pdfs=False)

            self.assertEqual(metadata["suite_name"], "longlistbench-crosspage-multihop")
            self.assertGreaterEqual(metadata["total_cases"], 3)
            self.assertEqual(metadata["total_documents"], metadata["total_cases"])
            self.assertEqual(
                {case["complexity_regime"] for case in metadata["cases"]},
                {"claim_crosspage_multihop"},
            )
            self.assertEqual(
                {case["difficulty"] for case in metadata["cases"]},
                {"multihop", "mixed"},
            )

            for case in metadata["cases"]:
                sample_id = case["id"]
                sample_metadata = json.loads((out_dir / "metadata" / f"{sample_id}.json").read_text(encoding="utf-8"))
                ground_truth = json.loads((out_dir / "ground_truth" / f"{sample_id}.json").read_text(encoding="utf-8"))

                self.assertEqual(sample_metadata["id"], sample_id)
                self.assertEqual(sample_metadata["document_count"], 1)
                self.assertEqual(sample_metadata["format"], "crosspage")
                self.assertGreaterEqual(sample_metadata["minimum_gap_pages_between_primary_and_last_evidence"], 60)
                self.assertGreaterEqual(len(sample_metadata["join_requirements"]), 3)
                self.assertEqual(len(ground_truth), case["num_claims"])

                html = (out_dir / "html" / f"{sample_id}.html").read_text(encoding="utf-8")
                self.assertIn("Claim Intake File Cards", html)
                self.assertIn("Claim Financial Ledger", html)
                self.assertNotIn("join on", html.lower())

    def test_config_has_strong_cross_page_join_cases(self) -> None:
        self.assertGreaterEqual(len(MULTIHOP_CASE_CONFIGS), 3)
        all_edges = {edge for config in MULTIHOP_CASE_CONFIGS for edge in config.join_requirements}

        self.assertIn("incident_number -> financial ledger", all_edges)
        self.assertIn("policy_number -> policy register", all_edges)
        self.assertIn("unit_number -> driver roster", all_edges)
        self.assertIn("cause_code -> cause classification appendix", all_edges)


if __name__ == "__main__":
    unittest.main()
