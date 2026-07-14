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
    metadata = runner._metadata_from_payload(parsed, "claude-opus-4-8", "xhigh")

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
        model_key="claude_opus48",
        requested_model="claude-opus-4-8",
        effort="xhigh",
        extra_denied_paths=[tmp_path / "duplicate-data"],
    )

    payload = json.loads((tmp_path / runner.RUN_METADATA_FILE).read_text(encoding="utf-8"))
    assert payload["cli_version_observed_at_metadata_write"] == "2.1.207 (Claude Code)"
    assert payload["additional_denied_paths"] == [str((tmp_path / "duplicate-data").resolve())]
    assert "claude_cli_version" not in payload


def test_run_claude_denies_additional_paths(tmp_path, monkeypatch) -> None:
    (tmp_path / "prompt.md").write_text("extract", encoding="utf-8")
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return type(
            "Completed",
            (),
            {
                "returncode": 0,
                "stdout": json.dumps(
                    {
                        "type": "result",
                        "subtype": "success",
                        "is_error": False,
                        "modelUsage": {"claude-opus-4-8": {}},
                    }
                ),
            },
        )()

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    monkeypatch.setattr(runner, "_claude_cli_version", lambda: "test")

    status, _output, _metadata = runner.run_claude(
        tmp_path,
        tmp_path / "repo",
        60,
        "claude-opus-4-8",
        "xhigh",
        [tmp_path / "duplicate-data"],
    )

    profile = captured["cmd"][captured["cmd"].index("-p") + 1]
    assert status == 0
    assert f'(subpath "{(tmp_path / "repo").resolve()}")' in profile
    assert f'(subpath "{(tmp_path / "duplicate-data").resolve()}")' in profile


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
            },
            "claude-opus-4-8",
            "xhigh",
        )


def test_metadata_accepts_context_qualified_requested_model() -> None:
    metadata = runner._metadata_from_payload(
        {
            "type": "result",
            "modelUsage": {
                "claude-fable-5[1m]": {
                    "inputTokens": 1,
                    "outputTokens": 2,
                }
            },
        },
        "claude-fable-5",
        "xhigh",
    )

    assert metadata["requested_model"] == "claude-fable-5"
    assert metadata["matching_inference_models"] == ["claude-fable-5[1m]"]
