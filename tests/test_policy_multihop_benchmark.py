import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.generate_policy_multihop_benchmark import (
    POLICY_MULTIHOP_CASE_CONFIGS,
    generate_policy_multihop_suite,
)


class PolicyMultiHopBenchmarkTests(unittest.TestCase):
    def test_generate_policy_multihop_suite_writes_lob_specific_policy_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            metadata = generate_policy_multihop_suite(out_dir, render_pdfs=False)

            self.assertEqual(metadata["suite_name"], "longlistbench-policy-multihop")
            self.assertGreaterEqual(metadata["total_cases"], 3)
            self.assertEqual(metadata["total_documents"], metadata["total_cases"])
            self.assertEqual(set(metadata["lobs"]), {"BOP", "CGL", "WC"})
            self.assertEqual(
                {case["complexity_regime"] for case in metadata["cases"]},
                {"policy_multi_hop", "mixed"},
            )
            self.assertEqual(
                {case["target_record_type"] for case in metadata["cases"]},
                {"policy_packet_item"},
            )

            for case in metadata["cases"]:
                sample_id = case["id"]
                sample_metadata = json.loads((out_dir / "metadata" / f"{sample_id}.json").read_text(encoding="utf-8"))
                ground_truth = json.loads((out_dir / "ground_truth" / f"{sample_id}.json").read_text(encoding="utf-8"))

                self.assertEqual(sample_metadata["id"], sample_id)
                self.assertEqual(sample_metadata["domain"], "policy_review")
                self.assertEqual(sample_metadata["target_record_type"], "policy_packet_item")
                self.assertIn(sample_metadata["primary_target_record_type"], sample_metadata["target_record_types"])
                self.assertGreaterEqual(len(sample_metadata["target_record_types"]), 4)
                self.assertEqual(sample_metadata["document_count"], 1)
                self.assertEqual(sample_metadata["format"], "crosspage")
                self.assertGreaterEqual(sample_metadata["minimum_gap_pages_between_primary_and_last_evidence"], 70)
                self.assertGreaterEqual(len(sample_metadata["join_requirements"]), 5)
                self.assertIn(sample_metadata["lob"], {"BOP", "CGL", "WC"})
                self.assertIn("policy_number", sample_metadata["schema_fields"])
                self.assertIn("record_type", sample_metadata["schema_fields"])
                self.assertEqual(len(ground_truth), case["num_policy_items"])
                self.assertEqual(len(ground_truth), case["num_target_records"])
                self.assertGreater(case["num_policy_items"], case["num_primary_policy_items"])
                record_types = {record["record_type"] for record in ground_truth}
                self.assertIn("policy_form_item", record_types)
                self.assertIn("policy_endorsement_item", record_types)
                self.assertIn("policy_premium_item", record_types)
                self.assertIn("policy_location_item", record_types)

                first = ground_truth[0]
                self.assertIn("record_type", first)
                self.assertIn("form_number", first)
                self.assertIn("policy_number", first)
                self.assertIn("lob", first)
                self.assertNotIn("incident_number", first)

                html = (out_dir / "html" / f"{sample_id}.html").read_text(encoding="utf-8")
                if sample_id.startswith("multihop_bop"):
                    self.assertIn("B U S I N E S S O W N E R S   D E C L A R A T I O N S", html)
                    self.assertNotIn("BOP-000", html)
                    self.assertNotIn("BP-EN-", html)
                    self.assertNotIn("item_id", sample_metadata["schema_fields"])
                    self.assertNotIn("record_id", sample_metadata["schema_fields"])
                    self.assertNotIn("applies_to_record_id", sample_metadata["schema_fields"])
                    self.assertNotIn("materiality", sample_metadata["schema_fields"])
                    self.assertNotIn("item number", html.lower())
                if sample_metadata["lob"] == "CGL":
                    endorsement_records = [
                        record for record in ground_truth if record["record_type"] == "policy_endorsement_item"
                    ]
                    for record in endorsement_records:
                        self.assertIn(
                            f'<div class="endorsement-title">{record["exclusion_name"]}</div>',
                            html,
                        )
                self.assertIn("premium summary", html.lower())
                self.assertNotIn("join on", html.lower())
                self.assertNotIn("renewal application", html.lower())
                self.assertNotIn("application schedule", html.lower())
                self.assertNotIn("expiring policy", html.lower())

            by_lob = {case["lob"]: case["id"] for case in metadata["cases"]}
            bop = json.loads((out_dir / "ground_truth" / f"{by_lob['BOP']}.json").read_text(encoding="utf-8"))[0]
            wc = json.loads((out_dir / "ground_truth" / f"{by_lob['WC']}.json").read_text(encoding="utf-8"))[0]
            cgl = json.loads((out_dir / "ground_truth" / f"{by_lob['CGL']}.json").read_text(encoding="utf-8"))[0]

            self.assertIn("location_number", bop)
            self.assertIn("building_number", bop)
            self.assertIn("coverage", bop)
            self.assertIn("class_code", wc)
            self.assertIn("annual_payroll", wc)
            self.assertIn("manual_rate", wc)
            self.assertIn("coverage_part", cgl)
            self.assertIn("exposure_basis", cgl)
            self.assertIn("exclusion_name", cgl)

    def test_config_uses_real_policy_review_join_shapes(self) -> None:
        self.assertGreaterEqual(len(POLICY_MULTIHOP_CASE_CONFIGS), 3)
        all_edges = {edge for config in POLICY_MULTIHOP_CASE_CONFIGS for edge in config.join_requirements}

        self.assertIn("form_number -> forms and endorsements schedule", all_edges)
        self.assertIn("form_number/edition_date/form_title -> forms and endorsements schedule", all_edges)
        self.assertIn("location_number/building_number/coverage -> premium summary", all_edges)
        self.assertIn("state/class_code -> payroll and rate schedule", all_edges)
        self.assertIn("coverage_part -> limits schedule", all_edges)
        self.assertNotIn("item_id -> renewal application schedule", all_edges)
        self.assertFalse(any("application" in edge.lower() for edge in all_edges))
        self.assertFalse(any("expiring" in edge.lower() for edge in all_edges))
        self.assertFalse(any("coverage_item_id" in edge.lower() for edge in all_edges))


if __name__ == "__main__":
    unittest.main()
