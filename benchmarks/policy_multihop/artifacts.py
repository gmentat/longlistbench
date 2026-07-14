"""Artifact writing for policy-centered multi-hop benchmark cases."""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from ..dataset_layout import (
        artifact_path,
        artifact_relative_path,
        ensure_organized_dataset_dirs,
        manifest_path,
        record_count_summary,
    )
except ImportError:
    from dataset_layout import (
        artifact_path,
        artifact_relative_path,
        ensure_organized_dataset_dirs,
        manifest_path,
        record_count_summary,
    )

from .config import (
    LEGACY_POLICY_CASE_IDS,
    POLICY_MULTIHOP_CASE_CONFIGS,
    SUITE_DESCRIPTION,
    SUITE_NAME,
    PolicyMultiHopCaseConfig,
)
from .html import case_html
from .llm_text import (
    DEFAULT_GEMINI_MODEL,
    DEFAULT_THINKING_LEVEL,
    PolicyTextBank,
    generate_gemini_policy_text_bank,
)
from .records import build_policy_target_records, case_profile, generate_policy_items
from .util import count_pdf_pages, dataset_version, stable_seed, write_json


async def _render_pdf(html_path: Path, pdf_path: Path) -> None:
    synthetic_dir = Path(__file__).resolve().parents[1] / "synthetic"
    if str(synthetic_dir) not in sys.path:
        sys.path.insert(0, str(synthetic_dir))
    from html_to_pdf import html_to_pdf

    await html_to_pdf(html_path, pdf_path)


def _transcripts_available(dataset_dir: Path, sample_id: str) -> list[str]:
    available: list[str] = []
    ocr = artifact_path(dataset_dir, sample_id, "ocr")
    if ocr.exists() and ocr.stat().st_size > 0:
        available.append("ocr")
    return available


def _instance_files(dataset_dir: Path, sample_id: str) -> dict[str, Any]:
    files = {
        "ground_truth": artifact_relative_path(dataset_dir, sample_id, "ground_truth"),
        "pdf": artifact_relative_path(dataset_dir, sample_id, "pdf"),
        "html": artifact_relative_path(dataset_dir, sample_id, "html"),
        "ocr_md": artifact_relative_path(dataset_dir, sample_id, "ocr"),
    }
    for key, artifact in [
        ("json_size_bytes", "ground_truth"),
        ("pdf_size_bytes", "pdf"),
        ("html_size_bytes", "html"),
        ("ocr_size_bytes", "ocr"),
    ]:
        path = artifact_path(dataset_dir, sample_id, artifact)
        files[key] = path.stat().st_size if path.exists() else 0
    return files


