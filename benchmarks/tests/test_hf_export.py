import json
import tempfile
import unittest
from pathlib import Path

from benchmarks import export_hf_dataset


class HuggingFaceExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp.name) / "data"
        for relative in [
            "ground_truth",
            "pdfs",
            "transcripts/ocr_gemini",
            "schemas",
        ]:
            (self.data_dir / relative).mkdir(parents=True, exist_ok=True)
        (self.data_dir / "schemas" / "loss_run_incident.schema.json").write_text(
            '{"title":"LossRunIncident","type":"object"}',
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _write_instance(self, instance):
        sample_id = instance["id"]
        target_records = [{"id": sample_id, "value": "expected"}]
        (self.data_dir / "ground_truth" / f"{sample_id}.json").write_text(
            json.dumps(target_records),
            encoding="utf-8",
        )
        (self.data_dir / "pdfs" / f"{sample_id}.pdf").write_bytes(b"%PDF-1.4\n")
        if "ocr" in instance.get("transcripts_available", []):
            (self.data_dir / "transcripts" / "ocr_gemini" / f"{sample_id}.md").write_text(
                f"ocr {sample_id}",
                encoding="utf-8",
            )
        instance["files"] = {
            "ground_truth": f"ground_truth/{sample_id}.json",
            "pdf": f"pdfs/{sample_id}.pdf",
            "ocr_md": f"transcripts/ocr_gemini/{sample_id}.md",
        }
        return instance

    def test_build_config_rows_normalizes_manifest_instances(self):
        instances = [
            self._write_instance(
                {
                    "id": "ifta_mileage_by_vehicle_001",
                    "difficulty": "ifta_mileage_by_vehicle",
                    "format": "production_like_pdf",
                    "domain": "commercial_insurance_operations",
                    "target_record_type": "vehicle_state_mileage_row",
                    "num_target_records": 1,
                    "pages_estimate": 8,
                    "problems": ["high_density_long_list"],
                    "transcripts_available": ["ocr"],
                }
            ),
            self._write_instance(
                {
                    "id": "multihop_012_001_crosspage",
                    "difficulty": "multihop",
                    "format": "crosspage",
                    "domain": "claims",
                    "target_record_type": "loss_run_incident",
                    "num_target_records": 1,
                    "pdf_page_count": 76,
                    "problems": ["cross_page_join"],
                    "transcripts_available": ["ocr"],
                }
            ),
            self._write_instance(
                {
                    "id": "multihop_bop_012_001",
                    "difficulty": "multihop",
                    "format": "crosspage",
                    "domain": "policy_review",
                    "target_record_type": "policy_packet_item",
                    "num_target_records": 1,
                    "pdf_page_count": 90,
                    "problems": ["businessowners_policy"],
                    "transcripts_available": ["ocr"],
                }
            ),
        ]
        (self.data_dir / "manifest.json").write_text(
            json.dumps({"instances": instances}),
            encoding="utf-8",
        )

        rows_by_config = export_hf_dataset.build_config_rows(self.data_dir)

        self.assertEqual(
            [row["document_id"] for row in rows_by_config["core_operations"]],
            ["ifta_mileage_by_vehicle_001"],
        )
        self.assertEqual(
            [row["document_id"] for row in rows_by_config["claim_multihop"]],
            ["multihop_012_001_crosspage"],
        )
        self.assertEqual(
            [row["document_id"] for row in rows_by_config["policy_packets"]],
            ["multihop_bop_012_001"],
        )

        core_row = rows_by_config["core_operations"][0]
        self.assertEqual(core_row["domain"], "commercial_insurance_operations")
        self.assertEqual(core_row["target_field"], "records")
        self.assertEqual(json.loads(core_row["ground_truth"])["records"][0]["id"], "ifta_mileage_by_vehicle_001")
        self.assertEqual(core_row["ocr_transcript"], "ocr ifta_mileage_by_vehicle_001")

        policy_row = rows_by_config["policy_packets"][0]
        self.assertEqual(policy_row["target_field"], "records")
        self.assertEqual(policy_row["target_record_type"], "policy_packet_item")
        self.assertEqual(json.loads(policy_row["ground_truth"])["records"][0]["id"], "multihop_bop_012_001")
        self.assertEqual(policy_row["ocr_transcript"], "ocr multihop_bop_012_001")

    def test_dataset_card_lists_hf_config_paths(self):
        summary = {
            "core_operations": {
                "rows": 28,
                "targets": 31088,
                "min_targets": 260,
                "max_targets": 2571,
                "min_pages": 15,
                "max_pages": 144,
                "domains": {"commercial_insurance_operations": 28},
                "target_fields": ["incidents", "records"],
            },
            "claim_multihop": {
                "rows": 3,
                "targets": 77,
                "min_targets": 12,
                "max_targets": 40,
                "min_pages": 76,
                "max_pages": 198,
                "domains": {"claims": 3},
                "target_fields": ["incidents"],
            },
            "policy_packets": {
                "rows": 5,
                "targets": 1945,
                "min_targets": 48,
                "max_targets": 800,
                "min_pages": 30,
                "max_pages": 214,
                "domains": {"policy_review": 5},
                "target_fields": ["records"],
            },
        }

        card = export_hf_dataset.dataset_card("kaydotai/LongListBench", summary)

        self.assertIn("pretty_name: LongListBench", card)
        self.assertIn("- benchmark", card)
        self.assertIn("path: data/core_operations/test-*.parquet", card)
        self.assertIn("Records/doc range", card)
        self.assertIn("| `core_operations` |", card)
        self.assertIn('load_dataset("kaydotai/LongListBench", "core_operations", split="test")', card)
        self.assertIn("Pdf(decode=False)", card)
        self.assertIn("## Canonical Scoring", card)
        self.assertIn("evaluate_record_extraction", card)
        self.assertIn("schemas/policy_packet_item.schema.json", card)
        self.assertIn("schemas/loss_run_claim_row.schema.json", card)
        self.assertIn("schemas/policy_schedule_record.schema.json", card)
        self.assertIn("@misc{fedoruk2026longlistbench", card)
        self.assertIn("| `policy_packets` |", card)


if __name__ == "__main__":
    unittest.main()
