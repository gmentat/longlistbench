import json
import unittest

from benchmarks.extraction_core import (
    build_record_extraction_prompt,
    parse_json_response,
)


class ExtractionCoreTests(unittest.TestCase):
    def test_build_record_extraction_prompt_uses_generic_records_contract(self):
        ground_truth = [
            {
                "record_type": "vehicle_state_mileage_row",
                "record_id": "hidden-001",
                "unit_number": "TRK-101",
                "jurisdiction": "PA",
                "taxable_miles": 1200,
            }
        ]

        prompt = build_record_extraction_prompt("OCR BODY", ground_truth)

        self.assertIn('{ "records": [ ... ] }', prompt)
        self.assertIn("vehicle_state_mileage_row", prompt)
        self.assertIn("unit_number", prompt)
        self.assertIn("jurisdiction", prompt)
        self.assertIn("taxable_miles", prompt)
        self.assertNotIn("hidden-001", prompt)
        self.assertNotIn("record_id", prompt)
        self.assertIn("OCR BODY", prompt)

    def test_parse_json_response_salvages_truncated_records_array(self):
        raw = json.dumps(
            {
                "records": [
                    {"unit_number": "TRK-101", "jurisdiction": "PA"},
                    {"unit_number": "TRK-102", "jurisdiction": "OH"},
                ]
            }
        )
        truncated = raw.rsplit("}", 1)[0]

        parsed = parse_json_response(truncated)

        self.assertEqual(
            parsed,
            {
                "records": [
                    {"unit_number": "TRK-101", "jurisdiction": "PA"},
                    {"unit_number": "TRK-102", "jurisdiction": "OH"},
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
