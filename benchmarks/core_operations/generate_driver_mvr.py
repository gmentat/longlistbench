#!/usr/bin/env python3
"""Generate synthetic driver rosters with sparse MVR report enrichment."""

from __future__ import annotations

import argparse
import asyncio
import json
from html import escape
from pathlib import Path
import random
from typing import Any, Sequence

from playwright.async_api import async_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tmp" / "core_operations" / "driver_mvr"
SAMPLE_IDS = (
    "driver_mvr_packet_001",
    "driver_mvr_packet_002",
    "driver_mvr_packet_003",
)
COMPANIES = {
    "driver_mvr_packet_001": "Crescent Basin Transport, Inc.",
    "driver_mvr_packet_002": "Harbor Ridge Logistics, LLC",
    "driver_mvr_packet_003": "Prairie Route Carriers, Inc.",
}
SAMPLE_CONFIGS = {
    "driver_mvr_packet_001": {
        "seed": 3303,
        "record_count": 260,
        "first_name_offset": 0,
        "last_name_offset": 0,
    },
    "driver_mvr_packet_002": {
        "seed": 3302,
        "record_count": 500,
        "first_name_offset": 11,
        "last_name_offset": 19,
    },
    "driver_mvr_packet_003": {
        "seed": 3303,
        "record_count": 500,
        "first_name_offset": 22,
        "last_name_offset": 38,
    },
}
FIRST_NAMES = (
    "Rosa", "Caleb", "Nina", "Andre", "Priya", "Jonah", "Maya", "Arman",
    "Tessa", "Reed", "Clara", "Elias", "Farah", "Sonia", "Lucian", "Greta",
    "Noemi", "Cecilia", "Marcus", "Avery", "Daphne", "Theo", "Lina", "Rafael",
    "Mira", "Omar", "Selena", "Julian", "Iris", "Devon", "Alma", "Mateo",
    "Renee", "Silas", "Vera", "Adrian", "Lena", "Kai", "Mina", "Nolan",
    "Marta", "Ibrahim", "Elena", "Victor", "Leah", "Samir", "Daria", "Owen",
    "Anika", "Milan",
)
LAST_NAMES = (
    "Nguyen", "Nassar", "Walsh", "Mensah", "Torres", "Duarte", "Hayes",
    "Haddad", "Santos", "Kaminski", "Chen", "Serrano", "Diaz", "Bauer",
    "Sawyer", "Soto", "Velasquez", "Talbot", "Bishop", "Ortega", "Farrell",
    "Madsen", "Price", "Parker", "Singh", "Carver", "Abbott", "Vargas",
    "Novak", "Kovacs", "Kline", "Malik", "Arias", "Markovic", "Ilyin",
    "Romano", "Patel", "Rossi", "Sorensen", "Yu", "Tan", "Moreno", "Petrov",
    "Foster", "Quinn", "Kim", "Bennett", "Navarro", "Holt", "Coleman",
    "Okafor", "Barrera", "Wynn", "Hughes", "Gallagher", "Lambert", "Mendez",
    "Rivera", "Reyes", "Rahman",
)
STATE_CODES = (
    "AL", "AZ", "AR", "CA", "CO", "FL", "GA", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "MD", "MI", "MN", "MS", "MO", "MT", "NE", "NV",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "SC", "TN", "TX",
    "UT", "VA", "WA", "WV", "WY",
)
VIOLATIONS = (
    "None",
    "Speeding - 2024-11-04",
    "Lane violation - 2023-08-17",
    "Failure to obey traffic control - 2022-05-29",
    "Unsafe following distance - 2025-02-08",
)
REPORT_COUNT = 8


def h(value: object) -> str:
    return escape("" if value is None else str(value))


