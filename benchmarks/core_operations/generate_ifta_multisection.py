#!/usr/bin/env python3
"""Generate deterministic synthetic IFTA multi-section return packets."""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageOps
from playwright.async_api import async_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]


STATE_NAMES = {
    "AL": "Alabama",
    "AR": "Arkansas",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "FL": "Florida",
    "GA": "Georgia",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MD": "Maryland",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MS": "Mississippi",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}


@dataclass(frozen=True)
class IftaRecord:
    return_id: str
    filing_year: int
    quarter: str
    filing_type: str
    jurisdiction: str
    fuel_type: str
    total_miles: int
    taxable_miles: int
    taxable_gallons: int
    tax_paid_gallons: int
    net_gallons: int
    tax_rate: float
    tax_due_refund: float
    surtax_due: float
    interest_due: float
    total_due_refund: float


def h(value: object) -> str:
    return escape(str(value), quote=True)


def money(value: float) -> str:
    if value < 0:
        return f"(${abs(value):,.2f})"
    return f"${value:,.2f}"


def intfmt(value: int) -> str:
    return f"{value:,}"


def make_records(seed: int, returns: int) -> list[IftaRecord]:
    rng = random.Random(seed)
    codes = list(STATE_NAMES)
    records: list[IftaRecord] = []
    for ret_idx in range(returns):
        year = 2023 + (ret_idx % 4)
        quarter = f"Q{ret_idx % 4 + 1}"
        filing_type = "Amended" if ret_idx % 5 in {2, 4} else "Original"
        return_id = f"RTN-{year}-{quarter}-{seed % 97:02d}-{ret_idx + 1:03d}"
        selected = codes[:]
        rng.shuffle(selected)
        selected = selected[: rng.randint(31, 36)]
        # Keep some repeated-state order patterns across returns.
        if ret_idx % 3 == 0:
            selected = sorted(selected)
        for code in selected:
            total_miles = rng.randint(420, 285_000)
            taxable_miles = max(0, total_miles - rng.randint(0, min(total_miles, 950)))
            taxable_gallons = max(1, round(taxable_miles / rng.uniform(5.3, 8.4)))
            if rng.random() < 0.35:
                tax_paid_gallons = rng.randint(0, taxable_gallons * 2)
            else:
                tax_paid_gallons = 0
            net_gallons = taxable_gallons - tax_paid_gallons
            rate = round(rng.uniform(0.165, 0.765), 4)
            tax_due = round(net_gallons * rate, 2)
            surtax = 0.0 if rng.random() < 0.76 else round(abs(tax_due) * rng.uniform(0.015, 0.085), 2)
            interest = 0.0 if rng.random() < 0.86 else round(abs(tax_due) * rng.uniform(0.004, 0.021), 2)
            records.append(
                IftaRecord(
                    return_id=return_id,
                    filing_year=year,
                    quarter=quarter,
                    filing_type=filing_type,
                    jurisdiction=code,
                    fuel_type="DI",
                    total_miles=total_miles,
                    taxable_miles=taxable_miles,
                    taxable_gallons=taxable_gallons,
                    tax_paid_gallons=tax_paid_gallons,
                    net_gallons=net_gallons,
                    tax_rate=rate,
                    tax_due_refund=tax_due,
                    surtax_due=surtax,
                    interest_due=interest,
                    total_due_refund=round(tax_due + surtax + interest, 2),
                )
            )
    return records


def group_by_return(records: list[IftaRecord]) -> list[tuple[str, list[IftaRecord]]]:
    groups: dict[str, list[IftaRecord]] = {}
    for record in records:
        groups.setdefault(record.return_id, []).append(record)
    return list(groups.items())


