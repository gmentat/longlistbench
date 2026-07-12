import json

import pytest

from benchmarks import run_claude_cli_evaluation as runner


def test_parse_result_payload_and_metadata() -> None:
    payload = {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "duration_ms": 1250,
        "num_turns": 3,
        "total_cost_usd": 0.25,
        "session_id": "test-session",
        "modelUsage": {
            "claude-opus-4-8": {
                "inputTokens": 10,
                "cacheReadInputTokens": 20,
                "cacheCreationInputTokens": 30,
                "outputTokens": 40,
            },
            "claude-haiku-4-5": {
                "inputTokens": 2,
                "cacheReadInputTokens": 0,
                "cacheCreationInputTokens": 0,
                "outputTokens": 1,
            },
        },
    }

    parsed = runner._parse_result_payload("warning\n" + json.dumps(payload))
    metadata = runner._metadata_from_payload(parsed)

    assert metadata["requested_model"] == "claude-opus-4-8"
    assert metadata["duration_seconds"] == 1.25
    assert metadata["tokens"] == {
        "requests": 3,
        "input_tokens": 62,
        "cached_input_tokens": 20,
        "cache_creation_input_tokens": 30,
        "output_tokens": 41,
        "total_tokens": 103,
    }
    assert metadata["estimated_api_cost_usd"] == 0.25


def test_cli_version_is_labeled_as_metadata_write_observation(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runner, "_claude_cli_version", lambda: "2.1.207 (Claude Code)")

    runner._write_run_metadata(
        output_dir=tmp_path,
        transcript="ocr",
        sample_metadata={},
    )

    payload = json.loads((tmp_path / runner.RUN_METADATA_FILE).read_text(encoding="utf-8"))
    assert payload["cli_version_observed_at_metadata_write"] == "2.1.207 (Claude Code)"
    assert "claude_cli_version" not in payload


def test_metadata_rejects_unexpected_inference_model() -> None:
    with pytest.raises(ValueError, match="Requested claude-opus-4-8"):
        runner._metadata_from_payload(
            {
                "modelUsage": {
                    "claude-sonnet-4-6": {
                        "inputTokens": 1,
                        "outputTokens": 1,
                    }
                }
            }
        )
