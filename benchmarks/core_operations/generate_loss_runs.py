#!/usr/bin/env python3
"""Generate deterministic synthetic loss-run artifacts for LongListBench."""

from __future__ import annotations

import argparse
import asyncio
import html
import json
import math
import random
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]


FIRST_NAMES = [
    "Avery",
    "Blake",
    "Casey",
    "Dakota",
    "Emery",
    "Finley",
    "Harper",
    "Jordan",
    "Kai",
    "Logan",
    "Morgan",
    "Parker",
    "Quinn",
    "Reese",
    "Rowan",
    "Sawyer",
    "Taylor",
    "Vaughn",
    "Winter",
    "Zion",
]
LAST_NAMES = [
    "Aldridge",
    "Benton",
    "Carver",
    "Delaney",
    "Ellis",
    "Foster",
    "Gaines",
    "Hollis",
    "Ivers",
    "Keller",
    "Larkin",
    "Mercer",
    "Nolan",
    "Osborne",
    "Priest",
    "Quint",
    "Ramos",
    "Serrano",
    "Talbot",
    "Voss",
]
CLAIMANTS = [
    "Alder Logistics Repair",
    "Bayline Warehouse",
    "Canyon Fleet Body",
    "Dover Equipment Rental",
    "East Ridge Collision",
    "Fairmont Cold Storage",
    "Grove Street Produce",
    "Harbor Medical Supply",
    "Ironwood Trailer Works",
    "Juniper Transit Yard",
    "Keystone Materials",
    "Lakeview Auto Glass",
    "Mason Retail Group",
    "Northline Distribution",
    "Oak Valley Repair",
    "Palisade Container",
    "Quarry Road Terminal",
    "Riverbend Concrete",
    "Stonebridge Foods",
    "Tamarack Freight",
]
INSUREDS = [
    "Northstar Cartage LLC",
    "Harborline Produce Transport Inc",
    "Cedar Valley Supply Chain LLC",
]
DESCRIPTIONS = [
    "rear impact while backing toward a dock door",
    "cargo load shifted during an abrupt traffic stop",
    "windshield and cowl damage attributed to road debris",
    "minor bodily injury allegation after a lane-change contact",
    "parked tractor struck during overnight staging",
    "trailer door contacted by loading equipment",
    "property damage reported at a private receiving yard",
    "towing and storage reimbursement requested after disablement",
    "side-swipe contact reported near an interstate ramp",
    "forklift contact with parked trailer during unloading",
    "mirror and fairing damage found after delivery",
    "subrogation file opened for possible third-party recovery",
    "cargo shortage noticed after consignee inspection",
    "fuel-island scrape reported during yard maneuver",
    "reefer unit service call included in repair estimate",
    "parking-lot contact reported by third-party claimant",
    "steer tire failure led to roadside service invoice",
    "roll-up door damage noted during post-trip inspection",
    "loading bay bollard contact reported by warehouse staff",
    "claim opened from late-submitted repair documentation",
]
DESCRIPTION_DETAILS = [
    "photos were received with the initial notice",
    "repair estimate remains under carrier review",
    "liability position was not final at valuation date",
    "rental and downtime amounts were still being reconciled",
    "supplemental invoice was requested from the vendor",
    "subrogation diary was retained for follow-up",
    "medical reserve was reviewed without closing the file",
    "salvage credit had not posted to the run",
    "coverage was accepted subject to deductible application",
    "claim notes reference separate correspondence from the claimant",
]
CONTINUATION_NOTES = [
    "Continuation: reserve position retained pending supervisor diary review.",
    "Continuation: payment history may exclude late-posted recovery activity.",
    "Continuation: claim office noted deductible handling outside this extract.",
    "Continuation: liability review remains tied to the listed unit file.",
    "Continuation: closing date reflects carrier system status at valuation.",
    "Continuation: vendor documentation was indexed after first notice.",
]
FOOTNOTES = [
    "Recoveries shown above may not include salvage posted after the valuation date.",
    "Closed claims can reopen if a supplemental medical bill or repair invoice is received.",
    "Driver information is shown only when included in the carrier export.",
    "Some zero activity policy periods are retained for underwriting continuity.",
    "Rows marked pending are subject to reserve review by the carrier claim office.",
]
STATES = ["PA", "OH", "NJ", "MD", "VA", "NY"]
STATUSES = ["Open", "Closed", "Pending", "Reopened"]


@dataclass(frozen=True)
class Section:
    section_index: int
    policy_number: str
    customer_number: str
    insured: str
    state: str
    effective_date: date
    expiry_date: date
    claims: list[dict[str, Any]]
    no_claims: bool = False


def _money(value: float | int) -> str:
    return f"${value:,.2f}"


def _date(value: date | None) -> str:
    return value.strftime("%m/%d/%y") if value else ""