def _evidence_map(config: PolicyMultiHopCaseConfig) -> list[dict[str, Any]]:
    gap1, gap2, gap3, gap4 = config.spacer_pages
    if config.lob == "BOP":
        primary = [
            ("businessowners_declarations", 1, "policy_number", ["named_insured", "policy_period"]),
            ("described_premises_schedule", 3 + gap1, "location_number/building_number", ["premises_address"]),
            ("property_and_liability_coverage_schedule", 4 + gap1, "location_number/building_number/coverage", ["limit", "deductible", "valuation"]),
            ("classification_and_rating_schedule", 5 + gap1, "location_number/building_number/class_code", ["classification", "premium"]),
            ("forms_and_endorsements_schedule", 6 + gap1 + gap2, "form_number/edition_date/form_title", ["schedule_source"]),
        ]
    elif config.lob == "WC":
        primary = [
            ("workers_comp_information_page", 1, "policy_number", ["named_insured", "policy_period"]),
            ("classification_schedule", 3 + gap1, "state/class_code", ["classification", "governing_class"]),
            ("payroll_and_rate_schedule", 4 + gap1, "state/class_code/location_number", ["annual_payroll", "manual_rate", "estimated_premium"]),
            ("experience_modification_summary", 5 + gap1, "policy_number", ["experience_mod", "schedule_credit_debit"]),
            ("forms_and_endorsements_schedule", 6 + gap1 + gap2, "form_number", ["form_title", "edition_date"]),
        ]
    else:
        primary = [
            ("cgl_declarations", 1, "policy_number", ["named_insured", "policy_period"]),
            ("limits_schedule", 3 + gap1, "coverage_part", ["limit_type", "limit"]),
            ("classification_and_location_schedule", 4 + gap1, "location_number/class_code", ["classification", "territory"]),
            ("exposure_and_rating_schedule", 5 + gap1, "location_number/class_code/exposure_basis", ["exposure", "rate", "premium"]),
            ("forms_and_exclusions_schedule", 6 + gap1 + gap2, "form_number", ["form_title", "exclusion_name"]),
        ]
    evidence = [
        {"section": section, "approx_page_after_cover": page, "join_key": join_key, "fields": fields}
        for section, page, join_key, fields in primary
    ]
    if config.lob == "BOP":
        evidence.extend(
            [
                {
                    "section": "endorsement_detail_pages",
                    "approx_page_after_cover": 7 + gap1 + gap2 + gap3,
                    "join_key": "location_number/building_number/coverage/form_number",
                    "fields": ["endorsement_effective_date", "limit", "deductible"],
                },
                {
                    "section": "material_policy_provisions",
                    "approx_page_after_cover": 7 + gap1 + gap2,
                    "join_key": "form_number/coverage/location_number/building_number",
                    "fields": ["clause_title", "clause_type", "clause_scope", "clause_text"],
                },
                {
                    "section": "premium_summary",
                    "approx_page_after_cover": 8 + gap1 + gap2 + gap3 + gap4,
                    "join_key": "location_number/building_number/coverage",
                    "fields": ["premium"],
                },
            ]
        )
    else:
        evidence.extend(
            [
                {
                    "section": "endorsement_detail_pages",
                    "approx_page_after_cover": 7 + gap1 + gap2 + gap3,
                    "join_key": "form_number/edition_date/state_or_location/class_code",
                    "fields": ["endorsement_effective_date", "materiality"],
                },
                {
                    "section": "material_policy_provisions",
                    "approx_page_after_cover": 7 + gap1 + gap2,
                    "join_key": "form_number/state_or_location/class_code",
                    "fields": ["clause_title", "clause_type", "clause_scope", "clause_text"],
                },
                {
                    "section": "premium_summary",
                    "approx_page_after_cover": 8 + gap1 + gap2 + gap3 + gap4,
                    "join_key": "state_or_location/class_code/exposure_or_payroll",
                    "fields": ["premium", "estimated_premium"],
                },
            ]
        )
    return evidence


def _schema_fields(items: list[dict[str, Any]]) -> list[str]:
    return sorted({field for item in items for field in item})


def _make_text_bank(
    config: PolicyMultiHopCaseConfig,
    profile: dict[str, str],
    items: list[dict[str, Any]],
    *,
    output_dir: Path,
    text_generator: str,
    gemini_model: str,
    thinking_level: str,
    text_cache_dir: Path | None,
    force_text: bool,
) -> PolicyTextBank | None:
    if text_generator == "template":
        return None
    if text_generator != "gemini":
        raise ValueError(f"Unsupported text generator: {text_generator}")
    cache_dir = text_cache_dir or output_dir / "generated_text" / "policy_multihop"
    print(f"Generating Gemini policy prose for {config.id} ({config.lob})...", flush=True)
    return generate_gemini_policy_text_bank(
        config,
        profile,
        items,
        model=gemini_model,
        thinking_level=thinking_level,
        cache_dir=cache_dir,
        force=force_text,
    )