def header(record: IftaRecord, page_label: str, page_no: int) -> str:
    return f"""
    <div class="topbar">
      <div><b>International Fuel Tax Agreement Return</b><br><span>Account: SYN-{record.filing_year}-{record.return_id[-3:]}</span></div>
      <div class="center"><b>{h(record.return_id)}</b><br>{h(record.filing_type)} return - {record.filing_year} {h(record.quarter)}</div>
      <div class="right">Page {page_no}<br>{h(page_label)}</div>
    </div>
    """


def render_financial_page(record: IftaRecord, rows: list[IftaRecord], page_no: int) -> str:
    total_due = sum(r.total_due_refund for r in rows)
    tax_due = sum(r.tax_due_refund for r in rows)
    interest = sum(r.interest_due for r in rows)
    surtax = sum(r.surtax_due for r in rows)
    vehicles = 7 + (len(rows) % 13)
    return f"""
    <section class="page">
      {header(record, "return summary", page_no)}
      <h1>IFTA Return Summary</h1>
      <div class="summary-grid">
        <div><span>Legal name</span><b>{h(company_name(record.return_id))}</b></div>
        <div><span>License year</span><b>{record.filing_year}</b></div>
        <div><span>Quarter ending</span><b>{h(record.quarter)}</b></div>
        <div><span>Fuel type</span><b>Diesel (DI)</b></div>
        <div><span>Filing status</span><b>{h(record.filing_type)}</b></div>
        <div><span>Return id</span><b>{h(record.return_id)}</b></div>
      </div>
      <table class="line-items">
        <tbody>
          <tr><td>Total jurisdiction tax due or credit</td><td>{money(tax_due)}</td></tr>
          <tr><td>Surtax and additional jurisdiction charges</td><td>{money(surtax)}</td></tr>
          <tr><td>Interest assessed on late or amended filings</td><td>{money(interest)}</td></tr>
          <tr><td>Vehicles reported for this return</td><td>{vehicles}</td></tr>
          <tr><td>Balance due or refund carried to payment screen</td><td>{money(total_due)}</td></tr>
        </tbody>
      </table>
      <p class="notice">The following schedules were printed from separate portal views and retained with the filed return package. Review totals against the quarter, fuel type, and return id shown above.</p>
    </section>
    """


def render_schedule_a(record: IftaRecord, rows: list[IftaRecord], page_no: int) -> str:
    chunks = [rows[i : i + 18] for i in range(0, len(rows), 18)]
    pages = []
    for chunk_idx, chunk in enumerate(chunks):
        body = []
        for idx, r in enumerate(chunk, start=1 + chunk_idx * 18):
            note = "" if idx % 5 else "<br><span class=\"muted\">manual trip-sheet adjustment retained</span>"
            body.append(
                f"<tr><td>{idx:02d}</td><td>{h(STATE_NAMES[r.jurisdiction])}<br><b>{r.jurisdiction}</b>{note}</td>"
                f"<td class=\"num\">{intfmt(r.total_miles)}</td><td class=\"num\">{intfmt(r.taxable_miles)}</td>"
                f"<td class=\"num\">{intfmt(r.taxable_gallons)}</td><td class=\"num\">{intfmt(r.tax_paid_gallons)}</td></tr>"
            )
        pages.append(
            f"""
            <section class="page">
              {header(record, f"Schedule A {'continued' if chunk_idx else 'distance/gallons'}", page_no + chunk_idx)}
              <h1>Schedule A - Distance And Gallons</h1>
              <table class="schedule miles">
                <thead><tr><th>No.</th><th>Jurisdiction</th><th>Total miles</th><th>Taxable miles</th><th>Taxable gallons</th><th>Tax paid gallons</th></tr></thead>
                <tbody>{''.join(body)}</tbody>
              </table>
              <div class="footnote">Schedule continues for the return shown in the header. Blank states are omitted when no distance was reported.</div>
            </section>
            """
        )
    return "".join(pages)


