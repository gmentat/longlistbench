import unittest

from benchmarks.evaluation_metrics import (
    evaluate_extraction,
    evaluate_record_extraction,
    uses_record_evaluator,
)


class EvaluationMetricsTests(unittest.TestCase):
    def test_generic_rows_without_record_type_use_record_evaluator(self):
        ground_truth = [
            {
                "vehicle": "118",
                "state": "Arkansas",
                "identified_miles": 2750.1,
                "unidentified_miles": 60.4,
                "total_miles": 2810.5,
            }
        ]
        predicted = [
            {
                "vehicle": "118",
                "state": "Arkansas",
                "identified_miles": 2750.1,
                "unidentified_miles": 60.4,
                "total_miles": 2810.5,
            }
        ]

        self.assertTrue(uses_record_evaluator(ground_truth))
        metrics = evaluate_record_extraction(predicted, ground_truth)
        self.assertEqual(metrics["ground_truth_count"], 1)
        self.assertEqual(metrics["predicted_count"], 1)
        self.assertEqual(metrics["f1"], 1.0)

    def test_loss_run_incidents_keep_incident_evaluator(self):
        ground_truth = [{"incident_number": "INC001", "policy_number": "P1"}]

        self.assertFalse(uses_record_evaluator(ground_truth))

    def test_record_type_is_not_required_for_generic_matching(self):
        ground_truth = [
            {
                "record_type": "bop_coverage_item",
                "policy_number": "BP1",
                "named_insured": "Example LLC",
                "coverage": "Business Personal Property",
                "limit": 60000,
            }
        ]
        predicted = [
            {
                "record_type": "coverage_row",
                "policy_number": "BP1",
                "named_insured": "Example LLC",
                "coverage": "Business Personal Property",
                "limit": "$60,000",
            }
        ]

        metrics = evaluate_record_extraction(predicted, ground_truth)

        self.assertEqual(metrics["f1"], 1.0)

    def test_global_policy_fields_do_not_inflate_generic_scores(self):
        ground_truth = [
            {
                "policy_number": "BP1",
                "named_insured": "Example LLC",
                "policy_period": "01/01/2026 to 01/01/2027",
                "coverage": "Business Personal Property",
            }
        ]
        predicted = [
            {
                "policy_number": "BP1",
                "named_insured": "Example LLC",
                "policy_period": "01/01/2026 to 01/01/2027",
            }
        ]

        metrics = evaluate_record_extraction(predicted, ground_truth)

        self.assertEqual(metrics["found"], 0)
        self.assertEqual(metrics["total_gold_field_pairs"], 1)
        self.assertEqual(metrics["recall"], 0.0)

    def test_blank_generic_fields_are_not_scored_as_required_facts(self):
        ground_truth = [
            {
                "record_type": "cgl_exposure_item",
                "item_id": "CGL-0002",
                "form_number": "CG 20 10",
                "endorsement_number": "",
                "endorsement_effective_date": "",
            }
        ]
        predicted = [
            {
                "record_type": "cgl_exposure_item",
                "item_id": "CGL-0002",
                "form_number": "CG 20 10",
            }
        ]

        metrics = evaluate_record_extraction(predicted, ground_truth)

        self.assertEqual(metrics["f1"], 1.0)
        self.assertEqual(metrics["total_gold_field_pairs"], metrics["total_pred_field_pairs"])

    def test_generic_accounting_parentheses_match_negative_numbers(self):
        ground_truth = [{"jurisdiction": "PA", "tax_due_credit": -116.08}]
        predicted = [{"jurisdiction": "PA", "tax_due_credit": "($116.08)"}]

        metrics = evaluate_record_extraction(predicted, ground_truth)

        self.assertEqual(metrics["f1"], 1.0)

    def test_generic_id_only_prediction_does_not_pass_full_record_scoring(self):
        ground_truth = [
            {
                "unit_number": "TRK-101",
                "jurisdiction": "PA",
                "taxable_miles": 12500,
                "tax_due": 742.19,
            }
        ]
        predicted = [
            {
                "unit_number": "TRK-101",
                "jurisdiction": "PA",
            }
        ]

        metrics = evaluate_record_extraction(predicted, ground_truth)

        self.assertEqual(metrics["found"], 2)
        self.assertEqual(metrics["total_gold_field_pairs"], 4)
        self.assertEqual(metrics["total_pred_field_pairs"], 2)
        self.assertEqual(metrics["recall"], 0.5)
        self.assertLess(metrics["f1"], 1.0)

    def test_zero_default_financial_breakdowns_are_not_scored(self):
        ground_truth = [
            {
                "incident_number": "#10001",
                "reference_number": "L260001",
                "company_name": "Example Trucking",
                "coverage_type": "Liability",
                "status": "Open",
                "policy_number": "P1",
                "policy_state": "PA",
                "description": "Rear-end collision",
                "date_of_loss": "01/01/2026",
                "loss_state": "PA",
                "date_reported": "01/02/2026",
                "insured": "Example Trucking",
                "bi": {"reserve": 100.0, "paid": 0.0, "recovered": 0.0, "total_incurred": 100.0},
            }
        ]
        predicted = [
            {
                "incident_number": "#10001",
                "reference_number": "L260001",
                "company_name": "Example Trucking",
                "coverage_type": "Liability",
                "status": "Open",
                "policy_number": "P1",
                "policy_state": "PA",
                "description": "Rear-end collision",
                "date_of_loss": "01/01/2026",
                "loss_state": "PA",
                "date_reported": "01/02/2026",
                "insured": "Example Trucking",
            }
        ]

        metrics = evaluate_extraction(predicted, ground_truth)

        self.assertLess(metrics["recall"], 1.0)
        self.assertEqual(metrics["total_gold_field_pairs"], metrics["total_pred_field_pairs"] + 2)

    def test_claim_description_trailing_period_is_normalized(self):
        ground_truth = [
            {
                "incident_number": "#10001",
                "reference_number": "L260001",
                "company_name": "Example Trucking",
                "coverage_type": "Liability",
                "status": "Open",
                "policy_number": "P1",
                "policy_state": "PA",
                "description": "Rear-end collision",
                "date_of_loss": "01/01/2026",
                "loss_state": "PA",
                "date_reported": "01/02/2026",
                "insured": "Example Trucking",
            }
        ]
        predicted = [{**ground_truth[0], "description": "Rear-end collision."}]

        metrics = evaluate_extraction(predicted, ground_truth)

        self.assertEqual(metrics["f1"], 1.0)

    def test_claim_unit_number_matches_full_vehicle_context_by_suffix(self):
        ground_truth = [
            {
                "incident_number": "#10001",
                "reference_number": "L260001",
                "company_name": "Example Trucking",
                "coverage_type": "Liability",
                "status": "Open",
                "policy_number": "P1",
                "policy_state": "PA",
                "unit_number": "2024 KW 600001",
                "description": "Rear-end collision",
                "date_of_loss": "01/01/2026",
                "loss_state": "PA",
                "date_reported": "01/02/2026",
                "insured": "Example Trucking",
            }
        ]
        predicted = [{**ground_truth[0], "unit_number": "600001"}]

        metrics = evaluate_extraction(predicted, ground_truth)

        self.assertEqual(metrics["f1"], 1.0)

    def test_empty_incident_number_does_not_match_known_incident(self):
        ground_truth = [
            {
                "incident_number": "#10001",
                "reference_number": "L260001",
                "company_name": "Example Trucking",
                "coverage_type": "Liability",
                "status": "Open",
                "policy_number": "P1",
                "policy_state": "PA",
                "description": "Rear-end collision",
                "date_of_loss": "01/01/2026",
                "loss_state": "PA",
                "date_reported": "01/02/2026",
                "insured": "Example Trucking",
            }
        ]
        predicted = [
            {
                "incident_number": "",
                "reference_number": "L260001",
                "company_name": "Example Trucking",
                "coverage_type": "Liability",
                "status": "Open",
                "policy_number": "P1",
                "policy_state": "PA",
                "description": "Rear-end collision",
                "date_of_loss": "01/01/2026",
                "loss_state": "PA",
                "date_reported": "01/02/2026",
                "insured": "Example Trucking",
            }
        ]

        metrics = evaluate_extraction(predicted, ground_truth)

        self.assertEqual(metrics["found"], 0)
        self.assertEqual(metrics["f1"], 0.0)

    def test_claim_id_only_prediction_does_not_pass_full_incident_scoring(self):
        ground_truth = [
            {
                "incident_number": "#10001",
                "reference_number": "L260001",
                "company_name": "Example Trucking",
                "coverage_type": "Liability",
                "status": "Open",
                "policy_number": "P1",
                "policy_state": "PA",
                "description": "Rear-end collision",
                "date_of_loss": "01/01/2026",
                "loss_state": "PA",
                "date_reported": "01/02/2026",
                "insured": "Example Trucking",
                "bi": {"reserve": 1000.0, "paid": 250.0, "recovered": 0.0, "total_incurred": 1250.0},
            }
        ]
        predicted = [
            {
                **ground_truth[0],
                "company_name": "Wrong Company",
                "coverage_type": "Cargo",
                "status": "Closed",
                "policy_number": "P2",
                "policy_state": "OH",
                "description": "Wrong loss description",
                "date_of_loss": "02/01/2026",
                "loss_state": "OH",
                "date_reported": "02/02/2026",
                "insured": "Wrong Insured",
                "bi": {"reserve": 0.0, "paid": 0.0, "recovered": 0.0, "total_incurred": 0.0},
            }
        ]

        metrics = evaluate_extraction(predicted, ground_truth)

        self.assertEqual(metrics["found"], 10)
        self.assertEqual(metrics["total_gold_field_pairs"], 23)
        self.assertEqual(metrics["total_pred_field_pairs"], 20)
        self.assertEqual(metrics["exact_record_matches"], 0)
        self.assertLess(metrics["recall"], 0.5)
        self.assertLess(metrics["f1"], 0.5)


if __name__ == "__main__":
    unittest.main()
