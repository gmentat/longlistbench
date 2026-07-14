#!/usr/bin/env python3
"""Generate single-document cross-page multi-hop benchmark cases.

Each case is one long PDF. The primary loss-run schedule appears near the
front, while required fields are recoverable only by joining keys against
distant appendices later in the same document. The gap is filled with dense,
realistic distractor pages so simple adjacent-page overlap is insufficient.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import random
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

try:
    from .dataset_layout import (
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


SUITE_NAME = "longlistbench-v1"
SUITE_DESCRIPTION = (
    "Benchmark for long-list entity extraction under layout, OCR, scale, and "
    "long-range cross-page evidence complexity."
)


@dataclass(frozen=True)
class MultiHopCaseConfig:
    id: str
    case_type: str
    num_incidents: int
    seed_offset: int
    spacer_pages: tuple[int, int, int]
    join_requirements: tuple[str, ...]
    complexity_tags: tuple[str, ...]


MULTIHOP_CASE_CONFIGS: tuple[MultiHopCaseConfig, ...] = (
    MultiHopCaseConfig(
        id="multihop_012_001_crosspage",
        case_type="multihop",
        num_incidents=12,
        seed_offset=101,
        spacer_pages=(20, 16, 12),
        join_requirements=(
            "unit_number -> driver roster",
            "cause_code -> cause classification appendix",
            "incident_number -> financial ledger",
        ),
        complexity_tags=(
            "cross_page_join",
            "long_range_evidence",
            "coded_values",
        ),
    ),
    MultiHopCaseConfig(
        id="multihop_025_001_crosspage",
        case_type="multihop",
        num_incidents=25,
        seed_offset=202,
        spacer_pages=(30, 26, 24),
        join_requirements=(
            "policy_number -> policy register",
            "incident_number -> claimant index",
            "incident_number -> financial ledger",
        ),
        complexity_tags=(
            "cross_page_join",
            "long_range_evidence",
            "many_to_one_policy",
            "claimant_lookup",
        ),
    ),
    MultiHopCaseConfig(
        id="mixed_040_001_crosspage",
        case_type="mixed",
        num_incidents=40,
        seed_offset=303,
        spacer_pages=(42, 40, 36),
        join_requirements=(
            "policy_number -> policy register",
            "unit_number -> driver roster",
            "cause_code -> cause classification appendix",
            "incident_number -> claimant index",
            "incident_number -> financial ledger",
        ),
        complexity_tags=(
            "cross_page_join",
            "long_range_evidence",
            "mixed_layout",
            "distractor_sections",
            "longer_list",
        ),
    ),
)


CAUSE_CODES = [
    {
        "code": "BKD",
        "coverage_type": "Liability",
        "description": "Insured vehicle backed into fixed object or parked vehicle",
        "handler": "Auto Liability Unit",
    },
    {
        "code": "RER",
        "coverage_type": "Liability",
        "description": "Insured vehicle rear-ended another vehicle",
        "handler": "Auto Liability Unit",
    },
    {
        "code": "TRN",
        "coverage_type": "Liability",
        "description": "Wide turn or lane change contact with another vehicle",
        "handler": "Complex Liability Desk",
    },
    {
        "code": "ROL",
        "coverage_type": "Physical Damage",
        "description": "Rollover or loss of control damage to insured vehicle",
        "handler": "Physical Damage Desk",
    },
    {
        "code": "CGO",
        "coverage_type": "Cargo",
        "description": "Cargo shortage, damage, contamination, or spoilage",
        "handler": "Cargo Claims Desk",
    },
    {
        "code": "IMD",
        "coverage_type": "Inland Marine",
        "description": "Equipment or transported vehicle damage during handling",
        "handler": "Inland Marine Unit",
    },
]

TRUCK_PREFIXES = ("FR", "KW", "PB", "VL", "MK", "IN")
DRIVER_FIRST_NAMES = (
    "Jordan",
    "Morgan",
    "Taylor",
    "Casey",
    "Riley",
    "Avery",
    "Cameron",
    "Hayden",
    "Parker",
    "Quinn",
    "Reese",
    "Sawyer",
)
DRIVER_LAST_NAMES = (
    "Bennett",
    "Collins",
    "Foster",
    "Griffin",
    "Hayes",
    "Madden",
    "Nolan",
    "Porter",
    "Ramsey",
    "Sutton",
    "Vaughn",
    "Whitaker",
)
CLAIMANT_FIRST_NAMES = (
    "Alicia",
    "Brandon",
    "Carmen",
    "Derek",
    "Elena",
    "Felix",
    "Greta",
    "Hector",
    "Iris",
    "Julian",
    "Kara",
    "Lena",
    "Micah",
    "Nina",
    "Omar",
    "Priya",
)
CLAIMANT_LAST_NAMES = (
    "Archer",
    "Blake",
    "Calder",
    "Diaz",
    "Ellis",
    "Finch",
    "Gaines",
    "Holloway",
    "Ibarra",
    "Keane",
    "Lowell",
    "Morris",
    "Navarro",
    "Olsen",
    "Patel",
    "Quintero",
)
ADJUSTER_NOTE_TEMPLATES = (
    "Driver statement and first notice are indexed; reserve review is pending supervisor sign-off.",
    "Claimant packet was matched after mail-room review; liability diary remains open.",
    "Repair estimate and coverage page were attached separately for underwriting review.",
    "Prior-carrier note conflicts with the current roster; use the active roster before closing.",
    "Subrogation diary remains open while deductible recovery is reconciled to the ledger.",
    "Coverage coding was updated after review of the loss narrative and unit assignment.",
    "Medical and property files were split during intake; both references belong to this claim.",
    "Late notice was accepted after the account manager confirmed the reported loss date.",
    "Reserve worksheet was revised at close; use the final ledger block for incurred amounts.",
    "Claimant correspondence was scanned out of order and should be read with the notice index.",
    "Coverage counsel requested a follow-up diary; no coverage change is shown in this packet.",
    "The unit roster and policy register must both be checked before assigning the account name.",
)
COMMON_CLAIM_STRESSORS = (
    "cross_page_join",
    "long_range_evidence",
    "distractor_sections",
    "ocr_condition",
    "page_breaks",
    "large_doc",
    "multiple_tables",
    "multi_row",
    "multi_column",
    "duplicates",
    "natural_long_range_join",
    "inherited_context",
    "non_target_rows",
    "mixed_prose_tables",
    "non_sequential_identifiers",
)


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


def _review_reference(case_id: str, page_idx: int, prefix: str) -> str:
    return f"{prefix}-{_stable_seed(1300 + page_idx, case_id, page_idx) % 900000 + 100000}"


def _count_pdf_pages(pdf_path: Path) -> int | None:
    if not pdf_path.exists():
        return None
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, flags=re.MULTILINE)
    return int(match.group(1)) if match else None


def _money(value: float | int | None) -> str:
    return f"${float(value or 0.0):,.2f}"


def _table(headers: list[str], rows: list[list[Any]], *, class_name: str = "data-table") -> str:
    header_html = "".join(f"<th>{escape(str(header))}</th>" for header in headers)
    row_html = []
    for row in rows:
        row_html.append(
            "<tr>"
            + "".join(f"<td>{escape(str(value))}</td>" for value in row)
            + "</tr>"
        )
    return f"""
<table class="{class_name}">
  <thead><tr>{header_html}</tr></thead>
  <tbody>{''.join(row_html)}</tbody>
</table>
"""


def _page(
    title: str,
    body: str,
    *,
    class_name: str = "",
    source_label: str = "Claims Administration File",
) -> str:
    return f"""
<section class="page {class_name}">
  <div class="page-head">
    <span>{escape(title)}</span>
    <span>{escape(source_label)}</span>
  </div>
  {body}
