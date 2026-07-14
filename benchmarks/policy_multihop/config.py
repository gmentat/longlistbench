"""Configuration for policy-centered LongListBench cases."""

from __future__ import annotations

from dataclasses import dataclass


SUITE_NAME = "longlistbench-v1"
SUITE_DESCRIPTION = (
    "Benchmark for long-list entity extraction under layout, OCR, scale, and "
    "long-range cross-page evidence complexity."
)

LEGACY_POLICY_CASE_IDS = {
    "multihop_policy_012_001_crosspage",
    "multihop_policy_025_001_crosspage",
    "mixed_policy_040_001_crosspage",
}


@dataclass(frozen=True)
class PolicyMultiHopCaseConfig:
    id: str
    lob: str
    case_type: str
    target_record_type: str
    num_items: int
    seed_offset: int
    spacer_pages: tuple[int, int, int, int]
    join_requirements: tuple[str, ...]
    complexity_tags: tuple[str, ...]


POLICY_MULTIHOP_CASE_CONFIGS: tuple[PolicyMultiHopCaseConfig, ...] = (
    PolicyMultiHopCaseConfig(
        id="multihop_bop_012_001",
        lob="BOP",
        case_type="policy_multi_hop",
        target_record_type="bop_coverage_item",
        num_items=48,
        seed_offset=501,
        spacer_pages=(12, 10, 10, 8),
        join_requirements=(
            "location_number/building_number -> businessowners declarations",
            "location_number/building_number -> described premises schedule",
            "location_number/building_number/class_code -> classification/rating schedule",
            "form_number/edition_date/form_title -> forms and endorsements schedule",
            "location_number/building_number/coverage/form_number -> endorsement detail pages",
            "location_number/building_number/coverage -> premium summary",
            "form_number/coverage/location/building -> material clause pages",
        ),
        complexity_tags=(
            "businessowners_policy",
            "location_scoped_coverage",
            "form_endorsement_links",
            "material_clause_extraction",
            "long_range_evidence",
            "heterogeneous_record_list",
        ),
    ),
    PolicyMultiHopCaseConfig(
        id="multihop_wc_025_001",
        lob="WC",
        case_type="policy_multi_hop",
        target_record_type="wc_class_code_item",
        num_items=60,
        seed_offset=502,
        spacer_pages=(18, 16, 14, 12),
        join_requirements=(
            "state/class_code/location_number -> workers compensation information page",
            "state/class_code -> classification schedule",
            "state/class_code -> payroll and rate schedule",
            "form_number -> forms and endorsements schedule",
            "form_number/edition_date/state/class_code -> endorsement detail pages",
            "state/class_code/location_number -> premium summary",
            "state/class_code/form_number -> material clause pages",
        ),
        complexity_tags=(
            "workers_compensation_policy",
            "class_code_payroll_rating",
            "experience_mod_and_schedule_rating",
            "material_clause_extraction",
            "long_range_evidence",
            "heterogeneous_record_list",
        ),
    ),
    PolicyMultiHopCaseConfig(
        id="mixed_cgl_040_001",
        lob="CGL",
        case_type="mixed",
        target_record_type="cgl_exposure_item",
        num_items=72,
        seed_offset=503,
        spacer_pages=(20, 18, 18, 14),
        join_requirements=(
            "location_number/class_code -> cgl declarations",
            "location_number/class_code -> classification schedule",
            "class_code/exposure_basis -> rating schedule",
            "coverage_part -> limits schedule",
            "form_number -> forms and exclusions schedule",
            "form_number/edition_date/location_number/class_code -> endorsement detail pages",
            "location_number/class_code/exposure_basis -> premium summary",
            "location_number/class_code/form_number -> material clause pages",
        ),
        complexity_tags=(
            "commercial_general_liability",
            "exposure_rating_rows",
            "limits_forms_exclusions",
            "material_clause_extraction",
            "long_range_evidence",
            "heterogeneous_record_list",
            "distractor_forms",
            "distractor_locations",
        ),
    ),
)