def render_jurisdiction_tax_detail(
    record: IftaRecord,
    rows: list[IftaRecord],
    page_no: int,
    *,
    split_supplemental_rows: bool = False,
) -> str:
    ordered = rows[:]
    random.Random(record.return_id).shuffle(ordered)
    rows_per_page = 18 if split_supplemental_rows else 24
    chunks = [ordered[i : i + rows_per_page] for i in range(0, len(ordered), rows_per_page)]
    pages = []
    for chunk_idx, chunk in enumerate(chunks):
        body = []
        for idx, r in enumerate(chunk, start=1 + chunk_idx * rows_per_page):
            split_surtax = split_supplemental_rows and r.surtax_due != 0.0
            split_interest = split_supplemental_rows and r.interest_due != 0.0 and idx % 3 == 0
            base_interest = 0.0 if split_interest else r.interest_due
            base_total = round(r.tax_due_refund + base_interest, 2)
            body.append(
                f"<tr><td>{idx:02d}</td><td>{r.jurisdiction}</td><td>{h(STATE_NAMES[r.jurisdiction])}</td>"
                f"<td>{h(r.fuel_type)}</td><td class=\"num\">{r.tax_rate:.4f}</td>"
                f"<td class=\"num\">{intfmt(r.net_gallons)}</td><td class=\"num\">{money(r.tax_due_refund)}</td>"
                f"<td class=\"num\">{money(0.0) if split_surtax else money(r.surtax_due)}</td>"
                f"<td class=\"num\">{money(base_interest)}</td>"
                f"<td class=\"num\">{money(base_total if (split_surtax or split_interest) else r.total_due_refund)}</td></tr>"
            )
            if split_surtax:
                body.append(
                    f"<tr class=\"supplemental\"><td></td><td>{r.jurisdiction}</td><td>Surchg</td>"
                    f"<td>{h(r.fuel_type)}</td><td class=\"num\"></td><td class=\"num\"></td>"
                    f"<td class=\"num\"></td><td class=\"num\">{money(r.surtax_due)}</td>"
                    f"<td class=\"num\"></td><td class=\"num\">{money(r.surtax_due)}</td></tr>"
                )
            if split_interest:
                body.append(
                    f"<tr class=\"supplemental\"><td></td><td>{r.jurisdiction}</td><td>Interest adj</td>"
                    f"<td>{h(r.fuel_type)}</td><td class=\"num\"></td><td class=\"num\"></td>"
                    f"<td class=\"num\"></td><td class=\"num\"></td>"
                    f"<td class=\"num\">{money(r.interest_due)}</td><td class=\"num\">{money(r.interest_due)}</td></tr>"
                )
        reconciliation = ""
        if chunk_idx == len(chunks) - 1:
            reconciliation = f"""
              <table class="reconciliation">
                <tbody>
                  <tr><td>Total tax due or credit</td><td>{money(sum(r.tax_due_refund for r in rows))}</td></tr>
                  <tr><td>Surcharge and supplemental jurisdiction charges</td><td>{money(sum(r.surtax_due for r in rows))}</td></tr>
                  <tr><td>Interest due</td><td>{money(sum(r.interest_due for r in rows))}</td></tr>
                  <tr><td>Total amount carried to return summary</td><td>{money(sum(r.total_due_refund for r in rows))}</td></tr>
                </tbody>
              </table>
            """
        pages.append(
            f"""
            <section class="page">
              {header(record, f"Jurisdictions {'continued' if chunk_idx else 'tax detail'}", page_no + chunk_idx)}
              <h1>Jurisdictions</h1>
              <table class="schedule jurisdiction-tax">
                <thead>
                  <tr>
                    <th>No.</th><th>D1 Jur</th><th>Jurisdiction Name</th><th>D2 Fuel</th><th>D3 Tax Rate</th>
                    <th>D8 Net Tax Gal.</th><th>D9 Tax Due/(Credit)</th><th>Surtax/Fees</th><th>D10 Interest</th><th>D11 Total Due</th>
                  </tr>
                </thead>
                <tbody>{''.join(body)}</tbody>
              </table>
              {reconciliation}
              <div class="footnote">Retain this jurisdiction detail with the quarterly IFTA return filing package.</div>
            </section>
            """
        )
    return "".join(pages)


