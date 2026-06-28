"""HTML assembly for synthetic policy multi-hop packets."""

from __future__ import annotations

import random
import re
import textwrap
from html import escape
from typing import Any, Callable

from .config import PolicyMultiHopCaseConfig
from .llm_text import PolicyTextBank
from .records import build_policy_clause_records_for_item
from .util import money, stable_seed


def _html_escape_rows(rows: list[list[Any]]) -> str:
    return "\n".join(
        "<tr>" + "".join(f"<td>{escape(str(cell))}</td>" for cell in row) + "</tr>"
        for row in rows
    )


def _table(headers: list[str], rows: list[list[Any]], *, class_name: str = "policy-table") -> str:
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    return (
        f'<table class="{class_name}"><thead><tr>{head}</tr></thead>'
        f"<tbody>{_html_escape_rows(rows)}</tbody></table>"
    )


def _field_grid(fields: list[tuple[str, Any]]) -> str:
    blocks = [
        (
            '<div class="field">'
            f'<span class="label">{escape(label)}</span>'
            f'<span class="value">{escape(str(value))}</span>'
            "</div>"
        )
        for label, value in fields
    ]
    return '<div class="field-grid">' + "".join(blocks) + "</div>"


def _page(profile: dict[str, str], title: str, body: str, *, form_id: str = "") -> str:
    form_markup = f'<div class="form-id">{escape(form_id)}</div>' if form_id else ""
    return f"""
<section class="page">
  <div class="page-head">
    <div>
      <div class="doc-kicker">{escape(profile["carrier"])} | {escape(profile["lob_display"])}</div>
      <h1>{escape(title)}</h1>
    </div>
    <div class="policy-stamp">
      <div>{escape(profile["policy_number"])}</div>
      <div>{escape(profile["policy_period"])}</div>
    </div>
  </div>
  {body}
  <div class="page-foot">
    <span>{escape(profile["named_insured"])}</span>
    {form_markup}
  </div>
</section>
"""


