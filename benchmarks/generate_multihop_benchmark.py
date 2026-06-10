#!/usr/bin/env python3
"""Generate cross-document multi-hop benchmark packets.

The base LongListBench suite measures long-list extraction from one rendered
document. This extension creates case folders where no single document contains
the full incident record. Systems must join a primary loss-run summary against
supporting documents such as driver rosters, policy registers, cause-code
legends, claimant indexes, and financial ledgers.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

try:
    from .canonical_transcripts import write_canonical_markdown_from_html
except ImportError:
    from canonical_transcripts import write_canonical_markdown_from_html


SUITE_NAME = "longlistbench-multihop"
SUITE_DESCRIPTION = (
    "Cross-document long-list extraction cases requiring joins across rendered "
    "loss-run summaries and supporting reference documents."
)


@dataclass(frozen=True)
class MultiHopCaseConfig:
    id: str
    case_type: str
    num_incidents: int
    seed_offset: int
    documents: tuple[str, ...]
    join_requirements: tuple[str, ...]
    complexity_tags: tuple[str, ...]


MULTIHOP_CASE_CONFIGS: tuple[MultiHopCaseConfig, ...] = (
    MultiHopCaseConfig(
        id="multihop_012_001_roster_cause",
        case_type="multi_hop",
        num_incidents=12,
        seed_offset=101,
        documents=(
            "loss_run_summary",
            "driver_roster",
            "cause_code_legend",
            "financial_ledger",
        ),
        join_requirements=(
            "unit_number -> driver_roster",
            "cause_code -> cause_code_legend",
            "incident_number -> financial_ledger",
        ),
        complexity_tags=(
            "cross_document_join",
            "coded_values",
            "supporting_ledger",
        ),
    ),
    MultiHopCaseConfig(
        id="multihop_025_001_policy_claimant",
        case_type="multi_hop",
        num_incidents=25,
        seed_offset=202,
        documents=(
            "loss_run_summary",
            "policy_register",
            "claimant_index",
            "financial_ledger",
        ),
        join_requirements=(
            "policy_number -> policy_register",
            "incident_number -> claimant_index",
            "incident_number -> financial_ledger",
        ),
        complexity_tags=(
            "cross_document_join",
            "many_to_one_policy",
            "claimant_lookup",
        ),
    ),
    MultiHopCaseConfig(
        id="mixed_040_001_full_packet",
        case_type="mixed",
        num_incidents=40,
        seed_offset=303,
        documents=(
            "loss_run_summary",
            "policy_register",
            "driver_roster",
            "cause_code_legend",
            "claimant_index",
            "financial_ledger",
            "distractor_claims_export",
        ),
        join_requirements=(
            "policy_number -> policy_register",
            "unit_number -> driver_roster",
            "cause_code -> cause_code_legend",
            "incident_number -> claimant_index",
            "incident_number -> financial_ledger",
        ),
        complexity_tags=(
            "cross_document_join",
            "mixed_layout",
            "distractor_documents",
            "longer_list",
        ),
    ),
)


CAUSE_CODES = [
    {
        "code": "BKD",
        "coverage_type": "Liability",
        "description": "Insured vehicle backed into fixed object or parked vehicle",
    },
    {
        "code": "RER",
        "coverage_type": "Liability",
        "description": "Insured vehicle rear-ended another vehicle",
    },
    {
        "code": "TRN",
        "coverage_type": "Liability",
        "description": "Wide turn or lane change contact with another vehicle",
    },
    {
        "code": "ROL",
        "coverage_type": "Physical Damage",
        "description": "Rollover or loss of control damage to insured vehicle",
    },
    {
        "code": "CGO",
        "coverage_type": "Cargo",
        "description": "Cargo shortage, damage, contamination, or spoilage",
    },
    {
        "code": "IMD",
        "coverage_type": "Inland Marine",
        "description": "Equipment or transported vehicle damage during handling",
    },
]

TRUCK_PREFIXES = ("FR", "KW", "PB", "VL", "MK", "IN")


def _dataset_version() -> str:
    version_path = Path(__file__).resolve().parents[1] / "VERSION"
    try:
        version = version_path.read_text(encoding="utf-8").strip()
    except OSError:
        return "1.0.0"
    return version or "1.0.0"


def _ensure_synthetic_imports() -> None:
    synthetic_path = str(Path(__file__).parent / "synthetic")
    if synthetic_path not in sys.path:
        sys.path.insert(0, synthetic_path)


def _stable_seed(base_seed: int, case_id: str, offset: int) -> int:
    seed_material = f"{base_seed}:{case_id}:{offset}".encode("utf-8")
    seed_offset = int(hashlib.md5(seed_material).hexdigest()[:8], 16) % 10000
    return base_seed + seed_offset


def _money(value: float | int | None) -> str:
    return f"${float(value or 0.0):,.2f}"


def _table(headers: list[str], rows: list[list[Any]], *, class_name: str = "claims-table") -> str:
    header_html = "".join(f"<th>{escape(str(header))}</th>" for header in headers)
    row_html = []
    for row in rows:
        row_html.append(
            "<tr>"
            + "".join(f"<td>{escape(str(value))}</td>" for value in row)
            + "</tr>"
        )
    return f"""