def render_adjustment_page(record: IftaRecord, rows: list[IftaRecord], page_no: int) -> str:
    rng = random.Random(record.return_id + "adjust")
    body = []
    for label in ["Prior credit applied", "Payment posted", "Penalty reviewed", "Refund carry-forward", "Notice balance"]:
        amount = rng.uniform(-1200, 4200)
        body.append(f"<tr><td>{h(label)}</td><td>{money(amount)}</td><td>return-level adjustment</td></tr>")
    samples = rows[:4]
    for r in samples:
        body.append(
            f"<tr class=\"support\"><td>{r.jurisdiction} review notation</td><td>{money(r.total_due_refund)}</td><td>carried into return reconciliation</td></tr>"
        )
    return f"""
    <section class="page">
      {header(record, "adjustments and payment", page_no)}
      <h1>Adjustment And Payment Detail</h1>
      <table class="adjustments"><thead><tr><th>Description</th><th>Amount</th><th>Review note</th></tr></thead><tbody>{''.join(body)}</tbody></table>
      <p class="notice">This page is included for return reconciliation and payment review. Amounts may repeat jurisdiction references from the supporting schedules.</p>
    </section>
    """


def company_name(return_id: str) -> str:
    names = [
        "Northline Freight Cooperative",
        "Cedar Spur Logistics LLC",
        "Summit Plain Transport Inc.",
        "Prairie Bend Distribution Co.",
        "Harbor Ridge Carrier Group",
    ]
    return names[sum(ord(c) for c in return_id) % len(names)]


