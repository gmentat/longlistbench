import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATHS = {
    "codex_gpt56_sol": ROOT
    / "benchmarks/results/codex_gpt56_sol_full_current_ocr_v2/evaluation_report.json",
    "claude_fable5": ROOT
    / "benchmarks/results/claude_fable5_full_current_ocr_v2/evaluation_report.json",
    "codex_gpt55": ROOT
    / "benchmarks/results/codex_full_current_ocr_v2/evaluation_report.json",
    "claude_opus48": ROOT
    / "benchmarks/results/claude_opus48_full_current_ocr_v2/evaluation_report.json",
}

OVERALL_LABELS = {
    "codex_gpt56_sol": (
        "Codex CLI `gpt-5.6-sol`, xhigh",
        "Codex CLI, GPT-5.6-Sol (xhigh)",
    ),
    "claude_fable5": (
        "Claude Code `claude-fable-5`, xhigh",
        "Claude Code, Fable 5 (xhigh)",
    ),
    "codex_gpt55": (
        "Codex CLI `gpt-5.5`, xhigh",
        "Codex CLI, GPT-5.5 (xhigh)",
    ),
    "claude_opus48": (
        "Claude Code `claude-opus-4-8`, xhigh",
        "Claude Code, Opus 4.8 (xhigh)",
    ),
}

PROBLEM_LABELS = {
    "driver_mvr_request_and_roster": "Sparse record enrichment (driver/MVR)",
    "claim_crosspage_multihop": "Long-range claim joins",
    "ifta_return_schedule_details": "Split return schedules",
    "loss_run_external": "Mixed row/detail loss runs",
    "ifta_tax_return_inquiry_detail": "Tax inquiry detail tables",
    "policy_multi_hop": "Heterogeneous policy records",
    "ifta_multisection_return_packet": "Cross-section return joins",
    "ifta_tax_return_summary": "Tax-summary scale tests",
    "driver_schedule_spreadsheet_export": "Driver-schedule scale test",
    "ifta_mileage_by_vehicle": "Mileage-by-vehicle scale tests",
    "vehicle_schedule_spreadsheet_export": "Vehicle-schedule scale tests",
}


def _load_stats(path: Path, expected_key: str) -> tuple[dict, dict]:
    report = json.loads(path.read_text(encoding="utf-8"))
    assert list(report["model_stats"]) == [expected_key]
    return report, report["model_stats"][expected_key]


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _tex_int(value: int) -> str:
    return f"{value:,}".replace(",", "{,}")


def _tex_pct(value: float) -> str:
    return _pct(value).replace("%", r"\%")


