import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_REPORT = ROOT / "benchmarks/results/codex_full_current_ocr_v2/evaluation_report.json"
CLAUDE_REPORT = ROOT / "benchmarks/results/claude_opus48_full_current_ocr_v2/evaluation_report.json"

FAMILY_LABELS = {
    "ifta_multisection_return_packet": "IFTA multisection return packet",
    "driver_mvr_request_and_roster": "Driver/MVR request and roster",
    "policy_multi_hop": "Policy multi-hop",
    "ifta_tax_return_inquiry_detail": "IFTA tax return inquiry detail",
    "ifta_return_schedule_details": "IFTA return schedule details",
    "claim_crosspage_multihop": "Claim cross-page multi-hop",
    "loss_run_external": "External loss run",
    "driver_schedule_spreadsheet_export": "Driver schedule spreadsheet export",
    "ifta_tax_return_summary": "IFTA tax return summary",
    "ifta_mileage_by_vehicle": "IFTA mileage by vehicle",
    "vehicle_schedule_spreadsheet_export": "Vehicle schedule spreadsheet export",
}


def _load_stats(path: Path) -> tuple[dict, dict]:
    report = json.loads(path.read_text(encoding="utf-8"))
    assert len(report["model_stats"]) == 1
    return report, next(iter(report["model_stats"].values()))


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _tex_int(value: int) -> str:
    return f"{value:,}".replace(",", "{,}")


def _tex_pct(value: float) -> str:
    return _pct(value).replace("%", r"\%")


def test_release_tables_match_saved_reports() -> None:
    codex_report, codex = _load_stats(CODEX_REPORT)
    claude_report, claude = _load_stats(CLAUDE_REPORT)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    results_tex = (ROOT / "paper/contents/5_results.tex").read_text(encoding="utf-8")

    assert codex_report["dataset"]["manifest_sha256"] == claude_report["dataset"]["manifest_sha256"]
    for stats in (codex, claude):
        assert stats["total_samples"] == 36
        assert stats["total_rows"] == 33_450
        assert stats["errors"] == 0

    readme_overall_rows = [
        ("Codex CLI `gpt-5.5`, xhigh", codex),
        ("Claude Code `claude-opus-4-8`, xhigh", claude),
    ]
    for label, stats in readme_overall_rows:
        expected = (
            f"| {label} | 36 | 33,450 | 0 | {_pct(stats['exact_record_recall'])} | "
            f"{stats['complete_documents']}/36 ({_pct(stats['complete_document_rate'])}) | "
            f"{_pct(stats['weighted_f1'])} |"
        )
        assert expected in readme

    expected_tex_rows = [
        (r"Codex CLI \texttt{gpt-5.5}, xhigh reasoning", codex),
        (r"Claude Code \texttt{opus-4-8}, xhigh effort", claude),
    ]
    for label, stats in expected_tex_rows:
        expected = (
            f"{label} & 36 & 33{{,}}450 & {_tex_pct(stats['exact_record_recall'])} & "
            f"{stats['complete_documents']}/36 ({_tex_pct(stats['complete_document_rate'])}) & "
            f"{_tex_pct(stats['weighted_f1'])} \\\\"
        )
        assert expected in results_tex

    for role_key, role_label in (
        ("structural_challenge", "Structural challenges"),
        ("scale_control", "Scale tests"),
    ):
        codex_role = codex["by_evaluation_role"][role_key]
        claude_role = claude["by_evaluation_role"][role_key]
        assert codex_role["count"] == claude_role["count"]
        assert codex_role["rows"] == claude_role["rows"]
        readme_role = (
            f"| {role_label} | {codex_role['count']} | {codex_role['rows']:,} | "
            f"{_pct(codex_role['exact_record_recall'])} | "
            f"{_pct(claude_role['exact_record_recall'])} | "
            f"{codex_role['complete_documents']}/{codex_role['count']} "
            f"({_pct(codex_role['complete_document_rate'])}) | "
            f"{claude_role['complete_documents']}/{claude_role['count']} "
            f"({_pct(claude_role['complete_document_rate'])}) |"
        )
        assert readme_role in readme
        tex_role = (
            f"{role_label} & {codex_role['count']} & {_tex_int(codex_role['rows'])} & "
            f"{_tex_pct(codex_role['exact_record_recall'])} & "
            f"{_tex_pct(claude_role['exact_record_recall'])} & "
            f"{codex_role['complete_documents']}/{codex_role['count']} "
            f"({_tex_pct(codex_role['complete_document_rate'])}) & "
            f"{claude_role['complete_documents']}/{claude_role['count']} "
            f"({_tex_pct(claude_role['complete_document_rate'])}) \\\\"
        )
        assert tex_role in results_tex

    codex_families = codex["by_complexity_regime"]
    claude_families = claude["by_complexity_regime"]
    for family_key, label in FAMILY_LABELS.items():
        codex_family = codex_families[family_key]
        claude_family = claude_families[family_key]
        assert codex_family["count"] == claude_family["count"]
        assert codex_family["rows"] == claude_family["rows"]

        readme_row = (
            f"| {label} | {codex_family['count']} | {codex_family['rows']:,} | "
            f"{_pct(codex_family['exact_record_recall'])} | "
            f"{_pct(claude_family['exact_record_recall'])} |"
        )
        assert readme_row in readme

        tex_row = (
            f"{label} & {codex_family['count']} & {_tex_int(codex_family['rows'])} & "
            f"{_tex_pct(codex_family['exact_record_recall'])} & "
            f"{_tex_pct(claude_family['exact_record_recall'])} & "
            f"{_tex_pct(codex_family['weighted_f1'])} & "
            f"{_tex_pct(claude_family['weighted_f1'])} \\\\"
        )
        assert tex_row in results_tex

    codex_stressors = codex["by_stressor"]
    claude_stressors = claude["by_stressor"]
    stressor_sentence = (
        f"Heterogeneous lists score "
        f"{_tex_pct(codex_stressors['heterogeneous_record_list']['exact_record_recall'])} "
        f"for Codex and "
        f"{_tex_pct(claude_stressors['heterogeneous_record_list']['exact_record_recall'])} "
        f"for Claude; long-range evidence scores "
        f"{_tex_pct(codex_stressors['long_range_evidence']['exact_record_recall'])} and "
        f"{_tex_pct(claude_stressors['long_range_evidence']['exact_record_recall'])}; "
        f"split records score "
        f"{_tex_pct(codex_stressors['split_records']['exact_record_recall'])} and "
        f"{_tex_pct(claude_stressors['split_records']['exact_record_recall'])}; "
        f"inherited context scores "
        f"{_tex_pct(codex_stressors['inherited_context']['exact_record_recall'])} and "
        f"{_tex_pct(claude_stressors['inherited_context']['exact_record_recall'])}."
    )
    assert stressor_sentence in results_tex