</section>
"""


def _html_document(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
  <style>
    @page {{ size: Letter; margin: 12mm; }}
    body {{
      margin: 0;
      color: #111827;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 8.5pt;
      line-height: 1.28;
      background: #fff;
    }}
    .page {{
      page-break-before: always;
      min-height: 245mm;
      position: relative;
    }}
    .page:first-of-type {{ page-break-before: auto; }}
    .page-head {{
      display: flex;
      justify-content: space-between;
      border-bottom: 1px solid #6b7280;
      color: #4b5563;
      font-size: 7.5pt;
      letter-spacing: 0.04em;
      margin-bottom: 10px;
      padding-bottom: 3px;
      text-transform: uppercase;
    }}
    h1 {{ font-size: 19pt; margin: 8px 0 4px; }}
    h2 {{ font-size: 13pt; margin: 8px 0 7px; }}
    h3 {{ font-size: 10pt; margin: 8px 0 5px; }}
    .cover {{
      font-family: Arial, Helvetica, sans-serif;
      border: 2px solid #111827;
      padding: 20px;
    }}
    .cover-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 24px;
      margin-top: 20px;
    }}
    .label {{ color: #4b5563; display: block; font-size: 7.5pt; margin-bottom: 1px; text-transform: uppercase; }}
    .value {{ font-size: 10pt; margin-bottom: 8px; }}
    .notice {{
      border-left: 5px solid #374151;
      background: #f3f4f6;
      padding: 9px 12px;
      margin: 12px 0;
      font-family: Arial, Helvetica, sans-serif;
    }}
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
    th, td {{ border: 1px solid #9ca3af; padding: 3px 4px; vertical-align: top; word-wrap: break-word; }}
    th {{ background: #1f2937; color: #fff; font-family: Arial, Helvetica, sans-serif; font-size: 7.2pt; }}
    td {{ font-size: 7.5pt; }}
    .wide td {{ font-size: 6.5pt; padding: 2px 3px; }}
    .roster th {{ background: #374151; }}
    .ledger th {{ background: #334155; }}
    .memo {{
      font-family: "Courier New", monospace;
      font-size: 7.5pt;
      white-space: normal;
    }}
    .memo-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px 14px;
    }}
    .memo-card {{
      border: 1px solid #cbd5e1;
      padding: 7px;
      min-height: 62px;
      background: #fafafa;
    }}
    .worksheet {{
      font-family: Arial, Helvetica, sans-serif;
      font-size: 7.3pt;
    }}
    .worksheet h2,
    .sparse-report h2 {{
      font-family: Arial, Helvetica, sans-serif;
      font-size: 11pt;
      margin-bottom: 8px;
    }}
    .worksheet-meta {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 6px 18px;
      margin: 8px 0 10px;
      font-size: 7pt;
    }}
    .worksheet-table th {{
      background: #f1f5f9;
      color: #111827;
      font-size: 6.6pt;
      font-weight: 700;
      text-align: left;
    }}
    .worksheet-table td {{
      font-size: 6.7pt;
      padding: 2px 3px;
    }}
    .ledger-lite th {{
      background: #e5e7eb;
      color: #111827;
    }}
    .sparse-report {{
      font-family: Arial, Helvetica, sans-serif;
      width: 100%;
      margin: 4px 0 0;
      font-size: 7.4pt;
    }}
    .dense-notes {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 12px;
      margin-top: 9px;
    }}
    .dense-note {{
      border: 1px solid #cbd5e1;
      background: #f8fafc;
      min-height: 58px;
      padding: 6px;
      font-size: 6.9pt;
      line-height: 1.25;
    }}
    .sparse-title {{
      text-align: center;
      font-weight: 700;
      letter-spacing: 0.02em;
      margin-bottom: 16px;
    }}
    .report-meta {{
      display: grid;
      grid-template-columns: 95px 1fr;
      gap: 3px 8px;
      margin: 12px 0;
      font-size: 7pt;
    }}
    .report-address {{
      float: right;
      width: 215px;
      line-height: 1.2;
      margin: 8px 0 18px 20px;
      font-size: 7pt;
    }}
    .checklist {{
      display: grid;
      grid-template-columns: 18px 1fr 85px;
      border-top: 1px solid #cbd5e1;
      border-left: 1px solid #cbd5e1;
      margin-top: 10px;
    }}
    .checklist div {{
      border-right: 1px solid #cbd5e1;
      border-bottom: 1px solid #cbd5e1;
      padding: 4px 5px;
    }}
    .form-footer {{
      position: absolute;
      bottom: 14mm;
      left: 12mm;
      right: 12mm;
      border-top: 1px solid #cbd5e1;
      padding-top: 5px;
      color: #64748b;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 6.8pt;
      text-align: center;
    }}
    .stamp {{
      display: inline-block;
      border: 1px solid #991b1b;
      color: #991b1b;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 8pt;
      padding: 2px 6px;
      transform: rotate(-3deg);
    }}
    .two-col {{
      column-count: 2;
      column-gap: 22px;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 7.4pt;
    }}
    .claim-card-grid,
    .policy-card-grid,
    .ledger-grid,
    .claimant-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 10px;
      margin-top: 10px;
    }}
    .claim-card,
    .policy-card,
    .claimant-card,
    .ledger-claim {{
      break-inside: avoid;
      border: 1px solid #94a3b8;
      background: #fff;
      padding: 6px 7px;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 7.1pt;
      line-height: 1.25;
      min-height: 86px;
    }}
    .claim-card:nth-child(3n),
    .policy-card:nth-child(4n),
    .claimant-card:nth-child(5n) {{
      background: #f8fafc;
    }}
    .card-line {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      border-bottom: 1px dotted #cbd5e1;
      padding: 1px 0;
    }}
    .card-line span:first-child {{
      color: #475569;
      font-size: 6.7pt;
      text-transform: uppercase;
    }}
    .card-note {{
      margin-top: 4px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 7pt;
    }}
    .cause-list {{
      font-family: Georgia, "Times New Roman", serif;
      font-size: 8pt;
      line-height: 1.35;
      margin-top: 12px;
    }}
    .cause-entry {{
      break-inside: avoid;
      margin: 0 0 9px;
      padding-bottom: 7px;
      border-bottom: 1px solid #cbd5e1;
    }}
    .ledger-strip {{
      display: grid;
      grid-template-columns: 42px repeat(4, 1fr);
      gap: 0;
      margin-top: 4px;
      border-left: 1px solid #cbd5e1;
      border-top: 1px solid #cbd5e1;
    }}
    .ledger-strip div {{
      border-right: 1px solid #cbd5e1;
      border-bottom: 1px solid #cbd5e1;
      padding: 2px 3px;
      font-size: 6.4pt;
    }}
    .ledger-strip .ledger-label {{
      background: #f1f5f9;
      font-weight: 700;
    }}
    .portal {{
      display: grid;
      grid-template-columns: 165px 1fr;
      gap: 16px;
      font-family: Arial, Helvetica, sans-serif;
    }}
    .portal-side {{
      border: 1px solid #111827;
      background: #f8fafc;
      padding: 9px;
      font-size: 7pt;
    }}
    .portal-main h2 {{
      margin-top: 0;
      color: #334155;
      font-size: 14pt;
    }}
    .portal-main table th {{
      background: #e2e8f0;
      color: #111827;
    }}
    .letterhead {{
      font-family: Arial, Helvetica, sans-serif;
      width: 78%;
      margin: 22px auto;
    }}
    .seal {{
      width: 54px;
      height: 54px;
      border: 2px solid #475569;
      border-radius: 50%;
      margin: 0 auto 10px;
      text-align: center;
      line-height: 54px;
      font-size: 18pt;
      color: #475569;
    }}
    .spreadsheet-page {{
      font-family: Arial, Helvetica, sans-serif;
      font-size: 7.2pt;
      padding-top: 8px;
    }}
    .spreadsheet-page h2 {{
      text-align: center;
      font-size: 11pt;
      margin: 0 0 8px;
    }}
    .spreadsheet-page table {{
      width: 74%;
      margin: 0 auto 18px;
    }}
    .spreadsheet-page th,
    .spreadsheet-page td {{
      border: 0;
      padding: 2px 7px;
      text-align: left;
    }}
    .spreadsheet-page th {{
      background: transparent;
      color: #111827;
      font-weight: bold;
    }}
    .mini-report {{
      margin-bottom: 12px;
      border-bottom: 1px solid #cbd5e1;
      padding-bottom: 8px;
    }}
    .mini-report h3 {{
      font-family: Arial, Helvetica, sans-serif;
      font-size: 9pt;
      margin: 0 0 4px;
    }}
    .rotated-page {{
      min-height: 245mm;
      position: relative;
      font-family: Arial, Helvetica, sans-serif;
    }}
    .rotated-inner {{
      position: absolute;
      left: 48%;
      top: 52%;
      width: 520px;
      transform: translate(-50%, -50%) rotate(90deg);
      transform-origin: center center;
    }}
    .rotated-inner th {{
      background: #f1f5f9;
      color: #111827;
    }}
    .sideways-marker {{
      position: absolute;
      left: 8px;
      top: 50%;
      transform: rotate(90deg);
      color: #64748b;
      font-size: 7pt;
    }}
    .system-print {{
      color: #111;
      font-family: "Courier New", Courier, monospace;
      font-size: 7.2pt;
    }}
    .system-banner {{
      border: 1px solid #111;
      display: flex;
      font-weight: 700;
      justify-content: space-between;
      margin-bottom: 8px;
      padding: 5px 7px;
    }}
    .system-print table {{ table-layout: auto; }}
    .system-print th {{
      background: #fff;
      border-color: #111;
      color: #111;
      font-family: "Courier New", Courier, monospace;
      font-size: 6.6pt;
    }}
    .system-print td {{ border-color: #555; font-size: 6.7pt; }}
    .diary-stream {{ border-top: 2px solid #222; margin-top: 8px; }}
    .diary-entry {{
      border-bottom: 1px solid #777;
      display: grid;
      gap: 7px;
      grid-template-columns: 82px 72px 1fr;
      padding: 6px 2px;
    }}
    .diary-entry:nth-child(even) {{ background: #f4f4f4; }}
    .diary-entry .date {{ font-weight: 700; }}
    .claim-form {{
      border: 1.5px solid #222;
      font-family: Arial, Helvetica, sans-serif;
      padding: 10px 12px;
    }}
    .claim-form-title {{
      border-bottom: 2px solid #222;
      font-size: 13pt;
      font-weight: 700;
      margin-bottom: 9px;
      padding-bottom: 5px;
      text-align: center;
      text-transform: uppercase;
    }}
    .claim-form-grid {{
      display: grid;
      gap: 0;
      grid-template-columns: 1fr 1fr 1fr;
      margin-bottom: 9px;
    }}
    .claim-form-field {{
      border: 1px solid #777;
      min-height: 38px;
      padding: 4px 5px;
    }}
    .claim-form-field.wide {{ grid-column: span 2; }}
    .claim-form-field .label {{ color: #222; font-size: 6.4pt; }}
    .claim-narrative {{
      border: 1px solid #777;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 8pt;
      line-height: 1.42;
      min-height: 132px;
      padding: 8px 10px;
    }}
    .letter-page {{
      font-family: "Times New Roman", Times, serif;
      font-size: 9pt;
      line-height: 1.42;
      margin: 10px 34px;
    }}
    .letter-masthead {{
      border-bottom: 3px double #222;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 16pt;
      font-weight: 700;
      margin-bottom: 18px;
      padding-bottom: 7px;
    }}
    .letter-page .address-block {{ margin: 16px 0; white-space: pre-line; }}
    .letter-page .subject-line {{ font-weight: 700; margin: 14px 0; }}
    .estimate-sheet {{
      border: 1px solid #333;
      font-family: Arial, Helvetica, sans-serif;
      padding: 9px;
    }}
    .estimate-head {{
      align-items: end;
      border-bottom: 4px solid #333;
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      padding-bottom: 6px;
    }}
    .estimate-head strong {{ font-size: 15pt; }}
    .estimate-sheet th {{ background: #555; }}
    .estimate-total {{
      border-top: 2px solid #222;
      font-size: 9pt;
      font-weight: 700;
      margin-left: auto;
      margin-top: 8px;
      padding-top: 5px;
      text-align: right;
      width: 42%;
    }}
    .coverage-sheet {{
      font-family: Arial, Helvetica, sans-serif;
      margin: 6px 20px;
    }}
    .coverage-sheet h2 {{
      border-bottom: 1px solid #111;
      font-size: 13pt;
      padding-bottom: 5px;
      text-align: center;
    }}
    .coverage-block {{
      border: 1px solid #444;
      margin: 8px 0;
      padding: 8px;
    }}
    .coverage-block dl {{
      display: grid;
      gap: 3px 9px;
      grid-template-columns: 130px 1fr;
      margin: 0;
    }}
    .coverage-block dt {{ font-weight: 700; }}
    .coverage-block dd {{ margin: 0; }}
  </style>
</head>
<body>
  {body}
</body>
</html>
"""


