#!/usr/bin/env python3
"""Render synthetic operational-document tables from committed ground truth."""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import re
from collections import OrderedDict
from html import escape
from pathlib import Path
from typing import Any, Iterable, Sequence

from playwright.async_api import async_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
DEFAULT_OUTPUT = REPO_ROOT / "tmp" / "core_operations" / "operational_tables"

COMPANIES = [
    "Northline Freight Cooperative",
    "Crescent Basin Transport, Inc.",
    "Harbor Ridge Logistics, LLC",
    "Prairie Route Carriers, Inc.",
    "Silver Basin Hauling, LLC",
    "Granite Harbor Freight, Inc.",
    "Juniper Valley Transport, LLC",
    "Redwood Plains Cartage, Inc.",
]

RETAINED_RETURN_VARIANTS = (1, 2, 5)
RETAINED_TAX_SUMMARY_VARIANTS = (1, 2)
MILEAGE_EXCEPTION_VARIANTS = {1, 3, 6, 8}
MILEAGE_LANDSCAPE_VARIANTS = {2, 3, 6, 7}
MILEAGE_EXCEPTION_EVENT_COUNT = 72
MILEAGE_EXCEPTION_LANDSCAPE_EVENT_COUNT = 68
MILEAGE_EXCEPTION_PAGE_ROWS = 24
MILEAGE_EXCEPTION_LANDSCAPE_PAGE_ROWS = 34


def h(value: object) -> str:
    return escape("" if value is None else str(value))


def integer(value: object) -> str:
    if value in (None, ""):
        return ""
    return f"{int(float(value)):,}"


def decimal(value: object) -> str:
    if value in (None, ""):
        return ""
    return f"{float(value):,.1f}"


def rate(value: object) -> str:
    if value in (None, ""):
        return ""
    return f"{float(value):.4f}"


def money(value: object) -> str:
    if value in (None, ""):
        return ""
    amount = float(value)
    return f"(${abs(amount):,.2f})" if amount < 0 else f"${amount:,.2f}"