<div class="table-section">
  <table class="{class_name}">
    <thead><tr>{header_html}</tr></thead>
    <tbody>
      {''.join(row_html)}
    </tbody>
  </table>
</div>
"""


def _html_document(title: str, body: str, *, subtitle: str = "") -> str:
    subtitle_html = f"<div>{escape(subtitle)}</div>" if subtitle else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
  <style>
    @page {{ size: A4; margin: 14mm; }}
    body {{ font-family: Arial, sans-serif; color: #1f2933; font-size: 9pt; }}
    .header {{ border-bottom: 2px solid #1f2933; margin-bottom: 14px; padding-bottom: 8px; }}
    .header h1 {{ font-size: 17pt; margin: 0 0 4px; }}
    .header div {{ color: #52606d; font-size: 9pt; }}
    .note {{ background: #fff7d6; border: 1px solid #e1b12c; padding: 8px; margin: 10px 0 14px; }}
    .table-section {{ margin: 12px 0; }}
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
    th {{ background: #243b53; color: white; font-weight: 700; }}
    th, td {{ border: 1px solid #9fb3c8; padding: 4px; vertical-align: top; word-wrap: break-word; }}
    tr:nth-child(even) td {{ background: #f5f7fa; }}
    .small {{ font-size: 7.2pt; }}
    .page-break {{ page-break-before: always; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{escape(title)}</h1>
    {subtitle_html}
  </div>
  {body}
</body>
</html>
"""


