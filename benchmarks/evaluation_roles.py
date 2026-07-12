"""Stable release taxonomy for interpreting benchmark family results."""

SCALE_CONTROL_REGIMES = frozenset(
    {
        "driver_schedule_spreadsheet_export",
        "ifta_mileage_by_vehicle",
        "ifta_tax_return_summary",
        "vehicle_schedule_spreadsheet_export",
    }
)

STRUCTURAL_CHALLENGE_REGIMES = frozenset(
    {
        "claim_crosspage_multihop",
        "driver_mvr_request_and_roster",
        "ifta_multisection_return_packet",
        "ifta_return_schedule_details",
        "ifta_tax_return_inquiry_detail",
        "loss_run_external",
        "policy_multi_hop",
    }
)


def evaluation_role(complexity_regime: str) -> str:
    """Map a declared document family to its preassigned evaluation role."""
    if complexity_regime in SCALE_CONTROL_REGIMES:
        return "scale_control"
    if complexity_regime in STRUCTURAL_CHALLENGE_REGIMES:
        return "structural_challenge"
    return "unclassified"