def _synthetic_name(rng: random.Random, index: int) -> str:
    first = FIRST_NAMES[(index + rng.randrange(len(FIRST_NAMES))) % len(FIRST_NAMES)]
    last = LAST_NAMES[(index * 3 + rng.randrange(len(LAST_NAMES))) % len(LAST_NAMES)]
    middle = chr(ord("A") + (index + rng.randrange(26)) % 26)
    return f"{first} {middle}. {last}"


def _make_claim(
    rng: random.Random,
    section: Section,
    local_index: int,
    global_index: int,
    sample_offset: int,
) -> dict[str, Any]:
    loss_date = section.effective_date + timedelta(days=20 + (global_index * 7) % 300)
    reported_date = loss_date + timedelta(days=1 + (global_index * 5) % 42)
    status = STATUSES[(global_index + rng.randrange(len(STATUSES))) % len(STATUSES)]
    is_closed = status == "Closed" or (status == "Reopened" and global_index % 3 == 0)
    closed_date = reported_date + timedelta(days=40 + (global_index * 11) % 210) if is_closed else None

    if status == "Closed":
        reserve = 0.0
        paid = round(750 + ((global_index * 2837) % 68000) + rng.random(), 2)
    else:
        reserve = round(1200 + ((global_index * 4129) % 92000) + rng.random(), 2)
        paid = round(((global_index * 617) % 42000) * (0.25 if status == "Open" else 0.55), 2)
    recovered = round(((global_index * 151) % 19000) * (0.4 if global_index % 5 == 0 else 0.0), 2)

    driver_visible = global_index % 4 != 0
    driver = _synthetic_name(rng, global_index) if driver_visible else ""
    claim_prefix = section.policy_number.replace("SC", "")
    claim_number = f"{claim_prefix}-{sample_offset + global_index:05d}"
    desc = DESCRIPTIONS[(global_index + rng.randrange(len(DESCRIPTIONS))) % len(DESCRIPTIONS)]
    if global_index % 7 == 0:
        desc += f"; {DESCRIPTION_DETAILS[(global_index + rng.randrange(len(DESCRIPTION_DETAILS))) % len(DESCRIPTION_DETAILS)]}"
    if global_index % 11 == 0:
        desc += f"; {DESCRIPTION_DETAILS[(global_index * 3 + rng.randrange(len(DESCRIPTION_DETAILS))) % len(DESCRIPTION_DETAILS)]}"

    return {
        "policy_number": section.policy_number,
        "effective_date": _date(section.effective_date),
        "claim_reported": "X",
        "claim_number": claim_number,
        "claimant": CLAIMANTS[(global_index + rng.randrange(len(CLAIMANTS))) % len(CLAIMANTS)],
        "date_reported": _date(reported_date),
        "date_of_loss": _date(loss_date),
        "claim_status": status,
        "date_closed": _date(closed_date),
        "adjuster": _synthetic_name(rng, global_index + 1000),
        "claim_reserves": reserve,
        "claim_paid": paid,
        "claim_recovered": recovered,
        "description": desc,
        "driver": driver,
        "_unit": f"TR-{1000 + (global_index * 17) % 8900}",
        "_note_style": global_index % 6,
        "_detail_style": global_index % 9,
        "_local_index": local_index,
    }