def render_document(sample_id: str, records: list[IftaRecord], *, split_supplemental_rows: bool = False) -> str:
    pages: list[str] = []
    page_no = 1
    for _, rows in group_by_return(records):
        first = rows[0]
        pages.append(render_financial_page(first, rows, page_no))
        page_no += 1
        pages.append(render_schedule_a(first, rows, page_no))
        page_no += math.ceil(len(rows) / 18)
        pages.append(render_jurisdiction_tax_detail(first, rows, page_no, split_supplemental_rows=split_supplemental_rows))
        page_no += math.ceil(len(rows) / (18 if split_supplemental_rows else 24))
        pages.append(render_adjustment_page(first, rows, page_no))
        page_no += 1
    css = """
    @page { size: letter portrait; margin: 0; }
    body { margin: 0; background: #fff; color: #111; font-family: Arial, Helvetica, sans-serif; }
    .page { box-sizing: border-box; width: 8.5in; min-height: 11in; padding: 0.38in 0.42in 0.42in; page-break-after: always; position: relative; }
    .topbar { display: grid; grid-template-columns: 1.2fr 1.25fr 0.7fr; gap: 0.12in; border-bottom: 1.2px solid #222; padding-bottom: 0.07in; font-size: 8.2pt; line-height: 1.22; }
    .topbar .center { text-align: center; }
    .topbar .right { text-align: right; }
    h1 { text-align: center; font-size: 12.4pt; text-transform: uppercase; margin: 0.18in 0 0.14in; letter-spacing: 0.025em; }
    .summary-grid { display: grid; grid-template-columns: 1.2fr 0.75fr 0.75fr; gap: 0.08in; border: 1px solid #222; padding: 0.08in; margin: 0.04in 0 0.15in; font-size: 9pt; }
    .summary-grid span { display: block; color: #333; font-size: 7.4pt; text-transform: uppercase; }
    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    .line-items { font-size: 9.2pt; margin-top: 0.12in; }
    .line-items td { border-bottom: 1px solid #aaa; padding: 7px 8px; }
    .line-items td:last-child { text-align: right; font-variant-numeric: tabular-nums; width: 1.7in; }
    .schedule { font-size: 8.1pt; line-height: 1.12; }
    .schedule th { border-top: 1px solid #222; border-bottom: 1px solid #222; padding: 4px 4px; text-align: left; vertical-align: bottom; background: #f6f6f6; }
    .schedule td { border-bottom: 1px solid #d0d0d0; padding: 4px 4px; vertical-align: top; height: 0.31in; }
    .schedule .num { text-align: right; font-variant-numeric: tabular-nums; }
    .schedule th:first-child, .schedule td:first-child { width: 0.36in; text-align: right; }
    .schedule th:nth-child(2), .schedule td:nth-child(2) { width: 1.48in; }
    .jurisdiction-tax { font-size: 6.65pt; line-height: 1.05; }
    .jurisdiction-tax th { padding: 3px 3px; }
    .jurisdiction-tax td { padding: 3px 3px; height: 0.235in; }
    .jurisdiction-tax th:first-child, .jurisdiction-tax td:first-child { width: 0.28in; text-align: right; }
    .jurisdiction-tax th:nth-child(2), .jurisdiction-tax td:nth-child(2) { width: 0.34in; text-align: center; }
    .jurisdiction-tax th:nth-child(3), .jurisdiction-tax td:nth-child(3) { width: 0.86in; }
    .jurisdiction-tax th:nth-child(4), .jurisdiction-tax td:nth-child(4) { width: 0.34in; text-align: center; }
    .jurisdiction-tax .supplemental { color: #222; background: #fbfbfb; }
    .jurisdiction-tax .supplemental td { border-bottom: 1px solid #e4e4e4; height: 0.18in; font-size: 6.35pt; }
    .reconciliation { width: 3.55in; margin: 0.12in 0 0 auto; font-size: 7.1pt; }
    .reconciliation td { border-bottom: 1px solid #c8c8c8; padding: 3px 4px; }
    .reconciliation td:last-child { text-align: right; font-variant-numeric: tabular-nums; width: 1.08in; }
    .adjustments { font-size: 8.8pt; margin-top: 0.12in; }
    .adjustments th, .adjustments td { border: 1px solid #aaa; padding: 6px 7px; }
    .adjustments .support { color: #333; background: #fafafa; }
    .notice { font-size: 9pt; line-height: 1.35; margin-top: 0.16in; }
    .footnote { position: absolute; left: 0.42in; right: 0.42in; bottom: 0.22in; border-top: 1px solid #bbb; padding-top: 0.05in; font-size: 7.6pt; color: #333; }
    .muted { color: #555; font-size: 7pt; }
    """
    return f"<!doctype html><html><head><meta charset=\"utf-8\"><title>{h(sample_id)}</title><style>{css}</style></head><body>{''.join(pages)}</body></html>"


async def render_pdf(html_path: Path, pdf_path: Path) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_path.read_text(encoding="utf-8"))
        await page.emulate_media(media="print")
        await page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True)
        await browser.close()


def scan_pdf(source_pdf: Path, output_pdf: Path, *, seed: int) -> None:
    """Rasterize a clean PDF into a mild scan-style PDF."""
    rng = random.Random(seed)
    pages = convert_from_path(str(source_pdf), dpi=135)
    scanned: list[Image.Image] = []
    for page_no, page in enumerate(pages, start=1):
        image = ImageOps.grayscale(page)
        image = ImageOps.autocontrast(image, cutoff=1)
        angle = rng.choice([-0.18, -0.12, -0.06, 0.0, 0.07, 0.14, 0.2])
        image = image.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False, fillcolor=255)
        if page_no % 5 == 0:
            image = image.filter(ImageFilter.GaussianBlur(radius=0.22))
        if page_no % 7 == 0:
            image = ImageOps.autocontrast(image.point(lambda p: min(255, max(0, int(p * 0.96 + 6)))))
        scanned.append(image.convert("RGB"))
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    first, rest = scanned[0], scanned[1:]
    first.save(output_pdf, "PDF", save_all=True, append_images=rest, resolution=135.0)