def test_release_tables_match_saved_reports() -> None:
    loaded = {
        key: _load_stats(path, key)
        for key, path in REPORT_PATHS.items()
    }
    reports = {key: value[0] for key, value in loaded.items()}
    stats = {key: value[1] for key, value in loaded.items()}
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    abstract = (ROOT / "paper/contents/0_abstract.tex").read_text(encoding="utf-8")
    results_tex = (ROOT / "paper/contents/5_results.tex").read_text(encoding="utf-8")
    conclusion = (ROOT / "paper/contents/7_conclusion.tex").read_text(encoding="utf-8")

    manifest_hashes = {report["dataset"]["manifest_sha256"] for report in reports.values()}
    assert len(manifest_hashes) == 1
    for report in reports.values():
        assert report["dataset"]["git_dirty"] is False
    for model_stats in stats.values():
        assert model_stats["total_samples"] == 36
        assert model_stats["total_rows"] == 33_450
        assert model_stats["errors"] == 0

    for key, (readme_label, tex_label) in OVERALL_LABELS.items():
        model_stats = stats[key]
        readme_row = (
            f"| {readme_label} | 36 | 33,450 | 0 | "
            f"{_pct(model_stats['exact_record_recall'])} | "
            f"{model_stats['complete_documents']}/36 "
            f"({_pct(model_stats['complete_document_rate'])}) | "
            f"{_pct(model_stats['weighted_f1'])} |"
        )
        assert readme_row in readme
        tex_row = (
            f"{tex_label} & {_tex_pct(model_stats['exact_record_recall'])} & "
            f"{model_stats['complete_documents']}/36 "
            f"({_tex_pct(model_stats['complete_document_rate'])}) & "
            f"{_tex_pct(model_stats['weighted_f1'])} & "
            f"{_tex_pct(model_stats['avg_f1'])} \\\\"
        )
        assert tex_row in results_tex

    sol = stats["codex_gpt56_sol"]
    fable = stats["claude_fable5"]
    for role_key, role_label in (
        ("structural_challenge", "Structural challenges"),
        ("scale_control", "Scale tests"),
    ):
        sol_role = sol["by_evaluation_role"][role_key]
        fable_role = fable["by_evaluation_role"][role_key]
        assert sol_role["count"] == fable_role["count"]
        assert sol_role["rows"] == fable_role["rows"]
        readme_role = (
            f"| {role_label} | {sol_role['count']} | {sol_role['rows']:,} | "
            f"{_pct(sol_role['exact_record_recall'])} | "
            f"{_pct(fable_role['exact_record_recall'])} | "
            f"{sol_role['complete_documents']}/{sol_role['count']} "
            f"({_pct(sol_role['complete_document_rate'])}) | "
            f"{fable_role['complete_documents']}/{fable_role['count']} "
            f"({_pct(fable_role['complete_document_rate'])}) |"
        )
        assert readme_role in readme
        tex_role = (
            f"{role_label} & {sol_role['count']} & {_tex_int(sol_role['rows'])} & "
            f"{_tex_pct(sol_role['exact_record_recall'])} & "
            f"{_tex_pct(fable_role['exact_record_recall'])} & "
            f"{sol_role['complete_documents']}/{sol_role['count']} "
            f"({_tex_pct(sol_role['complete_document_rate'])}) & "
            f"{fable_role['complete_documents']}/{fable_role['count']} "
            f"({_tex_pct(fable_role['complete_document_rate'])}) \\\\"
        )
        assert tex_role in results_tex

    for family_key, label in PROBLEM_LABELS.items():
        sol_family = sol["by_complexity_regime"][family_key]
        fable_family = fable["by_complexity_regime"][family_key]
        assert sol_family["count"] == fable_family["count"]
        assert sol_family["rows"] == fable_family["rows"]
        readme_row = (
            f"| {label} | {sol_family['count']} | {sol_family['rows']:,} | "
            f"{_pct(sol_family['exact_record_recall'])} | "
            f"{_pct(fable_family['exact_record_recall'])} |"
        )
        assert readme_row in readme
        tex_row = (
            f"{label} & {sol_family['count']} & {_tex_int(sol_family['rows'])} & "
            f"{_tex_pct(sol_family['exact_record_recall'])} & "
            f"{_tex_pct(fable_family['exact_record_recall'])} \\\\"
        )
        assert tex_row in results_tex

    sol_stressors = sol["by_stressor"]
    fable_stressors = fable["by_stressor"]
    stressor_sentence = (
        "Exact-record recall for GPT-5.6-Sol and Fable 5 is "
        f"{_tex_pct(sol_stressors['heterogeneous_record_list']['exact_record_recall'])} and "
        f"{_tex_pct(fable_stressors['heterogeneous_record_list']['exact_record_recall'])} "
        "on heterogeneous lists, "
        f"{_tex_pct(sol_stressors['long_range_evidence']['exact_record_recall'])} and "
        f"{_tex_pct(fable_stressors['long_range_evidence']['exact_record_recall'])} "
        "on long-range evidence, "
        f"{_tex_pct(sol_stressors['split_records']['exact_record_recall'])} and "
        f"{_tex_pct(fable_stressors['split_records']['exact_record_recall'])} "
        "on split records, "
        f"{_tex_pct(sol_stressors['inherited_context']['exact_record_recall'])} and "
        f"{_tex_pct(fable_stressors['inherited_context']['exact_record_recall'])} "
        "on inherited context, and "
        f"{_tex_pct(sol_stressors['layout_randomization']['exact_record_recall'])} and "
        f"{_tex_pct(fable_stressors['layout_randomization']['exact_record_recall'])} "
        "under layout randomization."
    )
    assert stressor_sentence in results_tex

    latest_summary = (
        f"recover {_tex_pct(sol['exact_record_recall'])} and "
        f"{_tex_pct(fable['exact_record_recall'])} of records exactly, but reproduce only "
        f"{sol['complete_documents']} and {fable['complete_documents']} of 36 complete document lists"
    )
    assert latest_summary in abstract
    assert (
        f"recover {_tex_pct(sol['exact_record_recall'])} and "
        f"{_tex_pct(fable['exact_record_recall'])} of target records exactly but complete only "
        f"{sol['complete_documents']} and {fable['complete_documents']} of 36 documents"
    ) in conclusion