def build_sections(sample_number: int, seed: int, total_claims: int = 300) -> tuple[list[Section], list[dict[str, Any]]]:
    rng = random.Random(seed)
    insured = INSUREDS[(sample_number - 1) % len(INSUREDS)]
    claim_rows: list[dict[str, Any]] = []
    sections: list[Section] = []
    global_index = 0
    policy_base = 928000 + sample_number * 137
    customer_base = 43000 + sample_number * 100
    start = date(2019, 4, 1) + timedelta(days=sample_number * 11)
    pattern = [8, 0, 5, 12, 1, 11, 0, 3, 6, 9, 4, 12, 0, 7, 10, 2, 13, 0, 5, 8, 3, 9]

    section_index = 0
    while global_index < total_claims:
        count = pattern[section_index % len(pattern)]
        if count and global_index + count > total_claims:
            count = total_claims - global_index
        effective = start + timedelta(days=365 * (section_index % 5) + 17 * (section_index // 5))
        policy = f"SC{policy_base + section_index:08d}"
        state = STATES[(section_index + sample_number) % len(STATES)]
        section_claims: list[dict[str, Any]] = []
        placeholder = Section(
            section_index=section_index,
            policy_number=policy,
            customer_number=f"C{customer_base + section_index:06d}",
            insured=insured,
            state=state,
            effective_date=effective,
            expiry_date=effective + timedelta(days=365),
            claims=[],
            no_claims=count == 0,
        )
        for local_index in range(count):
            row = _make_claim(
                rng=rng,
                section=placeholder,
                local_index=local_index + 1,
                global_index=global_index,
                sample_offset=10000,
            )
            section_claims.append(row)
            public_row = {key: value for key, value in row.items() if not key.startswith("_")}
            claim_rows.append(public_row)
            global_index += 1
        sections.append(
            Section(
                section_index=section_index,
                policy_number=policy,
                customer_number=placeholder.customer_number,
                insured=insured,
                state=state,
                effective_date=effective,
                expiry_date=placeholder.expiry_date,
                claims=section_claims,
                no_claims=count == 0,
            )
        )
        section_index += 1

    # Add trailing zero-claim periods, like carrier exports often do.
    for extra in range(4):
        idx = section_index + extra
        effective = start + timedelta(days=365 * (idx % 5) + 17 * (idx // 5))
        sections.append(
            Section(
                section_index=idx,
                policy_number=f"SC{policy_base + idx:08d}",
                customer_number=f"C{customer_base + idx:06d}",
                insured=insured,
                state=STATES[(idx + sample_number) % len(STATES)],
                effective_date=effective,
                expiry_date=effective + timedelta(days=365),
                claims=[],
                no_claims=True,
            )
        )

    return sections, claim_rows


def _css() -> str:
    return """
@page { size: letter landscape; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; color: #111; background: #eee; font-family: Arial, Helvetica, sans-serif; }
.page {
  width: 11in; min-height: 8.5in; page-break-after: always; background: white;
  padding: 0.30in 0.34in 0.25in 0.34in; position: relative;
}
.batch-header { display: grid; grid-template-columns: 1.2in 1fr 1.6in; align-items: start; gap: 0.16in; margin-bottom: 0.08in; }
.claims-mark { font-size: 9px; line-height: 1.02; color: #17365d; border: 1px solid #17365d; padding: 5px; width: 0.95in; text-align: center; letter-spacing: .3px; }
.claims-mark b { font-size: 10px; }
h1 { margin: 0; text-align: center; font-size: 16px; letter-spacing: .2px; font-weight: 700; }
.run-meta { text-align: right; font-size: 8px; line-height: 1.35; color: #333; }
.section-card { border-top: 2px solid #222; margin-top: 0.06in; padding-top: 0.04in; }
.section-grid { display: grid; grid-template-columns: 1.5fr 0.75fr 0.85fr 0.55fr 0.75fr; gap: 0.04in; font-size: 8.5px; line-height: 1.25; margin-bottom: 0.04in; }
.label { color: #444; text-transform: uppercase; font-size: 7px; letter-spacing: .2px; }
.value { font-weight: 700; }
.loss-table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 7.35px; line-height: 1.1; }
.loss-table th { border-top: 1px solid #333; border-bottom: 1px solid #333; padding: 3px 2px; text-align: left; vertical-align: bottom; font-weight: 700; background: #f4f4f4; }
.loss-table td { padding: 2.5px 2px; vertical-align: top; border-bottom: 1px solid #d5d5d5; overflow-wrap: anywhere; }
.loss-table .num, .loss-table .money { text-align: right; font-variant-numeric: tabular-nums; }
.loss-table .center { text-align: center; }
.loss-table .desc td { padding: 2px 3px 4px 0.18in; border-bottom: 0; color: #222; }
.loss-table .note td { font-size: 7px; color: #4a4a4a; padding-left: 0.08in; border-bottom: 0; }
.loss-table .separator td { border-bottom: 1px solid #888; padding: 0; height: 1px; }
.loss-table .totals td { border-top: 1px solid #222; border-bottom: 0; font-weight: 700; background: #fafafa; }
.loss-table .no-claims td { border: 1px solid #aaa; padding: 8px 5px; font-weight: 700; color: #222; background: #fbfbfb; }
.loss-table .small { font-size: 6.8px; color: #333; }
.claim-card { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 7.5px; line-height: 1.14; margin-top: 0.02in; }
.claim-card td { border: 1px solid #c8c8c8; padding: 3px 4px; vertical-align: top; overflow-wrap: anywhere; }
.claim-card .block-label { color: #444; text-transform: uppercase; font-size: 6.6px; letter-spacing: .15px; }
.claim-card .block-value { font-weight: 700; margin-top: 1px; }
.claim-card .amounts { background: #f9f9f9; font-variant-numeric: tabular-nums; }
.claim-card .detail { color: #222; }
.claim-card .subnote { color: #444; font-size: 6.9px; }
.register-title { font-size: 8px; font-weight: 700; text-transform: uppercase; border-bottom: 1px solid #333; margin: 0.06in 0 0.03in; padding-bottom: 0.02in; }
.reserve-panel { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 0.04in; border: 1px solid #bbb; padding: 0.04in; margin: 0.03in 0; font-size: 7.2px; background: #fbfbfb; }
.reserve-panel div { min-height: 0.16in; }
.reserve-panel .label { font-size: 6.4px; }
.micro-ledger { width: 100%; border-collapse: collapse; font-size: 7.25px; line-height: 1.1; margin-top: 0.02in; }
.micro-ledger td, .micro-ledger th { border: 1px solid #ccc; padding: 2px 3px; text-align: left; vertical-align: top; }
.micro-ledger th { background: #f4f4f4; font-size: 6.8px; text-transform: uppercase; }
.footnote { margin: 0.04in 0 0.01in 0.08in; font-size: 7px; color: #333; }
.continued { font-size: 7px; text-align: right; margin-top: 0.02in; color: #555; font-style: italic; }
.footer { position: absolute; left: 0.34in; right: 0.34in; bottom: 0.12in; border-top: 1px solid #999; padding-top: 0.03in; display: flex; justify-content: space-between; font-size: 7px; color: #333; }
.watermark { position: absolute; right: .5in; top: 3.7in; transform: rotate(-18deg); color: rgba(0,0,0,0.045); font-size: 54px; font-weight: 700; pointer-events: none; }
.thin { font-weight: 400; }
.w-eff { width: 7%; } .w-rep { width: 4%; } .w-num { width: 12%; } .w-claimant { width: 15%; }
.w-date { width: 7%; } .w-status { width: 6%; } .w-adjuster { width: 12%; } .w-money { width: 9%; }
"""


def _header(title: str, section: Section, page_num: int, page_count: int, valuation: str) -> str:
    return f"""
<div class="batch-header">
  <div class="claims-mark">CLAIMS<br><b>DIRECT ACCESS</b></div>
  <div>
    <h1>{html.escape(title)}</h1>
    <div style="text-align:center;font-size:8px;margin-top:3px;">External carrier loss history - as valued {valuation}</div>
  </div>
  <div class="run-meta">
    Run ID LR-{page_num:04d}<br>
    Page {page_num} of {page_count}<br>
    Printed 02/26/2026
  </div>
</div>
<div class="section-grid">
  <div><div class="label">Insured Name</div><div class="value">{html.escape(section.insured)}</div></div>
  <div><div class="label">Customer No.</div><div class="value">{html.escape(section.customer_number)}</div></div>
  <div><div class="label">Policy No.</div><div class="value">{html.escape(section.policy_number)}</div></div>
  <div><div class="label">State</div><div class="value">{html.escape(section.state)}</div></div>
  <div><div class="label">Policy Term</div><div class="value">{_date(section.effective_date)} - {_date(section.expiry_date)}</div></div>
</div>
"""


def _table_header() -> str:
    return """
<table class="loss-table">
<thead>
<tr>
  <th class="w-eff">Effective<br>Date</th>
  <th class="w-rep">Claim<br>Rptd</th>
  <th class="w-num">Claim Number</th>
  <th class="w-claimant">Claimant</th>
  <th class="w-date">Date<br>Reported</th>
  <th class="w-date">Date of<br>Loss</th>
  <th class="w-status">Status</th>
  <th class="w-date">Date<br>Closed</th>
  <th class="w-adjuster">Adjuster</th>
  <th class="w-money">Reserve</th>
  <th class="w-money">Paid</th>
  <th class="w-money">Recovered</th>
</tr>
</thead>
<tbody>
"""


def _claim_html(claim: dict[str, Any], rng: random.Random) -> str:
    note_style = claim["_note_style"]
    detail_style = claim["_detail_style"]
    driver = claim["driver"]
    unit = claim["_unit"]
    desc = html.escape(claim["description"])
    driver_note = ""
    if driver:
        if note_style in (0, 1):
            driver_note = f" &nbsp; | &nbsp; Driver: {html.escape(driver)}"
        elif note_style in (2, 3):
            driver_note = f" &nbsp; Unit {html.escape(unit)} / Operator {html.escape(driver)}"
        else:
            driver_note = f" &nbsp; Scheduled driver noted separately: {html.escape(driver)}"
    elif note_style in (4, 5):
        driver_note = " &nbsp; Driver not supplied in carrier export"

    continuation = ""
    if len(claim["description"]) > 70 or rng.random() < 0.18:
        continuation = (
            "<tr class='note'><td colspan='12'>"
            f"{html.escape(rng.choice(CONTINUATION_NOTES))} Unit {html.escape(unit)}."
            "</td></tr>"
        )
    detail_note = ""
    adjuster_cell = html.escape(claim["adjuster"])
    reserve_cell = _money(claim["claim_reserves"])
    paid_cell = _money(claim["claim_paid"])
    recovered_cell = _money(claim["claim_recovered"])
    if detail_style in (3, 7):
        adjuster_cell = "<span class='thin'>see ledger</span>"
        reserve_cell = paid_cell = recovered_cell = "<span class='thin'>see below</span>"
        detail_note = (
            "<tr class='note'><td colspan='12'>"
            f"Claim ledger: adjuster {html.escape(claim['adjuster'])}; reserve {_money(claim['claim_reserves'])}; "
            f"paid {_money(claim['claim_paid'])}; recovery {_money(claim['claim_recovered'])}."
            "</td></tr>"
        )
    elif detail_style == 5:
        reserve_cell = "<span class='thin'>pending ledger</span>"
        detail_note = (
            "<tr class='note'><td colspan='12'>"
            f"Financial detail: reserve carried as {_money(claim['claim_reserves'])}; "
            f"payments {_money(claim['claim_paid'])}; recoveries {_money(claim['claim_recovered'])}."
            "</td></tr>"
        )
    maybe_separator = "<tr class='separator'><td colspan='12'></td></tr>" if rng.random() < 0.08 else ""
    return f"""
<tr>
  <td>{html.escape(claim['effective_date'])}</td>
  <td class="center">{html.escape(claim['claim_reported'])}</td>
  <td>{html.escape(claim['claim_number'])}</td>
  <td>{html.escape(claim['claimant'])}</td>
  <td>{html.escape(claim['date_reported'])}</td>
  <td>{html.escape(claim['date_of_loss'])}</td>
  <td>{html.escape(claim['claim_status'])}</td>
  <td>{html.escape(claim['date_closed'])}</td>
  <td>{adjuster_cell}</td>
  <td class="money">{reserve_cell}</td>
  <td class="money">{paid_cell}</td>
  <td class="money">{recovered_cell}</td>
</tr>
<tr class="desc"><td colspan="12"><span class="small">Initial Claim Description:</span> {desc}{driver_note}</td></tr>
{detail_note}
{continuation}
{maybe_separator}
"""


def _driver_sentence(claim: dict[str, Any], note_style: int) -> str:
    driver = claim["driver"]
    unit = claim["_unit"]
    if driver:
        if note_style in (0, 1):
            return f"Driver: {html.escape(driver)}"
        if note_style in (2, 3):
            return f"Unit {html.escape(unit)} / Operator {html.escape(driver)}"
        return f"Scheduled driver: {html.escape(driver)}"
    if note_style in (4, 5):
        return "Driver not supplied in carrier export"
    return ""


def _claim_register_html(claim: dict[str, Any], rng: random.Random) -> str:
    driver_text = _driver_sentence(claim, claim["_note_style"])
    closed = claim["date_closed"] or "not closed"
    amount_line = (
        f"Reserve {_money(claim['claim_reserves'])} / Paid {_money(claim['claim_paid'])} / "
        f"Recovered {_money(claim['claim_recovered'])}"
    )
    audit_note = rng.choice(
        [
            "Carrier file extract; amount fields are valued as of report date.",
            "Entry retained in underwriting view even if activity is closed.",
            "Claim office notes may continue on adjacent lines in the source export.",
            "Loss data imported from carrier history rather than agency summary.",
        ]
    )
    return f"""
<tr>
  <td colspan="2"><div class="block-label">Claim file</div><div class="block-value">{html.escape(claim['claim_number'])}</div><div class="subnote">Effective {html.escape(claim['effective_date'])}</div></td>
  <td colspan="2"><div class="block-label">Claimant / loss</div><div class="block-value">{html.escape(claim['claimant'])}</div><div class="subnote">DOL {html.escape(claim['date_of_loss'])}; reported {html.escape(claim['date_reported'])}</div></td>
  <td colspan="1"><div class="block-label">Status</div><div class="block-value">{html.escape(claim['claim_status'])}</div><div class="subnote">Closed: {html.escape(closed)}</div></td>
  <td colspan="1"><div class="block-label">Rptd</div><div class="block-value">{html.escape(claim['claim_reported'])}</div></td>
</tr>
<tr class="amounts">
  <td colspan="3"><div class="block-label">Assigned handling</div><div class="block-value">{html.escape(claim['adjuster'])}</div><div class="subnote">{driver_text}</div></td>
  <td colspan="3"><div class="block-label">Financial position</div><div class="block-value">{html.escape(amount_line)}</div></td>
</tr>
<tr>
  <td colspan="6" class="detail"><span class="block-label">Claim description</span> {html.escape(claim['description'])}<br><span class="subnote">{html.escape(audit_note)}</span></td>
</tr>
"""


def _claim_card_html(claim: dict[str, Any], rng: random.Random) -> str:
    driver_text = _driver_sentence(claim, claim["_note_style"])
    detail_style = claim["_detail_style"]
    if detail_style in (3, 7):
        financial_text = (
            f"Separate ledger entry: {html.escape(claim['adjuster'])}; "
            f"reserve {_money(claim['claim_reserves'])}; paid {_money(claim['claim_paid'])}; "
            f"recovery {_money(claim['claim_recovered'])}."
        )
        handler_text = "see adjacent ledger"
    elif detail_style == 5:
        financial_text = (
            f"Pending ledger: reserve {_money(claim['claim_reserves'])}; "
            f"payments {_money(claim['claim_paid'])}; recoveries {_money(claim['claim_recovered'])}."
        )
        handler_text = html.escape(claim["adjuster"])
    else:
        financial_text = (
            f"Reserve {_money(claim['claim_reserves'])}; paid {_money(claim['claim_paid'])}; "
            f"recovered {_money(claim['claim_recovered'])}."
        )
        handler_text = html.escape(claim["adjuster"])
    extra = ""
    if rng.random() < 0.22:
        extra = f"<div class='subnote'>{html.escape(rng.choice(CONTINUATION_NOTES))} {html.escape(claim['_unit'])}.</div>"
    return f"""
<tr>
  <td colspan="2"><div class="block-label">Claim number</div><div class="block-value">{html.escape(claim['claim_number'])}</div></td>
  <td colspan="2"><div class="block-label">Claimant</div><div class="block-value">{html.escape(claim['claimant'])}</div></td>
  <td><div class="block-label">Loss date</div><div class="block-value">{html.escape(claim['date_of_loss'])}</div></td>
  <td><div class="block-label">Reported</div><div class="block-value">{html.escape(claim['date_reported'])}</div></td>
</tr>
<tr>
  <td><div class="block-label">Rptd</div><div class="block-value">{html.escape(claim['claim_reported'])}</div></td>
  <td><div class="block-label">Status</div><div class="block-value">{html.escape(claim['claim_status'])}</div></td>
  <td><div class="block-label">Closed</div><div class="block-value">{html.escape(claim['date_closed'] or '')}</div></td>
  <td colspan="3"><div class="block-label">Handler / driver</div><div class="block-value">{handler_text}</div><div class="subnote">{driver_text}</div></td>
</tr>
<tr class="amounts"><td colspan="6"><span class="block-label">Amounts</span> {financial_text}</td></tr>
<tr><td colspan="6" class="detail"><span class="block-label">Description</span> {html.escape(claim['description'])}{extra}</td></tr>
"""


def _claim_micro_ledger_html(claim: dict[str, Any], rng: random.Random) -> str:
    driver_text = _driver_sentence(claim, claim["_note_style"])
    return f"""
<tr>
  <td>{html.escape(claim['claim_number'])}<br><span class="subnote">eff. {html.escape(claim['effective_date'])}; rptd {html.escape(claim['claim_reported'])}</span></td>
  <td>{html.escape(claim['claimant'])}<br><span class="subnote">{html.escape(claim['description'])}</span></td>
  <td>{html.escape(claim['date_of_loss'])}<br><span class="subnote">reported {html.escape(claim['date_reported'])}</span></td>
  <td>{html.escape(claim['claim_status'])}<br><span class="subnote">closed {html.escape(claim['date_closed'] or '-')}</span></td>
  <td>{html.escape(claim['adjuster'])}<br><span class="subnote">{driver_text}</span></td>
  <td>reserve {_money(claim['claim_reserves'])}<br>paid {_money(claim['claim_paid'])}<br>recovered {_money(claim['claim_recovered'])}</td>
</tr>
"""


def _section_layout(section: Section) -> str:
    if section.no_claims:
        return "schedule"
    count = len(section.claims)
    variant = section.section_index % 4
    if variant == 1 and count <= 5:
        return "register"
    if variant == 2 and count <= 5:
        return "card"
    if variant == 3 and count <= 10:
        return "micro_ledger"
    return "schedule"


def _section_table_open(layout: str) -> str:
    if layout == "schedule":
        return _table_header()
    if layout == "register":
        return """
<div class="register-title">Claim file register - carrier history extract</div>
<table class="claim-card"><tbody>
"""
    if layout == "card":
        return """
<div class="register-title">Claim summary cards - policy period activity</div>
<table class="claim-card"><tbody>
"""
    return """
<div class="register-title">Reserve ledger view - open and closed claim activity</div>
<table class="micro-ledger">
<thead><tr><th>Claim / rptd</th><th>Claimant / notes</th><th>Dates</th><th>Status</th><th>Handling</th><th>Amounts</th></tr></thead>
<tbody>
"""


def _claim_for_layout(claim: dict[str, Any], rng: random.Random, layout: str) -> str:
    if layout == "register":
        return _claim_register_html(claim, rng)
    if layout == "card":
        return _claim_card_html(claim, rng)
    if layout == "micro_ledger":
        return _claim_micro_ledger_html(claim, rng)
    return _claim_html(claim, rng)


def _totals_for_layout(section: Section, layout: str) -> str:
    if layout == "schedule":
        return _totals_row(section)
    reserve = sum(float(row["claim_reserves"]) for row in section.claims)
    paid = sum(float(row["claim_paid"]) for row in section.claims)
    recovered = sum(float(row["claim_recovered"]) for row in section.claims)
    if layout == "micro_ledger":
        return f"""
<tr class="totals"><td colspan="5">Policy period total for {html.escape(section.policy_number)}</td><td>reserve {_money(reserve)}<br>paid {_money(paid)}<br>recovered {_money(recovered)}</td></tr>
"""
    return f"""
<tr class="amounts"><td colspan="6"><span class="block-label">Policy period total for {html.escape(section.policy_number)}</span>
Reserve {_money(reserve)} &nbsp; Paid {_money(paid)} &nbsp; Recovered {_money(recovered)}</td></tr>
"""


def _totals_row(section: Section) -> str:
    reserve = sum(float(row["claim_reserves"]) for row in section.claims)
    paid = sum(float(row["claim_paid"]) for row in section.claims)
    recovered = sum(float(row["claim_recovered"]) for row in section.claims)
    return f"""
<tr class="totals">
  <td colspan="9">Policy period total for {html.escape(section.policy_number)}</td>
  <td class="money">{_money(reserve)}</td>
  <td class="money">{_money(paid)}</td>
  <td class="money">{_money(recovered)}</td>
</tr>
"""


def paginate_sections(sections: list[Section], seed: int) -> list[list[Section]]:
    rng = random.Random(seed + 9901)
    pages: list[list[Section]] = []
    current: list[Section] = []
    used = 0
    page_budget = rng.choice([34, 36, 38])
    for section in sections:
        # Approximate vertical cost in table rows. This intentionally varies by
        # section so rows per page are not mechanically constant.
        layout = _section_layout(section)
        if section.no_claims:
            cost = 5
        elif layout == "schedule":
            cost = 6 + len(section.claims) * 2.45 + sum(1 for c in section.claims if c["_detail_style"] in (3, 5, 7)) * 0.7
        elif layout == "register":
            cost = 7 + len(section.claims) * 3.35
        elif layout == "card":
            cost = 7 + len(section.claims) * 4.25
        else:
            cost = 7 + len(section.claims) * 2.1
        if current and used + cost > page_budget:
            pages.append(current)
            current = []
            used = 0
            page_budget = rng.choice([34, 36, 38])
        current.append(section)
        used += cost
    if current:
        pages.append(current)
    return pages


def render_html(sample_id: str, sections: list[Section], seed: int) -> str:
    rng = random.Random(seed + 4400)
    pages = paginate_sections(sections, seed)
    valuation = "02/26/2026"
    page_html: list[str] = []
    for page_index, page_sections in enumerate(pages, start=1):
        first_section = page_sections[0]
        blocks = [
            '<section class="page">',
            '<div class="watermark">CLAIM COPY</div>' if page_index % 7 == 0 else "",
            _header("Loss Run Report", first_section, page_index, len(pages), valuation),
        ]
        for section in page_sections:
            blocks.append('<div class="section-card">')
            if section is not first_section:
                blocks.append(
                    '<div class="section-grid">'
                    f'<div><div class="label">Insured Name</div><div class="value">{html.escape(section.insured)}</div></div>'
                    f'<div><div class="label">Customer No.</div><div class="value">{html.escape(section.customer_number)}</div></div>'
                    f'<div><div class="label">Policy No.</div><div class="value">{html.escape(section.policy_number)}</div></div>'
                    f'<div><div class="label">State</div><div class="value">{html.escape(section.state)}</div></div>'
                    f'<div><div class="label">Policy Term</div><div class="value">{_date(section.effective_date)} - {_date(section.expiry_date)}</div></div>'
                    "</div>"
                )
            layout = _section_layout(section)
            blocks.append(_section_table_open(layout))
            if section.no_claims:
                blocks.append(
                    f"<tr class='no-claims'><td colspan='12'>No Claims Reported as of: {valuation}</td></tr>"
                    "<tr class='totals'><td colspan='9'>Policy period total</td><td class='money'>$0.00</td><td class='money'>$0.00</td><td class='money'>$0.00</td></tr>"
                )
            else:
                for claim in section.claims:
                    blocks.append(_claim_for_layout(claim, rng, layout))
                    if claim["_local_index"] % 7 == 0 and rng.random() < 0.35:
                        if layout == "schedule":
                            blocks.append(
                                f"<tr class='note'><td colspan='12'>Section note: {html.escape(rng.choice(FOOTNOTES))}</td></tr>"
                            )
                        elif layout == "micro_ledger":
                            blocks.append(
                                f"<tr><td colspan='6' class='subnote'>Section note: {html.escape(rng.choice(FOOTNOTES))}</td></tr>"
                            )
                        else:
                            blocks.append(
                                f"<tr><td colspan='6' class='subnote'>Section note: {html.escape(rng.choice(FOOTNOTES))}</td></tr>"
                            )
                blocks.append(_totals_for_layout(section, layout))
            blocks.append("</tbody></table>")
            if rng.random() < 0.25:
                blocks.append(f"<div class='footnote'>{html.escape(rng.choice(FOOTNOTES))}</div>")
            blocks.append("</div>")
        if page_index < len(pages) and rng.random() < 0.4:
            blocks.append("<div class='continued'>continued on next page</div>")
        blocks.append(
            f"<div class='footer'><span>Carrier claim history export - underwriting copy</span><span>Page {page_index} of {len(pages)}</span></div>"
        )
        blocks.append("</section>")
        page_html.append("\n".join(blocks))
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{html.escape(sample_id)}</title>
<style>{_css()}</style>
</head>
<body>
{''.join(page_html)}
</body>
</html>
"""


async def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from benchmarks.synthetic.html_to_pdf import html_to_pdf as render

    await render(html_path, pdf_path)


def write_metadata(sample_id: str, out_dir: Path, target_count: int, pages: int) -> dict[str, Any]:
    metadata = {
        "id": sample_id,
        "template": "loss_run_external",
        "target_record_type": "loss_run_claim_row",
        "num_target_records": target_count,
        "source_batch": "loss-run-hardened",
        "artifacts": {
            "pdf": f"pdfs/{sample_id}.pdf",
            "html": f"html/{sample_id}.html",
            "ground_truth": f"ground_truth/{sample_id}.json",
        },
        "provenance": "Deterministic synthetic values rendered by the public LongListBench generator; no production records are inputs.",
        "files": {
            "ground_truth": f"ground_truth/{sample_id}.json",
            "pdf": f"pdfs/{sample_id}.pdf",
            "html": f"html/{sample_id}.html",
            "metadata": f"metadata/{sample_id}.json",
            "json_size_bytes": (out_dir / "ground_truth" / f"{sample_id}.json").stat().st_size,
            "pdf_size_bytes": (out_dir / "pdfs" / f"{sample_id}.pdf").stat().st_size,
            "html_size_bytes": (out_dir / "html" / f"{sample_id}.html").stat().st_size,
            "ocr_md": f"transcripts/ocr_gemini/{sample_id}.md",
            "ocr_size_bytes": 0,
        },
        "transcripts_available": [],
        "complexity_regime": "loss_run_external",
        "difficulty": "loss_run_external",
        "format": "production_like_pdf",
        "domain": "commercial_insurance_operations",
        "problems": [
            "high_density_long_list",
            "production_like_layout",
            "variable_policy_sections",
            "continuation_notes",
            "summary_distractors",
            "sparse_driver_fields",
        ],
        "pages_estimate": pages,
        "pdf_page_count": pages,
        "dataset_version": (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "hf_config": "core_operations",
        "num_claims": target_count,
        "document_count": 1,
        "evidence_pattern": "single_document",
    }
    return metadata


async def generate(out_dir: Path) -> None:
    for subdir in ["pdfs", "html", "ground_truth", "metadata", "transcripts/ocr_gemini"]:
        (out_dir / subdir).mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {"samples": []}
    for sample_number in range(1, 4):
        sample_id = f"loss_run_external_{sample_number:03d}"
        seed = 86000 + sample_number * 977
        sections, claims = build_sections(sample_number, seed)
        html_text = render_html(sample_id, sections, seed)
        html_path = out_dir / "html" / f"{sample_id}.html"
        pdf_path = out_dir / "pdfs" / f"{sample_id}.pdf"
        gt_path = out_dir / "ground_truth" / f"{sample_id}.json"
        meta_path = out_dir / "metadata" / f"{sample_id}.json"
        html_path.write_text(html_text, encoding="utf-8")
        gt_path.write_text(json.dumps(claims, indent=2, ensure_ascii=False), encoding="utf-8")
        await html_to_pdf(html_path, pdf_path)

        # Use pdfinfo after rendering for exact page count.
        import subprocess

        info = subprocess.check_output(["pdfinfo", str(pdf_path)], text=True)
        pages = 0
        for line in info.splitlines():
            if line.startswith("Pages:"):
                pages = int(line.split(":", 1)[1].strip())
                break
        metadata = write_metadata(sample_id, out_dir, len(claims), pages)
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        manifest["samples"].append(
            {
                "id": sample_id,
                "records": len(claims),
                "sections": len(sections),
                "pages": pages,
                "driver_visible_records": sum(1 for item in claims if item["driver"]),
                "zero_claim_sections": sum(1 for section in sections if section.no_claims),
            }
        )

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "tmp" / "core_operations" / "loss_runs",
    )
    args = parser.parse_args()
    out_dir = args.out_dir
    asyncio.run(generate(out_dir))
    print(f"Wrote generated artifacts to {out_dir}")


if __name__ == "__main__":
    main()