def chunks(items: Sequence[Any], size: int) -> list[Sequence[Any]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def balanced_chunks(items: Sequence[Any], maximum: int, minimum: int | None = None) -> list[Sequence[Any]]:
    if not items:
        return []
    minimum = minimum or max(1, maximum // 2)
    page_count = math.ceil(len(items) / maximum)
    while page_count > 1 and len(items) // page_count < minimum:
        page_count -= 1
    base, remainder = divmod(len(items), page_count)
    output: list[Sequence[Any]] = []
    cursor = 0
    for page_index in range(page_count):
        take = base + (1 if page_index < remainder else 0)
        output.append(items[cursor : cursor + take])
        cursor += take
    return output


def read_rows(sample_id: str) -> list[dict[str, Any]]:
    path = DATA_DIR / "ground_truth" / f"{sample_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def html_document(title: str, pages: Iterable[str], css: str, *, landscape: bool = False, a3: bool = False) -> str:
    size = "A3 landscape" if a3 and landscape else "A3 portrait" if a3 else "letter landscape" if landscape else "letter portrait"
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{h(title)}</title>
<style>
  @page {{ size: {size}; margin: 0; }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; color: #111; background: #fff; }}
  body {{ font-family: Arial, Helvetica, sans-serif; }}
  .page {{ position: relative; width: 100%; page-break-after: always; overflow: hidden; }}
  .page:last-child {{ page-break-after: auto; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ vertical-align: top; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .center {{ text-align: center; }}
  .nowrap {{ white-space: nowrap; }}
  {css}
</style>
</head>
<body>{''.join(pages)}</body>
</html>"""


def page_footer(page_no: int, total_pages: int, left: str) -> str:
    return f"<div class='page-footer'><span>{h(left)}</span><span>Page {page_no} of {total_pages}</span></div>"


def grouped_in_order(rows: Sequence[dict[str, Any]], key: str) -> list[tuple[str, list[dict[str, Any]]]]:
    groups: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for row in rows:
        groups.setdefault(str(row[key]), []).append(row)
    return list(groups.items())


def paginate_groups(
    groups: Sequence[tuple[str, Sequence[dict[str, Any]]]],
    capacity: int,
) -> list[list[tuple[str, Sequence[dict[str, Any]], bool]]]:
    pages: list[list[tuple[str, Sequence[dict[str, Any]], bool]]] = []
    page: list[tuple[str, Sequence[dict[str, Any]], bool]] = []
    remaining = capacity
    for label, group_rows in groups:
        cursor = 0
        continuation = False
        while cursor < len(group_rows):
            if remaining < 5:
                pages.append(page)
                page = []
                remaining = capacity
            take = min(len(group_rows) - cursor, remaining - 1)
            page.append((label, group_rows[cursor : cursor + take], continuation))
            remaining -= take + 1
            cursor += take
            continuation = True
            if cursor < len(group_rows):
                pages.append(page)
                page = []
                remaining = capacity
    if page:
        pages.append(page)
    if len(pages) > 1:
        last_rows = sum(len(segment_rows) for _, segment_rows, _ in pages[-1])
        if last_rows < capacity * 0.55:
            first_continuation = pages[-2][0][2]
            flattened = [
                (label, row)
                for candidate in pages[-2:]
                for label, segment_rows, _ in candidate
                for row in segment_rows
            ]
            cut = (len(flattened) + 1) // 2

            def rebuild(
                values: Sequence[tuple[str, dict[str, Any]]],
                *,
                initial_continuation: bool,
            ) -> list[tuple[str, Sequence[dict[str, Any]], bool]]:
                rebuilt: list[tuple[str, Sequence[dict[str, Any]], bool]] = []
                for label, row in values:
                    if rebuilt and rebuilt[-1][0] == label:
                        previous = rebuilt[-1]
                        rebuilt[-1] = (label, [*previous[1], row], previous[2])
                    else:
                        rebuilt.append((label, [row], initial_continuation if not rebuilt else False))
                return rebuilt

            pages[-2] = rebuild(flattened[:cut], initial_continuation=first_continuation)
            pages[-1] = rebuild(
                flattened[cut:],
                initial_continuation=flattened[cut - 1][0] == flattened[cut][0],
            )
    return pages


def mileage_exception_rows(rows: Sequence[dict[str, Any]], variant: int) -> list[dict[str, str]]:
    """Build synthetic review events resembling support pages in real IFTA packets."""
    comments = (
        "The recorded position was insufficient to assign this interval to a jurisdiction.",
        "The distance was retained for review because the device message arrived after the trip closed.",
        "The reported jurisdiction changed near a border crossing; the trip record remains under review.",
        "An odometer reading was restored from the next accepted device message for this unit.",
        "A manually entered distance overlaps an automated trip segment and requires source verification.",
        "The fuel purchase state and travel state differ; no quarterly adjustment has been posted.",
        "The device reported a location gap between two accepted positions in the trip history.",
        "The review queue retained this segment because the jurisdiction assignment changed twice.",
    )
    location_results = (
        "No location",
        "Border proximity",
        "Recovered position",
        "Manual jurisdiction",
        "Position conflict",
        "Fuel-state mismatch",
    )
    sources = ("GPS/Odometer", "Trip segment", "Manual distance", "Fuel match", "Border event")
    statuses = ("Open", "Reviewed", "Pending source", "Resolved", "No adjustment")
    if not rows:
        return []
    events: list[dict[str, str]] = []
    stride = 17 + variant
    event_count = (
        MILEAGE_EXCEPTION_LANDSCAPE_EVENT_COUNT
        if variant in MILEAGE_LANDSCAPE_VARIANTS
        else MILEAGE_EXCEPTION_EVENT_COUNT
    )
    for event_index in range(event_count):
        row = rows[(event_index * stride + variant * 11) % len(rows)]
        day = 2 + ((event_index * 3 + variant) % 88)
        hour = 5 + ((event_index * 7 + variant) % 17)
        minute = (event_index * 13 + variant * 5) % 60
        events.append(
            {
                "number": str(101 + event_index),
                "timestamp": f"{7 + day // 31:02d}/{1 + day % 28:02d}/2025 {hour:02d}:{minute:02d}",
                "location_result": location_results[(event_index + variant) % len(location_results)],
                "source": sources[(event_index * 2 + variant) % len(sources)],
                "vehicle": str(row["vehicle"]),
                "jurisdiction": str(row["state"]),
                "status": statuses[(event_index * 3 + variant) % len(statuses)],
                "comment": comments[(event_index * 5 + variant) % len(comments)],
            }
        )
    return events


def mileage_exception_pages(
    rows: Sequence[dict[str, Any]],
    variant: int,
    company: str,
    title: str,
    *,
    first_page_number: int,
    total_pages: int,
) -> list[str]:
    events = mileage_exception_rows(rows, variant)
    rows_per_page = (
        MILEAGE_EXCEPTION_LANDSCAPE_PAGE_ROWS
        if variant in MILEAGE_LANDSCAPE_VARIANTS
        else MILEAGE_EXCEPTION_PAGE_ROWS
    )
    pages: list[str] = []
    for page_offset, page_rows in enumerate(
        balanced_chunks(events, rows_per_page, max(16, rows_per_page - 6))
    ):
        table_rows = "".join(
            "<tr>"
            f"<td class='num'>{h(event['number'])}</td>"
            f"<td class='nowrap'>{h(event['timestamp'])}</td>"
            f"<td>{h(event['location_result'])}</td>"
            f"<td>{h(event['source'])}</td>"
            f"<td>{h(event['vehicle'])}</td>"
            f"<td>{h(event['jurisdiction'])}</td>"
            f"<td>{h(event['status'])}</td>"
            f"<td>{h(event['comment'])}</td>"
            "</tr>"
            for event in page_rows
        )
        page_number = first_page_number + page_offset
        header = ""
        if page_offset == 0:
            header = f"""<header class="report-header">
    <div><b>{h(company)}</b><br>IFTA account {742000 + variant * 137}-A</div>
    <div><h1>Distance Review Activity</h1><div>Reporting period 07/01/2025 - 09/30/2025</div></div>
    <div class="right">Review queue<br>Quarterly filing support</div>
  </header>
  <div class="report-rule"></div>"""
        table_header = "<thead><tr><th>#</th><th>Event date / time</th><th>Location result</th><th>Source</th><th>Unit</th><th>Juris.</th><th>Review status</th><th>Comment</th></tr></thead>" if page_offset == 0 else ""
        colgroup = """<colgroup>
    <col style="width:.3in"><col style="width:1.05in"><col style="width:.9in">
    <col style="width:.85in"><col style="width:.62in"><col style="width:.7in">
    <col style="width:.9in"><col>
  </colgroup>"""
        continuation_class = "" if page_offset == 0 else " exception-continuation"
        pages.append(
            f"""<section class="page mileage-page mileage-exception-page{continuation_class} variant-{variant}">
  {header}
  <table class="exception-table">{colgroup}{table_header}<tbody>{table_rows}</tbody></table>
  {page_footer(page_number, total_pages, title)}
</section>"""
        )
    return pages


def mileage_html(sample_id: str, rows: list[dict[str, Any]], variant: int) -> str:
    company = COMPANIES[(variant - 1) % len(COMPANIES)]
    groups = grouped_in_order(rows, "vehicle")
    inherited = variant in {1, 3, 5, 7}
    landscape = variant in MILEAGE_LANDSCAPE_VARIANTS
    if inherited and landscape:
        capacity = 34
    elif inherited:
        capacity = 34
    elif landscape:
        capacity = 40
    else:
        capacity = 38
    page_groups = paginate_groups(groups, capacity)
    pages: list[str] = []
    title_by_variant = {
        1: "IFTA Mileage - All Trucks",
        2: "Quarterly Distance Detail",
        3: "Vehicle / Jurisdiction Mileage",
        4: "IFTA Distance Export",
        5: "Mileage Detail by Unit",
        6: "Fuel Tax Mileage Register",
        7: "Quarterly Unit Mileage",
        8: "Jurisdiction Distance File",
    }
    title = title_by_variant[variant]
    exception_events = mileage_exception_rows(rows, variant) if variant in MILEAGE_EXCEPTION_VARIANTS else []
    exception_rows_per_page = (
        MILEAGE_EXCEPTION_LANDSCAPE_PAGE_ROWS
        if landscape
        else MILEAGE_EXCEPTION_PAGE_ROWS
    )
    exception_page_count = len(
        balanced_chunks(
            exception_events,
            exception_rows_per_page,
            max(16, exception_rows_per_page - 6),
        )
    )
    total_pages = len(page_groups) + exception_page_count
    for page_no, segments in enumerate(page_groups, start=1):
        body: list[str] = []
        row_index = 0
        for vehicle, segment_rows, continued in segments:
            if inherited:
                body.append(
                    f"<tr class='unit-band'><td colspan='5'>Unit {h(vehicle)}"
                    f"<span>{'Continued' if continued else 'Quarterly unit detail'}</span></td></tr>"
                )
                for row in segment_rows:
                    row_index += 1
                    body.append(
                        f"<tr><td class='line-no'>{row_index}</td><td>{h(row['state'])}</td>"
                        f"<td class='num'>{decimal(row['identified_miles'])}</td>"
                        f"<td class='num'>{decimal(row['unidentified_miles'])}</td>"
                        f"<td class='num'>{decimal(row['total_miles'])}</td></tr>"
                    )
                if segment_rows and segment_rows[-1] == dict(groups)[vehicle][-1]:
                    body.append(
                        f"<tr class='subtotal'><td colspan='2'>Unit {h(vehicle)} total</td>"
                        f"<td class='num'>{decimal(sum(float(r['identified_miles']) for r in segment_rows))}</td>"
                        f"<td class='num'>{decimal(sum(float(r['unidentified_miles']) for r in segment_rows))}</td>"
                        f"<td class='num'>{decimal(sum(float(r['total_miles']) for r in segment_rows))}</td></tr>"
                    )
            else:
                for row in segment_rows:
                    body.append(
                        f"<tr><td>{h(vehicle)}</td><td>{h(row['state'])}</td>"
                        f"<td class='num'>{decimal(row['total_miles'])}</td>"
                        f"<td class='num'>{decimal(row['identified_miles'])}</td>"
                        f"<td class='num'>{decimal(row['unidentified_miles'])}</td>"
                        f"<td class='center'>{'R' if float(row['unidentified_miles']) else ''}</td></tr>"
                    )
                if segment_rows and segment_rows[-1] == dict(groups)[vehicle][-1]:
                    body.append(
                        f"<tr class='subtotal'><td colspan='2'>{h(vehicle)} subtotal</td>"
                        f"<td class='num'>{decimal(sum(float(r['total_miles']) for r in segment_rows))}</td>"
                        f"<td class='num'>{decimal(sum(float(r['identified_miles']) for r in segment_rows))}</td>"
                        f"<td class='num'>{decimal(sum(float(r['unidentified_miles']) for r in segment_rows))}</td><td></td></tr>"
                    )
        if inherited:
            columns = "<th>#</th><th>Jurisdiction</th><th>Identified miles</th><th>Unidentified miles</th><th>Total miles</th>"
        else:
            columns = "<th>Unit</th><th>Jurisdiction</th><th>Total miles</th><th>ELD matched</th><th>Unassigned</th><th>Flag</th>"
        pages.append(
            f"""<section class="page mileage-page variant-{variant}">
  <header class="report-header">
    <div><b>{h(company)}</b><br>IFTA account {742000 + variant * 137}-A</div>
    <div><h1>{h(title)}</h1><div>Reporting period 07/01/2025 - 09/30/2025</div></div>
    <div class="right">Generated 10/{12 + variant}/2025<br>Fuel tax reporting copy</div>
  </header>
  <div class="report-rule"></div>
  <table class="mileage-table"><thead><tr>{columns}</tr></thead><tbody>{''.join(body)}</tbody></table>
  <div class="foot-note">Miles shown as reported by unit and jurisdiction. Unassigned distance is included in the total and is not an additional mileage category.</div>
  {page_footer(page_no, total_pages, title)}
</section>"""
        )
    if exception_page_count:
        pages.extend(
            mileage_exception_pages(
                rows,
                variant,
                company,
                title,
                first_page_number=len(page_groups) + 1,
                total_pages=total_pages,
            )
        )
    css = """
  .mileage-page { height: 8.5in; padding: .34in .4in .34in; }
  .report-header { display: grid; grid-template-columns: 1fr 1.65fr 1fr; align-items: start; font-size: 8pt; line-height: 1.35; }
  .report-header h1 { margin: 0 0 .03in; text-align: center; font-size: 15pt; }
  .report-header > div:nth-child(2) { text-align: center; }
  .report-header .right { text-align: right; }
  .report-rule { margin: .1in 0 .09in; border-top: 1.5px solid #222; }
  .mileage-table { font-size: 7.4pt; }
  .mileage-table th { border: 1px solid #444; padding: 3px 4px; text-align: left; background: #f1f2f2; }
  .mileage-table td { border: 1px solid #777; padding: 2px 4px; height: .145in; }
  .mileage-table .line-no { width: .28in; text-align: right; color: #444; }
  .unit-band td { padding: 4px 6px; font-weight: 700; background: #e4e7e8; border-top: 1.5px solid #222; }
  .unit-band span { float: right; font-weight: 400; font-style: italic; }
  .subtotal td { font-weight: 700; border-top: 1.5px solid #333; background: #f7f7f7; }
  .exception-table { table-layout: fixed; font-size: 6.5pt; }
  .exception-table th, .exception-table td { border: 1px solid #888; padding: 3px 4px; line-height: 1.18; }
  .exception-table th { background: #eceeef; text-align: left; }
  .exception-table th:nth-child(1) { width: .3in; }
  .exception-table th:nth-child(2) { width: 1.05in; }
  .exception-table th:nth-child(3) { width: .9in; }
  .exception-table th:nth-child(4) { width: .85in; }
  .exception-table th:nth-child(5) { width: .62in; }
  .exception-table th:nth-child(6) { width: .7in; }
  .exception-table th:nth-child(7) { width: .9in; }
  .exception-continuation { padding-top: .1in; }
  .foot-note { position: absolute; left: .4in; bottom: .36in; font-size: 6.5pt; color: #444; }
  .page-footer { position: absolute; left: .4in; right: .4in; bottom: .14in; display: flex; justify-content: space-between; border-top: 1px solid #999; padding-top: 3px; font-size: 6.5pt; }
"""
    if not landscape:
        css += """
  .mileage-page { height: 11in; padding: .38in .38in .36in; }
  .mileage-table { font-size: 8.1pt; }
  .mileage-table td { height: .205in; padding: 3px 4px; }
  .exception-table { font-size: 7.4pt; }
  .exception-table th, .exception-table td { padding: 4px 5px; }
"""
    return html_document(sample_id, pages, css, landscape=landscape)


def return_groups(rows: Sequence[dict[str, Any]]) -> list[tuple[str, list[dict[str, Any]]]]:
    groups: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    last_regular = ""
    for row in rows:
        schedule = str(row["schedule"])
        match = re.fullmatch(r"Return Totals \((.+)\)", schedule)
        if match:
            key = match.group(1)
        else:
            key = schedule
            last_regular = key
        groups.setdefault(key or last_regular, []).append(row)
    return list(groups.items())


def return_row_cells(row: dict[str, Any], *, show_schedule: bool = False) -> str:
    schedule = h(row["schedule"]) if show_schedule else ""
    return (
        f"<td>{schedule}</td><td>{h(row['jurisdiction'])}</td><td class='center'>{h(row['surcharge'])}</td>"
        f"<td class='num'>{integer(row['distance_miles'])}</td><td class='num'>{integer(row['taxable_distance_miles'])}</td>"
        f"<td class='num'>{integer(row['taxable_volume'])}</td><td class='num'>{integer(row['tax_paid_volume'])}</td>"
        f"<td class='num'>{integer(row['net_taxable_volume'])}</td><td class='num'>{rate(row['tax_rate'])}</td>"
        f"<td class='num'>{money(row['tax_due_credit'])}</td><td class='num'>{money(row['interest_due'])}</td>"
        f"<td class='num'>{money(row['total_due'])}</td>"
    )


def return_schedule_html(sample_id: str, rows: list[dict[str, Any]], variant: int) -> str:
    groups = return_groups(rows)
    split_tables = variant in {2, 5}
    pages: list[str] = []
    company = COMPANIES[(variant + 1) % len(COMPANIES)]
    for group_index, (schedule, group_rows) in enumerate(groups, start=1):
        regular = [row for row in group_rows if not str(row["schedule"]).startswith("Return Totals")]
        totals = [row for row in group_rows if str(row["schedule"]).startswith("Return Totals")]
        if split_tables:
            left = []
            right = []
            for row in regular:
                left.append(
                    f"<tr><td>{h(row['jurisdiction'])}</td><td class='center'>{h(row['surcharge'])}</td>"
                    f"<td class='num'>{integer(row['distance_miles'])}</td><td class='num'>{integer(row['taxable_distance_miles'])}</td>"
                    f"<td class='num'>{integer(row['taxable_volume'])}</td><td class='num'>{integer(row['tax_paid_volume'])}</td></tr>"
                )
                right.append(
                    f"<tr><td>{h(row['jurisdiction'])}</td><td class='num'>{integer(row['net_taxable_volume'])}</td>"
                    f"<td class='num'>{rate(row['tax_rate'])}</td><td class='num'>{money(row['tax_due_credit'])}</td>"
                    f"<td class='num'>{money(row['interest_due'])}</td><td class='num'>{money(row['total_due'])}</td></tr>"
                )
            total_note = ""
            if totals:
                total = totals[0]
                total_note = (
                    f"<div class='return-total'><b>{h(total['schedule'])}</b>"
                    f"<div class='return-total-grid'>"
                    f"<span><label>Distance</label>{integer(total['distance_miles'])}</span>"
                    f"<span><label>Taxable dist.</label>{integer(total['taxable_distance_miles'])}</span>"
                    f"<span><label>Taxable vol.</label>{integer(total['taxable_volume'])}</span>"
                    f"<span><label>Tax-paid vol.</label>{integer(total['tax_paid_volume'])}</span>"
                    f"<span><label>Net vol.</label>{integer(total['net_taxable_volume'])}</span>"
                    f"<span><label>Due / credit</label>{money(total['tax_due_credit'])}</span>"
                    f"<span><label>Interest</label>{money(total['interest_due'])}</span>"
                    f"<span><label>Total due</label>{money(total['total_due'])}</span>"
                    f"</div></div>"
                )
            body = f"""<div class="split-grid">
  <div><h2>Schedule A - Distance and fuel</h2><table><thead><tr><th>Juris.</th><th>Surch.</th><th>Distance</th><th>Taxable dist.</th><th>Taxable vol.</th><th>Tax-paid vol.</th></tr></thead><tbody>{''.join(left)}</tbody></table></div>
  <div><h2>Schedule B - Tax computation</h2><table><thead><tr><th>Juris.</th><th>Net vol.</th><th>Rate</th><th>Due / credit</th><th>Interest</th><th>Total due</th></tr></thead><tbody>{''.join(right)}</tbody></table></div>
</div>{total_note}"""
        else:
            trs = []
            for row_index, row in enumerate(group_rows):
                cls = "total-row" if str(row["schedule"]).startswith("Return Totals") else ""
                trs.append(f"<tr class='{cls}'>{return_row_cells(row, show_schedule=row_index == 0 or bool(cls))}</tr>")
            body = f"""<table class="return-table"><thead><tr>
  <th>Schedule</th><th>Juris.</th><th>Surch.</th><th>Distance</th><th>Taxable distance</th><th>Taxable volume</th><th>Tax-paid volume</th><th>Net volume</th><th>Rate</th><th>Due / credit</th><th>Interest</th><th>Total due</th>
</tr></thead><tbody>{''.join(trs)}</tbody></table>"""
        pages.append(
            f"""<section class="page return-page variant-{variant}">
  <div class="browser-line"><span>10/{10 + variant}/2025, {8 + variant}:2{variant} AM</span><span>IFTA Return Detail</span><span>File {780000 + variant * 83}</span></div>
  <header><div><b>{h(company)}</b><br>Account {381000 + variant * 71}</div><div><h1>Return Schedule Details</h1><div>{h(schedule)} &nbsp; | &nbsp; Diesel</div></div><div class="right">Original filing<br>Quarter {((group_index - 1) % 4) + 1}, {2020 + (group_index - 1) // 4}</div></header>
  <div class="instruction">Jurisdiction activity is reported below. Surcharge rows are part of the same filing; subtotal and payment lines are not separate jurisdiction filings.</div>
  {body}
  {page_footer(group_index, len(groups), 'IFTA return detail')}
</section>"""
        )
    css = """
  .return-page { height: 8.5in; padding: .28in .34in .32in; font-size: 7pt; }
  .browser-line { display: grid; grid-template-columns: 1fr 1fr 1fr; font-size: 6.5pt; margin-bottom: .12in; }
  .browser-line span:nth-child(2) { text-align: center; }
  .browser-line span:last-child { text-align: right; }
  .return-page header { display: grid; grid-template-columns: 1fr 1.8fr 1fr; align-items: start; line-height: 1.3; }
  .return-page header h1 { margin: 0; text-align: center; font-size: 15pt; }
  .return-page header > div:nth-child(2) { text-align: center; }
  .right { text-align: right; }
  .instruction { border-top: 1px solid #333; border-bottom: 1px solid #999; margin: .11in 0 .1in; padding: .055in .03in; color: #333; }
  .return-table { table-layout: fixed; font-size: 6.6pt; }
  .return-table th, .return-table td, .split-grid th, .split-grid td { border: 1px solid #aaa; padding: 3px 3px; height: .185in; }
  .return-table th, .split-grid th { background: #eef0f1; font-weight: 700; text-align: center; }
  .return-table th:first-child { width: 1.05in; }
  .total-row td { background: #f1f1f1; border-top: 1.5px solid #333; font-weight: 700; }
  .split-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .14in; }
  .split-grid h2 { margin: 0 0 .055in; padding-bottom: .03in; border-bottom: 1.5px solid #333; font-size: 9.5pt; }
  .split-grid table { table-layout: fixed; font-size: 6.7pt; }
  .return-total { margin-top: .07in; border: 1px solid #444; padding: .05in .06in; font-size: 6.3pt; }
  .return-total > b { display: block; margin-bottom: .035in; }
  .return-total-grid { display: grid; grid-template-columns: repeat(8, 1fr); }
  .return-total-grid span { min-width: 0; border-left: 1px solid #bbb; padding-left: .045in; font-variant-numeric: tabular-nums; }
  .return-total-grid span:first-child { border-left: 0; padding-left: 0; }
  .return-total-grid label { display: block; margin-bottom: 1px; color: #555; font-size: 5.3pt; font-weight: 700; text-transform: uppercase; }
  .page-footer { position: absolute; left: .34in; right: .34in; bottom: .12in; display: flex; justify-content: space-between; border-top: 1px solid #999; padding-top: 3px; font-size: 6.5pt; }
"""
    return html_document(sample_id, pages, css, landscape=True)


def tax_summary_groups(rows: Sequence[dict[str, Any]]) -> list[Sequence[dict[str, Any]]]:
    # The source list has no filing identifier. Balance it into plausible
    # jurisdiction schedules instead of leaving a four-row final filing.
    return balanced_chunks(rows, 42, 35)


def tax_summary_html(sample_id: str, rows: list[dict[str, Any]], variant: int) -> str:
    groups = tax_summary_groups(rows)
    split_tables = variant in {2, 4}
    pages: list[str] = []
    company = COMPANIES[(variant + 3) % len(COMPANIES)]
    page_no = 0
    page_specs: list[tuple[str, int, Sequence[dict[str, Any]], str]] = []
    for return_no, group_rows in enumerate(groups, start=1):
        if split_tables:
            page_specs.append(("distance", return_no, group_rows, "Schedule A - Distance and Fuel"))
            page_specs.append(("tax", return_no, group_rows, "Schedule B - Tax Computation"))
        else:
            page_specs.append(("full", return_no, group_rows, "Jurisdiction Tax Summary"))
    for mode, return_no, group_rows, page_title in page_specs:
        page_no += 1
        if mode == "distance":
            cols = "<th>Juris.</th><th>Fuel</th><th>Total miles</th><th>Taxable miles</th><th>Taxable gal.</th><th>Tax-paid gal.</th>"
            trs = [
                f"<tr><td>{h(r['jurisdiction'])}</td><td>{h(r['fuel_type'])}</td><td class='num'>{integer(r['total_miles'])}</td><td class='num'>{integer(r['taxable_miles'])}</td><td class='num'>{integer(r['taxable_gallons'])}</td><td class='num'>{integer(r['gallons_purchased'])}</td></tr>"
                for r in group_rows
            ]
        elif mode == "tax":
            cols = "<th>Juris.</th><th>Net taxable gal.</th><th>Tax rate</th><th>Tax due / refund</th><th>Surtax</th><th>Interest</th><th>Total due / refund</th>"
            trs = [
                f"<tr><td>{h(r['jurisdiction'])}</td><td class='num'>{integer(r['net_taxable_gallons'])}</td><td class='num'>{rate(r['tax_rate'])}</td><td class='num'>{money(r['tax_due_refund'])}</td><td class='num'>{money(r['surtax_due'])}</td><td class='num'>{money(r['interest_due'])}</td><td class='num'>{money(r['total_due_refund'])}</td></tr>"
                for r in group_rows
            ]
        else:
            cols = "<th>Juris.</th><th>Fuel</th><th>Total mi.</th><th>Taxable mi.</th><th>Taxable gal.</th><th>Tax-paid gal.</th><th>Net gal.</th><th>Rate</th><th>Tax due / refund</th><th>Surtax</th><th>Interest</th><th>Total</th>"
            trs = [
                f"<tr><td>{h(r['jurisdiction'])}</td><td>{h(r['fuel_type'])}</td><td class='num'>{integer(r['total_miles'])}</td><td class='num'>{integer(r['taxable_miles'])}</td><td class='num'>{integer(r['taxable_gallons'])}</td><td class='num'>{integer(r['gallons_purchased'])}</td><td class='num'>{integer(r['net_taxable_gallons'])}</td><td class='num'>{rate(r['tax_rate'])}</td><td class='num'>{money(r['tax_due_refund'])}</td><td class='num'>{money(r['surtax_due'])}</td><td class='num'>{money(r['interest_due'])}</td><td class='num'>{money(r['total_due_refund'])}</td></tr>"
                for r in group_rows
            ]
        total_due = sum(float(r["total_due_refund"]) for r in group_rows)
        pages.append(
            f"""<section class="page tax-summary-page variant-{variant}">
  <div class="form-banner"><span>INTERSTATE FUEL TAX AGREEMENT</span><b>{h(page_title)}</b><span>Form FT-{240 + variant}</span></div>
  <div class="form-meta"><div><label>Licensee</label><b>{h(company)}</b></div><div><label>Account</label><b>{391000 + variant * 59}</b></div><div><label>Filing</label><b>Return {return_no:02d}</b></div><div><label>Period</label><b>Q{((return_no - 1) % 4) + 1} {2021 + (return_no - 1) // 4}</b></div></div>
  <div class="notice">Report jurisdiction activity for the fuel type shown. Parenthesized amounts are credits. Totals below include only this filing period.</div>
  <table class="tax-table"><thead><tr>{cols}</tr></thead><tbody>{''.join(trs)}</tbody></table>
  <div class="certification"><span>Return {return_no:02d} calculated total</span><b>{money(total_due)}</b><span>Prepared from distance and fuel-purchase records</span><span class="signature">Authorized review ____________________</span></div>
  {page_footer(page_no, len(page_specs), 'IFTA jurisdiction schedule')}
</section>"""
        )
    css = """
  .tax-summary-page { height: 8.5in; padding: .28in .34in .32in; font-size: 7pt; }
  .form-banner { display: grid; grid-template-columns: 1fr 1.5fr 1fr; align-items: end; border-bottom: 2px solid #243c51; padding-bottom: .065in; color: #243c51; }
  .form-banner b { text-align: center; font-size: 13pt; }
  .form-banner span:last-child { text-align: right; }
  .form-meta { display: grid; grid-template-columns: 1.6fr .75fr .7fr .7fr; border: 1px solid #738495; margin-top: .09in; }
  .form-meta div { padding: .055in .07in; border-right: 1px solid #9aa6b0; }
  .form-meta div:last-child { border-right: 0; }
  .form-meta label { display: block; color: #556775; font-size: 6pt; text-transform: uppercase; }
  .notice { padding: .06in .02in; font-size: 6.5pt; color: #444; }
  .tax-table { table-layout: fixed; font-size: 6.45pt; }
  .tax-table th { background: #e7ebee; border: 1px solid #8897a3; padding: 3px 2px; text-align: center; }
  .tax-table td { border: 1px solid #a8b1b8; padding: 2px 3px; height: .14in; }
  .certification { margin-top: .08in; display: grid; grid-template-columns: 1fr .55fr 1.5fr 1.3fr; gap: .08in; align-items: end; border-top: 1px solid #556775; padding-top: .055in; font-size: 6.5pt; }
  .signature { text-align: right; }
  .page-footer { position: absolute; left: .34in; right: .34in; bottom: .12in; display: flex; justify-content: space-between; border-top: 1px solid #999; padding-top: 3px; font-size: 6.5pt; }
"""
    return html_document(sample_id, pages, css, landscape=True)


def rewrite_tax_inquiry_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    account = dict(rows[0])
    output.append(account)
    pattern = re.compile(r"^(?P<state>[A-Z]{2}) (?P<miles>[\d,]+) miles$")
    for index, row in enumerate(rows[1:], start=1):
        match = pattern.match(str(row["value"]))
        if not match:
            if re.match(r"^[A-Z]{2} taxable distance$", str(row.get("field", ""))):
                output.append(dict(row))
                continue
            raise ValueError(f"Unexpected inquiry row value: {row['value']!r}")
        return_no = (index - 1) // 42 + 1
        output.append(
            {
                "section": f"Schedule B - Return {return_no:02d}",
                "field": f"{match.group('state')} taxable distance",
                "value": f"{match.group('miles')} miles",
                "page": row["page"],
            }
        )
    return output


def tax_inquiry_html(sample_id: str, rows: list[dict[str, Any]], variant: int) -> str:
    account = rows[0]
    detail = rows[1:]
    by_page: OrderedDict[int, list[dict[str, Any]]] = OrderedDict()
    for row in detail:
        by_page.setdefault(int(row["page"]), []).append(row)
    pages: list[str] = []
    total_pages = 1 + len(by_page)
    pages.append(
        f"""<section class="page inquiry-page cover variant-{variant}">
  <div class="portal-head"><b>Fuel Tax Services</b><span>Tax Return Inquiry - IFTA</span><span>Printed 10/{12 + variant}/2025</span></div>
  <h1>TAX RETURN INQUIRY</h1>
  <h2>Tax Return Information</h2>
  <div class="field-grid">
    <div><label>{h(account['field'])}</label><b>{h(account['value'])}</b></div><div><label>Legal name</label><b>{h(COMPANIES[variant + 1])}</b></div>
    <div><label>License year</label><b>2025</b></div><div><label>Return quarter</label><b>3</b></div>
    <div><label>Fuel type</label><b>DIESEL</b></div><div><label>Amendment no.</label><b>0</b></div>
    <div><label>Filing status</label><b>PAID</b></div><div><label>Invoice date</label><b>10/14/2025</b></div>
  </div>
  <h2>Return Details</h2>
  <div class="amount-grid"><span>Total miles</span><b>{integer(sum(int(re.sub(r'\D', '', r['value'])) for r in detail))}</b><span>Schedules attached</span><b>{len(by_page)}</b><span>Payment status</span><b>Paid</b><span>Amended filing</span><b>No</b></div>
  <h2>Payment Details</h2>
  <table class="payment"><thead><tr><th>Payment type</th><th>Confirmation</th><th>Received</th><th>Amount</th></tr></thead><tbody><tr><td>ACH debit</td><td>FT{variant}912804</td><td>10/14/2025</td><td class="num">$2,238.14</td></tr></tbody></table>
  <div class="certify">This inquiry reflects the accepted return and associated jurisdiction schedules. Corrections require an amended filing.</div>
  {page_footer(1, total_pages, 'Tax return inquiry')}
</section>"""
    )
    for output_page, (source_page, page_rows) in enumerate(by_page.items(), start=2):
        sections: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
        for row in page_rows:
            sections.setdefault(str(row["section"]), []).append(row)
        blocks = []
        for section, section_rows in sections.items():
            trs = []
            for line_no, row in enumerate(section_rows, start=1):
                state = str(row["field"]).split()[0]
                trs.append(
                    f"<tr><td class='line'>{line_no:02d}</td><td>{h(state)}</td><td>{h(row['field'])}</td><td class='num'>{h(row['value'])}</td></tr>"
                )
            blocks.append(
                f"<h2>{h(section)}</h2><table class='detail'><thead><tr><th>Line</th><th>Juris.</th><th>Reported field</th><th>Reported value</th></tr></thead><tbody>{''.join(trs)}</tbody></table>"
            )
        pages.append(
            f"""<section class="page inquiry-page variant-{variant}">
  <div class="portal-head"><b>Fuel Tax Services</b><span>Tax Return Inquiry - IFTA</span><span>Account {h(account['value'])}</span></div>
  <h1>JURISDICTION SCHEDULE DETAIL</h1>
  {''.join(blocks)}
  <div class="schedule-note">Distances are reported in miles. A blank adjustment indicator means no manual correction was entered for the jurisdiction line.</div>
  {page_footer(output_page, total_pages, f'Tax return inquiry - source page {source_page}')}
</section>"""
        )
    css = """
  .inquiry-page { height: 11in; padding: .38in .5in .38in; font-size: 8pt; }
  .portal-head { display: grid; grid-template-columns: 1fr 1fr 1fr; border-bottom: 1px solid #49657b; padding-bottom: .08in; color: #30495e; }
  .portal-head span:nth-child(2) { text-align: center; }
  .portal-head span:last-child { text-align: right; }
  .inquiry-page h1 { font-size: 14pt; margin: .14in 0 .16in; letter-spacing: .04em; }
  .inquiry-page h2 { margin: .1in 0 .04in; padding-bottom: .025in; border-bottom: 1.5px solid #48647a; color: #556d80; font-size: 9pt; }
  .field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .1in .55in; }
  .field-grid div { display: grid; grid-template-columns: 1fr 1fr; min-height: .24in; align-items: center; }
  .field-grid label { color: #4f5960; }
  .amount-grid { width: 68%; display: grid; grid-template-columns: 1.4fr .8fr; gap: .09in; }
  .payment th, .payment td { border: 1px solid #bcc6cd; padding: 5px 7px; }
  .payment th { text-align: left; background: #edf1f3; color: #536675; }
  .certify, .schedule-note { margin-top: .28in; padding: .12in; background: #f4f6f7; border-left: 3px solid #49657b; color: #3d474e; }
  .detail { font-size: 8pt; }
  .detail th, .detail td { border: 1px solid #aeb9c1; padding: 2px 5px; height: .15in; }
  .detail th { background: #e9eef1; text-align: left; }
  .detail .line { width: .42in; text-align: right; color: #666; }
  .page-footer { position: absolute; left: .5in; right: .5in; bottom: .14in; display: flex; justify-content: space-between; border-top: 1px solid #aaa; padding-top: 3px; font-size: 6.5pt; }
"""
    return html_document(sample_id, pages, css)


def driver_schedule_html(sample_id: str, rows: list[dict[str, Any]]) -> str:
    sections = [
        ("Active commercial drivers", rows[:180], "standard"),
        ("Seasonal and relief drivers", rows[180:340], "compact"),
        ("Annual review queue", rows[340:], "review"),
    ]
    pages: list[str] = []
    page_specs: list[tuple[str, str, Sequence[dict[str, Any]], int, int]] = []
    for section_name, section_rows, style in sections:
        section_chunks = balanced_chunks(section_rows, 32 if style != "review" else 28, 22)
        for index, page_rows in enumerate(section_chunks, start=1):
            page_specs.append((section_name, style, page_rows, index, len(section_chunks)))
    pages.append(
        """<section class="page driver-cover">
  <div class="binder-tab">DRIVER QUALIFICATION</div>
  <h1>Driver Schedule and Annual MVR Review</h1>
  <p class="lead">This file contains the active driver roster, seasonal driver supplement, and the annual motor-vehicle-record review queue maintained for the current policy term.</p>
  <div class="cover-grid"><div><label>Named insured</label><b>Granite Harbor Freight, Inc.</b></div><div><label>Review period</label><b>01/01/2026 - 12/31/2026</b></div><div><label>Drivers listed</label><b>500</b></div><div><label>Roster sources</label><b>Safety system / payroll / MVR vendor</b></div></div>
  <h2>File organization</h2><p>The roster is printed in source-system order. License state and number originate in the qualification file; dates of birth are retained for MVR matching. Review status and exception notes are administrative fields and are not part of the driver schedule.</p>
  <div class="signature-block"><span>Prepared by ____________________</span><span>Reviewed ____________________</span><span>Date ____________________</span></div>
  <div class="page-footer"><span>Driver qualification file</span><span>Cover</span></div>
</section>"""
    )
    total_pages = 1 + len(page_specs)
    for output_index, (section_name, style, page_rows, section_page, section_total) in enumerate(page_specs, start=2):
        trs = []
        for line_no, row in enumerate(page_rows, start=1):
            if style == "compact":
                cells = f"<td>{h(row['state_licensed'])}</td><td>{h(row['driver_license_number'])}</td><td>{h(row['name'])}</td><td>{h(row['date_of_birth'])}</td>"
            elif style == "review":
                cells = f"<td>{line_no:03d}</td><td>{h(row['name'])}</td><td>{h(row['date_of_birth'])}</td><td>{h(row['state_licensed'])}</td><td>{h(row['driver_license_number'])}</td><td>{'Due' if line_no % 7 == 0 else ''}</td>"
            else:
                cells = f"<td>{h(row['name'])}</td><td>{h(row['state_licensed'])}</td><td>{h(row['driver_license_number'])}</td><td>{h(row['date_of_birth'])}</td>"
            trs.append(f"<tr>{cells}</tr>")
        if style == "compact":
            headers = "<th>Lic. state</th><th>License number</th><th>Driver name</th><th>Date of birth</th>"
        elif style == "review":
            headers = "<th>Seq.</th><th>Driver</th><th>DOB</th><th>State</th><th>License no.</th><th>Review</th>"
        else:
            headers = "<th>Driver name</th><th>State licensed</th><th>Driver license number</th><th>Date of birth</th>"
        roster_note = (
            "Blank review cells indicate no annual-review exception was recorded when this queue was printed."
            if style == "review"
            else "Entries are shown in source-system order as of the roster export date."
        )
        pages.append(
            f"""<section class="page driver-page {h(style)}">
  <header><div><b>Granite Harbor Freight, Inc.</b><br>Driver qualification file</div><div><h1>{h(section_name)}</h1><span>{'Continuation' if section_page > 1 else 'Roster section'}</span></div><div class="right">Policy term 2026<br>Section page {section_page} of {section_total}</div></header>
  <table><thead><tr>{headers}</tr></thead><tbody>{''.join(trs)}</tbody></table>
  <div class="roster-note">{roster_note}</div>
  {page_footer(output_index, total_pages, 'Driver schedule')}
</section>"""
        )
    css = """
  .driver-cover, .driver-page { height: 11in; padding: .48in .58in .42in; }
  .driver-cover { font-family: Georgia, 'Times New Roman', serif; }
  .binder-tab { font: 700 8pt Arial, sans-serif; letter-spacing: .12em; border-bottom: 2px solid #1f3e54; padding-bottom: .08in; }
  .driver-cover h1 { font-size: 25pt; margin: .7in 0 .28in; color: #17384d; }
  .driver-cover .lead { width: 78%; font-size: 12pt; line-height: 1.55; }
  .cover-grid { margin-top: .55in; display: grid; grid-template-columns: 1fr 1fr; border: 1px solid #60788a; }
  .cover-grid div { padding: .16in; border-right: 1px solid #a4b0b8; border-bottom: 1px solid #a4b0b8; }
  .cover-grid label { display: block; font: 7pt Arial, sans-serif; text-transform: uppercase; color: #5c6d78; }
  .driver-cover h2 { margin-top: .55in; font-size: 14pt; }
  .driver-cover p { line-height: 1.5; }
  .signature-block { margin-top: .75in; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: .25in; font-size: 9pt; }
  .driver-page header { display: grid; grid-template-columns: 1fr 1.5fr 1fr; margin-bottom: .13in; font-size: 7.5pt; }
  .driver-page header h1 { margin: 0; font-size: 14pt; text-align: center; }
  .driver-page header > div:nth-child(2) { text-align: center; }
  .right { text-align: right; }
  .driver-page table { font-size: 8.2pt; }
  .driver-page th { border-top: 2px solid #223f53; border-bottom: 1px solid #223f53; background: #e9eef1; padding: 5px 6px; text-align: left; }
  .driver-page td { border-bottom: 1px solid #c4cbd0; padding: 4px 6px; height: .25in; }
  .driver-page.compact td { height: .255in; }
  .driver-page.review td { height: .285in; }
  .roster-note { margin-top: .12in; font-size: 7pt; color: #555; }
  .page-footer { position: absolute; left: .58in; right: .58in; bottom: .15in; display: flex; justify-content: space-between; border-top: 1px solid #999; padding-top: 3px; font-size: 6.5pt; }
"""
    return html_document(sample_id, pages, css)


def vehicle_schedule_html(sample_id: str, rows: list[dict[str, Any]], variant: int) -> str:
    company = COMPANIES[5 + variant]
    section_sizes = [280, 260, len(rows) - 540]
    labels = ["Power units and straight trucks", "Trailers and intermodal equipment", "Supplemental scheduled autos"]
    page_specs: list[tuple[str, int, int, Sequence[dict[str, Any]], int]] = []
    cursor = 0
    for section_index, (section_size, label) in enumerate(zip(section_sizes, labels), start=1):
        section_rows = rows[cursor : cursor + section_size]
        cursor += section_size
        section_chunks = balanced_chunks(section_rows, 37, 30)
        for section_page, page_rows in enumerate(section_chunks, start=1):
            page_specs.append((label, section_page, len(section_chunks), page_rows, section_index))
    pages: list[str] = []
    total_pages = 1 + len(page_specs)
    pages.append(
        f"""<section class="page vehicle-cover variant-{variant}">
  <div class="schedule-label">COMMERCIAL AUTO</div><h1>Schedule of Covered Autos</h1>
  <div class="policy-grid"><div><label>Named insured</label><b>{h(company)}</b></div><div><label>Policy number</label><b>CA-{781200 + variant * 421}</b></div><div><label>Policy period</label><b>04/01/2026 - 04/01/2027</b></div><div><label>Scheduled units</label><b>800</b></div></div>
  <p>This schedule lists power units, trailers, and supplemental autos reported for the policy term. Blank company-unit or plate fields reflect the source fleet schedule and do not remove the vehicle from the policy schedule.</p>
  <h2>Schedule sections</h2><table class="section-index"><tr><td>1</td><td>Power units and straight trucks</td><td>280 units</td></tr><tr><td>2</td><td>Trailers and intermodal equipment</td><td>260 units</td></tr><tr><td>3</td><td>Supplemental scheduled autos</td><td>260 units</td></tr></table>
  <div class="form-note">Changes made after the effective date are shown on the applicable endorsement and may not appear on this print date.</div>
  {page_footer(1, total_pages, 'Commercial auto schedule')}
</section>"""
    )
    for output_page, (label, section_page, section_total, page_rows, section_index) in enumerate(page_specs, start=2):
        trs = []
        for row in page_rows:
            if section_index == 2 and variant == 2:
                cells = f"<td>{h(row['company_vehicle_number'])}</td><td>{h(row['veh_number'])}</td><td>{h(row['body_type'])}</td><td>{h(row['make'])}</td><td>{h(row['model'])}</td><td>{h(row['year'])}</td><td>{h(row['plate_number'])}</td>"
            else:
                cells = f"<td>{h(row['veh_number'])}</td><td>{h(row['company_vehicle_number'])}</td><td>{h(row['plate_number'])}</td><td>{h(row['year'])}</td><td>{h(row['make'])}</td><td>{h(row['model'])}</td><td>{h(row['body_type'])}</td>"
            trs.append(f"<tr>{cells}</tr>")
        if section_index == 2 and variant == 2:
            headers = "<th>Company unit</th><th>Schedule no.</th><th>Equipment type</th><th>Make</th><th>Model</th><th>Year</th><th>Plate</th>"
        else:
            headers = "<th>Veh. no.</th><th>Company unit</th><th>Plate no.</th><th>Year</th><th>Make</th><th>Model</th><th>Body type</th>"
        pages.append(
            f"""<section class="page vehicle-page variant-{variant}">
  <header><div><b>{h(company)}</b><br>Policy CA-{781200 + variant * 421}</div><div><h1>{h(label)}</h1><span>{'Continuation' if section_page > 1 else 'Schedule section ' + str(section_index)}</span></div><div class="right">Effective 04/01/2026<br>{section_page} of {section_total}</div></header>
  <table><thead><tr>{headers}</tr></thead><tbody>{''.join(trs)}</tbody></table>
  <div class="schedule-note">Vehicle symbols and coverage terms are shown in the declarations. This schedule identifies the autos reported for rating.</div>
  {page_footer(output_page, total_pages, 'Schedule of covered autos')}
</section>"""
        )
    css = """
  .vehicle-cover, .vehicle-page { height: 8.5in; padding: .36in .45in .34in; }
  .schedule-label { border-bottom: 2px solid #222; padding-bottom: .06in; font-size: 8pt; font-weight: 700; letter-spacing: .12em; }
  .vehicle-cover h1 { margin: .42in 0 .2in; font-size: 25pt; }
  .policy-grid { display: grid; grid-template-columns: 1.5fr 1fr 1fr .6fr; border: 1px solid #555; }
  .policy-grid div { padding: .12in; border-right: 1px solid #aaa; }
  .policy-grid label { display: block; font-size: 6.5pt; text-transform: uppercase; color: #555; }
  .vehicle-cover p { margin: .35in 0; width: 82%; font: 11pt/1.45 Georgia, serif; }
  .vehicle-cover h2 { margin-top: .3in; font-size: 13pt; }
  .section-index { width: 72%; }
  .section-index td { border-bottom: 1px solid #aaa; padding: .09in; }
  .form-note { margin-top: .4in; border: 1px solid #777; padding: .12in; width: 78%; font-size: 8pt; }
  .vehicle-page header { display: grid; grid-template-columns: 1fr 1.8fr 1fr; font-size: 7pt; margin-bottom: .1in; }
  .vehicle-page header h1 { margin: 0; text-align: center; font-size: 13pt; }
  .vehicle-page header > div:nth-child(2) { text-align: center; }
  .right { text-align: right; }
  .vehicle-page table { table-layout: fixed; font-size: 7.2pt; }
  .vehicle-page th { border: 1px solid #666; padding: 4px 5px; text-align: left; background: #e8eaeb; }
  .vehicle-page td { border: 1px solid #aaa; padding: 3px 5px; height: .168in; }
  .vehicle-page.variant-2 tbody tr:nth-child(5n) td { border-bottom: 1.5px solid #555; }
  .schedule-note { margin-top: .08in; font-size: 6.5pt; color: #444; }
  .page-footer { position: absolute; left: .45in; right: .45in; bottom: .13in; display: flex; justify-content: space-between; border-top: 1px solid #999; padding-top: 3px; font-size: 6.5pt; }
"""
    return html_document(sample_id, pages, css, landscape=True)


def build_documents(output_dir: Path) -> list[dict[str, Any]]:
    html_dir = output_dir / "html"
    pdf_dir = output_dir / "pdfs"
    gt_dir = output_dir / "ground_truth"
    for directory in (html_dir, pdf_dir, gt_dir):
        directory.mkdir(parents=True, exist_ok=True)

    documents: list[dict[str, Any]] = []

    for index in range(1, 9):
        sample_id = f"ifta_mileage_by_vehicle_{index:03d}"
        rows = read_rows(sample_id)
        documents.append({"sample_id": sample_id, "family": "ifta_mileage", "rows": rows, "html": mileage_html(sample_id, rows, index)})

    for index in RETAINED_RETURN_VARIANTS:
        sample_id = f"ifta_return_schedule_{index:03d}"
        rows = read_rows(sample_id)
        documents.append({"sample_id": sample_id, "family": "ifta_return", "rows": rows, "html": return_schedule_html(sample_id, rows, index)})

    for index in RETAINED_TAX_SUMMARY_VARIANTS:
        sample_id = f"ifta_tax_summary_{index:03d}"
        rows = read_rows(sample_id)
        documents.append({"sample_id": sample_id, "family": "ifta_tax_summary", "rows": rows, "html": tax_summary_html(sample_id, rows, index)})

    for index in range(1, 3):
        sample_id = f"ifta_tax_inquiry_{index:03d}"
        rows = rewrite_tax_inquiry_rows(read_rows(sample_id))
        documents.append({"sample_id": sample_id, "family": "ifta_tax_inquiry", "rows": rows, "html": tax_inquiry_html(sample_id, rows, index), "ground_truth_changed": True})

    sample_id = "driver_schedule_sparse_001"
    rows = read_rows(sample_id)
    documents.append({"sample_id": sample_id, "family": "driver_schedule", "rows": rows, "html": driver_schedule_html(sample_id, rows)})

    for index in range(1, 3):
        sample_id = f"vehicle_schedule_sparse_{index:03d}"
        rows = read_rows(sample_id)
        documents.append({"sample_id": sample_id, "family": "vehicle_schedule", "rows": rows, "html": vehicle_schedule_html(sample_id, rows, index)})

    for document in documents:
        sample_id = document["sample_id"]
        (html_dir / f"{sample_id}.html").write_text(document["html"], encoding="utf-8")
        (gt_dir / f"{sample_id}.json").write_text(json.dumps(document["rows"], indent=2) + "\n", encoding="utf-8")
        document["html_path"] = html_dir / f"{sample_id}.html"
        document["pdf_path"] = pdf_dir / f"{sample_id}.pdf"
    return documents


async def render_documents(documents: Sequence[dict[str, Any]]) -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        for document in documents:
            await page.set_content(document["html"], wait_until="load")
            await page.emulate_media(media="print")
            await page.pdf(
                path=str(document["pdf_path"]),
                prefer_css_page_size=True,
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            print(f"rendered {document['sample_id']}")
        await browser.close()


def write_summary(output_dir: Path, documents: Sequence[dict[str, Any]]) -> None:
    summary = {
        "purpose": "Reproducible rendering of synthetic operational documents",
        "source": str(DATA_DIR.relative_to(REPO_ROOT) / "ground_truth"),
        "documents": [
            {
                "sample_id": document["sample_id"],
                "family": document["family"],
                "target_records": len(document["rows"]),
                "ground_truth_changed": bool(document.get("ground_truth_changed")),
            }
            for document in documents
        ],
    }
    (output_dir / "REVIEW_MANIFEST.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Synthetic Operational Document Render",
        "",
        "These PDFs are visual-review candidates. OCR and agent extraction have not been rerun.",
        "All values come from the committed synthetic ground truth. The two tax-inquiry files replace artificial `jurisdiction row N` labels with realistic Schedule B field labels while preserving 650 records per document.",
        "",
        "| Family | Documents | Records |",
        "|---|---:|---:|",
    ]
    family_counts: OrderedDict[str, list[int]] = OrderedDict()
    for document in documents:
        values = family_counts.setdefault(document["family"], [0, 0])
        values[0] += 1
        values[1] += len(document["rows"])
    for family, (count, records) in family_counts.items():
        lines.append(f"| `{family}` | {count} | {records:,} |")
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-render", action="store_true")
    return parser.parse_args()


def main() -> None:
    global DATA_DIR
    args = parse_args()
    DATA_DIR = args.data_dir.resolve()
    documents = build_documents(args.output)
    write_summary(args.output, documents)
    if not args.no_render:
        asyncio.run(render_documents(documents))


if __name__ == "__main__":
    main()
