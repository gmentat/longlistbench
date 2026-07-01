#!/usr/bin/env python3
"""Validate that every numeric ground-truth value is faithfully recoverable from
the released OCR transcript.

The existing validate_ocr_vs_golden.py checks only *identifier* coverage
(incident/reference/policy/item ids). It does NOT catch digit-level OCR
corruptions on numeric value fields (e.g. tax_due 19,247.72 transcribed as
19,247.22, or taxable_miles 117,616 transcribed as 117,166). Under the official
zero-tolerance scorer those corrupted cells become unsolvable from the only
released transcript, so they should be caught before publishing.

For each sample, every numeric field whose |value| >= --min-abs is checked for a
sign-aware textual representation in the OCR (with/without thousands separators,
1- or 2-decimal, integer forms, and accounting parentheses for negatives). A
miss means the ground-truth value is not present in the transcript -- almost
always an OCR misread (verify against the HTML source, which is the canonical
layout).

Exit code is non-zero if any sample has misses, so this can gate regeneration.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from .dataset_layout import (
        default_dataset_dir,
        ground_truth_path,
        iter_transcript_paths,
        sample_id_from_transcript_path,
        transcript_path,
    )
except ImportError:
    from dataset_layout import (
        default_dataset_dir,
        ground_truth_path,
        iter_transcript_paths,
        sample_id_from_transcript_path,
        transcript_path,
    )


def representations(value: float) -> set[str]:
    """Plausible unsigned textual forms of a numeric value as it may appear in OCR."""
    a = abs(round(float(value), 2))
    out: set[str] = set()
    if abs(a - round(a)) < 1e-9:  # integer-valued
        n = int(round(a))
        out |= {f"{n:,}", str(n), f"{n:,}.00", f"{n}.00"}
    else:
        out |= {f"{a:,.2f}", f"{a:.2f}", f"{a:,.1f}", f"{a:.1f}", f"{a:g}"}
    return out | {form.replace(",", "") for form in out}


def _compact_numeric(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


def _negative_form_found(form: str, compact_ocr_text: str) -> bool:
    form = _compact_numeric(form)
    variants = {
        f"-{form}",
        f"(${form})",
        f"({form})",
    }
    if not form.startswith("$"):
        variants.add(f"-$" + form)
    return any(variant in compact_ocr_text for variant in variants)


def _positive_form_found(form: str, compact_ocr_text: str) -> bool:
    form = _compact_numeric(form)
    start = 0
    while True:
        index = compact_ocr_text.find(form, start)
        if index == -1:
            return False
        sign_index = index - 1
        if sign_index >= 0 and compact_ocr_text[sign_index] == "$":
            sign_index -= 1
        prefix = compact_ocr_text[sign_index] if sign_index >= 0 else ""
        suffix = compact_ocr_text[index + len(form): index + len(form) + 1]
        if prefix not in {"-", "("} and suffix != ")":
            return True
        start = index + len(form)


def _numeric_value_found_compact(value: float, compact_ocr_text: str) -> bool:
    forms = representations(value)
    if round(float(value), 2) < 0:
        return any(_negative_form_found(form, compact_ocr_text) for form in forms)
    return any(_positive_form_found(form, compact_ocr_text) for form in forms)


def numeric_value_found(value: float, ocr_text: str) -> bool:
    return _numeric_value_found_compact(value, _compact_numeric(ocr_text))


def _record_key(record: dict) -> str | None:
    for field in (
        "jurisdiction", "return_id", "policy_number", "incident_number",
        "claim_number", "vin", "veh_number", "item_id", "unit_number",
    ):
        value = record.get(field)
        if value:
            return str(value)
    return None


def _iter_numeric_fields(value: object, prefix: str = ""):
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)):
        yield prefix, value
        return
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from _iter_numeric_fields(child, child_prefix)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}[{index}]" if prefix else f"[{index}]"
            yield from _iter_numeric_fields(child, child_prefix)


def check_sample(records: list[dict], ocr_text: str, min_abs: float) -> list[dict]:
    compact_ocr_text = _compact_numeric(ocr_text)
    misses: list[dict] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        for field, value in _iter_numeric_fields(record):
            if abs(value) < min_abs:
                continue
            if not _numeric_value_found_compact(float(value), compact_ocr_text):
                misses.append(
                    {
                        "record_index": index,
                        "record_key": _record_key(record),
                        "field": field,
                        "value": round(float(value), 2),
                    }
                )
    return misses


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims-dir", default=None, help="Dataset directory (default: data/)")
    parser.add_argument("--sample", default=None, help="Validate a single sample id")
    parser.add_argument(
        "--min-abs", type=float, default=10.0,
        help="Ignore numeric values with absolute magnitude below this (default 10)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="List each missing value")
    args = parser.parse_args()

    dataset_dir = Path(args.claims_dir) if args.claims_dir else default_dataset_dir()
    if args.sample:
        samples = [args.sample]
    else:
        samples = [
            sample_id_from_transcript_path(dataset_dir, p, "ocr")
            for p in iter_transcript_paths(dataset_dir, "ocr")
        ]

    total_misses = 0
    docs_with_misses = 0
    print("=" * 70)
    print("OCR NUMERIC FIDELITY (ground-truth values recoverable from OCR)")
    print("=" * 70)
    for sample in sorted(samples):
        gt_path = ground_truth_path(dataset_dir, sample)
        ocr_path = transcript_path(dataset_dir, sample, "ocr")
        if not gt_path.exists() or not ocr_path.exists():
            continue
        records = json.loads(gt_path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            continue
        misses = check_sample(records, ocr_path.read_text(encoding="utf-8"), args.min_abs)
        if misses:
            docs_with_misses += 1
            total_misses += len(misses)
            print(f"✗ {sample}: {len(misses)} GT numeric value(s) not found in OCR")
            if args.verbose:
                for miss in misses:
                    print(
                        f"    idx {miss['record_index']:>5}  {miss['record_key']!s:<12}"
                        f"  {miss['field']:<26} {miss['value']}"
                    )
        else:
            print(f"✓ {sample}")

    print("\n" + "=" * 70)
    print(f"Samples with corrupted numeric values: {docs_with_misses}")
    print(f"Total unrecoverable GT numeric values: {total_misses}")
    return 1 if total_misses else 0


if __name__ == "__main__":
    raise SystemExit(main())
