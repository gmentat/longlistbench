from benchmarks import run_codex_cli_evaluation as runner


def test_status_summary_fails_when_any_sample_fails() -> None:
    assert runner._all_statuses_succeeded([("a", 0), ("b", "skip")])
    assert not runner._all_statuses_succeeded([])
    assert not runner._all_statuses_succeeded([("a", 0), ("b", "timeout")])
    assert not runner._all_statuses_succeeded([("a", "error: invalid JSON")])
