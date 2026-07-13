#!/usr/bin/env python3
"""Validate rendered HTML tables and page scaffolds."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

try:
    from pdf2image import pdfinfo_from_path
except ImportError:
    pdfinfo_from_path = None


@dataclass(frozen=True)
class SparseColumnFinding:
    sample_id: str
    page: int
    title: str
    section: str
    header: str
    empty_rate: float
    row_count: int


@dataclass
class ParsedTable:
    page: int
    title: str
    section: str
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)


class RenderedTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.page_count = 0
        self.title = ""
        self.section = ""
        self.capture_heading: str | None = None
        self.heading_parts: list[str] = []
        self.table: ParsedTable | None = None
        self.tables: list[ParsedTable] = []
        self.row: list[str] | None = None
        self.cell_parts: list[str] | None = None
        self.cell_tag: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "section" and "page" in (attrs_dict.get("class") or "").split():
            self.page_count += 1
            self.title = ""
            self.section = ""
        elif tag in {"h1", "h2"}:
            self.capture_heading = tag
            self.heading_parts = []
        elif tag == "table":
            self.table = ParsedTable(self.page_count, self.title, self.section)
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in {"th", "td"} and self.row is not None:
            self.cell_tag = tag
            self.cell_parts = []

    def handle_data(self, data: str) -> None:
        if self.capture_heading:
            self.heading_parts.append(data)
        if self.cell_parts is not None:
            self.cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == self.capture_heading:
            text = " ".join("".join(self.heading_parts).split())
            if tag == "h1":
                self.title = text
            else:
                self.section = text
            self.capture_heading = None
            self.heading_parts = []
        elif tag == self.cell_tag and self.cell_parts is not None and self.row is not None:
            self.row.append(" ".join("".join(self.cell_parts).split()))
            self.cell_parts = None
            self.cell_tag = None
        elif tag == "tr" and self.row is not None and self.table is not None:
            if self.row:
                if not self.table.headers:
                    self.table.headers = self.row
                else:
                    self.table.rows.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def parse_rendered_html(path: Path) -> RenderedTableParser:
    parser = RenderedTableParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def find_sparse_columns(
    html_dir: Path,
    *,
    threshold: float = 0.8,
    min_rows: int = 4,
) -> list[SparseColumnFinding]:
    findings: list[SparseColumnFinding] = []
    for path in sorted(html_dir.glob("*.html")):
        sample_id = path.stem
        for table in parse_rendered_html(path).tables:
            width = len(table.headers)
            rows = [row for row in table.rows if len(row) == width]
            if width == 0 or len(rows) < min_rows:
                continue
            for column, header in enumerate(table.headers):
                empty_rate = sum(not row[column] for row in rows) / len(rows)
                if empty_rate >= threshold:
                    findings.append(
                        SparseColumnFinding(
                            sample_id=sample_id,
                            page=table.page,
                            title=table.title,
                            section=table.section,
                            header=header,
                            empty_rate=empty_rate,
                            row_count=len(rows),
                        )
                    )
    return findings


def is_expected_sparse_column(finding: SparseColumnFinding) -> bool:
    if finding.sample_id.startswith("loss_run_external_") and finding.header == "DateClosed":
        return True
    if finding.sample_id.startswith("vehicle_schedule_sparse_") and finding.header in {
        "Plate",
        "Company unit",
    }:
        return True
    if finding.sample_id in {
        "mixed_040_001_crosspage",
        "multihop_012_001_crosspage",
        "multihop_025_001_crosspage",
    } and finding.header == "Company vehicle #":
        return True
    return False


def find_page_scaffold_mismatches(dataset_dir: Path) -> list[tuple[str, int, int]]:
    mismatches = []
    metadata_dir = dataset_dir / "metadata"
    for html_path in sorted((dataset_dir / "html").glob("*.html")):
        parser = parse_rendered_html(html_path)
        if parser.page_count == 0:
            continue
        pdf_path = dataset_dir / "pdfs" / f"{html_path.stem}.pdf"
        if pdfinfo_from_path is not None and pdf_path.exists():
            pdf_page_count = int(pdfinfo_from_path(str(pdf_path))["Pages"])
        else:
            metadata_path = metadata_dir / f"{html_path.stem}.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            pdf_page_count = int(metadata["pdf_page_count"])
        if parser.page_count != pdf_page_count:
            mismatches.append((html_path.stem, parser.page_count, pdf_page_count))
    return mismatches


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-dir", type=Path, default=Path("data"))
    parser.add_argument("--threshold", type=float, default=0.8)
    parser.add_argument("--min-rows", type=int, default=4)
    args = parser.parse_args()

    findings = find_sparse_columns(
        args.dataset_dir / "html",
        threshold=args.threshold,
        min_rows=args.min_rows,
    )
    unexpected = [finding for finding in findings if not is_expected_sparse_column(finding)]
    mismatches = find_page_scaffold_mismatches(args.dataset_dir)

    for finding in unexpected:
        print(
            f"{finding.sample_id}:p{finding.page} "
            f"[{finding.title} / {finding.section}] "
            f"{finding.header} is {finding.empty_rate:.0%} empty "
            f"across {finding.row_count} rows"
        )
    for sample_id, html_pages, pdf_pages in mismatches:
        print(
            f"{sample_id}: HTML declares {html_pages} pages, "
            f"but metadata records {pdf_pages} PDF pages"
        )

    if unexpected or mismatches:
        raise SystemExit(1)
    print(
        f"HTML table/page validation passed: {len(findings)} expected sparse columns, "
        f"{len(mismatches)} page mismatches"
    )


if __name__ == "__main__":
    main()