def _html_document(title: str, body: str) -> str:
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<style>
@page {{ size: Letter portrait; margin: 0.42in; }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: #fff;
  color: #20242a;
  font-family: "Aptos", "Helvetica Neue", Arial, sans-serif;
  font-size: 9px;
}}
.page {{
  break-after: page;
  min-height: 9.95in;
  padding: 0.04in 0.02in 0.15in;
  position: relative;
}}
.page:last-child {{ break-after: auto; }}
.page-head {{
  align-items: flex-start;
  border-bottom: 2px solid #16324f;
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  padding-bottom: 7px;
}}
.doc-kicker {{
  color: #53606f;
  font-size: 7px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}
h1 {{
  color: #10243f;
  font-size: 15px;
  margin: 2px 0 0;
}}
h2 {{
  color: #10243f;
  font-size: 10.5px;
  margin: 9px 0 5px;
}}
p {{ line-height: 1.26; margin: 3px 0 5px; }}
.policy-stamp {{
  border: 1px solid #8492a6;
  color: #314158;
  font-size: 7px;
  line-height: 1.35;
  padding: 4px 7px;
  text-align: right;
  text-transform: uppercase;
}}
.page-foot {{
  bottom: 0.02in;
  color: #6b7280;
  display: flex;
  font-size: 7px;
  justify-content: space-between;
  left: 0.02in;
  position: absolute;
  right: 0.02in;
}}
.form-id {{ color: #4b5563; font-weight: 700; }}
.clause-grid {{
  column-count: 2;
  column-gap: 20px;
}}
.clause-card {{
  break-inside: avoid;
  border: 1px solid #cbd5e1;
  margin: 0 0 7px;
  padding: 7px;
}}
.clause-card h2 {{
  font-size: 9.5px;
  margin: 0 0 4px;
  text-transform: uppercase;
}}
.clause-card p {{
  font-size: 8.1px;
  line-height: 1.22;
  margin: 2px 0;
}}
.clause-card .clause-meta {{
  color: #475569;
  font-size: 7.2px;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}}
.declarations {{
  display: grid;
  gap: 12px;
  grid-template-columns: 1.15fr 0.85fr;
}}
.declaration-box, .notice-box, .form-box {{
  background: #fff;
  border: 1px solid #9aa7b6;
  padding: 9px;
}}
.field-grid {{
  display: grid;
  gap: 5px 11px;
  grid-template-columns: 1fr 1fr;
}}
.field {{
  border-bottom: 1px solid #d4dae3;
  min-height: 27px;
  padding-bottom: 3px;
}}
.label {{
  color: #5b677a;
  display: block;
  font-size: 6.8px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}}
.value {{ font-weight: 700; }}
.policy-table {{
  background: #fff;
  border-collapse: collapse;
  margin: 6px 0 9px;
  width: 100%;
}}
.policy-table th {{
  background: #173b59;
  border: 1px solid #173b59;
  color: #fff;
  font-size: 6.8px;
  padding: 4px;
  text-align: left;
  text-transform: uppercase;
}}
.policy-table td {{
  border: 1px solid #c9d1dc;
  padding: 4px;
  vertical-align: top;
}}
.policy-table.compact td {{ padding: 2.8px 3.5px; }}
.policy-table.compact th {{ padding: 3.5px; }}
.two-col {{
  display: grid;
  gap: 11px;
  grid-template-columns: 1fr 1fr;
}}
.three-col {{
  display: grid;
  gap: 9px;
  grid-template-columns: 1fr 1fr 1fr;
}}
.form-title {{
  border: 1.5px solid #1f2937;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
  padding: 6px;
  text-align: center;
  text-transform: uppercase;
}}
.form-meta-row {{
  display: flex;
  font-size: 8px;
  justify-content: space-between;
  margin: 5px 0 10px;
}}
.policy-form-body {{
  background: #fff;
  border: 1px solid #d1d5db;
  padding: 10px 13px;
}}
.policy-form-body.two-column {{
  column-count: 2;
  column-gap: 24px;
}}
.policy-form-body p {{
  font-size: 8.6px;
  line-height: 1.22;
  margin: 0 0 4.5px;
  text-align: justify;
}}
.policy-form-body .clause-heading {{
  break-after: avoid;
  font-weight: 800;
  letter-spacing: 0.02em;
  margin: 8px 0 4px;
  text-transform: uppercase;
}}
.policy-form-body .subclause {{ margin-left: 13px; }}
.letter-block {{
  background: #fff;
  border: 1px solid #d1d5db;
  padding: 14px 18px;
}}
.letter-block p {{
  font-size: 9px;
  line-height: 1.28;
  margin: 0 0 7px;
}}
.endorsement {{
  background: #fff;
  border: 1.5px solid #27364a;
  padding: 11px;
}}
.endorsement-title {{
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.03em;
  margin-bottom: 8px;
  text-align: center;
  text-transform: uppercase;
}}
.small {{ font-size: 7.5px; }}
.muted {{ color: #687386; }}
.schedule-note, .fact-box {{
  background: #f8fafc;
  border-left: 4px solid #345c7c;
  margin: 7px 0;
  padding: 7px;
}}
.schedule-ledger {{
  margin: 6px 0 9px;
}}
.schedule-entry {{
  border-bottom: 1px solid #c8d0dc;
  break-inside: avoid;
  display: grid;
  gap: 8px;
  grid-template-columns: 0.76in 1fr;
  page-break-inside: avoid;
  padding: 5px 0 6px;
}}
.schedule-entry:first-child {{
  border-top: 2px solid #173b59;
}}
.schedule-entry:nth-child(odd) {{
  background: #fbfcfe;
}}
.schedule-entry .entry-id {{
  color: #0f2f4d;
  font-weight: 800;
  letter-spacing: 0.02em;
}}
.schedule-entry .entry-body {{
  line-height: 1.22;
}}
.schedule-entry .entry-note {{
  margin: 0 0 3px;
}}
.schedule-entry .entry-fields {{
  display: grid;
  gap: 3px 12px;
  grid-template-columns: 1fr 1fr;
}}
.schedule-entry .entry-fields.single {{
  display: block;
}}
.schedule-entry .entry-field {{
  min-width: 0;
}}
.schedule-entry .entry-label {{
  color: #5b677a;
  font-size: 6.6px;
  font-weight: 800;
  letter-spacing: 0.04em;
  margin-right: 3px;
  text-transform: uppercase;
}}
.schedule-entry .entry-value {{
  font-weight: 650;
}}
.signature-row {{
  display: grid;
  gap: 24px;
  grid-template-columns: 1fr 1fr;
  margin-top: 13px;
}}
.signature-line {{
  border-top: 1px solid #333;
  color: #5b677a;
  padding-top: 4px;
}}
.typed-page {{
  break-after: page;
  color: #000;
  font-family: "Courier New", Courier, monospace;
  min-height: 9.95in;
  padding: 0.08in 0.18in 0.12in;
  position: relative;
}}
.typed-page:last-child {{ break-after: auto; }}
.typed-logo {{
  font-family: Arial, Helvetica, sans-serif;
  font-size: 28px;
  font-weight: 900;
  letter-spacing: -0.06em;
  line-height: 0.8;
  margin-left: 0.34in;
  text-transform: lowercase;
}}
.typed-logo-sub {{
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8px;
  letter-spacing: 0.08em;
  margin: 1px 0 3px 0.56in;
  text-transform: uppercase;
}}
.typed-border {{
  border: 1.2px solid #000;
  display: flex;
  flex-direction: column;
  height: 9.34in;
  margin: 0 auto;
  padding: 0.03in 0.28in 0.02in;
  width: 7.34in;
}}
.typed-border pre {{
  flex: 1;
  font-size: 10.3px;
  line-height: 1.12;
  margin: 0;
  overflow: hidden;
  white-space: pre-wrap;
}}
.typed-bottom {{
  border-top: 1px solid transparent;
  font-size: 10.3px;
  line-height: 1.08;
  white-space: pre;
}}
.coverage-form-page {{
  break-after: page;
  color: #111;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 9.85px;
  line-height: 1.12;
  min-height: 9.95in;
  padding: 0.18in 0.32in 0.2in;
  position: relative;
}}
.coverage-form-page:last-child {{ break-after: auto; }}
.coverage-form-head {{
  display: flex;
  font-size: 9.3px;
  font-weight: 700;
  justify-content: flex-end;
  letter-spacing: 0.02em;
  line-height: 1.1;
  margin-bottom: 0.22in;
  text-align: right;
  text-transform: uppercase;
}}
.coverage-form-title {{
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.01em;
  margin-bottom: 0.18in;
  text-align: center;
  text-transform: uppercase;
}}
.coverage-columns {{
  column-count: 2;
  column-gap: 0.46in;
}}
.coverage-columns p {{
  margin: 0 0 4px;
  orphans: 2;
  text-align: justify;
  widows: 2;
}}
.coverage-section {{
  break-after: avoid;
  font-weight: 800;
  margin: 6px 0 2px !important;
  text-transform: uppercase;
}}
.coverage-heading {{
  break-after: avoid;
  font-weight: 700;
  margin: 4px 0 2px !important;
}}
.coverage-indent-1 {{ padding-left: 14px; text-indent: -14px; }}
.coverage-indent-2 {{ padding-left: 25px; text-indent: -13px; }}
.coverage-indent-3 {{ padding-left: 38px; text-indent: -16px; }}
.coverage-form-code {{
  display: block;
  font-weight: 800;
}}
.coverage-form-foot {{
  bottom: 0.08in;
  display: flex;
  font-size: 8.6px;
  justify-content: space-between;
  left: 0.32in;
  position: absolute;
  right: 0.32in;
}}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def _draft(bank: PolicyTextBank | None, kind: str, page_idx: int) -> dict[str, Any] | None:
    pages = bank.pages(kind) if bank else []
    if not pages:
        return None
    return pages[page_idx % len(pages)]


def _normalized_policy_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def _bop_coverage_form_draft(
    bank: PolicyTextBank | None,
    item: dict[str, Any],
    page_idx: int,
) -> dict[str, Any] | None:
    pages = bank.pages("coverage_form") if bank else []
    if not pages:
        return None
    item_coverage = _normalized_policy_key(item.get("coverage", ""))
    item_form = _normalized_policy_key(item.get("form_number", ""))
    exact_matches = [
        page
        for page in pages
        if _normalized_policy_key(page.get("coverage", "")) == item_coverage
        and _normalized_policy_key(page.get("form_number", "")) == item_form
    ]
    if exact_matches:
        return exact_matches[0]
    coverage_matches = [
        page
        for page in pages
        if _normalized_policy_key(page.get("coverage", "")) == item_coverage
    ]
    if coverage_matches:
        return coverage_matches[0]
    return pages[page_idx % len(pages)]


def _sample_window(items: list[dict[str, Any]], page_idx: int, size: int) -> list[dict[str, Any]]:
    start = (page_idx * size) % len(items)
    return [items[(start + offset) % len(items)] for offset in range(min(size, len(items)))]


def _paragraphs(lines: list[str]) -> str:
    html: list[str] = []
    for index, line in enumerate(lines):
        class_name = ' class="clause-heading"' if index == 0 or re.match(r"^(Part|Section|Item|Condition|Notice)\b", line) else ""
        html.append(f"<p{class_name}>{escape(line)}</p>")
    return "".join(html)


def _fallback_lines(profile: dict[str, str], kind: str, item: dict[str, Any]) -> list[str]:
    lob = profile["lob"]
    if lob == "BOP":
        subject = f"{item.get('coverage', 'scheduled coverage')} at Location {item.get('location_number', '')}, Building {item.get('building_number', '')}"
        return [
            "Policy Conditions",
            f"This page applies to {subject} only when that coverage is shown in the declarations or an attached schedule.",
            "The declarations, coverage form, schedules, and endorsements are read together as one policy packet.",
            "A limit, deductible, valuation basis, or coinsurance entry does not broaden coverage beyond the applicable form.",
            "Location-specific terms apply only to the premises described for that location and building number.",
            "Records supporting occupancy, construction, property values, business income, and scheduled interests must be retained for audit or coverage review.",
        ]
    if lob == "WC":
        subject = f"classification {item.get('class_code', '')} in {item.get('state', '')}"
        return [
            "Policy Conditions",
            f"This page applies to {subject} as shown in the information page and classification schedule.",
            "Estimated remuneration, class assignments, rates, and premium are subject to audit after the policy period.",
            "The experience modification factor and schedule rating entry apply unless a state-specific endorsement provides otherwise.",
            "Payroll records, job duties, certificates, and subcontractor information must be retained for rating verification.",
            "No notice, inspection, or audit changes coverage unless an endorsement is issued and attached to the policy.",
        ]
    subject = f"classification {item.get('class_code', '')} at Location {item.get('location_number', '')}"
    return [
        "Coverage Part Conditions",
        f"This page applies to {subject} as shown in the declarations, classification schedule, and exposure rating schedule.",
        "Classification, territory, and exposure entries are rating information and do not create coverage by themselves.",
        "Limits, exclusions, additional insured status, and completed-operations terms are controlled by the applicable forms and endorsements.",
        "Records supporting sales, payroll, area, contracts, leases, or operations must be retained for audit and coverage review.",
        "Any endorsement listed for a scheduled item applies according to its own terms and effective date.",
    ]


def _supplemental_lines(profile: dict[str, str], kind: str, item: dict[str, Any]) -> list[str]:
    if profile["lob"] == "BOP":
        key = f"Location {item.get('location_number', '')}, Building {item.get('building_number', '')}"
        return [
            f"References to scheduled premises include {key} only when that location and building are shown in the declarations or a later endorsement.",
            "Headings are included for ease of reading and do not alter the scope of coverage, exclusions, valuation terms, deductible entries, or premium calculations.",
            "If two schedule entries appear to conflict, the entry with the later effective date controls for the affected coverage and premises.",
            "The insured should retain valuation worksheets, lease documents, occupancy records, equipment schedules, and business-income work papers used to support the policy entries.",
            "Coverage summaries on one page do not replace the forms schedule, endorsement schedule, or premium schedule issued for the same policy period.",
            "A producer request, certificate, binder note, invoice, or correspondence item does not amend a scheduled entry unless an endorsement is issued.",
            "Loss valuation, business income calculations, and scheduled property values may require supporting records at the time of audit or adjustment.",
            "When a location, building, or coverage appears on multiple schedules, the premises, coverage, form number, and effective date should be read together.",
        ]
    if profile["lob"] == "WC":
        key = f"{item.get('state', '')} class code {item.get('class_code', '')}"
        return [
            f"References to classification, remuneration, and rating basis include {key} only for the state and operation shown in the information page.",
            "Headings are included for ease of reading and do not alter statutory benefits, employers liability limits, audit rights, or state amendatory provisions.",
            "If a state endorsement and a general condition address the same subject, the state-specific endorsement controls for the affected state.",
            "The insured should retain payroll journals, tax filings, subcontractor certificates, job-duty records, and officer status records used to support the classification entries.",
            "Classification summaries on one page do not replace the information page, payroll schedule, endorsement schedule, or premium audit statement.",
            "A certificate, binder note, invoice, or producer correspondence item does not amend a payroll or class-code entry unless an endorsement is issued.",
            "Final premium may require allocation of remuneration by state, governing class, officer status, overtime treatment, and subcontracted work records.",
            "When a class code appears on multiple schedules, the state, item identifier, and effective date should be used to read the entries together.",
        ]
    key = f"class code {item.get('class_code', '')} at Location {item.get('location_number', '')}"
    return [
        f"References to classification, territory, and exposure basis include {key} only when that operation appears in the declarations or rating schedule.",
        "Headings are included for ease of reading and do not alter limits, exclusions, additional-insured status, completed-operations treatment, or premium calculations.",
        "If a form schedule and an endorsement detail page address the same operation, the endorsement detail controls from its effective date.",
        "The insured should retain sales records, payroll records, contracts, leases, certificates, and location records used to support the exposure entries.",
        "Coverage summaries on one page do not replace the limits schedule, exposure schedule, forms schedule, or exclusion endorsement attached to the policy.",
        "A certificate, binder note, invoice, or producer correspondence item does not amend an exposure or additional-insured entry unless an endorsement is issued.",
        "Final premium may require allocation of sales, payroll, area, contract cost, territory, products-completed operations, and other exposure records.",
        "When a class code appears on multiple schedules, the item identifier, location, form number, and effective date should be used to read the entries together.",
    ]


def _dense_policy_clause_lines(profile: dict[str, str], kind: str, item: dict[str, Any]) -> list[str]:
    """Add realistic policy-form density for non-BOP long-range filler pages."""
    if profile["lob"] == "WC":
        state = item.get("state", "")
        class_code = item.get("class_code", "")
        classification = item.get("classification", "scheduled operation")
        payroll = item.get("annual_payroll", "estimated remuneration")
        return [
            "Section A - Records And Audit",
            f"The insured must keep payroll journals, tax filings, job-duty records, and contract labor records for {classification} assigned to class code {class_code} in {state}.",
            f"The remuneration entry of {payroll} is an estimate for rating purposes and may be revised after audit without changing the coverage afforded by the policy.",
            "Separate records are required when an employee performs duties that may fall under more than one classification or more than one covered state.",
            "If adequate records are not available, remuneration may be assigned to the highest rated applicable classification permitted by the rating rules.",
            "Section B - State And Classification Conditions",
            "State amendatory endorsements, statutory benefit provisions, and assigned-risk rules apply before any conflicting general condition in this policy packet.",
            "A classification shown on a schedule is not a warranty that all operations at the insured location are limited to that class.",
            "Officer, partner, member, volunteer, leased-worker, and subcontractor treatment is determined by the attached endorsements and the applicable state rules.",
            "Certificates from subcontractors must be available for audit and must identify the period of work, covered operations, and limits carried by the subcontractor.",
            "Section C - Premium And Experience Rating",
            "The experience modification factor, schedule rating factor, expense constant, assessments, and state surcharges are applied as shown on the information page or premium schedule.",
            "A deposit premium, installment invoice, binder, or producer worksheet is not a substitute for the final audited premium calculation.",
            "If operations change during the policy period, premium may be adjusted from the effective date of the change when the records support the adjustment.",
            "The governing class, if any, is determined by the rating rules and not by the order in which entries appear on the schedule.",
            "Section D - Notices And Endorsements",
            "Cancellation, nonrenewal, waiver of subrogation, alternate employer, and designated workplace endorsements apply only when listed in the forms schedule.",
            "Notice to a producer, certificate holder, or payroll service does not amend the policy unless the insurer issues an endorsement.",
        ]
    if profile["lob"] == "CGL":
        class_code = item.get("class_code", "")
        location = item.get("location_number", "")
        exposure_basis = item.get("exposure_basis", "exposure basis")
        exposure = item.get("exposure", "scheduled exposure")
        return [
            "Section A - Schedule References",
            f"The declarations identify class code {class_code} at Location {location} with {exposure_basis.lower()} of {exposure}; that entry is used for rating and schedule reference purposes.",
            "Coverage applies only as provided by the applicable coverage form, limits schedule, exclusion endorsements, and any additional-insured endorsement attached to the policy.",
            "A location, project, classification, or exposure entry does not create coverage for operations that are otherwise excluded or outside the policy territory.",
            "Section B - Limits And Aggregates",
            "The each occurrence, damage to premises rented to you, medical expense, personal and advertising injury, products-completed operations, and general aggregate limits apply as stated in the declarations.",
            "A sublimit, deductible, self-insured retention, or endorsement limit is part of the applicable limit and does not increase that limit.",
            "When more than one scheduled operation could apply to a claim, the most specific applicable form and endorsement must be read with the declarations.",
            "Section C - Additional Insureds And Contracts",
            "Additional insured status applies only when the attached endorsement, written contract requirement, and completed schedule identify the party or operation.",
            "A certificate of insurance, bid document, invoice, permit, or producer email does not amend the policy or waive an exclusion.",
            "Contractual liability, primary and noncontributory wording, waiver of transfer rights, and completed-operations extensions apply only to the extent stated in an endorsement.",
            "Section D - Records And Audit",
            "The insured must retain sales records, payroll records, job-cost ledgers, subcontract agreements, certificates, lease records, and location records that support the exposure basis.",
            "Final premium may be adjusted after audit if the actual exposure, classification, territory, or operation differs from the schedule.",
            "If records are incomplete, exposure may be assigned according to the rating rules and the information available at audit.",
            "Section E - Endorsement Order",
            "Endorsements with later effective dates apply only from their effective dates and only to the classifications, locations, projects, or operations they identify.",
            "The forms schedule, declarations, exposure schedule, and endorsement detail pages must be read together before determining whether a scheduled item is covered.",
        ]
    return []


def _augment_lines(profile: dict[str, str], kind: str, item: dict[str, Any], lines: list[str]) -> list[str]:
    augmented = [line for line in lines if line.strip()]
    target = 16 if profile["lob"] == "BOP" else 22
    if len(augmented) >= target:
        return augmented
    for line in [*_supplemental_lines(profile, kind, item), *_dense_policy_clause_lines(profile, kind, item)]:
        if line not in augmented:
            augmented.append(line)
        if len(augmented) >= target:
            break
    return augmented


def _item_fact_rows(profile: dict[str, str], item: dict[str, Any]) -> list[tuple[str, Any]]:
    if profile["lob"] == "BOP":
        return [
            ("Item", item["item_id"]),
            ("Coverage", item["coverage"]),
            ("Location / Building", f"{item['location_number']} / {item['building_number']}"),
            ("Address", item["premises_address"]),
            ("Limit / Deductible", f"{item['limit']} / {item['deductible']}"),
            ("Form", f"{item['form_number']} {item['edition_date']}"),
        ]
    if profile["lob"] == "WC":
        return [
            ("Item", item["item_id"]),
            ("State / Class", f"{item['state']} / {item['class_code']}"),
            ("Classification", item["classification"]),
            ("Payroll / Rate", f"{item['annual_payroll']} / {item['manual_rate']}"),
            ("Premium", item["estimated_premium"]),
            ("Form", f"{item['form_number']} {item['edition_date']}"),
        ]
    return [
        ("Item", item["item_id"]),
        ("Class / Territory", f"{item['class_code']} / {item['territory']}"),
        ("Exposure", f"{item['exposure_basis']} {item['exposure']}"),
        ("Limit", f"{item['limit_type']}: {item['limit']}"),
        ("Premium", item["premium"]),
        ("Form", f"{item['form_number']} {item['edition_date']}"),
    ]


def _fact_box(profile: dict[str, str], item: dict[str, Any]) -> str:
    return '<div class="fact-box">' + _field_grid(_item_fact_rows(profile, item)) + "</div>"


def _typed_logo(profile: dict[str, str]) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", profile["carrier"].split()[0]).lower() or "carrier"


def _typed_policy_period(profile: dict[str, str]) -> tuple[str, str]:
    parts = [part.strip() for part in profile["policy_period"].split("-")]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return profile["policy_period"], profile["policy_period"]


def _typed_money_value(value: str) -> int:
    digits = re.sub(r"[^0-9]", "", str(value))
    return int(digits or "0")


def _typed_wrap(text: str, *, width: int = 82, indent: str = "  ") -> list[str]:
    return textwrap.wrap(
        text,
        width=width,
        initial_indent=indent,
        subsequent_indent=indent,
        break_long_words=False,
        break_on_hyphens=False,
    )


def _typed_center(text: str, width: int = 78) -> str:
    return text[:width].center(width)


def _typed_fit(value: Any, width: int) -> str:
    text = re.sub(r"\s+", " ", str(value)).strip()
    if len(text) > width:
        return text[: max(0, width - 1)] + "."
    return text.ljust(width)


def _typed_form_page(
    profile: dict[str, str],
    *,
    lines: list[str],
    form_id: str,
    page_no: int = 1,
    continued: bool = False,
) -> str:
    issue_date, effective_date = _typed_policy_period(profile)
    continuation = "    (CONTINUED)" if continued else ""
    bottom = (
        f"DATE OF ISSUE: {issue_date}    (BPP){continuation}\n"
        f"FORM: {form_id:<18} BPP  {effective_date:<12}  035      13      {profile['policy_number']:<12} 2701"
    )
    page_label = "" if page_no == 1 else f"PAGE NO: {page_no}"
    body = "\n".join(lines)
    return f"""
<section class="typed-page">
  <div class="typed-logo">{escape(_typed_logo(profile))}</div>
  <div class="typed-logo-sub">INSURANCE</div>
  <div class="typed-border">
    <pre>{escape(page_label + chr(10) + body if page_label else body)}</pre>
    <div class="typed-bottom">{escape(bottom)}</div>
  </div>
</section>
"""


def _typed_policy_header(profile: dict[str, str]) -> list[str]:
    start_date, end_date = _typed_policy_period(profile)
    return [
        f"{profile['carrier'].upper():<44} POLICY NUMBER: {profile['policy_number']}",
        f"{profile['named_insured'][:38].upper():<38} EFF DATE: {start_date:<10} EXP DATE: {end_date}",
        "",
    ]


def _bop_typed_draft_page(
    profile: dict[str, str],
    kind: str,
    title: str,
    form_id: str,
    page_idx: int,
    item: dict[str, Any],
    lines: list[str],
) -> str:
    normalized_title = re.sub(r"\s+", " ", title).strip().upper() or "POLICY FORM"
    if kind == "notice":
        normalized_title = normalized_title.replace("POLICYHOLDER ", "")
    form_code = {
        "policy_form": f"{item['form_number'].replace(' ', '')} ED. {item.get('edition_date', '05 24')}",
        "notice": f"SNT{8300 + page_idx:04d} ({item.get('edition_date', '05 24')})",
        "amendatory": f"SAM{6200 + page_idx:04d} ({item.get('edition_date', '05 24')})",
        "billing": f"BPA{7100 + page_idx:04d} ({item.get('edition_date', '05 24')})",
    }.get(kind, form_id or f"BPF{9000 + page_idx:04d}")

    content: list[str] = []
    content.extend(_typed_policy_header(profile))
    content.append(_typed_center(normalized_title))
    content.append("=" * 78)
    content.append("")

    if kind == "policy_form":
        content.extend(
            [
                f"LOCATION: {item.get('location_number', ''):<3}  BUILDING: {item.get('building_number', ''):<3}",
                f"COVERAGE: {item.get('coverage', '')}",
                f"FORM: {item.get('form_number', ''):<12} EDITION: {item.get('edition_date', ''):<8} LIMIT: {item.get('limit', ''):>12}",
                "-" * 78,
            ]
        )
    elif kind == "billing":
        content.extend(
            [
                "PREMIUM, AUDIT AND ACCOUNTING CONDITIONS",
                f"COVERAGE: {item.get('coverage', ''):<28} ESTIMATED PREMIUM: {item.get('premium', '')}",
                "-" * 78,
            ]
        )
    elif kind == "amendatory":
        content.extend(
            [
                "THIS ENDORSEMENT MODIFIES INSURANCE PROVIDED UNDER THE FOLLOWING:",
                "BUSINESSOWNERS COVERAGE FORM AND SCHEDULED PREMISES",
                "-" * 78,
            ]
        )
    else:
        content.extend(
            [
                "THIS NOTICE IS ATTACHED TO AND MADE PART OF THE POLICY.",
                "IT DOES NOT CHANGE COVERAGE UNLESS A SEPARATE ENDORSEMENT SAYS SO.",
                "-" * 78,
            ]
        )

    section_labels = ["A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.", "I.", "J.", "K.", "L.", "M.", "N."]
    for idx, line in enumerate(lines[:14]):
        text = re.sub(r"\s+", " ", str(line)).strip()
        if not text:
            continue
        if idx < len(section_labels):
            wrapped = textwrap.wrap(
                text,
                width=74,
                initial_indent=f"{section_labels[idx]} ",
                subsequent_indent="   ",
                break_long_words=False,
                break_on_hyphens=False,
            )
            content.extend(wrapped)
        else:
            content.extend(_typed_wrap(text, width=76, indent="  "))
        content.append("")

    content.extend(
        [
            "-" * 78,
            "THIS FORM MUST BE READ WITH THE DECLARATIONS, SCHEDULES AND ENDORSEMENTS.",
            "NO ORAL STATEMENT OR PRODUCER CORRESPONDENCE CHANGES THIS FORM.",
        ]
    )
    return _typed_form_page(profile, lines=content, form_id=form_code)


def _bop_coverage_form_page(
    profile: dict[str, str],
    title: str,
    form_id: str,
    page_idx: int,
    item: dict[str, Any],
    lines: list[str],
    *,
    generated_body: bool = False,
) -> str:
    form_code = f"{item['form_number'].replace(' ', '')} ED. {item.get('edition_date', '05 24')}"
    form_title = re.sub(r"\s+", " ", str(item.get("form_title") or title or "Businessowners Coverage Form")).strip()
    if generated_body:
        form_title = re.sub(r"\s+", " ", str(title or form_title)).strip()
    elif item.get("form_number") == "BPF 00 13":
        form_title = "Businessowners Coverage Form"

    coverage_key = str(item.get("coverage", "scheduled coverage")).lower()

    def para(text: str, class_name: str = "") -> str:
        class_attr = f' class="{class_name}"' if class_name else ""
        return f"<p{class_attr}>{escape(text)}</p>"

    def generated_parts() -> list[str]:
        parts: list[str] = []
        for raw_line in lines:
            text = re.sub(r"\s+", " ", str(raw_line)).strip()
            if not text:
                continue
            class_name = ""
            if re.match(r"^(SECTION|PART|CONDITION|EXCLUSION|LIMIT|LIMITS|DUTIES|VALUATION|SCHEDULE|DEFINITIONS)\b", text, re.IGNORECASE):
                class_name = "coverage-section"
            elif re.match(r"^[A-Z]\.\s+", text) or re.match(r"^\d+\.\s+", text):
                class_name = "coverage-heading"
            elif re.match(r"^[a-z]\.\s+", text) or re.match(r"^\([a-z0-9]+\)\s+", text):
                class_name = "coverage-indent-2"
            parts.append(para(text, class_name))
        return parts

    main_form_parts = [
        para("Various provisions in this policy restrict coverage. Read the entire policy carefully to determine rights, duties and what is and is not covered."),
        para("Throughout this Coverage Form, the words \"you\" and \"your\" refer to the Named Insured shown in the Declarations. The words \"we\", \"us\" and \"our\" refer to the company providing this insurance."),
        para("Other words and phrases that appear in quotation marks have special meaning. Refer to the Definitions section and to any endorsement that changes this form."),
        para("SECTION I - PROPERTY", "coverage-section"),
        para("A. Coverage", "coverage-heading"),
        para("We will pay for direct physical loss of or damage to Covered Property at the premises described in the Declarations caused by or resulting from a Covered Cause of Loss."),
        para("1. Covered Property", "coverage-heading"),
        para("Covered Property includes Buildings as described under Paragraph a. below, Business Personal Property as described under Paragraph b. below, or both, depending on whether a Limit Of Insurance is shown in the Declarations.", "coverage-indent-1"),
        para("a. Buildings, meaning the buildings and structures at the described premises, including:", "coverage-indent-2"),
        para("(1) Completed additions;", "coverage-indent-3"),
        para("(2) Fixtures, including outdoor fixtures;", "coverage-indent-3"),
        para("(3) Permanently installed machinery and equipment; and", "coverage-indent-3"),
        para("(4) Personal property owned by you that is used to maintain or service the buildings or structures or the premises.", "coverage-indent-3"),
        para("b. Business Personal Property located in or on the buildings at the described premises, or in the open or in a vehicle within 100 feet of those premises, including:", "coverage-indent-2"),
        para("(1) Property you own that is used in your business;", "coverage-indent-3"),
        para("(2) Property of others that is in your care, custody or control, except as otherwise provided in this policy; and", "coverage-indent-3"),
        para("(3) Tenant improvements and betterments made a part of a building or structure you occupy but do not own.", "coverage-indent-3"),
        para("2. Property Not Covered", "coverage-heading"),
        para("Covered Property does not include aircraft, watercraft, automobiles, money, securities, contraband, land, crops, lawns, outdoor fences, electronic data, or any property more specifically excluded by this form or by endorsement.", "coverage-indent-1"),
        para("3. Covered Causes Of Loss", "coverage-heading"),
        para("Direct physical loss is covered unless the loss is excluded or limited in this Coverage Form or in an endorsement attached to this policy.", "coverage-indent-1"),
        para("4. Limitations", "coverage-heading"),
        para("We will not pay for loss of or damage to property that is missing where the only evidence of loss is an inventory shortage, unexplained disappearance, or shortage disclosed on taking inventory.", "coverage-indent-1"),
        para("SECTION II - ADDITIONAL COVERAGES", "coverage-section"),
        para("Additional coverages apply only within the limit, period, territory and conditions stated for the coverage. These coverages do not increase the Limits Of Insurance unless this form or an endorsement specifically states otherwise."),
        para("a. Debris removal, preservation of property, fire department service charge and related expenses are subject to the terms shown in the Declarations and schedules.", "coverage-indent-2"),
        para("b. Business income, extra expense and ordinary payroll provisions require records showing sales, payroll, continuing expenses and the period of restoration.", "coverage-indent-2"),
        para("SECTION III - CONDITIONS", "coverage-section"),
        para("The following conditions apply in addition to the Common Policy Conditions and any conditions shown in the Declarations or endorsements."),
        para("a. You must give prompt notice of loss, protect covered property from further damage, and keep an accurate record of repair costs and emergency expenses.", "coverage-indent-2"),
        para("b. At our request, you must provide inventories, invoices, lease agreements, payroll records, sales records, diagrams and other records supporting the claim.", "coverage-indent-2"),
        para("c. If another form or endorsement addresses the same subject, the more specific provision controls for the affected coverage.", "coverage-indent-2"),
        para("SECTION IV - HOW THIS FORM IS READ", "coverage-section"),
        para(f"Coverage for {coverage_key} is determined by reading the Declarations, this form, the forms schedule and any endorsement naming the same coverage and premises reference."),
        para("If a schedule and an endorsement both refer to the same coverage and premises, use the later effective date and the more specific policy provision."),
    ]
    optional_form_parts = [
        para("Various provisions in this policy restrict coverage. Read the entire policy carefully to determine rights, duties and what is and is not covered."),
        para("This form modifies insurance provided under the Businessowners Coverage Form. It applies only when the form number and edition are shown in the forms schedule or in an endorsement attached to this policy."),
        para("The Declarations and schedules identify the premises, coverage, limit, deductible, valuation entry, rating basis and premium associated with this form."),
        para("SECTION I - SCHEDULED COVERAGE", "coverage-section"),
        para("A. Coverage Grant", "coverage-heading"),
        para(f"We will provide {coverage_key} only to the extent the coverage is shown in the Declarations or schedules and is not excluded or limited by this form.", "coverage-indent-1"),
        para("a. The scheduled coverage, premises reference, form number and effective date must be read together.", "coverage-indent-2"),
        para("b. A coverage summary, certificate, invoice or producer request does not broaden coverage or change the applicable limit.", "coverage-indent-2"),
        para("B. Limits And Deductibles", "coverage-heading"),
        para("The most we will pay is the applicable limit shown for the scheduled coverage. A sublimit shown in this form or an endorsement is part of, and does not increase, that limit.", "coverage-indent-1"),
        para("a. The deductible applies separately to each covered loss unless the Declarations or endorsement states another method.", "coverage-indent-2"),
        para("b. If more than one deductible could apply, the more specific deductible for the affected cause of loss or premises controls.", "coverage-indent-2"),
        para("C. Conditions", "coverage-heading"),
        para("You must maintain records supporting values, occupancy, payroll, sales, contracts, leases, equipment, operations and other rating information used to issue this form.", "coverage-indent-1"),
        para("At our request, you must allow inspection of the described premises and must provide books and records needed for audit, claim review or policy correction.", "coverage-indent-1"),
        para("D. Valuation And Period Of Coverage", "coverage-heading"),
        para("Valuation, waiting periods, restoration periods and other time-based provisions are determined by the Declarations and by the schedule that names this form.", "coverage-indent-1"),
        para("If the Declarations show a valuation basis or time period for the scheduled coverage, that entry applies only to the premises to which the form is attached.", "coverage-indent-1"),
        para("SECTION II - EXCLUSIONS AND LIMITATIONS", "coverage-section"),
        para("We do not pay for loss, cost or liability excluded by the Businessowners Coverage Form, by this form, or by any endorsement effective for the same scheduled coverage."),
        para("a. No coverage is provided unless it is described by the applicable schedule, form number and premises reference.", "coverage-indent-2"),
        para("b. No oral statement, binder note, certificate, finance agreement or billing notice changes this form.", "coverage-indent-2"),
        para("c. If this form applies to more than one scheduled premises, each premises is treated separately for limits, deductibles and conditions unless the schedule states otherwise.", "coverage-indent-2"),
        para("SECTION III - CHANGES TO THIS FORM", "coverage-section"),
        para("Any change to this form must be made by endorsement issued by us. If two endorsements conflict, the endorsement with the later effective date controls for the affected coverage."),
        para("A change in ownership, occupancy, use, operations or rating basis must be reported as required by the Common Policy Conditions and any state amendatory endorsement."),
        para("SECTION IV - HOW THIS FORM IS READ", "coverage-section"),
        para(f"Coverage for {coverage_key} is determined by reading the Declarations, this form, the forms schedule and any endorsement naming the same coverage and premises reference."),
        para("If the same coverage appears on multiple schedules, use the location, building, form number and effective date to connect the entries."),
    ]
    if generated_body:
        body_parts = generated_parts()
        supplemental_parts = main_form_parts if item.get("form_number") == "BPF 00 13" else optional_form_parts
        for part in supplemental_parts[3:]:
            if len(body_parts) >= 28:
                break
            if part not in body_parts:
                body_parts.append(part)
    else:
        body_parts = main_form_parts if item.get("form_number") == "BPF 00 13" else optional_form_parts

    return f"""
<section class="coverage-form-page">
  <div class="coverage-form-head">
    <div>Businessowners<span class="coverage-form-code">{escape(form_code)}</span></div>
  </div>
  <div class="coverage-form-title">{escape(form_title)}</div>
  <div class="coverage-columns">
    {"".join(body_parts)}
  </div>
  <div class="coverage-form-foot">
    <span>{escape(form_code)}</span>
    <span>{escape(profile["policy_number"])}</span>
    <span>Page {page_idx + 1}</span>
  </div>
</section>
"""


def _bop_typed_endorsement_page(
    profile: dict[str, str],
    title: str,
    page_idx: int,
    item: dict[str, Any],
    lines: list[str],
) -> str:
    form_code = f"{item['form_number'].replace(' ', '')} ED. {item.get('edition_date', '05 24')}"
    raw_title = str(item.get("form_title") or title or "Policy Change Endorsement")
    normalized_title = re.sub(r"\s+", " ", raw_title).strip().upper()
    if "ENDORSEMENT" not in normalized_title and "EXCLUSION" not in normalized_title:
        normalized_title = f"{normalized_title} ENDORSEMENT"
    item_lines = [
        f"This endorsement applies to {item.get('coverage', 'the scheduled coverage')} shown for the scheduled premises below.",
        f"The premises reference for this endorsement is Location {item.get('location_number', '')}, Building {item.get('building_number', '')}.",
        f"The scheduled form is {item.get('form_number', '')} edition {item.get('edition_date', '')}, subject to the terms below.",
        f"The limit shown for the affected scheduled coverage is {item.get('limit', '')}; the deductible shown is {item.get('deductible', '')}.",
        f"The valuation or rating basis shown for the scheduled coverage is {item.get('valuation', item.get('business_income_basis', 'as scheduled'))}.",
        "This endorsement does not change any other scheduled premises unless another schedule expressly states that it applies.",
        "The declarations, coverage form, forms schedule, endorsement schedule and premium schedule must be read together before applying this endorsement.",
        "A binder, certificate, producer request, invoice, audit worksheet or loss-control note does not change this endorsement unless a revised endorsement is issued.",
        "If a location, building, coverage, form number or effective date differs between schedules, the later and more specific endorsement controls for that scheduled item.",
        "The insured must keep occupancy records, valuation worksheets, lease agreements, payroll records, sales records and equipment schedules that support the scheduled entry.",
        "Any premium adjustment arising from this endorsement is shown in the premium summary or later billing notice and does not expand the applicable limit.",
        "This endorsement applies separately to each premises, coverage and form reference identified in the schedule unless the endorsement states otherwise.",
    ]
    content: list[str] = []
    content.extend(_typed_policy_header(profile))
    content.append(_typed_center(normalized_title))
    content.append(_typed_center("THIS ENDORSEMENT CHANGES THE POLICY. PLEASE READ IT CAREFULLY."))
    content.append("=" * 78)
    content.extend(
        [
            "",
            "SCHEDULE",
            "-" * 78,
            f"EFFECTIVE DATE: {item.get('endorsement_effective_date', ''):<10}",
            f"LOCATION: {item.get('location_number', ''):<3} BUILDING: {item.get('building_number', ''):<3}",
            f"COVERAGE: {item.get('coverage', '')}",
            f"FORM: {item.get('form_number', ''):<12} EDITION: {item.get('edition_date', ''):<8} LIMIT: {item.get('limit', ''):>12}",
            "-" * 78,
            "",
        ]
    )
    section_labels = ["A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.", "I.", "J.", "K.", "L."]
    for idx, line in enumerate(item_lines):
        text = re.sub(r"\s+", " ", str(line)).strip()
        if not text:
            continue
        label = section_labels[idx] if idx < len(section_labels) else "  "
        content.extend(
            textwrap.wrap(
                text,
                width=74,
                initial_indent=f"{label} ",
                subsequent_indent="   ",
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
        content.append("")
    content.extend(
        [
            "-" * 78,
            "ALL OTHER TERMS AND CONDITIONS OF THIS POLICY REMAIN UNCHANGED.",
        ]
    )
    return _typed_form_page(profile, lines=content, form_id=form_code, page_no=page_idx)


def _bop_typed_notice_page(
    profile: dict[str, str],
    title: str,
    page_idx: int,
) -> str:
    form_code = f"BPN{8300 + page_idx:04d} ED. 05-24"
    normalized_title = re.sub(r"\s+", " ", title).strip().upper() or "IMPORTANT POLICYHOLDER NOTICE"
    content: list[str] = []
    content.extend(_typed_policy_header(profile))
    content.append(_typed_center(normalized_title))
    content.append("=" * 78)
    content.extend(
        [
            "",
            "THIS NOTICE IS PROVIDED FOR INFORMATIONAL PURPOSES.",
            "IT DOES NOT CHANGE THE COVERAGE PROVIDED BY THIS POLICY.",
            "-" * 78,
            "",
            "NOTICE TO POLICYHOLDER",
            "",
            "The policy consists of the declarations, coverage forms, schedules, notices,",
            "and endorsements issued by the company. Read all pages together before",
            "relying on a single schedule or summary.",
            "",
            "A certificate of insurance, billing statement, producer correspondence,",
            "or claim notice does not change a limit, deductible, location, form,",
            "classification, exclusion, premium, or effective date.",
            "",
            "If the policyholder requests a change, the change is effective only when",
            "the company issues an endorsement or revised declarations page. Retain",
            "all later endorsements with the policy packet.",
            "",
            "Questions about billing, audit, loss reporting, or policy changes should",
            "be directed to the producer or servicing office shown in the declarations.",
            "",
            "The forms schedule identifies the edition date for each coverage form,",
            "endorsement, amendatory page and notice attached to the policy packet.",
            "",
            "If more than one schedule refers to the same location or building, read",
            "the location number, building number, coverage name, form number, and",
            "effective date together before relying on the entry.",
            "",
            "The insured should retain the full packet, including replaced pages,",
            "because later endorsements may apply only from their effective dates.",
            "",
            "-" * 78,
            "KEEP THIS NOTICE WITH YOUR POLICY FOR FUTURE REFERENCE.",
        ]
    )
    return _typed_form_page(profile, lines=content, form_id=form_code)


def _bop_typed_billing_page(
    profile: dict[str, str],
    title: str,
    page_idx: int,
    item: dict[str, Any],
) -> str:
    form_code = f"BPA{7100 + page_idx:04d} ED. 05-24"
    normalized_title = re.sub(r"\s+", " ", title).strip().upper() or "PREMIUM AUDIT AND ACCOUNTING CONDITIONS"
    total_label = item.get("premium", "$0")
    content: list[str] = []
    content.extend(_typed_policy_header(profile))
    content.append(_typed_center(normalized_title))
    content.append("=" * 78)
    content.extend(
        [
            "",
            "ACCOUNT SUMMARY",
            "-" * 78,
            f"POLICY NUMBER: {profile['policy_number']:<18} BILLING METHOD: DIRECT BILL",
            f"NAMED INSURED: {profile['named_insured'][:44]}",
            f"SCHEDULED COVERAGE: {item.get('coverage', '')}",
            f"LOCATION: {item.get('location_number', ''):<3} BUILDING: {item.get('building_number', ''):<3} SCHEDULED PREMIUM: {total_label:>12}",
            "-" * 78,
            "",
            "PREMIUM CONDITIONS",
            "",
            "1. Premium shown in this policy is an estimate unless the declarations or",
            "   premium schedule states that the premium is fully earned or not auditable.",
            "",
            "2. Final premium may depend on payroll, sales, property values, occupancy,",
            "   location, classification, endorsements, and other rating information.",
            "",
            "3. The insured must keep records needed to verify the premium basis and",
            "   must make those records available for audit during normal business hours.",
            "",
            "4. A payment plan, installment bill, finance agreement, or invoice does not",
            "   amend coverage and does not replace the declarations or schedules.",
            "",
            "5. Return premium, additional premium, fees, and taxes are calculated using",
            "   the policy terms, rating plan, and applicable law.",
            "",
            "6. Premium shown for a single scheduled coverage does not change limits,",
            "   deductibles, valuation terms, covered premises, or exclusions.",
            "",
            "7. If the insured requests a change during the policy period, any resulting",
            "   premium adjustment applies from the effective date shown on the",
            "   endorsement or revised declarations page.",
            "",
            "8. Audit correspondence, worksheets, and installment notices are part of",
            "   policy administration records and should be retained with this packet.",
            "",
            "-" * 78,
            "THIS PAGE IS PART OF THE POLICY PACKET BUT DOES NOT GRANT COVERAGE.",
        ]
    )
    return _typed_form_page(profile, lines=content, form_id=form_code)


def _bop_typed_amendatory_page(
    profile: dict[str, str],
    title: str,
    page_idx: int,
    item: dict[str, Any],
) -> str:
    form_code = f"BPA{6200 + page_idx:04d} ED. 05-24"
    normalized_title = re.sub(r"\s+", " ", title).strip().upper() or "STATE AMENDATORY ENDORSEMENT"
    state_match = re.search(r",\s*([A-Z]{2})\s+\d{5}", profile.get("mailing_address", ""))
    state = state_match.group(1) if state_match else "STATE"
    content: list[str] = []
    content.extend(_typed_policy_header(profile))
    content.append(_typed_center(normalized_title))
    content.append(_typed_center("THIS ENDORSEMENT CHANGES THE POLICY. PLEASE READ IT CAREFULLY."))
    content.append("=" * 78)
    content.extend(
        [
            "",
            "SCHEDULE",
            "-" * 78,
            f"APPLIES IN: {state:<8} POLICY FORM: BUSINESSOWNERS COVERAGE FORM",
            f"LOCATION: {item.get('location_number', ''):<3} BUILDING: {item.get('building_number', ''):<3} FORM REFERENCE: {item.get('form_number', '')}",
            "-" * 78,
            "",
            "The following provisions amend the policy only to the extent required by",
            "law or regulation applicable to the state shown in the schedule.",
            "",
            "1. Cancellation, nonrenewal, and conditional renewal notices are provided",
            "   according to the time period required by applicable law.",
            "",
            "2. Any provision conflicting with mandatory state law is amended to conform",
            "   to that law, but only for the policy or premises subject to that law.",
            "",
            "3. Duties after loss, appraisal, legal action, and proof-of-loss provisions",
            "   apply as amended by this endorsement and the declarations.",
            "",
            "4. This endorsement does not change scheduled limits, deductibles, forms,",
            "   classifications, rating bases, or premiums unless a row in the schedule",
            "   or another endorsement specifically states the change.",
            "",
            "5. If this endorsement conflicts with another state amendatory endorsement,",
            "   the provision applicable to the described premises controls.",
            "",
            "6. Notice periods, appraisal rights, cancellation terms, and suit limitation",
            "   provisions apply only as amended for the state and policy period shown.",
            "",
            "7. This endorsement must be read with the declarations, coverage form,",
            "   forms schedule, and any endorsement naming the same location or coverage.",
            "",
            "-" * 78,
            "ALL OTHER TERMS AND CONDITIONS OF THIS POLICY REMAIN UNCHANGED.",
        ]
    )
    return _typed_form_page(profile, lines=content, form_id=form_code)


def _bop_typed_schedule_page(
    profile: dict[str, str],
    title: str,
    form_id: str,
    headers: list[tuple[str, int]],
    rows: list[list[Any]],
    *,
    note: str = "",
) -> str:
    lines: list[str] = []
    lines.extend(_typed_policy_header(profile))
    lines.append(_typed_center("BUSINESSOWNERS POLICY"))
    lines.append(_typed_center(title.upper()))
    lines.append("=" * 78)
    if note:
        lines.extend(_typed_wrap(note, width=76, indent="  "))
        lines.append("")

    header_line = " ".join(_typed_fit(label.upper(), width) for label, width in headers)
    lines.append(header_line.rstrip())
    lines.append("-" * 78)
    for row in rows:
        wrapped_cells: list[list[str]] = []
        for cell, (_, width) in zip(row, headers):
            text = re.sub(r"\s+", " ", str(cell)).strip()
            wrapped = textwrap.wrap(
                text,
                width=width,
                break_long_words=False,
                break_on_hyphens=False,
            ) or [""]
            wrapped_cells.append(wrapped)
        row_height = max(len(cell) for cell in wrapped_cells)
        for line_idx in range(row_height):
            cells = [
                _typed_fit(cell_lines[line_idx] if line_idx < len(cell_lines) else "", width)
                for cell_lines, (_, width) in zip(wrapped_cells, headers)
            ]
            lines.append(" ".join(cells).rstrip())
    lines.append("-" * 78)
    lines.extend(
        [
            "",
            "SCHEDULE ENTRIES APPLY ONLY WITH THE DECLARATIONS AND ATTACHED FORMS.",
            "WHERE A COVERAGE APPEARS ON MULTIPLE SCHEDULES, READ THE LOCATION,",
            "BUILDING, FORM NUMBER AND EFFECTIVE DATE TOGETHER.",
        ]
    )
    return _typed_form_page(profile, lines=lines, form_id=form_id)


def _bop_typed_detail_schedule_page(
    profile: dict[str, str],
    title: str,
    form_id: str,
    entries: list[list[str]],
    *,
    note: str = "",
) -> str:
    lines: list[str] = []
    lines.extend(_typed_policy_header(profile))
    lines.append(_typed_center("BUSINESSOWNERS POLICY"))
    lines.append(_typed_center(title.upper()))
    lines.append("=" * 78)
    if note:
        lines.extend(_typed_wrap(note, width=76, indent="  "))
        lines.append("")

    for entry in entries:
        for idx, raw_line in enumerate(entry):
            prefix = "" if idx == 0 else "  "
            lines.extend(_typed_wrap(raw_line, width=76, indent=prefix))
        lines.append("-" * 78)

    lines.extend(
        [
            "",
            "SCHEDULE ENTRIES APPLY ONLY WITH THE DECLARATIONS AND ATTACHED FORMS.",
            "WHERE A COVERAGE APPEARS ON MULTIPLE SCHEDULES, READ THE LOCATION,",
            "BUILDING, FORM NUMBER AND EFFECTIVE DATE TOGETHER.",
        ]
    )
    return _typed_form_page(profile, lines=lines, form_id=form_id)


def _bop_declaration_page_one(profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    start_date, end_date = _typed_policy_period(profile)
    policy = profile["policy_number"]
    total_premium = sum(_typed_money_value(item.get("premium", "0")) for item in items)
    first = items[0]
    liability_limit = next((item["limit"] for item in items if item.get("coverage") == "Hired and Non-Owned Auto"), "$1,000,000")
    lines = [
        f"{profile['carrier'].upper():<44} PRIOR POLICY: {policy[:-2]}25",
        "",
        "              B U S I N E S S O W N E R S   D E C L A R A T I O N S",
        "",
        f"POLICY PERIOD: FROM {start_date:<10} TO  {end_date:<10}        *---------------------------*",
        f"                                                        *       POLICY NUMBER       *",
        f"                                                        *   {policy:<21} *",
        f"                                                        *---------------------------*",
        "    N A M E D   I N S U R E D :                 P R O D U C E R :",
        " - - - - - - - - - - - - - - - - - - - -       - - - - - - - - - - - - - - - -",
        f"{profile['named_insured']:<45}{profile['producer_name']}",
        f"{profile['mailing_address']:<45}{profile['producer_code']}",
        "",
        "    DIRECT BILL",
        "                                             AGENT: " + profile["producer_code"].replace("-", " "),
        "                                             CLAIM REPORTING: (800)555-0147",
        "                                             SERVICING CARRIER: (401)555-0180",
        " - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -",
        f"THIS POLICY RENEWAL IS OFFERED CONTINGENT UPON RECEIPT OF PAYMENT",
        f"WHICH IS DUE ON {start_date}.",
        " - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -",
        f"    INSURED IS: LLC                 Business Desc: {first.get('classification', 'COMMERCIAL OPERATIONS')[:28].upper()}",
        " - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -",
        "In Return for the Payment of the Premium, & Subject to all the Terms of This",
        "Policy, We Agree with You to Provide the Insurance as Stated in this Policy.",
        "--------------------------------------------------------------------------------",
        "",
        "P R O P E R T Y - Businessowners Coverage Form",
        "  Refer to SECTION I-PROPERTY in the Businessowners Coverage Form and Any",
        "  Schedule or Endorsements Attached.",
        "",
        "L I A B I L I T Y   &   M E D I C A L   P A Y M E N T S",
        "Except for Damage to Premises Rented to You, Each Paid Claim for the",
        "Following Coverages Reduces the Amount of Insurance We Provide During",
        "the Policy Period. Refer to SECTION II-LIABILITY in the Businessowners",
        "Coverage Form, the Following Schedule and Any Attached Endorsements.",
        "",
        "  Limits of Insurance",
        f"    Liability and Medical Expenses (Each Occurrence)              {liability_limit:>12}",
        f"    Medical Expenses (Per Person)                                 {'$5,000':>12}",
        f"    Other Than Products/Completed Operations Aggregate            {'$2,000,000':>12}",
        f"    Products/Completed Operations Aggregate                       {'$2,000,000':>12}",
        f"    Damage to Premises Rented to You (Any One Premises)           {'$300,000':>12}",
        "",
        f"  Estimated Businessowners Premium                                {money(total_premium):>12}",
    ]
    return _typed_form_page(profile, lines=lines, form_id="CBF2102X ED. 05-24", continued=True)


def _bop_declaration_page_two(profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    start_date, end_date = _typed_policy_period(profile)
    policy = profile["policy_number"]
    forms = []
    for item in items:
        forms.append(f"{item['form_number'].replace(' ', '')}({item['edition_date']})*")
    forms.extend(["CBF003(05/24)*", "CBF211(02/25)*", "CBF430(05/24)*", "CBF210(11/25)*", "SL2404(03/25)*"])
    unique_forms = list(dict.fromkeys(forms))
    form_lines = textwrap.wrap(",  ".join(unique_forms), width=76, break_long_words=False, break_on_hyphens=False)
    optional_rows = [
        ("Businessowners Extension Endorsement", "See CBF210"),
        ("Auto Service Industry Extension", "See CBF340"),
        ("Employee Tools - Per Occurrence", "$    10,000"),
        ("                 Per Employee", "$     1,000"),
    ]
    total_premium = sum(_typed_money_value(item.get("premium", "0")) for item in items)
    lines = [
        f"{profile['carrier'].upper():<44} POLICY NO: {policy}",
        f"{profile['named_insured'][:38].upper():<38} EFF DATE: {start_date:<10} EXP DATE: {end_date}",
        "",
        "              B U S I N E S S O W N E R S   D E C L A R A T I O N S",
        "--------------------------------------------------------------------------------",
        "",
        "",
        "P R O P E R T Y   L I A B I L I T Y   &   M E D I C A L   P A Y M E N T S",
        "  The following Optional Coverages/Endorsements (and/or applicable Limits)",
        "  modify insurance provided under Section I - Property and/or Section II",
        "  Liability of the Businessowners Coverage Form.",
        "",
    ]
    for label, value in optional_rows:
        lines.append(f"  {label:<61}{value:>16}")
    lines.extend(
        [
            "  --------------------------------------------------------------------------",
            f"                                            *Businessowners Premium  {money(total_premium):>12}",
            "                                            ----------------------------------",
            "",
            "",
            "  ------------------------------------------------------------------------",
            "  FORMS APPLICABLE:",
        ]
    )
    lines.extend(f"  {line}" for line in form_lines)
    lines.append("  ------------------------------------------------------------------------")
    lines.extend([""] * 12)
    return _typed_form_page(profile, lines=lines, form_id="CBF2102X ED. 05-24", page_no=2)


def _draft_page(
    profile: dict[str, str],
    kind: str,
    page_idx: int,
    items: list[dict[str, Any]],
    text_bank: PolicyTextBank | None,
) -> str:
    item = _sample_window(items, page_idx, 1)[0]
    generated_bop_coverage_form = False
    if profile["lob"] == "BOP" and kind == "policy_form":
        draft = _bop_coverage_form_draft(text_bank, item, page_idx)
        generated_bop_coverage_form = draft is not None
        if draft is None:
            draft = _draft(text_bank, kind, page_idx)
            generated_bop_coverage_form = draft is not None
    else:
        draft = _draft(text_bank, kind, page_idx)
    title = str(draft.get("title")) if draft else {
        "policy_form": "Policy Conditions",
        "notice": "Policyholder Notice",
        "amendatory": "State Amendatory Endorsement",
        "billing": "Premium Audit and Accounting Conditions",
    }.get(kind, "Policy Conditions")
    form_id = str(draft.get("form_id")) if draft else kind.upper()
    lines = [str(line) for line in draft.get("paragraphs", [])] if draft else _fallback_lines(profile, kind, item)
    if not (profile["lob"] == "BOP" and kind == "policy_form" and generated_bop_coverage_form):
        lines = _augment_lines(profile, kind, item, lines)
    if profile["lob"] == "BOP":
        if kind == "policy_form":
            return _bop_coverage_form_page(
                profile,
                title,
                form_id,
                page_idx,
                item,
                lines,
                generated_body=generated_bop_coverage_form,
            )
        if kind == "notice":
            return _bop_typed_notice_page(profile, title, page_idx)
        if kind == "billing":
            return _bop_typed_billing_page(profile, title, page_idx, item)
        if kind == "amendatory":
            return _bop_typed_amendatory_page(profile, title, page_idx, item)
        return _bop_typed_draft_page(profile, kind, title, form_id, page_idx, item, lines)
    body = f"""
<div class="form-title">{escape(title)}</div>
<div class="form-meta-row">
  <span>{escape(form_id)} policy form</span>
  <span>Policy No. {escape(profile["policy_number"])}</span>
</div>
{_fact_box(profile, item)}
<div class="policy-form-body two-column">
  {_paragraphs(lines)}
</div>
"""
    return _page(profile, title, body, form_id=form_id)


def _cover_page(profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    if profile["lob"] == "BOP":
        return _bop_declaration_page_one(profile, items)

    policy_rows = [
        ["Named Insured", profile["named_insured"]],
        ["Mailing Address", profile["mailing_address"]],
        ["Policy Number", profile["policy_number"]],
        ["Policy Period", profile["policy_period"]],
        ["Scheduled Items", len(items)],
    ]
    transaction_rows = [
        ["Transaction", "Issued policy packet"],
        ["Producer", profile["producer_name"]],
        ["Producer Code", profile["producer_code"]],
        ["Audit Basis", "Annual unless otherwise stated"],
        ["Payment Plan", "Direct bill - quarterly installments"],
        ["Countersignature", "Required where applicable by state law"],
    ]
    index_rows = [
        ["1", "Declarations and information page", "Policy-wide administrative values"],
        ["2", "Locations / classifications", "Location, state, class, or territory keys"],
        ["3", "Coverage, limits, payroll, or exposure schedules", "Scheduled item values"],
        ["4", "Forms and endorsements", "Form number, edition, and source"],
        ["5", "Endorsement details", "Effective dates and modified items"],
        ["6", "Premium summary", "Item-level premium or estimated premium"],
    ]
    body = f"""
<div class="declarations">
  <div class="declaration-box">
    <h2>Policy Declarations Package</h2>
    {_table(["Item", "Value"], policy_rows)}
    <p class="small muted">This declarations package, schedules, forms, and endorsements should be read together as one policy.</p>
  </div>
  <div class="notice-box">
    <h2>Transaction Information</h2>
    {_table(["Item", "Value"], transaction_rows, class_name="policy-table compact")}
  </div>
</div>
<h2>Document Schedule</h2>
{_table(["Part", "Section", "Purpose"], index_rows, class_name="policy-table compact")}
<div class="signature-row">
  <div class="signature-line">Authorized Representative</div>
  <div class="signature-line">Named Insured Acknowledgment</div>
</div>
"""
    return _page(profile, "Policy Declarations Package", body, form_id="SPEC-DEC")


def _declarations_page(profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    if profile["lob"] == "BOP":
        return _bop_declaration_page_two(profile, items)

    total = sum(int(re.sub(r"[^0-9]", "", item.get("premium") or item.get("estimated_premium", "0"))) for item in items)
    fields = [
        ("Carrier", profile["carrier"]),
        ("Named Insured", profile["named_insured"]),
        ("Policy Number", profile["policy_number"]),
        ("Policy Period", profile["policy_period"]),
        ("Line of Business", profile["lob_display"]),
        ("Estimated Premium", money(total)),
    ]
    body = f"""
<div class="declarations">
  <div class="declaration-box">{_field_grid(fields)}</div>
  <div class="notice-box">
    <h2>Policy Information</h2>
    <p>This declarations package identifies the coverage part and schedules that control item-level coverage, rating, forms, and premium.</p>
    {_table(["Producer", "Code"], [[profile["producer_name"], profile["producer_code"]]], class_name="policy-table compact")}
  </div>
</div>
<div class="three-col">
  <div class="form-box"><h2>Coverage Part</h2><p>Coverage applies only as shown in the attached declarations, schedules, forms, and endorsements.</p></div>
  <div class="form-box"><h2>Audit and Rating</h2><p>Premium may be subject to audit, rating basis verification, or payroll/exposure adjustment.</p></div>
  <div class="form-box"><h2>Forms</h2><p>Attached endorsements can amend limits, exclusions, covered locations, or scheduled parties.</p></div>
</div>
"""
    title = {
        "BOP": "Businessowners Policy Declarations",
        "WC": "Workers Compensation and Employers Liability Information Page",
        "CGL": "Commercial General Liability Coverage Part Declarations",
    }[profile["lob"]]
    form_id = {"BOP": "BP DS 01", "WC": "WC 00 00 01 A", "CGL": "CG DS 01"}[profile["lob"]]
    return _page(profile, title, body, form_id=form_id)


def _chunked_table_pages(
    profile: dict[str, str],
    title: str,
    headers: list[str],
    rows: list[list[Any]],
    *,
    form_id: str,
    page_size: int = 18,
    note: str = "",
) -> str:
    def row_markup(row: list[Any], absolute_index: int) -> str:
        pairs = [(str(header), str(value)) for header, value in zip(headers, row, strict=False)]
        if not pairs:
            return ""
        item_label = pairs[0][1]
        rest = pairs[1:]
        fields = "".join(
            '<div class="entry-field">'
            f'<span class="entry-label">{escape(label)}</span>'
            f'<span class="entry-value">{escape(value)}</span>'
            "</div>"
            for label, value in rest
        )
        variant = absolute_index % 4
        if variant == 0:
            note_text = "; ".join(f"{label.lower()} {value}" for label, value in rest[:3])
            body = f'<p class="entry-note">Schedule entry {escape(item_label)} records {escape(note_text)}.</p>'
            body += f'<div class="entry-fields">{fields}</div>'
        elif variant == 1:
            first = rest[0] if rest else ("Reference", item_label)
            tail = rest[1:]
            tail_fields = "".join(
                '<div class="entry-field">'
                f'<span class="entry-label">{escape(label)}</span>'
                f'<span class="entry-value">{escape(value)}</span>'
                "</div>"
                for label, value in tail
            )
            body = (
                f'<p class="entry-note">{escape(first[0])}: '
                f'<strong>{escape(first[1])}</strong>. The remaining values below apply to this same scheduled item.</p>'
                f'<div class="entry-fields">{tail_fields}</div>'
            )
        elif variant == 2:
            left = rest[: (len(rest) + 1) // 2]
            right = rest[(len(rest) + 1) // 2 :]
            left_text = " / ".join(f"{label}: {value}" for label, value in left)
            right_text = " / ".join(f"{label}: {value}" for label, value in right)
            body = (
                f'<p class="entry-note"><strong>{escape(item_label)}</strong> - {escape(left_text)}</p>'
                f'<p class="entry-note">{escape(right_text)}</p>'
            )
        else:
            detail = ". ".join(f"{label} is {value}" for label, value in rest)
            body = f'<p class="entry-note">{escape(item_label)}. {escape(detail)}.</p>'
            body += f'<div class="entry-fields single">{fields}</div>'
        return (
            f'<div class="schedule-entry v{variant}">'
            f'<div class="entry-id">{escape(item_label)}</div>'
            f'<div class="entry-body">{body}</div>'
            "</div>"
        )

    pages: list[str] = []
    for chunk_index, start in enumerate(range(0, len(rows), page_size), start=1):
        chunk = rows[start:start + page_size]
        suffix = f" - Continued {chunk_index}" if len(rows) > page_size and chunk_index > 1 else ""
        body = (f'<div class="schedule-note">{escape(note)}</div>' if note else "")
        body += '<div class="schedule-ledger">'
        body += "".join(row_markup(row, start + offset) for offset, row in enumerate(chunk))
        body += "</div>"
        body += """
<div class="two-col">
  <div class="form-box">
    <h2>Schedule Conditions</h2>
    <p>Entries on this schedule apply only to the coverage part, location, class, state, or form reference shown on the same row.</p>
  </div>
  <div class="form-box">
    <h2>Reading This Schedule</h2>
    <p>Read scheduled lines together with the declarations and attached forms to determine the complete scheduled item.</p>
  </div>
</div>
"""
        pages.append(_page(profile, title + suffix, body, form_id=form_id))
    return "".join(pages)


def _bop_schedule_pages(profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for item in items:
        grouped.setdefault((item["location_number"], item["building_number"]), []).append(item)

    premises = []
    coverages = []
    rating = []
    for (location_number, building_number), group in grouped.items():
        first = group[0]
        premises.append(
            [
                f"LOC {location_number}                                  BLDG {building_number}",
                f"PREMISES: {first['premises_address']}",
                f"CLASS CODE: {first['class_code']}    CLASSIFICATION: {first['classification']}",
                "The coverages for this premises are shown on the later property and liability coverage schedule.",
            ]
        )
        coverage_entry = [
            f"LOC {location_number} - {first['premises_address']}",
            f"BUILDING {building_number}",
        ]
        coverage_entry.extend(
            f"{item['coverage']}: LIMIT {item['limit']}; DED {item['deductible']}; {item['valuation']}; COINS {item['coinsurance']}"
            for item in group
        )
        coverages.append(coverage_entry)

        rating_entry = [
            f"LOC {location_number} / BLDG {building_number}",
            f"CLASS {first['class_code']} - {first['classification']}",
        ]
        rating_entry.extend(
            f"{item['coverage']}: BUSINESS INCOME BASIS {item['business_income_basis']}; PREMIUM {item['premium']}"
            for item in group
        )
        rating.append(rating_entry)
    return (
        _bop_typed_detail_schedule_page(
            profile,
            "Described Premises Schedule",
            "BPS2102 ED. 05-24",
            premises,
            note="Premises numbers are used throughout the declarations. Several coverages may apply to the same premises.",
        )
        + _bop_typed_detail_schedule_page(
            profile,
            "Property and Liability Coverage Schedule",
            "BPS2103 ED. 05-24",
            coverages,
            note="Coverage entries are grouped under the premises shown above. A coverage shown in one group does not apply to another premises.",
        )
        + _bop_typed_detail_schedule_page(
            profile,
            "Classification and Rating Schedule",
            "BPS2104 ED. 05-24",
            rating,
            note="Rating entries summarize class, income basis, and premium by premises group.",
        )
    )


def _wc_schedule_pages(profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    class_rows = [[item["item_id"], item["state"], item["class_code"], item["classification"], item["location_number"], item["governing_class"]] for item in items]
    payroll_rows = [[item["item_id"], item["state"], item["class_code"], item["annual_payroll"], item["manual_rate"], item["estimated_premium"]] for item in items]
    mod_fields = [
        ("Experience Modification Factor", items[0]["experience_mod"]),
        ("Schedule Credit/Debit", items[0]["schedule_credit_debit"]),
        ("Premium Basis", items[0]["premium_basis"]),
        ("Governing Class", next(item["class_code"] for item in items if item["governing_class"] == "Yes")),
    ]
    mod_page = _page(profile, "Experience Modification and Rating Summary", f'<div class="declaration-box">{_field_grid(mod_fields)}</div>', form_id="WC 00 04 14 A")
    return (
        _chunked_table_pages(profile, "Workers Compensation Classification Schedule", ["Item", "State", "Class", "Classification", "Loc", "Governing"], class_rows, form_id="WC DS 02", page_size=14, note="Rows are keyed by state and class code; payroll and premium appear on a later schedule.")
        + _chunked_table_pages(profile, "Payroll and Rate Schedule", ["Item", "State", "Class", "Payroll", "Rate", "Estimated Premium"], payroll_rows, form_id="WC DS 03", page_size=14)
        + mod_page
    )


def _cgl_schedule_pages(profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    limits = [[item["item_id"], item["coverage_part"], item["limit_type"], item["limit"]] for item in items]
    classifications = [[item["item_id"], item["location_number"], item["class_code"], item["classification"], item["territory"]] for item in items]
    rating = [[item["item_id"], item["class_code"], item["exposure_basis"], item["exposure"], item["rate"], item["products_completed_ops_rate"], item["premium"]] for item in items]
    return (
        _chunked_table_pages(profile, "Commercial General Liability Limits Schedule", ["Item", "Coverage Part", "Limit Type", "Limit"], limits, form_id="CG DS 02", page_size=16)
        + _chunked_table_pages(profile, "Classification and Location Schedule", ["Item", "Loc", "Class", "Classification", "Territory"], classifications, form_id="CG DS 03", page_size=15, note="Classification rows apply with the exposure/rate schedule and the limits schedule.")
        + _chunked_table_pages(profile, "Exposure and Premium Rating Schedule", ["Item", "Class", "Basis", "Exposure", "Rate", "PCO Rate", "Premium"], rating, form_id="CG DS 04", page_size=14)
    )


def _forms_schedule_pages(profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    rows = [[item["form_number"], item["edition_date"], item["form_title"], item["item_id"], item.get("endorsement_number") or "Policy jacket"] for item in items]
    if profile["lob"] == "BOP":
        form_rows: list[dict[str, str]] = []
        seen_forms: set[tuple[str, str, str, str]] = set()
        for item in items:
            source = "Endorsement attached" if item.get("endorsement_number") else "Policy jacket"
            key = (item["form_number"], item["edition_date"], item["form_title"], source)
            if key in seen_forms:
                continue
            seen_forms.add(key)
            form_rows.append(
                {
                    "form_number": item["form_number"],
                    "edition_date": item["edition_date"],
                    "form_title": item["form_title"],
                    "source": source,
                }
            )
        entries = [
            [
                f"FORM: {row['form_number']}    EDITION: {row['edition_date']}",
                f"TITLE: {row['form_title']}",
                f"SOURCE: {row['source']}",
            ]
            for row in form_rows
        ]
        pages: list[str] = []
        for chunk_idx, start in enumerate(range(0, len(entries), 8), start=1):
            title = "Forms and Endorsements Schedule" if chunk_idx == 1 else "Forms and Endorsements Schedule - Continued"
            pages.append(
                _bop_typed_detail_schedule_page(
                    profile,
                    title,
                    "BPS2105 ED. 05-24",
                    entries[start:start + 8],
                    note="This schedule lists forms attached to the policy. Use the coverage schedules and individual endorsements to determine where a form applies.",
                )
            )
        return "".join(pages)
    if profile["lob"] == "CGL":
        cgl_rows = [row + [item["exclusion_name"]] for row, item in zip(rows, items)]
        return _chunked_table_pages(profile, "Forms, Endorsements, and Exclusions Schedule", ["Form", "Edition", "Title", "Item", "Source", "Exclusion Concept"], cgl_rows, form_id="CG DS 05", page_size=12, note="Forms can control limits or exclusions independently from the rating schedule.")
    return _chunked_table_pages(profile, "Forms and Endorsements Schedule", ["Form", "Edition", "Title", "Item", "Source"], rows, form_id="WC DS 04", page_size=13, note="Form numbers and edition dates apply with the item schedule.")


def _clause_records(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in items:
        records.extend(build_policy_clause_records_for_item(item))
    return records


def _bop_typed_clause_pages(profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    pages: list[str] = []
    clauses = _clause_records(items)
    page_size = 8
    for page_no, start in enumerate(range(0, len(clauses), page_size), start=1):
        chunk = clauses[start:start + page_size]
        lines: list[str] = []
        lines.extend(_typed_policy_header(profile))
        lines.append(_typed_center("MATERIAL POLICY PROVISIONS"))
        lines.append(_typed_center("READ WITH DECLARATIONS, SCHEDULES, FORMS AND ENDORSEMENTS"))
        lines.append("=" * 78)
        lines.extend(
            [
                "The following provisions are part of the current policy packet. Each",
                "entry must be read with the scheduled premises, form number, edition",
                "date, and any endorsement applying to the same coverage.",
                "-" * 78,
                "",
            ]
        )
        for idx, clause in enumerate(chunk, start=start + 1):
            intro_variants = [
                (
                    f"{clause['form_number']} edition {clause['edition_date']} contains a "
                    f"{clause['clause_type']} provision for {clause['clause_scope']}."
                ),
                (
                    f"For {clause['clause_scope']}, read {clause['form_number']} "
                    f"edition {clause['edition_date']} as the controlling {clause['clause_type']} provision."
                ),
                (
                    f"The policy applies the following {clause['clause_type']} provision under "
                    f"{clause['form_number']} edition {clause['edition_date']} to {clause['clause_scope']}."
                ),
            ]
            intro = intro_variants[idx % len(intro_variants)]
            lines.extend(
                [
                    f"{idx:03d}. {clause['clause_title'].upper()}",
                ]
            )
            lines.extend(_typed_wrap(intro, width=76, indent="     "))
            lines.extend(_typed_wrap(clause["clause_text"], width=76, indent="     "))
            lines.append("")
        lines.extend(
            [
                "-" * 78,
                "ARCHIVED OR PRIOR-TERM CLAUSES APPEARING ELSEWHERE DO NOT MODIFY THIS POLICY.",
            ]
        )
        pages.append(
            _typed_form_page(
                profile,
                lines=lines,
                form_id="BPC4401 ED. 05-24",
                page_no=page_no,
                continued=page_no > 1,
            )
        )
    return "".join(pages)


def _clause_detail_pages(profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    if profile["lob"] == "BOP":
        return _bop_typed_clause_pages(profile, items)

    pages: list[str] = []
    clauses = _clause_records(items)
    page_size = 16 if profile["lob"] == "WC" else 14
    for page_no, start in enumerate(range(0, len(clauses), page_size), start=1):
        chunk = clauses[start:start + page_size]
        paragraphs = []
        for idx, clause in enumerate(chunk, start=start + 1):
            if profile["lob"] == "WC":
                context = (
                    f"{clause.get('state', '')} class {clause.get('class_code', '')} "
                    f"({clause.get('classification', '')})"
                )
            else:
                context = (
                    f"class {clause.get('class_code', '')} ({clause.get('classification', '')}) "
                    f"at Location {clause.get('location_number', '')}"
                )
                if clause.get("exclusion_name"):
                    context += f", with {clause['exclusion_name']}"
            intro_variants = [
                (
                    f"{clause['form_number']} edition {clause['edition_date']} is a "
                    f"{clause['clause_type']} provision for {clause['clause_scope']}."
                ),
                (
                    f"For {context}, the applicable form is {clause['form_number']} "
                    f"edition {clause['edition_date']} and the provision is treated as {clause['clause_type']}."
                ),
                (
                    f"The provision below is read with {clause['form_number']} edition "
                    f"{clause['edition_date']} for {clause['clause_scope']}."
                ),
            ]
            paragraphs.append(f'<p class="clause-heading">{escape(clause["clause_title"])}</p>')
            paragraphs.append(f"<p>{escape(intro_variants[idx % len(intro_variants)])}</p>")
            paragraphs.append(f"<p>{escape(clause['clause_text'])}</p>")
        notice = """
<div class="schedule-note">
  Material provisions in this section apply to the current policy term. Similar prior-term or advisory notes in archive pages are retained for underwriting reference.
</div>
"""
        body = notice + '<div class="policy-form-body two-column">' + "".join(paragraphs) + "</div>"
        title = "Material Policy Provisions" if page_no == 1 else f"Material Policy Provisions - Continued {page_no}"
        pages.append(_page(profile, title, body, form_id="CLAUSE-SCH"))
    return "".join(pages)


def _endorsement_detail_pages(profile: dict[str, str], items: list[dict[str, Any]], text_bank: PolicyTextBank | None) -> str:
    endorsed = [item for item in items if item.get("endorsement_number")]
    pages: list[str] = []
    for chunk_index, item in enumerate(endorsed, start=1):
        draft = _draft(text_bank, "endorsement", chunk_index)
        title = str(draft.get("title")) if draft else "Policy Change Endorsement"
        lines = [str(line) for line in draft.get("paragraphs", [])] if draft else _fallback_lines(profile, "endorsement", item)
        if profile["lob"] == "CGL":
            title = str(item.get("exclusion_name") or title)
            lines = _fallback_lines(profile, "endorsement", item)
        form_id = item["form_number"]
        lines = _augment_lines(profile, "endorsement", item, lines)
        if profile["lob"] == "BOP":
            pages.append(_bop_typed_endorsement_page(profile, title, chunk_index, item, lines))
            continue
        item_rows = _item_fact_rows(profile, item)
        item_rows.extend(
            [
                ("Endorsement", item["endorsement_number"]),
                ("Effective Date", item.get("endorsement_effective_date", "")),
                ("Materiality", item["materiality"]),
            ]
        )
        body = f"""
<div class="endorsement">
  <div class="endorsement-title">{escape(title)}</div>
  <div class="form-meta-row">
    <span>Endorsement No. {escape(item["endorsement_number"])}</span>
    <span>Effective {escape(item.get("endorsement_effective_date", ""))}</span>
  </div>
  <div class="fact-box">{_field_grid(item_rows)}</div>
  <div class="policy-form-body two-column">{_paragraphs(lines)}</div>
  <div class="signature-row">
    <div class="signature-line">Authorized Representative</div>
    <div class="signature-line">Countersignature Date</div>
  </div>
</div>
"""
        pages.append(_page(profile, f"{title} {chunk_index}", body, form_id=form_id))
    return "".join(pages)


def _premium_summary_pages(profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    if profile["lob"] == "WC":
        rows = [[item["item_id"], item["state"], item["class_code"], item["annual_payroll"], item["estimated_premium"]] for item in items]
        headers = ["Item", "State", "Class", "Payroll", "Estimated Premium"]
    elif profile["lob"] == "CGL":
        rows = [[item["item_id"], item["class_code"], item["exposure_basis"], item["exposure"], item["premium"]] for item in items]
        headers = ["Item", "Class", "Basis", "Exposure", "Premium"]
    else:
        rows = [[item["item_id"], item["coverage"], item["location_number"], item["limit"], item["premium"]] for item in items]
        headers = ["Item", "Coverage", "Loc", "Limit", "Premium"]
    total = sum(int(re.sub(r"[^0-9]", "", item.get("premium") or item.get("estimated_premium", "0"))) for item in items)
    note = f"Total scheduled premium for the rows shown on this schedule: {money(total)}."
    if profile["lob"] == "BOP":
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for item in items:
            grouped.setdefault((item["location_number"], item["building_number"]), []).append(item)
        premium_entries = [
            entry
            for (location_number, building_number), group in grouped.items()
            for entry in [
                [
                    f"LOC {location_number} / BLDG {building_number} - {group[0]['premises_address']}",
                    f"PREMISES SUBTOTAL: {money(sum(_typed_money_value(item.get('premium', '0')) for item in group))}",
                    *[
                        f"{item['coverage']}: PREMIUM {item['premium']}; LIMIT {item['limit']}"
                        for item in group
                    ],
                ]
            ]
        ]
        return _bop_typed_detail_schedule_page(
            profile,
            "Premium Summary Schedule",
            "BPS2106 ED. 05-24",
            premium_entries,
            note=f"{note} Premium rows are grouped by premises and must be read with the coverage schedule.",
        )
    return _chunked_table_pages(profile, "Premium Summary", headers, rows, form_id="PREM-SCH", page_size=20, note=note)


def _spacer_pages(
    config: PolicyMultiHopCaseConfig,
    profile: dict[str, str],
    count: int,
    start: int,
    items: list[dict[str, Any]],
    text_bank: PolicyTextBank | None,
) -> str:
    pages: list[str] = []
    rng = random.Random(stable_seed(9000 + start, config.id, count))
    builders: list[str] = [
        "policy_form",
        "policy_form",
        "policy_form",
        "policy_form",
        "policy_form",
        "billing",
        "billing",
        "notice",
        "amendatory",
    ]
    for offset in range(count):
        page_idx = start + offset
        kind = builders[(page_idx + rng.randrange(len(builders))) % len(builders)]
        pages.append(_draft_page(profile, kind, page_idx, items, text_bank))
    return "".join(pages)


def _distractor_section(config: PolicyMultiHopCaseConfig, profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    rows = []
    for idx, item in enumerate(items[: min(36, len(items))], start=1):
        rows.append([f"ARCH-{idx:03d}", item["form_number"], item.get("exclusion_name", item["form_title"]), item.get("limit", item.get("premium", "")), "Prior term only"])
    body = f"""
<p>Archived prior-term forms and advisory clause notes are retained with the file. They do not control the current policy period and are kept for underwriting reference.</p>
{_table(["Archive ID", "Form", "Subject", "Value", "Status"], rows, class_name="policy-table compact")}
"""
    return _page(profile, "Archived Prior-Term Forms", body, form_id="ARCH")


def _schedule_pages(config: PolicyMultiHopCaseConfig, profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    if config.lob == "BOP":
        return _bop_schedule_pages(profile, items)
    if config.lob == "WC":
        return _wc_schedule_pages(profile, items)
    return _cgl_schedule_pages(profile, items)


def case_html(
    config: PolicyMultiHopCaseConfig,
    profile: dict[str, str],
    items: list[dict[str, Any]],
    *,
    text_bank: PolicyTextBank | None = None,
) -> str:
    gap1, gap2, gap3, gap4 = config.spacer_pages
    body = (
        _cover_page(profile, items)
        + _declarations_page(profile, items)
        + _spacer_pages(config, profile, gap1, 1, items, text_bank)
        + _schedule_pages(config, profile, items)
        + _spacer_pages(config, profile, gap2, gap1 + 1, items, text_bank)
        + _forms_schedule_pages(profile, items)
        + _clause_detail_pages(profile, items)
        + _spacer_pages(config, profile, gap3, gap1 + gap2 + 1, items, text_bank)
        + _endorsement_detail_pages(profile, items, text_bank)
        + _spacer_pages(config, profile, gap4, gap1 + gap2 + gap3 + 1, items, text_bank)
        + _premium_summary_pages(profile, items)
        + _distractor_section(config, profile, items)
    )
    return _html_document(f"{profile['lob_display']} Specimen Packet", body)