def metadata(sample_id: str, records: list[IftaRecord], pdf_pages: int) -> dict:
    return {
        "id": sample_id,
        "template": "ifta_multisection_return_packet",
        "target_record_type": "ifta_multisection_jurisdiction_row",
        "num_target_records": len(records),
        "source_batch": "ifta-hardening-experiment",
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
            "ocr_md": f"transcripts/ocr_gemini/{sample_id}.md",
        },
        "transcripts_available": ["ocr"],
        "complexity_regime": "ifta_multisection_return_packet",
        "difficulty": "ifta_multisection_return_packet",
        "format": "production_like_pdf",
        "domain": "commercial_insurance_operations",
        "problems": [
            "high_density_long_list",
            "production_like_layout",
            "ocr_condition",
            "ocr_layout_condition",
            "page_breaks",
            "large_doc",
            "multiple_tables",
            "multi_row",
            "inherited_context",
            "split_records",
            "non_target_rows",
            "repeated_keys",
            "cross_section_join",
        ],
        "pages_estimate": pdf_pages,
        "pdf_page_count": pdf_pages,
        "dataset_version": (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "hf_config": "core_operations",
        "document_count": 1,
        "evidence_pattern": "single_document",
        "layout_revision": {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "purpose": "hard IFTA table extraction condition with fields split across return sections",
            "ocr_status": "layout-preserving Gemini OCR over scanned image PDF",
        },
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


async def generate(out_dir: Path, *, split_supplemental_rows: bool = False) -> None:
    for sub in ["html", "pdfs", "ground_truth", "metadata"]:
        (out_dir / sub).mkdir(parents=True, exist_ok=True)
    manifest = []
    for sample_id, seed, returns in [
        ("ifta_multisection_return_001", 9301, 10),
        ("ifta_multisection_return_002", 9402, 14),
    ]:
        records = make_records(seed, returns)
        html = render_document(sample_id, records, split_supplemental_rows=split_supplemental_rows)
        html_path = out_dir / "html" / f"{sample_id}.html"
        pdf_path = out_dir / "pdfs" / f"{sample_id}.pdf"
        clean_pdf_path = out_dir / "work" / f"{sample_id}.digital.pdf"
        html_path.write_text(html, encoding="utf-8")
        await render_pdf(html_path, clean_pdf_path)
        scan_pdf(clean_pdf_path, pdf_path, seed=seed)
        # The renderer creates one summary, Schedule A, jurisdiction detail,
        # and adjustment pages for each return in the current row ranges.
        pdf_pages = 0
        try:
            from pdf2image import pdfinfo_from_path

            pdf_pages = int(pdfinfo_from_path(str(pdf_path))["Pages"])
        except Exception:
            pdf_pages = html.count("<section class=\"page\"")
        rows = [asdict(r) for r in records]
        write_json(out_dir / "ground_truth" / f"{sample_id}.json", rows)
        meta = metadata(sample_id, records, pdf_pages)
        meta["files"]["json_size_bytes"] = (out_dir / "ground_truth" / f"{sample_id}.json").stat().st_size
        meta["files"]["pdf_size_bytes"] = pdf_path.stat().st_size
        meta["files"]["html_size_bytes"] = html_path.stat().st_size
        write_json(out_dir / "metadata" / f"{sample_id}.json", meta)
        manifest.append(meta)
        print(sample_id, "records", len(records), "pages", pdf_pages, "pdf", pdf_path)
    write_json(out_dir / "manifest.json", {"instances": manifest})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "tmp" / "core_operations" / "ifta_multisection",
    )
    parser.add_argument(
        "--split-supplemental-rows",
        action="store_true",
        help="Render surcharge/selected interest values as realistic continuation rows for extraction experiments.",
    )
    args = parser.parse_args()
    asyncio.run(generate(args.out, split_supplemental_rows=args.split_supplemental_rows))


if __name__ == "__main__":
    main()