def _assign_join_fields(incidents: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    enriched: list[dict[str, Any]] = []
    policy_pool: list[dict[str, str]] = []
    used_claim_ids: set[str] = set()
    used_references: set[str] = set()
    used_units: set[str] = set()

    for idx, incident in enumerate(incidents, start=1):
        item = json.loads(json.dumps(incident))
        cause = CAUSE_CODES[(idx + rng.randint(0, len(CAUSE_CODES) - 1)) % len(CAUSE_CODES)]
        while True:
            claim_id = f"#{rng.randint(41000, 98999)}-{rng.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}"
            if claim_id not in used_claim_ids:
                used_claim_ids.add(claim_id)
                break
        while True:
            reference = f"LR{rng.randint(23, 26)}-{rng.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{rng.randint(1000, 9999)}"
            if reference not in used_references:
                used_references.add(reference)
                break
        while True:
            unit = f"{rng.randint(2018, 2025)} {rng.choice(TRUCK_PREFIXES)} {rng.randint(200000, 899999):06d}"
            if unit not in used_units:
                used_units.add(unit)
                break
        item["incident_number"] = claim_id
        item["reference_number"] = reference

        if idx <= 8 or idx % 4 == 0 or not policy_pool:
            policy = {
                "policy_number": item["policy_number"],
                "company_name": item["company_name"],
                "insured": item["insured"],
                "division": item.get("division") or "General",
                "policy_state": item["policy_state"],
                "agency": item.get("agency") or f"Brokerage {idx:03d}",
            }
            policy_pool.append(policy)
            item["agency"] = policy["agency"]
        else:
            policy = rng.choice(policy_pool)
            item["policy_number"] = policy["policy_number"]
            item["company_name"] = policy["company_name"]
            item["insured"] = policy["insured"]
            item["division"] = policy["division"]
            item["policy_state"] = policy["policy_state"]
            item["agency"] = policy["agency"]

        item["unit_number"] = unit
        first = DRIVER_FIRST_NAMES[(idx + rng.randint(0, 4)) % len(DRIVER_FIRST_NAMES)]
        last = DRIVER_LAST_NAMES[(idx * 3 + rng.randint(0, 7)) % len(DRIVER_LAST_NAMES)]
        item["driver_name"] = f"{last}, {first}"
        item["cause_code"] = cause["code"]
        item["coverage_type"] = cause["coverage_type"]
        item["description"] = cause["description"]
        item["handler"] = cause["handler"]
        if not item.get("claimants"):
            first = CLAIMANT_FIRST_NAMES[(idx + rng.randint(0, 5)) % len(CLAIMANT_FIRST_NAMES)]
            last = CLAIMANT_LAST_NAMES[(idx * 5 + rng.randint(0, 9)) % len(CLAIMANT_LAST_NAMES)]
            item["claimants"] = [f"{last}, {first}"]
        if not item.get("adjuster_notes") or re.fullmatch(r"Indexed claimant notice \d{3};.*", str(item.get("adjuster_notes"))):
            item["adjuster_notes"] = ADJUSTER_NOTE_TEMPLATES[(idx + rng.randint(0, 5)) % len(ADJUSTER_NOTE_TEMPLATES)]
        enriched.append(item)

    return enriched


def _generate_case_incidents(config: MultiHopCaseConfig, base_seed: int) -> list[dict[str, Any]]:
    _ensure_synthetic_imports()
    from generate_claim_data import generate_incidents

    seed = _stable_seed(base_seed, config.id, config.seed_offset)
    raw_incidents = generate_incidents(config.num_incidents, seed=seed, start_year=2023)
    return _assign_join_fields([item.model_dump() for item in raw_incidents], seed=seed)


def _cover_page(config: MultiHopCaseConfig, incidents: list[dict[str, Any]]) -> str:
    insured = incidents[0]["insured"] if incidents else "Scheduled Insured"
    file_reference = f"UW-{_stable_seed(1100, config.id, 0) % 900000 + 100000}"
    body = f"""
<div class="cover">
  <div class="stamp">RENEWAL REVIEW COPY</div>
  <h1>Commercial Auto Claim History</h1>
  <p>Claim history and supporting file material prepared for account review.
  The packet includes claim summaries, correspondence, policy-service records,
  examiner notes, and financial detail retained in the claim system.</p>
  <div class="cover-grid">
    <div><div class="label">Account</div><div class="value">{escape(insured)}</div></div>
    <div><div class="label">Valuation Date</div><div class="value">01/31/2024</div></div>
    <div><div class="label">Claim Count</div><div class="value">{len(incidents)}</div></div>
    <div><div class="label">File Reference</div><div class="value">{file_reference}</div></div>
  </div>
  <div class="notice">
    Information in this packet comes from several claim and policy systems.
    File numbers, policy references, and document references are shown as they
    appear on each source page.
  </div>
</div>
"""
    return _page("Claim history cover", body)


def _portal_receipt_page(config: MultiHopCaseConfig, incidents: list[dict[str, Any]]) -> str:
    queue_id = f"RQ-{_stable_seed(1200, config.id, 0) % 900000 + 100000}"
    rows = [
        [
            idx,
            item["policy_number"],
            item["policy_state"],
            item["status"],
            item["date_reported"],
        ]
        for idx, item in enumerate(incidents[: min(10, len(incidents))], start=1)
    ]
    body = f"""
<div class="portal">
  <aside class="portal-side">
    <strong>Account Portal</strong><br>
    Queue: {queue_id}<br>
    Valuation: 01/31/2024<br>
    Rows staged: {len(incidents)}<br><br>
    <strong>Navigation</strong><br>
    Summary<br>
    Claim History<br>
    Fleet Units<br>
    Documents<br>
    Export Queue
  </aside>
  <main class="portal-main">
    <h2>Return Summary / Original Export Review</h2>
    <p>Carrier portal printout retained at the front of the account packet.
    The table below shows the first staged rows in the renewal review queue.</p>
    {_table(["#", "Policy", "State", "Status", "Reported"], rows)}
    <p style="margin-top: 18px; text-align: right; font-weight: bold;">Pending review queue: {len(incidents)}</p>
  </main>
</div>
"""
    return _page("Portal export receipt", body)


def _unit_spreadsheet_page(incidents: list[dict[str, Any]]) -> str:
    makes = ["Freightliner", "Kenworth", "Peterbilt", "Volvo", "Mack", "Utility", "Great Dane"]
    body_types = ["TRACTOR", "TRAILER", "TRUCK", "REEFER", "FLATBED"]
    rows = []
    for idx, item in enumerate(incidents[: min(38, len(incidents))], start=1):
        rows.append(
            [
                item["unit_number"].split()[-1],
                item["reference_number"] if idx % 5 == 0 else "",
                2012 + (idx % 13),
                makes[idx % len(makes)],
                body_types[idx % len(body_types)],
                item["policy_state"],
            ]
        )
    body = """
<div class="spreadsheet-page">
  <h2>Vehicle / Unit Reference Export</h2>
""" + _table(["Veh #", "Company vehicle #", "Year", "Make", "Body Type", "State"], rows) + """
</div>
"""
    return _page("Vehicle unit reference export", body)


def _primary_schedule_page(incidents: list[dict[str, Any]]) -> str:
    pages: list[str] = []
    for page_index, chunk in enumerate(_balanced_chunks(incidents, 10), start=1):
        cards = []
        for idx, item in enumerate(chunk, start=1 + (page_index - 1) * 10):
            unit_short = item["unit_number"].split()[-1]
            claim_label = _label(("Claim file", "File no.", "Loss file"), idx)
            ref_label = _label(("Reference", "Loss run ref.", "Carrier ref."), idx + 1)
            policy_label = _label(("Policy shown", "Policy on loss", "Policy ref."), idx + 2)
            unit_label = _label(("Unit listed", "Sched. unit", "Equipment no."), idx + 3)
            cause_label = _label(("Cause / status", "Coding / disposition", "Loss code / status"), idx + 4)
            cards.append(
                f"""
<article class="claim-card">
  <div class="card-line"><span>{escape(claim_label)}</span><strong>{escape(item["incident_number"])}</strong></div>
  <div class="card-line"><span>{escape(ref_label)}</span><strong>{escape(item["reference_number"])}</strong></div>
  <div class="card-line"><span>{escape(policy_label)}</span><strong>{escape(item["policy_number"])}</strong></div>
  <div class="card-line"><span>{escape(unit_label)}</span><strong>{escape(unit_short)}</strong></div>
  <div class="card-line"><span>{escape(cause_label)}</span><strong>{escape(item["cause_code"])} / {escape(item["status"])}</strong></div>
  <div class="card-note">
    Loss was entered for {escape(item["loss_state"])} with a loss date of
    {escape(item["date_of_loss"])} and report date {escape(item["date_reported"])}.
    The intake card was staged from the claim queue; driver, claimant, and
    financial detail are attached elsewhere in the account file.
  </div>
</article>"""
            )
        body = f"""
<h2>Claim Intake File Cards</h2>
<div class="notice">
  These file cards were printed from the intake queue. Policy, unit, and cause
  references retain the labels used when the loss was reported.
</div>
<div class="claim-card-grid">{''.join(cards)}</div>
"""
        title = "Primary claim file cards" if page_index == 1 else "Primary claim file cards continued"
        pages.append(_page(title, body))
    return "".join(pages)


def _sample_window(incidents: list[dict[str, Any]], page_idx: int, size: int) -> list[dict[str, Any]]:
    return [incidents[(page_idx + offset) % len(incidents)] for offset in range(size)]


def _balanced_chunks(items: list[Any], max_size: int) -> list[list[Any]]:
    if not items:
        return []
    chunk_count = (len(items) + max_size - 1) // max_size
    base_size, remainder = divmod(len(items), chunk_count)
    chunks: list[list[Any]] = []
    start = 0
    for chunk_index in range(chunk_count):
        chunk_size = base_size + (1 if chunk_index < remainder else 0)
        chunks.append(items[start : start + chunk_size])
        start += chunk_size
    return chunks


def _label(options: tuple[str, ...], index: int) -> str:
    return options[index % len(options)]


def _claim_diary_page(
    case_id: str,
    page_idx: int,
    rng: random.Random,
    incidents: list[dict[str, Any]],
) -> str:
    actions = (
        "Initial contact attempt documented; callback window entered for the assigned examiner.",
        "Repair documentation received and routed for review of labor rates and prior damage.",
        "Coverage question sent to policy services; diary extended pending the written response.",
        "Reserve review completed. No authority change was requested on this activity entry.",
        "Statement request issued to the reporting party and indexed to incoming correspondence.",
        "Recovery potential reviewed after liability discussion; follow-up remains open.",
        "Medical invoice image indexed. Coding review is pending before payment consideration.",
        "Supervisor reviewed the current file status and returned the activity to the examiner queue.",
    )
    entries = []
    for idx, item in enumerate(_sample_window(incidents, page_idx, 16), start=1):
        note = actions[(page_idx * 3 + idx) % len(actions)]
        entries.append(
            f"""
<div class="diary-entry">
  <div class="date">{(idx % 12) + 1:02d}/{(idx * 2 % 27) + 1:02d}/2024<br>{8 + idx % 9:02d}:{(idx * 7) % 60:02d}</div>
  <div>{escape(item['reference_number'])}<br>{escape(rng.choice(['EXAM', 'SUPV', 'CLERK', 'RECOV']))}</div>
  <div>{escape(note)}</div>
</div>"""
        )
    system_names = ("ClaimCenter Activity Detail", "Examiner Diary Print", "Open File Activity History")
    system_name = system_names[page_idx % len(system_names)]
    body = f"""
<div class="system-print">
  <div class="system-banner">
    <span>{escape(system_name)}</span>
    <span>Batch {_review_reference(case_id, page_idx, 'ACT')}</span>
  </div>
  <div>Activity range: 01/01/2024 - 03/31/2024 &nbsp;&nbsp; Sort: entered date / ascending</div>
  <div class="diary-stream">{''.join(entries)}</div>
</div>
"""
    return _page(
        system_name,
        body,
        class_name="system-print",
        source_label=rng.choice(("Claims System Print", "Activity History", "Examiner Queue")),
    )


def _repair_estimate_page(
    case_id: str,
    page_idx: int,
    rng: random.Random,
    incidents: list[dict[str, Any]],
) -> str:
    item = incidents[(page_idx * 3) % len(incidents)]
    operations = (
        "Remove and install front bumper assembly",
        "Repair left side cab panel",
        "Refinish repaired panel and blend adjacent surface",
        "Replace lamp assembly",
        "Inspect steering linkage and alignment",
        "Repair hood mounting bracket",
        "Replace mirror housing",
        "Clean debris and protect interior",
        "Scan vehicle systems before repair",
        "Scan vehicle systems after repair",
        "Road test and quality inspection",
        "Shop materials and hazardous-waste handling",
        "Remove and install grille assembly",
        "Repair lower step and mounting support",
        "Replace fasteners and one-time-use clips",
        "Apply corrosion protection to repaired surfaces",
        "Measure frame and record reference dimensions",
        "Final wash and delivery preparation",
    )
    rows = []
    subtotal = 0.0
    for idx, operation in enumerate(operations, start=1):
        labor_hours = round(rng.uniform(0.3, 6.5), 1)
        labor = round(labor_hours * rng.choice((76.0, 82.0, 89.0, 96.0)), 2)
        parts = round(rng.uniform(0, 1450), 2) if idx % 3 != 0 else 0.0
        subtotal += labor + parts
        rows.append(
            [
                idx,
                operation,
                f"{labor_hours:.1f}",
                _money(labor),
                _money(parts) if parts else "--",
            ]
        )
    estimate_number = _review_reference(case_id, page_idx, "EST")
    body = f"""
<div class="estimate-sheet">
  <div class="estimate-head">
    <strong>{escape(rng.choice(('Northline Fleet Repair', 'Harbor Commercial Collision', 'Summit Heavy Vehicle Repair')))}</strong>
    <span>Preliminary estimate<br>No. {escape(estimate_number)}</span>
  </div>
  <div class="worksheet-meta">
    <div><span class="label">File reference</span><br>{escape(item['reference_number'])}</div>
    <div><span class="label">Unit</span><br>{escape(item['unit_number'])}</div>
    <div><span class="label">Inspection date</span><br>{(page_idx % 12) + 1:02d}/{(page_idx * 3 % 27) + 1:02d}/2024</div>
  </div>
  {_table(['Line', 'Operation / Description', 'Labor Hrs', 'Labor', 'Parts'], rows, class_name='data-table worksheet-table')}
  <div class="estimate-total">Estimate subtotal: {_money(subtotal)}<br><span class="small">Supplemental damage subject to inspection</span></div>
</div>
"""
    return _page(
        "Repair estimate",
        body,
        class_name="estimate-page",
        source_label="Repair Facility Attachment",
    )


def _coverage_verification_page(
    case_id: str,
    page_idx: int,
    rng: random.Random,
    incidents: list[dict[str, Any]],
) -> str:
    blocks = []
    labels = (
        ("Policy reference", "Coverage status", "Jurisdiction", "Verification source"),
        ("Policy no.", "File disposition", "Policy state", "Record reviewed"),
        ("Contract number", "Coverage review", "Issuing state", "Source document"),
    )
    for idx, item in enumerate(_sample_window(incidents, page_idx, min(6, len(incidents)))):
        selected = labels[(page_idx + idx) % len(labels)]
        values = (
            item["policy_number"],
            rng.choice(("In force on reported date", "Verification pending", "Coverage issue referred")),
            item["policy_state"],
            rng.choice(("Declarations image", "Policy system", "Producer confirmation")),
        )
        fields = "".join(
            f"<dt>{escape(label)}</dt><dd>{escape(str(value))}</dd>"
            for label, value in zip(selected, values, strict=True)
        )
        blocks.append(
            f"""
<div class="coverage-block">
  <dl>{fields}</dl>
  <p><strong>Review note:</strong> {escape(rng.choice((
      'The loss notice remains subject to all policy terms, conditions, and applicable endorsements.',
      'Policy services was asked to confirm the scheduled auto and effective dates before payment review.',
      'This screen print records the coverage inquiry only; it is not a coverage determination.',
  )))}</p>
</div>"""
        )
    body = f"""
<div class="coverage-sheet">
  <h2>Policy Services - Coverage Verification</h2>
  <div class="worksheet-meta">
    <div><span class="label">Inquiry batch</span><br>{_review_reference(case_id, page_idx, 'CV')}</div>
    <div><span class="label">Requested by</span><br>Claims intake</div>
    <div><span class="label">Printed</span><br>{(page_idx % 12) + 1:02d}/{(page_idx * 5 % 27) + 1:02d}/2024</div>
  </div>
  {''.join(blocks)}
</div>
"""
    return _page(
        "Coverage verification",
        body,
        class_name="coverage-page",
        source_label="Policy Services",
    )


def _correspondence_page(
    case_id: str,
    page_idx: int,
    rng: random.Random,
    incidents: list[dict[str, Any]],
) -> str:
    item = incidents[(page_idx * 5 + 1) % len(incidents)]
    mastheads = ("HARBOR CLAIM SERVICES", "NORTHSTAR RECORDS UNIT", "SUMMIT CLAIM OPERATIONS")
    subjects = (
        "Request for supporting repair documentation",
        "Acknowledgment of reported commercial auto loss",
        "Status request regarding pending claim documentation",
        "Confirmation of correspondence received",
    )
    paragraphs = (
        "We are reviewing the reported matter identified below. Please provide any photographs, repair invoices, estimates, towing records, or other documents that have not already been submitted.",
        "Receipt of this correspondence does not constitute an admission of liability or a determination of coverage. The claim remains subject to investigation and the terms of the applicable policy.",
        "Please place the reference shown below on each response. Documents may be returned by secure upload or by mail to the records unit shown on this letter.",
    )
    recipient = rng.choice(("Records Department", "Fleet Manager", "Repair Facility", "Claim Reporting Contact"))
    body = f"""
<div class="letter-page">
  <div class="letter-masthead">{escape(mastheads[page_idx % len(mastheads)])}</div>
  <div>{(page_idx % 12) + 1:02d}/{(page_idx * 3 % 27) + 1:02d}/2024</div>
  <div class="address-block">{escape(recipient)}
{escape(item['company_name'])}
Commercial Auto Claims File</div>
  <div class="subject-line">Re: {escape(subjects[page_idx % len(subjects)])}<br>
  File reference: {escape(item['reference_number'])} &nbsp;&nbsp; Policy: {escape(item['policy_number'])}</div>
  <p>To whom it may concern:</p>
  <p>{escape(paragraphs[page_idx % len(paragraphs)])}</p>
  <p>{escape(paragraphs[(page_idx + 1) % len(paragraphs)])}</p>
  <p>{escape(paragraphs[(page_idx + 2) % len(paragraphs)])}</p>
  <p>Sincerely,</p>
  <p><strong>{escape(rng.choice(('Claims Records Unit', 'Assigned Examiner', 'Document Services')))}</strong><br>
  Correspondence control {_review_reference(case_id, page_idx, 'COR')}</p>
</div>
"""
    return _page(
        "Claim correspondence",
        body,
        class_name="correspondence-page",
        source_label="Correspondence Image",
    )


def _claim_status_report_page(
    case_id: str,
    page_idx: int,
    rng: random.Random,
    incidents: list[dict[str, Any]],
) -> str:
    item = incidents[(page_idx * 7 + 2) % len(incidents)]
    stages = (
        "Coverage review",
        "Liability investigation",
        "Damage evaluation",
        "Payment review",
        "Recovery review",
        "Closing review",
    )
    task_rows = []
    for idx in range(1, 13):
        task_rows.append(
            [
                f"{(idx % 12) + 1:02d}/{(idx * 4 % 27) + 1:02d}/2024",
                stages[(page_idx + idx) % len(stages)],
                rng.choice(("Open", "Complete", "Awaiting response", "Reassigned")),
                rng.choice(("Examiner", "Supervisor", "Records", "Recovery")),
            ]
        )
    narrative_sets = (
        (
            "The file was reviewed after receipt of additional photographs and a preliminary estimate. The reported sequence of events remains under investigation.",
            "Policy services has been asked to verify the scheduled unit and effective dates. No coverage determination is recorded on this report.",
            "The next review should address outstanding documentation, liability position, reserve adequacy, and any available recovery source.",
        ),
        (
            "Contact was completed with the reporting party. The physical-damage inspection is pending and the unit has not yet been released for repair.",
            "Correspondence images are indexed under the file reference shown above. A separate financial screen contains payment and reserve activity.",
            "Supervisor review is required if the anticipated exposure exceeds the examiner's current authority.",
        ),
        (
            "Available records were compared with the initial notice. The claim remains open while the examiner resolves conflicting descriptions of the event.",
            "Repair and towing records have been requested. Any medical or third-party property documentation will be reviewed in the applicable coverage file.",
            "The diary date was extended to allow time for the requested records and a policy-services response.",
        ),
    )
    narrative = narrative_sets[page_idx % len(narrative_sets)]
    body = f"""
<div class="claim-form">
  <div class="claim-form-title">Claim Status Report</div>
  <div class="claim-form-grid">
    <div class="claim-form-field"><span class="label">File number</span>{escape(item['incident_number'])}</div>
    <div class="claim-form-field"><span class="label">Reference</span>{escape(item['reference_number'])}</div>
    <div class="claim-form-field"><span class="label">Current status</span>{escape(item['status'])}</div>
    <div class="claim-form-field wide"><span class="label">Insured account</span>{escape(item['insured'])}</div>
    <div class="claim-form-field"><span class="label">Report date</span>{escape(item['date_reported'])}</div>
  </div>
  <div class="claim-narrative">
    <p><strong>Examiner summary</strong></p>
    <p>{escape(narrative[0])}</p>
    <p>{escape(narrative[1])}</p>
    <p>{escape(narrative[2])}</p>
  </div>
  {_table(['Diary', 'Work item', 'Status', 'Owner'], task_rows, class_name='data-table worksheet-table')}
  <div class="small" style="margin-top:8px;">Report control: {_review_reference(case_id, page_idx, 'STAT')}</div>
</div>
"""
    return _page(
        "Claim status report",
        body,
        class_name="claim-status-page",
        source_label="Examiner Report",
    )


def _subrogation_diary_page(
    case_id: str,
    page_idx: int,
    rng: random.Random,
    incidents: list[dict[str, Any]],
) -> str:
    rows = []
    actions = ["Demand review", "Carrier tender", "Closed no recovery", "Arbitration pending", "Diary follow-up"]
    for idx, item in enumerate(_sample_window(incidents, page_idx, 24), start=1):
        rows.append(
            [
                f"03/{(idx * 2 % 27) + 1:02d}/2024",
                item["incident_number"] if idx % 4 == 0 else f"SUB-{page_idx:03d}-{idx:02d}",
                item["reference_number"],
                actions[(idx + page_idx) % len(actions)],
                rng.choice(["Open", "Diary", "Closed", "Review"]),
                _money(rng.randint(0, 18500)),
            ]
        )
    body = f"""
<h2>Subrogation Diary Extract</h2>
<div class="worksheet-meta">
  <div><span class="label">Account file</span><br>{_review_reference(case_id, page_idx, "ACCT")}</div>
  <div><span class="label">Diary export</span><br>Subrogation module</div>
  <div><span class="label">Printed</span><br>03/31/2024</div>
</div>
{_table(["Diary Date", "File #", "Reference", "Action", "Status", "Recovery Est."], rows, class_name="data-table worksheet-table")}
<div class="dense-notes">
  <div class="dense-note"><strong>Diary note.</strong> The extract includes open and closed recovery activity. Some references are archival rows used by the claims team for reconciliation.</div>
  <div class="dense-note"><strong>Routing note.</strong> Recoveries are compared with the financial ledger and claim detail pages before any account-level recovery credit is applied.</div>
</div>
"""
    return _page(
        "Subrogation diary extract",
        body,
        class_name="worksheet",
        source_label="Recovery Unit Diary",
    )


def _first_notice_page(
    case_id: str,
    page_idx: int,
    rng: random.Random,
    incidents: list[dict[str, Any]],
) -> str:
    item = incidents[(page_idx * 11 + 3) % len(incidents)]
    narrative = rng.choice(
        (
            "The reporting contact advised that the scheduled vehicle was involved in a low-speed maneuver at a customer location. Photographs and the incident exchange form were requested.",
            "The loss was reported after a roadway incident involving the insured unit and another vehicle. Liability remains undetermined pending statements and scene documentation.",
            "The reporting party described damage discovered after delivery. Shipping records, photographs, and a written timeline were requested for review.",
            "The vehicle left the roadway during adverse conditions. Towing documentation and an inspection estimate were requested before the next file review.",
        )
    )
    fields = [
        ("Notice reference", item["reference_number"]),
        ("Reported", item["date_reported"]),
        ("Event date", item["date_of_loss"]),
        ("State", item["loss_state"]),
        ("Unit reported", item["unit_number"].split()[-1]),
        ("Intake status", rng.choice(("Assigned", "Pending verification", "Supervisor review"))),
        ("Reported by", rng.choice(("Fleet contact", "Broker reporting desk", "Driver supervisor"))),
        ("Contact method", rng.choice(("Telephone", "Secure portal", "Email attachment"))),
        ("Police report", rng.choice(("Requested", "Not available", "Received"))),
    ]
    handling_rows = [
        ["Policy verification", rng.choice(("Requested", "Complete", "Pending")), "Policy services"],
        ["Vehicle inspection", rng.choice(("Assigned", "Not required", "Pending")), "Damage unit"],
        ["Statement", rng.choice(("Requested", "Scheduled", "Not yet assigned")), "Examiner"],
        ["Photographs", rng.choice(("Received", "Requested", "Portal link sent")), "Records"],
        ["Recovery review", rng.choice(("Screened", "Deferred", "Pending liability")), "Recovery unit"],
        ["Next diary", f"{(page_idx % 12) + 1:02d}/{(page_idx * 7 % 27) + 1:02d}/2024", "Examiner"],
    ]
    cells = "".join(
        f'<div class="claim-form-field"><span class="label">{escape(label)}</span>{escape(str(value))}</div>'
        for label, value in fields
    )
    body = f"""
<div class="claim-form">
  <div class="claim-form-title">Commercial Auto - First Notice of Loss</div>
  <div class="claim-form-grid">{cells}</div>
  <div class="claim-narrative">
    <p><strong>Description as reported</strong></p>
    <p>{escape(narrative)}</p>
    <p><strong>Immediate handling:</strong> The intake unit created the file, requested available supporting records, and routed the notice for policy and assignment review.</p>
  </div>
  {_table(['Initial handling item', 'Disposition', 'Owner'], handling_rows, class_name='data-table worksheet-table')}
  <div class="small" style="margin-top:8px;">Intake control: {_review_reference(case_id, page_idx, 'FNOL')}</div>
</div>
"""
    return _page(
        "First notice of loss",
        body,
        class_name="first-notice-page",
        source_label="Claim Intake",
    )


def _document_index_page(
    case_id: str,
    page_idx: int,
    rng: random.Random,
    incidents: list[dict[str, Any]],
) -> str:
    document_types = (
        "Loss notice",
        "Photographs",
        "Repair estimate",
        "Coverage inquiry",
        "Police report request",
        "Recorded statement request",
        "Towing invoice",
        "Email correspondence",
        "Recovery notice",
        "Supervisor review",
    )
    rows = []
    for idx, item in enumerate(_sample_window(incidents, page_idx + 2, 30), start=1):
        rows.append(
            [
                f"{page_idx:03d}-{idx:04d}",
                item["reference_number"],
                document_types[(page_idx + idx) % len(document_types)],
                f"{(idx % 12) + 1:02d}/{(idx * 5 % 27) + 1:02d}/2024",
                rng.choice(("Incoming", "Outgoing", "System generated")),
                rng.choice(("Indexed", "Review pending", "Filed")),
            ]
        )
    body = f"""
<div class="system-print">
  <div class="system-banner">
    <span>Imaged Document Inventory</span>
    <span>Control {_review_reference(case_id, page_idx, 'IMG')}</span>
  </div>
  {_table(['Image ID', 'File Ref.', 'Document Description', 'Received / Sent', 'Direction', 'Index Status'], rows, class_name='data-table worksheet-table')}
  <p>End of page - results sorted by image date and document identifier.</p>
</div>
"""
    return _page(
        "Document inventory",
        body,
        class_name="system-print",
        source_label="Imaging System Print",
    )


def _supporting_file_pages(
    config: MultiHopCaseConfig,
    count: int,
    start: int,
    incidents: list[dict[str, Any]],
) -> str:
    rng = random.Random(_stable_seed(7000 + start, config.id, count))
    page_generators = [
        _claim_diary_page,
        _repair_estimate_page,
        _coverage_verification_page,
        _correspondence_page,
        _claim_status_report_page,
        _subrogation_diary_page,
        _first_notice_page,
        _document_index_page,
    ]
    schedule = [page_generators[index % len(page_generators)] for index in range(count)]
    rng.shuffle(schedule)
    pages = []
    previous_name = ""
    for offset, generator in enumerate(schedule):
        if generator.__name__ == previous_name and len(page_generators) > 1:
            swap_index = (offset + 1) % len(schedule)
            schedule[offset], schedule[swap_index] = schedule[swap_index], schedule[offset]
            generator = schedule[offset]
        pages.append(generator(config.id, start + offset, rng, incidents))
        previous_name = generator.__name__
    return "".join(pages)


def _driver_roster_section(incidents: list[dict[str, Any]]) -> str:
    pages: list[str] = []
    roster_rows = incidents + [
        {
            "unit_number": f"2023 ZZ {900000 + i}",
            "driver_name": f"{DRIVER_LAST_NAMES[i % len(DRIVER_LAST_NAMES)]}, Sam",
            "company_name": "Archived Fleet Services",
            "policy_state": "TX",
            "reference_number": f"ARCH-{i:03d}",
        }
        for i in range(1, 7)
    ]
    for page_index, chunk in enumerate(_balanced_chunks(roster_rows, 14), start=1):
        entries = []
        for idx, item in enumerate(chunk, start=1 + (page_index - 1) * 14):
            status = "inactive prior-term unit" if str(item["unit_number"]).startswith("2023 ZZ") else "active scheduled unit"
            unit_label = _label(("Unit", "Equipment", "Scheduled auto"), idx)
            driver_label = _label(("Assigned driver", "Driver assigned", "Operator shown"), idx + 1)
            account_label = _label(("Account / domicile", "Operating account", "Domicile record"), idx + 2)
            entries.append(
                f"""
<article class="claim-card">
  <div class="card-line"><span>{escape(unit_label)}</span><strong>{escape(item["unit_number"])}</strong></div>
  <div class="card-line"><span>{escape(driver_label)}</span><strong>{escape(item["driver_name"])}</strong></div>
  <div class="card-line"><span>{escape(account_label)}</span><strong>{escape(item["company_name"])} - {escape(item["policy_state"])}</strong></div>
  <div class="card-note">Roster status: {escape(status)}. Dispatch reference on file: {escape(item.get("reference_number") or "not shown")}.</div>
</article>"""
            )
        body = f"""
<h2>Fleet Driver Assignment Roster</h2>
<p>Driver assignment cards from the transportation management system. Archived
units are retained in this roster and must not be treated as current losses.</p>
<div class="claim-card-grid">{''.join(entries)}</div>
"""
        title = "Fleet driver assignment roster" if page_index == 1 else "Fleet driver assignment roster continued"
        pages.append(_page(title, body))
    return "".join(pages)


def _policy_register_section(incidents: list[dict[str, Any]]) -> str:
    by_policy: dict[str, dict[str, Any]] = {}
    for item in incidents:
        by_policy[item["policy_number"]] = item
    rows = list(sorted(by_policy.items()))
    rows.extend(
        [
            (
                f"ARCH-{i:03d}",
                {
                    "company_name": "Archive Holdings",
                    "insured": "Archive Holdings",
                    "division": "Runoff",
                    "policy_state": "NY",
                    "agency": "Do Not Use",
                },
            )
            for i in range(1, 5)
        ]
    )
    pages: list[str] = []
    for page_index, chunk in enumerate([rows[i : i + 10] for i in range(0, len(rows), 10)], start=1):
        cards = []
        for idx, (policy, item) in enumerate(chunk, start=1 + (page_index - 1) * 10):
            agency = item.get("agency") or "agency not printed"
            policy_label = _label(("Policy file", "Account policy", "Policy ref."), idx)
            insured_label = _label(("Named insured", "Insured shown", "Insured account"), idx + 1)
            company_label = _label(("Operating company", "Risk name", "Account name"), idx + 2)
            division_label = _label(("Division / state", "Operating division", "State/division"), idx + 3)
            cards.append(
                f"""
<article class="policy-card">
  <div class="card-line"><span>{escape(policy_label)}</span><strong>{escape(policy)}</strong></div>
  <div class="card-line"><span>{escape(insured_label)}</span><strong>{escape(item["insured"])}</strong></div>
  <div class="card-line"><span>{escape(company_label)}</span><strong>{escape(item["company_name"])}</strong></div>
  <div class="card-line"><span>{escape(division_label)}</span><strong>{escape(item.get("division") or "General")} - {escape(item["policy_state"])}</strong></div>
  <div class="card-note">Producer or agency note: {escape(agency)}. Runoff cards are retained for account history only.</div>
</article>"""
            )
        body = f"""
<h2>Policy Register</h2>
<p>Policy administration cards. The same policy may support more than one
current claim, and archived cards may resemble active account numbers.</p>
<div class="policy-card-grid">{''.join(cards)}</div>
"""
        title = "Policy register" if page_index == 1 else "Policy register continued"
        pages.append(_page(title, body))
    return "".join(pages)


def _cause_code_section() -> str:
    entries = []
    for item in CAUSE_CODES:
        entries.append(
            f"""
<div class="cause-entry">
  <strong>{escape(item["code"])}</strong> is assigned to {escape(item["coverage_type"])}
  when the intake narrative describes {escape(item["description"])}. Files coded
  this way are normally routed to <strong>{escape(item["handler"])}</strong> unless
  the reserve authority note requires manager review.
</div>"""
        )
    entries.append(
        """
<div class="cause-entry">
  <strong>REV</strong> appears in older extracts as a review marker. It is not a
  claim cause and should not be used to classify current losses.
</div>"""
    )
    body = f"""
<h2>Loss Cause Classification Appendix</h2>
<p>Internal reference page used by claim intake and reserving systems. The
definitions below are written as filing instructions rather than as a data export.</p>
<div class="cause-list">{''.join(entries)}</div>
"""
    return _page("Loss cause classification appendix", body)


def _claimant_index_section(incidents: list[dict[str, Any]]) -> str:
    pages: list[str] = []
    for page_index, chunk in enumerate(_balanced_chunks(incidents, 12), start=1):
        cards = []
        for idx, item in enumerate(chunk, start=1 + (page_index - 1) * 12):
            claimants = "; ".join(item.get("claimants") or [])
            claim_label = _label(("Claim file", "Notice file", "Mail-room file"), idx)
            party_label = _label(("Notice parties", "Claimant list", "Parties named"), idx + 1)
            ref_label = _label(("Notice ref.", "Mail ref.", "Loss-run ref."), idx + 2)
            cards.append(
                f"""
<article class="claimant-card">
  <div class="card-line"><span>{escape(ref_label)}</span><strong>{escape(item["reference_number"])}</strong></div>
  <div class="card-line"><span>{escape(party_label)}</span><strong>{escape(claimants)}</strong></div>
  <div class="card-note">{escape(item.get("adjuster_notes") or "")}</div>
</article>"""
            )
        body = f"""
<h2>Claimant Notice and Adjuster Note Index</h2>
<div class="two-col">
  <p>This correspondence index includes claimant-side references and adjuster
  diary snippets. Items are indexed by loss-run reference and may be sorted by
  mail-room receipt rather than by claim number.</p>
  <p>Short diary notes are included only when the scanned notice packet retained
  them in the account file.</p>
</div>
<div class="claimant-grid">{''.join(cards)}</div>
"""
        title = "Claimant notice index" if page_index == 1 else "Claimant notice index continued"
        pages.append(_page(title, body))
    return "".join(pages)


def _financial_ledger_section(incidents: list[dict[str, Any]]) -> str:
    pages: list[str] = []
    for page_index, chunk in enumerate(_balanced_chunks(incidents, 8), start=1):
        blocks = []
        for item in chunk:
            cells = []
            for label, key in (("BI", "bi"), ("PD", "pd"), ("LAE", "lae"), ("DED", "ded")):
                values = item.get(key) or {}
                cells.extend(
                    [
                        f'<div class="ledger-label">{label}</div>',
                        f"<div>Reserve<br><strong>{_money(values.get('reserve'))}</strong></div>",
                        f"<div>Paid<br><strong>{_money(values.get('paid'))}</strong></div>",
                        f"<div>Recovered<br><strong>{_money(values.get('recovered'))}</strong></div>",
                        f"<div>Incurred<br><strong>{_money(values.get('total_incurred'))}</strong></div>",
                    ]
                )
            blocks.append(
                f"""
<article class="ledger-claim">
  <div class="card-line"><span>Accounting ref</span><strong>{escape(item["reference_number"])}</strong></div>
  <div class="card-note">Accounting close extract; match this reference to the intake card before assigning claim number.</div>
  <div class="ledger-strip">{''.join(cells)}</div>
</article>"""
            )
        body = f"""
<h2>Claim Financial Ledger</h2>
<p>Reserve and payment ledger by coverage bucket. Each claim block is printed
from the accounting close packet and is keyed by the loss-run reference rather
than by claim number.</p>
<div class="ledger-grid">{''.join(blocks)}</div>
"""
        title = "Claim financial ledger" if page_index == 1 else "Claim financial ledger continued"
        pages.append(_page(title, body))
    return "".join(pages)


def _archived_distractor_section(config: MultiHopCaseConfig, incidents: list[dict[str, Any]]) -> str:
    rows = [
        [
            f"#9{idx:04d}",
            item["reference_number"],
            item["policy_number"],
            "Historical closed-file extract; not part of this valuation set",
        ]
        for idx, item in enumerate(reversed(incidents[:12]), start=1)
    ]
    body = """
<h2>Archived Claims Extract</h2>
<div class="notice">
  Archived extract retained for prior-year comparison. Incident identifiers do
  not belong to the current claim schedule.
</div>
""" + _table(["Claim #", "Reference", "Policy", "Archive Note"], rows)
    return _page("Archived claims extract", body)


def _case_html(config: MultiHopCaseConfig, incidents: list[dict[str, Any]]) -> str:
    first_gap, second_gap, third_gap = config.spacer_pages
    body = (
        _cover_page(config, incidents)
        + _portal_receipt_page(config, incidents)
        + _primary_schedule_page(incidents)
        + _unit_spreadsheet_page(incidents)
        + _supporting_file_pages(config, first_gap, 1, incidents)
        + _driver_roster_section(incidents)
        + _policy_register_section(incidents)
        + _supporting_file_pages(config, second_gap, first_gap + 1, incidents)
        + _cause_code_section()
        + _claimant_index_section(incidents)
        + _supporting_file_pages(config, third_gap, first_gap + second_gap + 1, incidents)
        + _financial_ledger_section(incidents)
    )
    if config.case_type == "mixed":
        body += _supporting_file_pages(config, 6, first_gap + second_gap + third_gap + 1, incidents)
        body += _archived_distractor_section(config, incidents)
    return _html_document("Commercial Auto Claim History", body)


async def _render_pdf(html_path: Path, pdf_path: Path) -> None:
    _ensure_synthetic_imports()
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


def _evidence_map(config: MultiHopCaseConfig) -> list[dict[str, Any]]:
    first_gap, second_gap, third_gap = config.spacer_pages
    return [
        {
            "section": "claim_intake_file_cards",
            "approx_page_after_cover": 1,
            "fields": [
                "incident_number",
                "reference_number",
                "policy_number",
                "unit_number",
                "cause_code",
                "status",
                "date_of_loss",
                "loss_state",
                "date_reported",
            ],
        },
        {
            "section": "fleet_driver_assignment_cards",
            "approx_page_after_cover": 2 + first_gap,
            "join_key": "unit_number",
            "fields": ["driver_name", "company_name", "policy_state"],
        },
        {
            "section": "policy_register_cards",
            "approx_page_after_cover": 3 + first_gap,
            "join_key": "policy_number",
            "fields": ["company_name", "insured", "division", "policy_state", "agency"],
        },
        {
            "section": "loss_cause_classification_narrative",
            "approx_page_after_cover": 4 + first_gap + second_gap,
            "join_key": "cause_code",
            "fields": ["coverage_type", "description", "handler"],
        },
        {
            "section": "claimant_notice_cards",
            "approx_page_after_cover": 5 + first_gap + second_gap,
            "join_key": "reference_number",
            "fields": ["claimants", "adjuster_notes"],
        },
        {
            "section": "claim_financial_ledger_blocks",
            "approx_page_after_cover": 6 + first_gap + second_gap + third_gap,
            "join_key": "reference_number",
            "fields": ["bi", "pd", "lae", "ded"],
        },
    ]


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_case(
    config: MultiHopCaseConfig,
    dataset_dir: Path,
    *,
    base_seed: int,
    render_pdf: bool,
) -> dict[str, Any]:
    ensure_organized_dataset_dirs(dataset_dir)
    incidents = _generate_case_incidents(config, base_seed)

    html_path = artifact_path(dataset_dir, config.id, "html")
    pdf_path = artifact_path(dataset_dir, config.id, "pdf")
    ground_truth_path = artifact_path(dataset_dir, config.id, "ground_truth")
    sample_metadata_path = artifact_path(dataset_dir, config.id, "metadata")

    html = _case_html(config, incidents)
    html_path.write_text(html, encoding="utf-8")
    _write_json(ground_truth_path, incidents)
    if render_pdf:
        asyncio.run(_render_pdf(html_path, pdf_path))

    seed = _stable_seed(base_seed, config.id, config.seed_offset)
    estimated_pages = 9 + sum(config.spacer_pages) + (7 if config.case_type == "mixed" else 0)
    rendered_pages = _count_pdf_pages(pdf_path) if render_pdf else None
    metadata = {
        "id": config.id,
        "difficulty": config.case_type,
        "complexity_regime": "claim_crosspage_multihop",
        "format": "crosspage",
        "domain": "claims",
        "target_record_type": "loss_run_incident",
        "num_claims": len(incidents),
        "num_target_records": len(incidents),
        "pages_estimate": rendered_pages or estimated_pages,
        "pdf_page_count": rendered_pages,
        "document_count": 1,
        "evidence_pattern": "single_document_long_range_cross_page_join",
        "minimum_gap_pages_between_primary_and_last_evidence": sum(config.spacer_pages),
        "problems": list(dict.fromkeys((*config.complexity_tags, *COMMON_CLAIM_STRESSORS))),
        "layout_templates": [
            "packet_cover",
            "portal_receipt",
            "claim_file_cards",
            "spreadsheet_unit_reference",
            "claim_diary",
            "first_notice_of_loss",
            "claim_status_report",
            "coverage_verification",
            "repair_estimate",
            "correspondence_image",
            "imaged_document_inventory",
            "recovery_diary",
            "driver_assignment_cards",
            "policy_register_cards",
            "cause_classification_narrative",
            "claimant_notice_cards",
            "financial_ledger_blocks",
        ],
        "has_duplicates": False,
        "seed": seed,
        "join_requirements": list(config.join_requirements),
        "evidence_map": _evidence_map(config),
        "files": _instance_files(dataset_dir, config.id),
        "transcripts_available": _transcripts_available(dataset_dir, config.id),
    }
    _write_json(sample_metadata_path, metadata)
    return metadata


def _empty_manifest(base_seed: int) -> dict[str, Any]:
    return {
        "dataset_name": SUITE_NAME,
        "version": _dataset_version(),
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


def _merge_manifest(dataset_dir: Path, new_instances: list[dict[str, Any]], base_seed: int) -> dict[str, Any]:
    existing_path = manifest_path(dataset_dir)
    if existing_path.exists():
        manifest = json.loads(existing_path.read_text(encoding="utf-8"))
    else:
        manifest = _empty_manifest(base_seed)

    replaced_ids = {instance["id"] for instance in new_instances}
    instances = [
        instance for instance in manifest.get("instances", [])
        if instance.get("id") not in replaced_ids
    ]
    instances.extend(new_instances)
    instances = sorted(instances, key=lambda item: item["id"])

    manifest["dataset_name"] = manifest.get("dataset_name") or SUITE_NAME
    manifest["version"] = _dataset_version()
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

    _write_json(dataset_dir / "manifest.json", manifest)
    _write_json(dataset_dir / "metadata.json", manifest)
    return manifest


def generate_multihop_suite(
    output_dir: Path,
    *,
    base_seed: int = 4242,
    render_pdfs: bool = True,
    case_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Generate configured cross-page cases into the organized dataset layout."""
    ensure_organized_dataset_dirs(output_dir)
    selected_configs = [
        config for config in MULTIHOP_CASE_CONFIGS if case_ids is None or config.id in case_ids
    ]

    cases = [
        _write_case(config, output_dir, base_seed=base_seed, render_pdf=render_pdfs)
        for config in selected_configs
    ]
    manifest = _merge_manifest(output_dir, cases, base_seed)

    return {
        "suite_name": "longlistbench-crosspage-multihop",
        "version": _dataset_version(),
        "description": "Single-document long-range cross-page multi-hop extraction cases.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_seed": base_seed,
        "total_cases": len(cases),
        "total_documents": len(cases),
        "total_incidents": sum(case["num_claims"] for case in cases),
        "case_types": sorted({case["complexity_regime"] for case in cases}),
        "manifest": "manifest.json",
        "dataset_total_instances": manifest["total_instances"],
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LongListBench cross-page multi-hop cases")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Organized dataset directory (default: data)",
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

    print(f"Generated {metadata['total_cases']} cross-page cases in {args.output}")
    print(f"Total documents: {metadata['total_documents']}")
    print(f"Total incidents: {metadata['total_incidents']}")


if __name__ == "__main__":
    main()