def report_indices(record_count: int, report_count: int = REPORT_COUNT) -> tuple[int, ...]:
    """Spread the sparse reports across the full roster deterministically."""
    if record_count < report_count:
        raise ValueError("report count cannot exceed the roster size")
    if report_count == 1:
        return (record_count // 2,)
    return tuple(
        round(index * (record_count - 1) / (report_count - 1))
        for index in range(report_count)
    )


def make_driver_rows(sample_id: str) -> list[dict[str, Any]]:
    """Generate the complete synthetic roster before sparse report selection."""
    config = SAMPLE_CONFIGS[sample_id]
    rng = random.Random(config["seed"])
    rows: list[dict[str, Any]] = []
    for index in range(config["record_count"]):
        state = rng.choice(STATE_CODES)
        birth_year = rng.randint(1968, 1998)
        hire_year = rng.randint(2014, 2025)
        violation = rng.choice(VIOLATIONS)
        accidents = "0"
        if rng.random() < 0.18:
            accidents = (
                f"1 - {rng.randint(2021, 2025)}-"
                f"{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"
            )
        first_name = FIRST_NAMES[
            (index + config["first_name_offset"]) % len(FIRST_NAMES)
        ]
        last_name = LAST_NAMES[
            (index + config["last_name_offset"]) % len(LAST_NAMES)
        ]
        rows.append(
            {
                "name": f"{first_name} {last_name}",
                "state_licensed": state,
                "license_number": (
                    f"{state} {rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{100 + index:03d} "
                    f"{200 + (index * 37) % 800:03d} "
                    f"{300 + (index * 53) % 700:03d}"
                ),
                "date_of_birth": (
                    f"{rng.randint(1, 12):02d}/{rng.randint(1, 28):02d}/{birth_year}"
                ),
                "date_hired": (
                    f"{rng.randint(1, 12):02d}/{rng.randint(1, 28):02d}/{hire_year}"
                ),
                "years_experienced": max(
                    1,
                    2026 - birth_year - rng.randint(21, 28),
                ),
                "mvr_run_date": f"01/{rng.randint(10, 28):02d}/2026",
                "license_class": rng.choice(("A", "A", "A", "B")),
                "accidents_last_5_years": accidents,
                "mvr_violations": violation,
            }
        )
    return rows


def sparse_ground_truth(
    rows: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected = set(report_indices(len(rows)))
    output: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []
    for index, source in enumerate(rows):
        row = dict(source)
        if index in selected:
            reports.append(row)
        else:
            row["accidents_last_5_years"] = None
            row["mvr_violations"] = None
        output.append(row)
    return output, reports


def html_document(sample_id: str, company: str, rows: list[dict], reports: list[dict]) -> str:
    request_rows = []
    for row in reports:
        identifier = str(row["license_number"]).removeprefix(f"{row['state_licensed']} ")
        request_rows.append(
            "<tr>"
            "<td>Certified driving record</td>"
            f"<td>{h(row['state_licensed'])}</td>"
            f"<td>{h(identifier)}</td>"
            f"<td>{h(row['mvr_run_date'])}</td>"
            "<td class='num'>$16.00</td>"
            "</tr>"
        )

    pages = [
        f"""<section class="page request-page">
  <div class="agency-mark">MVR</div>
  <div class="agency-title">MOTOR VEHICLE RECORDS BUREAU<br>EMPLOYER SERVICES UNIT</div>
  <div class="recipient">ATTN: SAFETY OPERATIONS<br>{h(company).upper()}<br>3188 ALDER RIDGE BLVD<br>GRAND RAPIDS MI 49503-1072</div>
  <div class="case-lines"><b>Issue date:</b> 01/22/2026<br><b>Batch reference:</b> MVR-2026-01-{h(sample_id[-3:])}</div>
  <h1>Report of Services Provided</h1>
  <p>This report identifies the certified driving records included in this packet.</p>
  <table class="request-table"><thead><tr><th>Inquiry</th><th>State</th><th>License identifier</th><th>Run date</th><th>Amount</th></tr></thead><tbody>{''.join(request_rows)}</tbody></table>
  <div class="request-note">INFORMATIONAL COPY - NO PAYMENT DUE</div>
  <div class="request-foot">Employer Services Unit | records@example.invalid | 517-555-0138<br>Packet summary</div>
</section>"""
    ]

    roster_chunks = [rows[index : index + 34] for index in range(0, len(rows), 34)]
    for page_number, chunk in enumerate(roster_chunks, start=1):
        body = []
        for row in chunk:
            body.append(
                "<tr>"
                f"<td>{h(row['name'])}</td>"
                f"<td>{h(row['state_licensed'])}</td>"
                f"<td>{h(row['license_number'])}</td>"
                f"<td>{h(row['date_of_birth'])}</td>"
                f"<td>{h(row['date_hired'])}</td>"
                f"<td class='center'>{h(row['years_experienced'])}</td>"
                f"<td>{h(row['mvr_run_date'])}</td>"
                f"<td class='center'>{h(row['license_class'])}</td>"
                "</tr>"
            )
        pages.append(
            f"""<section class="page roster-page">
  <header><div>Driver qualification system</div><div>Driver Schedule Export</div><div>06/11/2026 20:42</div></header>
  <h1>Driver Schedule</h1>
  <div class="roster-meta"><b>{h(company)}</b><br>Review period: 01/01/2026 - 01/01/2027 | Drivers: {len(rows)}</div>
  <table class="driver-table"><thead><tr><th>Name</th><th>State</th><th>Driver license number</th><th>Date of birth</th><th>Date hired</th><th>Years exp.</th><th>MVR run date</th><th>Class</th></tr></thead><tbody>{''.join(body)}</tbody></table>
  <footer><span>Driver schedule</span><span>Page {page_number} of {len(roster_chunks)}</span></footer>
</section>"""
        )

    for report_number, row in enumerate(reports, start=1):
        identifier = str(row["license_number"]).removeprefix(f"{row['state_licensed']} ")
        pages.append(
            f"""<section class="page report-page">
  <div class="report-agency">MOTOR VEHICLE RECORDS BUREAU<br>EMPLOYER SERVICES UNIT</div>
  <h1>Certified Employer Driving Record</h1>
  <div class="report-ref">Record {report_number} of {len(reports)} | {h(row['state_licensed'])} {h(identifier)} | Run {h(row['mvr_run_date'])}</div>
  <h2>Driver identification</h2>
  <div class="grid three"><div><label>Full name</label>{h(row['name']).upper()}</div><div><label>Date of birth</label>{h(row['date_of_birth'])}</div><div><label>License class</label>{h(row['license_class'])}</div></div>
  <h2>Credential</h2>
  <div class="grid four"><div><label>Jurisdiction</label>{h(row['state_licensed'])}</div><div><label>License number</label>{h(row['license_number'])}</div><div><label>Status</label>Valid</div><div><label>Record type</label>Employer certified</div></div>
  <h2>Five-year activity</h2>
  <table class="activity"><tr><th>Accidents</th><td>{h(row['accidents_last_5_years'])}</td></tr><tr><th>Moving violations</th><td>{h(row['mvr_violations'])}</td></tr></table>
  <div class="certification">Electronically certified for the employer request shown in this packet.</div>
  <footer><span>Certified driving record</span><span>Summary page 1 of 1</span></footer>
</section>"""
        )

    css = """
  @page { size: A4 portrait; margin: 0; }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; color: #111; font-family: Arial, Helvetica, sans-serif; }
  .page { position: relative; width: 100%; height: 11.69in; page-break-after: always; overflow: hidden; }
  .page:last-child { page-break-after: auto; }
  table { width: 100%; border-collapse: collapse; }
  .request-page { padding: .62in .72in .45in; font-size: 10pt; }
  .agency-mark { margin: 0 auto .08in; width: .62in; height: .62in; border: 2px solid #24485e; border-radius: 50%; display: grid; place-items: center; font-weight: 700; color: #24485e; }
  .agency-title, .report-agency { text-align: center; font-family: Georgia, serif; font-weight: 700; line-height: 1.3; }
  .recipient { float: right; width: 3.25in; margin-top: .45in; line-height: 1.25; }
  .case-lines { clear: both; padding-top: .3in; line-height: 1.5; }
  .request-page h1 { margin: .28in 0 .08in; font: 700 16pt Georgia, serif; }
  .request-table { margin-top: .18in; font-size: 8.5pt; }
  .request-table th { border-bottom: 2px solid #333; text-align: left; padding: 5px; }
  .request-table td { border-bottom: 1px solid #aaa; padding: 6px 5px; }
  .num { text-align: right; }
  .request-note { margin-top: .3in; text-align: center; font-weight: 700; }
  .request-foot { position: absolute; left: .72in; right: .72in; bottom: .35in; border-top: 1px solid #777; padding-top: 5px; text-align: center; font-size: 8pt; }
  .roster-page { padding: .35in .42in .38in; }
  .roster-page header { display: grid; grid-template-columns: 1fr 1fr 1fr; font-size: 7pt; color: #555; }
  .roster-page header div:nth-child(2) { text-align: center; }
  .roster-page header div:last-child { text-align: right; }
  .roster-page h1 { margin: .12in 0 .05in; font-size: 17pt; }
  .roster-meta { margin-bottom: .1in; font-size: 8.5pt; line-height: 1.35; }
  .driver-table { font-size: 7.1pt; }
  .driver-table th { border: 1px solid #555; padding: 4px; text-align: left; background: #edf1f3; }
  .driver-table td { border: 1px solid #999; padding: 3px 4px; height: .222in; }
  .center { text-align: center; }
  footer { position: absolute; left: .42in; right: .42in; bottom: .15in; display: flex; justify-content: space-between; border-top: 1px solid #888; padding-top: 4px; font-size: 7pt; }
  .report-page { padding: .72in .7in .5in; font-size: 11pt; }
  .report-page h1 { margin: .45in 0 .08in; text-align: center; font: 700 18pt Georgia, serif; }
  .report-ref { text-align: center; border-bottom: 2px solid #222; padding-bottom: .16in; }
  .report-page h2 { margin: .42in 0 .1in; border-bottom: 2px solid #222; font-size: 12pt; text-transform: uppercase; letter-spacing: .03em; }
  .grid { display: grid; gap: .12in; }
  .grid.three { grid-template-columns: 2fr 1fr 1fr; }
  .grid.four { grid-template-columns: repeat(4, 1fr); }
  .grid div { border: 1px solid #aaa; padding: .12in; min-height: .65in; }
  label { display: block; margin-bottom: .07in; color: #5b6870; font-size: 8pt; text-transform: uppercase; }
  .activity th, .activity td { border: 1px solid #777; padding: .16in; text-align: left; }
  .activity th { width: 2in; background: #edf1f3; }
  .certification { margin-top: .55in; padding: .16in; border: 1px solid #777; text-align: center; }
"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{h(sample_id)}</title><style>{css}</style></head><body>{''.join(pages)}</body></html>"


async def render_pdf(html: str, pdf_path: Path) -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="load")
        await page.emulate_media(media="print")
        await page.pdf(
            path=str(pdf_path),
            prefer_css_page_size=True,
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        await browser.close()


async def generate_sample(output_dir: Path, sample_id: str, render: bool) -> None:
    rows, reports = sparse_ground_truth(make_driver_rows(sample_id))
    html = html_document(sample_id, COMPANIES[sample_id], rows, reports)

    html_dir = output_dir / "html"
    ground_truth_dir = output_dir / "ground_truth"
    pdf_dir = output_dir / "pdfs"
    for directory in (html_dir, ground_truth_dir, pdf_dir):
        directory.mkdir(parents=True, exist_ok=True)
    (html_dir / f"{sample_id}.html").write_text(html, encoding="utf-8")
    (ground_truth_dir / f"{sample_id}.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if render:
        await render_pdf(html, pdf_dir / f"{sample_id}.pdf")
    print(f"generated {sample_id}: {len(rows)} drivers, {len(reports)} MVR reports")


async def generate(output_dir: Path, sample_ids: Sequence[str], render: bool) -> None:
    for sample_id in sample_ids:
        if sample_id not in SAMPLE_IDS:
            raise ValueError(f"Unknown driver/MVR sample: {sample_id}")
        await generate_sample(output_dir, sample_id, render)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--samples", nargs="+", choices=SAMPLE_IDS, default=list(SAMPLE_IDS))
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args()
    asyncio.run(generate(args.output_dir, args.samples, not args.no_render))


if __name__ == "__main__":
    main()