def _write_case(
    config: PolicyMultiHopCaseConfig,
    dataset_dir: Path,
    *,
    base_seed: int,
    render_pdf: bool,
    text_generator: str,
    gemini_model: str,
    thinking_level: str,
    text_cache_dir: Path | None,
    force_text: bool,
) -> dict[str, Any]:
    ensure_organized_dataset_dirs(dataset_dir)
    rng = random.Random(stable_seed(base_seed, config.id, config.seed_offset))
    profile = case_profile(config, rng)
    primary_items = generate_policy_items(config, profile, base_seed)
    target_records = build_policy_target_records(config, primary_items)
    text_bank = _make_text_bank(
        config,
        profile,
        primary_items,
        output_dir=dataset_dir,
        text_generator=text_generator,
        gemini_model=gemini_model,
        thinking_level=thinking_level,
        text_cache_dir=text_cache_dir,
        force_text=force_text,
    )
    if text_bank:
        print(f"Using {text_bank.generator} policy prose for {config.id}: {text_bank.metadata()['page_kinds']}", flush=True)

    html_path = artifact_path(dataset_dir, config.id, "html")
    pdf_path = artifact_path(dataset_dir, config.id, "pdf")
    ground_truth_path = artifact_path(dataset_dir, config.id, "ground_truth")
    sample_metadata_path = artifact_path(dataset_dir, config.id, "metadata")

    html = case_html(config, profile, primary_items, text_bank=text_bank)
    html_path.write_text(html, encoding="utf-8")
    write_json(ground_truth_path, target_records)
    if render_pdf:
        asyncio.run(_render_pdf(html_path, pdf_path))

    rendered_pages = count_pdf_pages(pdf_path) if render_pdf else None
    estimated_pages = 8 + sum(config.spacer_pages) + (1 if config.case_type == "mixed" else 0)
    metadata = {
        "id": config.id,
        "difficulty": "multihop" if config.case_type == "policy_multi_hop" else "mixed",
        "complexity_regime": config.case_type,
        "format": "crosspage",
        "domain": "policy_review",
        "lob": config.lob,
        "target_record_type": "policy_packet_item",
        "target_record_types": sorted({record["record_type"] for record in target_records}),
        "primary_target_record_type": config.target_record_type,
        "schema_fields": _schema_fields(target_records),
        "num_claims": len(target_records),
        "num_policy_items": len(target_records),
        "num_primary_policy_items": len(primary_items),
        "num_target_records": len(target_records),
        "pages_estimate": rendered_pages or estimated_pages,
        "pdf_page_count": rendered_pages,
        "html_pagination_mode": "flowing_sections",
        "document_count": 1,
        "evidence_pattern": "single_document_policy_packet_long_range_join",
        "minimum_gap_pages_between_primary_and_last_evidence": sum(config.spacer_pages),
        "problems": list(config.complexity_tags),
        "layout_templates": [
            "declarations",
            "locations_or_classifications",
            "coverage_or_limit_schedule",
            "rating_schedule",
            "forms_schedule",
            "material_policy_provisions",
            "endorsement_detail",
            "premium_summary",
            "policy_conditions",
        ],
        "record_collections": {
            record_type: sum(1 for record in target_records if record["record_type"] == record_type)
            for record_type in sorted({record["record_type"] for record in target_records})
        },
        "synthetic_text": {
            "source": "synthetic",
            "real_documents_used_for": "structural reference only",
            "copied_source_text": False,
            "text_generation": text_bank.metadata() if text_bank else {"generator": "template", "model": None},
        },
        "has_duplicates": False,
        "seed": stable_seed(base_seed, config.id, config.seed_offset),
        "join_requirements": list(config.join_requirements),
        "evidence_map": _evidence_map(config),
        "files": _instance_files(dataset_dir, config.id),
        "transcripts_available": _transcripts_available(dataset_dir, config.id),
    }
    write_json(sample_metadata_path, metadata)
    return metadata


def _empty_manifest(base_seed: int) -> dict[str, Any]:
    return {
        "dataset_name": SUITE_NAME,
        "version": dataset_version(),
        "description": SUITE_DESCRIPTION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_seed": base_seed,
        "schema_version": "1.0",
        "layout": {
            "type": "modality_separated",
            "pdfs": "pdfs/{sample_id}.pdf",
            "html": "html/{sample_id}.html",
            "ground_truth": "ground_truth/{sample_id}.json",
            "ocr_transcripts": "transcripts/ocr_gemini/{sample_id}.md",
            "metadata": "metadata/{sample_id}.json",
        },
        "instances": [],
    }


def _remove_legacy_policy_artifacts(dataset_dir: Path) -> None:
    for sample_id in LEGACY_POLICY_CASE_IDS:
        for artifact in ["pdf", "html", "ground_truth", "metadata", "canonical", "ocr"]:
            try:
                path = artifact_path(dataset_dir, sample_id, artifact)
            except ValueError:
                continue
            if path.exists():
                path.unlink()


def _merge_manifest(dataset_dir: Path, new_instances: list[dict[str, Any]], base_seed: int) -> dict[str, Any]:
    existing_path = manifest_path(dataset_dir)
    if existing_path.exists():
        manifest = json.loads(existing_path.read_text(encoding="utf-8"))
    else:
        manifest = _empty_manifest(base_seed)

    replaced_ids = {instance["id"] for instance in new_instances} | LEGACY_POLICY_CASE_IDS
    instances = [
        instance for instance in manifest.get("instances", [])
        if instance.get("id") not in replaced_ids
    ]
    instances.extend(new_instances)
    instances = sorted(instances, key=lambda item: item["id"])

    manifest["dataset_name"] = manifest.get("dataset_name") or SUITE_NAME
    manifest["version"] = dataset_version()
    manifest["description"] = SUITE_DESCRIPTION
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    manifest["instances"] = instances
    manifest["total_instances"] = len(instances)
    manifest.update(record_count_summary(instances))
    manifest["complexity_regimes"] = sorted(
        {str(instance.get("complexity_regime") or instance.get("difficulty")) for instance in instances}
    )
    manifest["transcript_conditions"] = sorted(
        {
            transcript
            for instance in instances
            for transcript in instance.get("transcripts_available", [])
        }
    )
    manifest.setdefault("layout", _empty_manifest(base_seed)["layout"])

    write_json(dataset_dir / "manifest.json", manifest)
    write_json(dataset_dir / "metadata.json", manifest)
    return manifest