def _assign_join_fields(incidents: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    enriched: list[dict[str, Any]] = []
    policy_pool: list[dict[str, str]] = []

    for idx, incident in enumerate(incidents, start=1):
        item = json.loads(json.dumps(incident))
        cause = CAUSE_CODES[(idx + rng.randint(0, len(CAUSE_CODES) - 1)) % len(CAUSE_CODES)]
        unit = f"2024 {TRUCK_PREFIXES[idx % len(TRUCK_PREFIXES)]} {600000 + idx:06d}"

        if idx <= 8 or idx % 4 == 0:
            policy = {
                "policy_number": item["policy_number"],
                "company_name": item["company_name"],
                "insured": item["insured"],
                "division": item.get("division") or "General",
                "policy_state": item["policy_state"],
                "agency": item.get("agency") or f"Brokerage {idx:03d}",
            }
            policy_pool.append(policy)
        else:
            policy = rng.choice(policy_pool)
            item["policy_number"] = policy["policy_number"]
            item["company_name"] = policy["company_name"]
            item["insured"] = policy["insured"]
            item["division"] = policy["division"]
            item["policy_state"] = policy["policy_state"]
            item["agency"] = policy["agency"]

        item["unit_number"] = unit
        item["driver_name"] = f"Driver-{idx:03d}, Alex"
        item["cause_code"] = cause["code"]
        item["coverage_type"] = cause["coverage_type"]
        item["description"] = cause["description"]
        item["handler"] = "Claims Adjuster"
        if not item.get("claimants"):
            item["claimants"] = [f"Claimant-{idx:03d}"]
        if not item.get("adjuster_notes"):
            item["adjuster_notes"] = f"Review supporting packet row {idx:03d} before closure."
        enriched.append(item)

    return enriched


def _loss_run_summary_doc(incidents: list[dict[str, Any]], case_id: str) -> str:
    rows = [
        [
            item["incident_number"],
            item["reference_number"],
            item["policy_number"],
            item["unit_number"],
            item["cause_code"],
            item["status"],
            item["date_of_loss"],
            item["loss_state"],
            item["date_reported"],
        ]
        for item in incidents
    ]
    body = """
<div class="note">
  Primary schedule only. Driver, policy, claimant, narrative, and financial
  fields must be reconciled from supporting packet documents using the visible
  keys in this table.
</div>
""" + _table(
        [
            "Incident #",
            "Reference #",
            "Policy #",
            "Unit #",
            "Cause Code",
            "Status",
            "Loss Date",
            "Loss State",
            "Reported",
        ],
        rows,
    )
    return _html_document(
        "Loss Run Summary",
        body,
        subtitle=f"Packet {case_id}; incomplete primary schedule",
    )


def _driver_roster_doc(incidents: list[dict[str, Any]], case_id: str) -> str:
    rows = [
        [
            item["unit_number"],
            item["driver_name"],
            item["company_name"],
            item["policy_state"],
            "Active",
        ]
        for item in incidents
    ]
    rows.extend(
        [
            [f"2023 ZZ {900000 + i}", f"Inactive-{i:03d}, Sam", "Archived Fleet", "TX", "Inactive"]
            for i in range(1, 4)
        ]
    )
    body = _table(["Unit #", "Driver", "Company", "Domicile", "Status"], rows)
    return _html_document(
        "Driver Roster",
        body,
        subtitle=f"Packet {case_id}; join on Unit #",
    )


def _policy_register_doc(incidents: list[dict[str, Any]], case_id: str) -> str:
    by_policy: dict[str, dict[str, Any]] = {}
    for item in incidents:
        by_policy[item["policy_number"]] = item
    rows = [
        [
            policy,
            item["company_name"],
            item["insured"],
            item.get("division") or "General",
            item["policy_state"],
            item.get("agency") or "",
        ]
        for policy, item in sorted(by_policy.items())
    ]
    rows.extend(
        [
            [f"ARCH-{i:03d}", "Archive Holdings", "Archive Holdings", "Runoff", "NY", "Do Not Use"]
            for i in range(1, 4)
        ]
    )
    body = _table(
        ["Policy #", "Company", "Insured", "Division", "Policy State", "Agency"],
        rows,
    )
    return _html_document(
        "Policy Register",
        body,
        subtitle=f"Packet {case_id}; join on Policy #",
    )


def _cause_code_legend_doc(_incidents: list[dict[str, Any]], case_id: str) -> str:
    rows = [
        [item["code"], item["coverage_type"], item["description"], "Claims Adjuster"]
        for item in CAUSE_CODES
    ]
    body = _table(["Cause Code", "Coverage Type", "Description", "Handler"], rows)
    return _html_document(
        "Cause Code Legend",
        body,
        subtitle=f"Packet {case_id}; join on Cause Code",
    )


def _financial_ledger_doc(incidents: list[dict[str, Any]], case_id: str) -> str:
    rows = []
    for item in incidents:
        row = [item["incident_number"]]
        for key in ("bi", "pd", "lae", "ded"):
            values = item.get(key) or {}
            row.extend(
                [
                    _money(values.get("reserve")),
                    _money(values.get("paid")),
                    _money(values.get("recovered")),
                    _money(values.get("total_incurred")),
                ]
            )
        rows.append(row)

    headers = ["Incident #"]
    for prefix in ("BI", "PD", "LAE", "DED"):
        headers.extend(
            [
                f"{prefix} Reserve",
                f"{prefix} Paid",
                f"{prefix} Recovered",
                f"{prefix} Total",
            ]
        )
    body = _table(headers, rows, class_name="claims-table small")
    return _html_document(
        "Financial Ledger",
        body,
        subtitle=f"Packet {case_id}; join on Incident #",
    )


def _claimant_index_doc(incidents: list[dict[str, Any]], case_id: str) -> str:
    rows = [
        [
            item["incident_number"],
            "; ".join(item.get("claimants") or []),
            item.get("adjuster_notes") or "",
        ]
        for item in incidents
    ]
    body = _table(["Incident #", "Claimants", "Adjuster Notes"], rows)
    return _html_document(
        "Claimant and Notes Index",
        body,
        subtitle=f"Packet {case_id}; join on Incident #",
    )


def _distractor_claims_export_doc(incidents: list[dict[str, Any]], case_id: str) -> str:
    rows = [
        [
            f"#9{idx:04d}",
            item["reference_number"],
            item["policy_number"],
            "Historical closed-file extract - not part of current packet",
        ]
        for idx, item in enumerate(reversed(incidents[:10]), start=1)
    ]
    body = """
<div class="note">
  Distractor export. These rows reuse some visible policy/reference values but
  incident identifiers are outside the target packet.
</div>
""" + _table(["Incident #", "Reference #", "Policy #", "Note"], rows)
    return _html_document(
        "Archived Claims Export",
        body,
        subtitle=f"Packet {case_id}; distractor document",
    )


DOCUMENT_BUILDERS = {
    "loss_run_summary": _loss_run_summary_doc,
    "driver_roster": _driver_roster_doc,
    "policy_register": _policy_register_doc,
    "cause_code_legend": _cause_code_legend_doc,
    "financial_ledger": _financial_ledger_doc,
    "claimant_index": _claimant_index_doc,
    "distractor_claims_export": _distractor_claims_export_doc,
}


def _generate_case_incidents(config: MultiHopCaseConfig, base_seed: int) -> list[dict[str, Any]]:
    _ensure_synthetic_imports()
    from generate_claim_data import generate_incidents

    seed = _stable_seed(base_seed, config.id, config.seed_offset)
    raw_incidents = generate_incidents(config.num_incidents, seed=seed, start_year=2023)
    return _assign_join_fields([item.model_dump() for item in raw_incidents], seed=seed)


async def _render_pdf(html_path: Path, pdf_path: Path) -> None:
    _ensure_synthetic_imports()
    from html_to_pdf import html_to_pdf

    await html_to_pdf(html_path, pdf_path)


async def _render_pdfs(render_tasks: list[Any]) -> None:
    await asyncio.gather(*render_tasks)


def _transcripts_available(case_dir: Path, doc_stem: str) -> list[str]:
    transcripts: list[str] = []
    if (case_dir / f"{doc_stem}_canonical.md").exists():
        transcripts.append("canonical")
    if (case_dir / f"{doc_stem}_ocr.md").exists() and (case_dir / f"{doc_stem}_ocr.md").stat().st_size > 0:
        transcripts.append("ocr")
    return transcripts


def _write_case(
    config: MultiHopCaseConfig,
    output_dir: Path,
    *,
    base_seed: int,
    render_pdfs: bool,
) -> dict[str, Any]:
    case_dir = output_dir / config.id
    case_dir.mkdir(parents=True, exist_ok=True)

    incidents = _generate_case_incidents(config, base_seed)
    ground_truth = {
        "case_id": config.id,
        "target_schema": "LossRunExtraction",
        "incidents": incidents,
    }
    (case_dir / "ground_truth.json").write_text(
        json.dumps(ground_truth, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    documents: list[dict[str, Any]] = []
    render_tasks = []
    for role in config.documents:
        builder = DOCUMENT_BUILDERS[role]
        doc_stem = role
        html_path = case_dir / f"{doc_stem}.html"
        pdf_path = case_dir / f"{doc_stem}.pdf"
        canonical_path = case_dir / f"{doc_stem}_canonical.md"

        html = builder(incidents, config.id)
        html_path.write_text(html, encoding="utf-8")
        write_canonical_markdown_from_html(html_path, canonical_path)
        if render_pdfs:
            render_tasks.append(_render_pdf(html_path, pdf_path))

        documents.append(
            {
                "id": doc_stem,
                "role": role,
                "files": {
                    "html": f"{doc_stem}.html",
                    "pdf": f"{doc_stem}.pdf",
                    "canonical_md": f"{doc_stem}_canonical.md",
                    "ocr_md": f"{doc_stem}_ocr.md",
                },
                "join_keys": _join_keys_for_role(role),
                "transcripts_available": ["canonical"],
            }
        )

    if render_tasks:
        asyncio.run(_render_pdfs(render_tasks))

    for document in documents:
        document["transcripts_available"] = _transcripts_available(case_dir, document["id"])

    manifest = {
        "id": config.id,
        "case_type": config.case_type,
        "num_incidents": config.num_incidents,
        "complexity_tags": list(config.complexity_tags),
        "join_requirements": list(config.join_requirements),
        "documents": documents,
        "ground_truth": "ground_truth.json",
        "transcript_conditions_planned": ["canonical", "ocr"],
        "transcript_conditions_available": sorted(
            {
                transcript
                for document in documents
                for transcript in document["transcripts_available"]
            }
        ),
    }
    (case_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "id": config.id,
        "case_type": config.case_type,
        "num_incidents": config.num_incidents,
        "num_documents": len(documents),
        "complexity_tags": list(config.complexity_tags),
        "join_requirements": list(config.join_requirements),
        "transcript_conditions_available": manifest["transcript_conditions_available"],
        "manifest": f"{config.id}/manifest.json",
    }


def _join_keys_for_role(role: str) -> list[str]:
    if role in {"loss_run_summary", "financial_ledger", "claimant_index"}:
        return ["incident_number"]
    if role == "driver_roster":
        return ["unit_number"]
    if role == "policy_register":
        return ["policy_number"]
    if role == "cause_code_legend":
        return ["cause_code"]
    return []


def generate_multihop_suite(
    output_dir: Path,
    *,
    base_seed: int = 4242,
    render_pdfs: bool = True,
    case_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Generate all configured multi-hop cases and return suite metadata."""
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_configs = [
        config for config in MULTIHOP_CASE_CONFIGS if case_ids is None or config.id in case_ids
    ]

    cases = [
        _write_case(config, output_dir, base_seed=base_seed, render_pdfs=render_pdfs)
        for config in selected_configs
    ]

    metadata = {
        "suite_name": SUITE_NAME,
        "version": _dataset_version(),
        "description": SUITE_DESCRIPTION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_seed": base_seed,
        "total_cases": len(cases),
        "total_documents": sum(case["num_documents"] for case in cases),
        "total_incidents": sum(case["num_incidents"] for case in cases),
        "case_types": sorted({case["case_type"] for case in cases}),
        "transcript_conditions_planned": ["canonical", "ocr"],
        "transcript_conditions_available": sorted(
            {
                transcript
                for case in cases
                for transcript in case["transcript_conditions_available"]
            }
        ),
        "cases": cases,
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LongListBench multi-hop cases")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).parent / "multihop_claims",
        help="Output directory (default: benchmarks/multihop_claims)",
    )
    parser.add_argument("--seed", type=int, default=4242, help="Base random seed")
    parser.add_argument(
        "--case-id",
        action="append",
        help="Generate only this case id; can be passed multiple times",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Write JSON/HTML/canonical transcripts only; skip PDF rendering",
    )
    args = parser.parse_args()

    metadata = generate_multihop_suite(
        args.output,
        base_seed=args.seed,
        render_pdfs=not args.no_pdf,
        case_ids=set(args.case_id) if args.case_id else None,
    )

    print(f"Generated {metadata['total_cases']} cases in {args.output}")
    print(f"Total documents: {metadata['total_documents']}")
    print(f"Total incidents: {metadata['total_incidents']}")


if __name__ == "__main__":
    main()
