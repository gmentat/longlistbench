import json
import unittest
from unittest import mock

from benchmarks import evaluate_models, regime_agentic, regime_chunked, regime_oneshot


def _full_incident(num: str = "#30001") -> dict:
    """A schema-complete incident usable as a prediction fixture."""
    fb = {"reserve": 0.0, "paid": 0.0, "recovered": 0.0, "total_incurred": 0.0}
    return {
        "incident_number": num,
        "reference_number": "L230001",
        "company_name": "Acme Trucking",
        "division": "General",
        "coverage_type": "Liability",
        "status": "Open",
        "policy_number": "P1",
        "policy_state": "CA",
        "cause_code": None,
        "description": "rear-end collision",
        "handler": "Claims Adjuster",
        "unit_number": None,
        "date_of_loss": "01/01/2023",
        "loss_state": "CA",
        "date_reported": "01/02/2023",
        "agency": None,
        "insured": "Acme Trucking",
        "claimants": [],
        "driver_name": None,
        "bi": dict(fb),
        "pd": dict(fb),
        "lae": dict(fb),
        "ded": dict(fb),
        "adjuster_notes": None,
    }


class Gpt55RegimeRegistrationTests(unittest.TestCase):
    """All three GPT-5.5 regimes are registered and wired to the right extractors."""

    def test_three_gpt55_regimes_registered(self) -> None:
        expected = {
            "gpt55_oneshot": regime_oneshot.extract_with_openai_oneshot,
            "gpt55_chunked": regime_chunked.extract_with_openai,
            "gpt55_agent": regime_agentic.extract_with_openai_agent,
        }
        for key, extract_fn in expected.items():
            self.assertIn(key, evaluate_models.MODELS)
            cfg = evaluate_models.MODELS[key]
            self.assertIs(cfg.extract_fn, extract_fn)
            self.assertEqual(cfg.provider, "OpenAI")


class AgenticExtractionTests(unittest.TestCase):
    def test_extract_with_openai_agent_parses_session_file(self) -> None:
        payload = json.dumps({"incidents": [_full_incident()]}).encode("utf-8")
        # Seam returns a result dict; the session-file path wins over final_output.
        seam = {"final_output": None, "file_bytes": payload, "usage": None, "behavior": []}
        with mock.patch.object(regime_agentic, "_run_agent_extraction", return_value=seam):
            result = regime_agentic.extract_with_openai_agent(
                client=None, ocr_text="irrelevant ocr text", model_id="gpt-5.5"
            )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["incident_number"], "#30001")

    def test_extract_with_openai_agent_falls_back_to_final_output(self) -> None:
        fenced = "```json\n" + json.dumps({"incidents": [_full_incident("#30002")]}) + "\n```"
        # No file bytes -> recover from final_output via parse_json_response.
        seam = {"final_output": fenced, "file_bytes": None, "usage": None, "behavior": []}
        with mock.patch.object(regime_agentic, "_run_agent_extraction", return_value=seam):
            result = regime_agentic.extract_with_openai_agent(
                client=None, ocr_text="irrelevant", model_id="gpt-5.5"
            )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["incident_number"], "#30002")

    def test_extract_with_openai_agent_raises_when_no_output(self) -> None:
        seam = {"final_output": None, "file_bytes": None, "usage": None, "behavior": []}
        with mock.patch.object(regime_agentic, "_run_agent_extraction", return_value=seam):
            with self.assertRaises(ValueError):
                regime_agentic.extract_with_openai_agent(
                    client=None, ocr_text="irrelevant", model_id="gpt-5.5"
                )


class OpenAiOneshotTests(unittest.TestCase):
    def _fake_client(self, content: str) -> mock.MagicMock:
        message = mock.MagicMock()
        message.parsed = None  # force JSON-mode parse path
        message.content = content
        response = mock.MagicMock()
        response.choices = [mock.MagicMock(message=message)]
        client = mock.MagicMock()
        client.beta.chat.completions.parse.return_value = response
        return client

    def test_oneshot_single_call_with_large_budget(self) -> None:
        content = json.dumps({"incidents": [_full_incident("#40001")]})
        client = self._fake_client(content)
        result = regime_oneshot.extract_with_openai_oneshot(client, "ocr text", "gpt-5.5")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["incident_number"], "#40001")
        # One-shot makes exactly one model call...
        client.beta.chat.completions.parse.assert_called_once()
        # ...with a large output budget (not the per-chunk 8192 default).
        kwargs = client.beta.chat.completions.parse.call_args.kwargs
        self.assertGreaterEqual(kwargs["max_completion_tokens"], 32000)


if __name__ == "__main__":
    unittest.main()