def generate_policy_multihop_suite(
    output_dir: Path,
    *,
    base_seed: int = 5252,
    render_pdfs: bool = True,
    case_ids: set[str] | None = None,
    text_generator: str = "template",
    gemini_model: str = DEFAULT_GEMINI_MODEL,
    thinking_level: str = DEFAULT_THINKING_LEVEL,
    text_cache_dir: Path | None = None,
    force_text: bool = False,
) -> dict[str, Any]:
    """Generate policy-centered cross-page cases into the organized dataset layout."""
    ensure_organized_dataset_dirs(output_dir)
    _remove_legacy_policy_artifacts(output_dir)
    selected_configs = [
        config for config in POLICY_MULTIHOP_CASE_CONFIGS if case_ids is None or config.id in case_ids
    ]
    cases = [
        _write_case(
            config,
            output_dir,
            base_seed=base_seed,
            render_pdf=render_pdfs,
            text_generator=text_generator,
            gemini_model=gemini_model,
            thinking_level=thinking_level,
            text_cache_dir=text_cache_dir,
            force_text=force_text,
        )
        for config in selected_configs
    ]
    manifest = _merge_manifest(output_dir, cases, base_seed)

    return {
        "suite_name": "longlistbench-policy-multihop",
        "version": dataset_version(),
        "description": "Single-document BOP/WC/CGL policy multi-hop extraction cases.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_seed": base_seed,
        "total_cases": len(cases),
        "total_documents": len(cases),
        "total_policy_items": sum(case["num_policy_items"] for case in cases),
        "total_primary_policy_items": sum(case["num_primary_policy_items"] for case in cases),
        "case_types": sorted({case["complexity_regime"] for case in cases}),
        "lobs": sorted({case["lob"] for case in cases}),
        "text_generator": text_generator,
        "gemini_model": gemini_model if text_generator == "gemini" else None,
        "gemini_thinking_level": thinking_level if text_generator == "gemini" else None,
        "manifest": "manifest.json",
        "dataset_total_instances": manifest["total_instances"],
        "cases": cases,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate LongListBench policy multi-hop cases")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "data",
        help="Organized dataset directory (default: data)",
    )
    parser.add_argument("--seed", type=int, default=5252, help="Base random seed")
    parser.add_argument("--case-id", action="append", help="Generate only this case id; can be passed multiple times")
    parser.add_argument("--no-pdf", action="store_true", help="Write JSON/HTML/canonical transcripts only; skip PDF rendering")
    parser.add_argument(
        "--text-generator",
        choices=["template", "gemini"],
        default="template",
        help="Generate long policy prose from local templates or Gemini-authored page drafts.",
    )
    parser.add_argument("--gemini-model", default=DEFAULT_GEMINI_MODEL, help="Gemini model for --text-generator gemini")
    parser.add_argument(
        "--thinking-level",
        default=DEFAULT_THINKING_LEVEL,
        choices=["minimal", "low", "medium", "high", "auto", "none"],
        help="Gemini thinking level for --text-generator gemini (default: high)",
    )
    parser.add_argument("--text-cache-dir", type=Path, help="Cache directory for Gemini-generated page drafts")
    parser.add_argument("--force-text", action="store_true", help="Regenerate Gemini page drafts even if cached")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    metadata = generate_policy_multihop_suite(
        args.output,
        base_seed=args.seed,
        render_pdfs=not args.no_pdf,
        case_ids=set(args.case_id) if args.case_id else None,
        text_generator=args.text_generator,
        gemini_model=args.gemini_model,
        thinking_level=args.thinking_level,
        text_cache_dir=args.text_cache_dir,
        force_text=args.force_text,
    )

    print(f"Generated {metadata['total_cases']} policy multi-hop cases in {args.output}")
    print(f"Total documents: {metadata['total_documents']}")
    print(f"Total policy items: {metadata['total_policy_items']}")
    print(f"LOBs: {', '.join(metadata['lobs'])}")
    print(f"Text generator: {metadata['text_generator']}")
