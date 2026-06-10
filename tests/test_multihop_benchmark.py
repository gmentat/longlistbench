import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.generate_multihop_benchmark import (
    MULTIHOP_CASE_CONFIGS,
    generate_multihop_suite,
)


class MultiHopBenchmarkTests(unittest.TestCase):
    def test_generate_multihop_suite_writes_case_manifests_and_ground_truth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            metadata = generate_multihop_suite(out_dir, render_pdfs=False)

            self.assertEqual(metadata["suite_name"], "longlistbench-multihop")
            self.assertGreaterEqual(metadata["total_cases"], 3)
            self.assertEqual(
                {case["case_type"] for case in metadata["cases"]},
                {"multi_hop", "mixed"},
            )

            for case in metadata["cases"]:
                case_dir = out_dir / case["id"]
                manifest = json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))
                ground_truth = json.loads((case_dir / "ground_truth.json").read_text(encoding="utf-8"))

                self.assertEqual(manifest["id"], case["id"])
                self.assertGreaterEqual(len(manifest["documents"]), 3)
                self.assertGreaterEqual(len(manifest["join_requirements"]), 3)
                self.assertEqual(len(ground_truth["incidents"]), case["num_incidents"])

                roles = {doc["role"] for doc in manifest["documents"]}
                self.assertIn("loss_run_summary", roles)
                self.assertTrue({"driver_roster", "policy_register", "financial_ledger"} & roles)
                self.assertIn("ocr", manifest["transcript_conditions_planned"])

    def test_config_has_strong_cross_document_join_cases(self) -> None:
        self.assertGreaterEqual(len(MULTIHOP_CASE_CONFIGS), 3)
        all_edges = {edge for config in MULTIHOP_CASE_CONFIGS for edge in config.join_requirements}

        self.assertIn("incident_number -> financial_ledger", all_edges)
        self.assertIn("policy_number -> policy_register", all_edges)
        self.assertIn("unit_number -> driver_roster", all_edges)
        self.assertIn("cause_code -> cause_code_legend", all_edges)


if __name__ == "__main__":
    unittest.main()
