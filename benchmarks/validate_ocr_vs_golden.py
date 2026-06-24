#!/usr/bin/env python3
"""
Validate OCR output against golden JSON data.

For loss-run claims, this checks incident and reference identifiers. For generic
policy-record fixtures, it checks visible policy/item/form/class/location
identifiers instead.
"""

import json
import re
from collections import Counter
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


def load_golden(json_path: Path) -> list[dict]:
    """Load golden claims from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_ocr_text(md_path: Path) -> str:
    """Load OCR text from markdown file."""
    return md_path.read_text(encoding="utf-8")


def _has_generic_records(records: list[dict]) -> bool:
    if not records:
        return False
    return not any(
        isinstance(record, dict) and ("incident_number" in record or "reference_number" in record)
        for record in records
    )


GENERIC_POLICY_FIELDS = ("policy_number",)
GENERIC_PRIMARY_FIELDS = (
    "item_id",
    "claim_number",
    "vehicle",
    "unit_number",
    "vin",
    "driver_name",
    "name",
    "license_number",
    "driver_license_number",
    "veh_number",
    "company_vehicle_number",
    "plate_number",
)
GENERIC_SCHEDULE_FIELDS = (
    "form_number",
    "class_code",
    "location_number",
    "building_number",
    "endorsement_number",
    "coverage_or_form",
    "coverage",
    "coverage_part",
    "state",
    "jurisdiction",
    "section",
)
CLAIM_IDENTIFIER_FIELDS = ("incident_number", "reference_number")


def _compact(value: str) -> str:
    return re.sub(r"\s+", "", value)


def _value_aliases(field: str, value: str) -> list[str]:
    aliases = [value]
    if field == "incident_number":
        match = re.search(r"\d+", value)
        if match:
            aliases.append(match.group())
    return aliases


def _identifier_found(
    value: str,
    ocr_text: str,
    compact_ocr_text: str,
    field: str = "",
) -> bool:
    for alias in _value_aliases(field, value):
        if alias in ocr_text or _compact(alias) in compact_ocr_text:
            return True
    return False


def extract_identifiers(claims: list[dict]) -> dict[str, set[str]]:
    """Extract key visible identifiers from golden records."""
    if _has_generic_records(claims):
        policy_numbers: set[str] = set()
        primary_ids: set[str] = set()
        schedule_values: set[str] = set()

        for record in claims:
            for field in GENERIC_POLICY_FIELDS:
                value = str(record.get(field) or "").strip()
                if value:
                    policy_numbers.add(value)
            for field in GENERIC_PRIMARY_FIELDS:
                value = str(record.get(field) or "").strip()
                if value:
                    primary_ids.add(value)
            for field in GENERIC_SCHEDULE_FIELDS:
                value = str(record.get(field) or "").strip()
                if value:
                    schedule_values.add(value)

        return {
            "policy_numbers": policy_numbers,
            "primary_ids": primary_ids,
            "schedule_values": schedule_values,
        }

    incident_numbers = set()
    reference_numbers = set()
    
    for claim in claims:
        inc_num = claim.get("incident_number", "")
        if inc_num:
            # Store both raw and numeric-only versions
            incident_numbers.add(inc_num)
            # Extract just the number part (e.g., "30001" from "#30001")
            match = re.search(r"\d+", inc_num)
            if match:
                incident_numbers.add(match.group())
        
        ref_num = claim.get("reference_number", "")
        if ref_num:
            reference_numbers.add(ref_num)
    
    return {
        "incident_numbers": incident_numbers,
        "reference_numbers": reference_numbers,
    }


def compute_affected_record_coverage(records: list[dict], ocr_text: str) -> dict:
    """Count how many per-record identifier fields are supported by OCR text."""
    compact_ocr_text = _compact(ocr_text)
    is_generic = _has_generic_records(records)
    fields = (
        GENERIC_POLICY_FIELDS + GENERIC_PRIMARY_FIELDS + GENERIC_SCHEDULE_FIELDS
        if is_generic
        else CLAIM_IDENTIFIER_FIELDS
    )

    total_field_pairs = 0
    supported_field_pairs = 0
    affected_records: set[int] = set()
    missing_by_field: Counter[str] = Counter()

    for index, record in enumerate(records):
        record_missing = False
        for field in fields:
            value = str(record.get(field) or "").strip()
            if not value:
                continue

            total_field_pairs += 1
            if _identifier_found(value, ocr_text, compact_ocr_text, field=field):
                supported_field_pairs += 1
            else:
                record_missing = True
                missing_by_field[field] += 1

        if record_missing:
            affected_records.add(index)

    support_coverage = (
        supported_field_pairs / total_field_pairs if total_field_pairs else 1.0
    )
    affected_record_rate = len(affected_records) / len(records) if records else 0.0

    return {
        "tracked_identifier_field_pairs": total_field_pairs,
        "supported_identifier_field_pairs": supported_field_pairs,
        "missing_identifier_field_pairs": total_field_pairs - supported_field_pairs,
        "identifier_field_coverage": support_coverage,
        "affected_records": len(affected_records),
        "affected_record_rate": affected_record_rate,
        "missing_by_field": dict(missing_by_field.most_common()),
    }


def check_coverage(ocr_text: str, identifiers: dict[str, set[str]]) -> dict:
    """Check how many identifiers appear in the OCR text."""
    results = {}
    compact_ocr_text = _compact(ocr_text)
    
    for id_type, id_set in identifiers.items():
        found = set()
        missing = set()
        
        for identifier in id_set:
            # Check if identifier appears in OCR text
            if _identifier_found(identifier, ocr_text, compact_ocr_text):
                found.add(identifier)
            else:
                missing.add(identifier)
        
        total = len(id_set)
        found_count = len(found)
        coverage = found_count / total if total > 0 else 0
        
        results[id_type] = {
            "total": total,
            "found": found_count,
            "missing": len(missing),
            "coverage": coverage,
            "missing_ids": sorted(missing)[:10],  # First 10 missing
        }
    
    return results


def validate_sample(sample_name: str, claims_dir: Path, verbose: bool = False) -> dict | None:
    """Validate a single sample's OCR against golden data."""
    json_path = ground_truth_path(claims_dir, sample_name)
    ocr_path = transcript_path(claims_dir, sample_name, "ocr")
    
    if not json_path.exists():
        return None
    
    if not ocr_path.exists():
        return {"error": "OCR file not found", "sample": sample_name}
    
    # Load data
    claims = load_golden(json_path)
    ocr_text = load_ocr_text(ocr_path)
    is_generic = _has_generic_records(claims)
    
    # Extract identifiers and check coverage
    identifiers = extract_identifiers(claims)
    coverage = check_coverage(ocr_text, identifiers)
    affected = compute_affected_record_coverage(claims, ocr_text)
    
    result = {
        "sample": sample_name,
        "num_claims": len(claims),
        "record_kind": "generic_records" if is_generic else "claims",
        "ocr_chars": len(ocr_text),
        "coverage": coverage,
        "affected": affected,
    }

    if is_generic:
        nonempty = [item for item in coverage.values() if item["total"] > 0]
        result["overall_coverage"] = (
            sum(item["coverage"] for item in nonempty) / len(nonempty) if nonempty else 0.0
        )
        result["missing_total"] = sum(item["missing"] for item in coverage.values())
    else:
        result.update(
            {
                "incident_coverage": coverage["incident_numbers"]["coverage"],
                "reference_coverage": coverage["reference_numbers"]["coverage"],
                "incident_missing": coverage["incident_numbers"]["missing"],
                "reference_missing": coverage["reference_numbers"]["missing"],
                "overall_coverage": min(
                    coverage["incident_numbers"]["coverage"],
                    coverage["reference_numbers"]["coverage"],
                ),
                "missing_total": (
                    coverage["incident_numbers"]["missing"]
                    + coverage["reference_numbers"]["missing"]
                ),
            }
        )
    
    if verbose:
        if is_generic:
            result["missing_identifiers"] = {
                key: value["missing_ids"]
                for key, value in coverage.items()
                if value["missing_ids"]
            }
        else:
            result["missing_incident_ids"] = coverage["incident_numbers"]["missing_ids"]
            result["missing_reference_ids"] = coverage["reference_numbers"]["missing_ids"]
    
    return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate OCR output against golden JSON data"
    )
    parser.add_argument(
        "--claims-dir",
        type=str,
        default=None,
        help="Dataset directory (default: data/ when present, else benchmarks/claims)",
    )
    parser.add_argument(
        "--sample",
        type=str,
        help="Validate a specific sample (e.g., 'easy_10_001_detailed')",
    )
    parser.add_argument(
        "--tiers",
        nargs="+",
        choices=["easy", "medium", "hard", "extreme", "multihop", "mixed"],
        help="Only validate samples whose filename starts with one of these tiers",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show missing identifiers",
    )
    
    args = parser.parse_args()
    
    claims_dir = Path(args.claims_dir) if args.claims_dir else default_dataset_dir()
    
    if not claims_dir.exists():
        print(f"Error: Claims directory not found: {claims_dir}")
        return
    
    # Find samples to validate
    if args.sample:
        samples = [args.sample]
    else:
        # Find all samples with OCR files
        ocr_files = iter_transcript_paths(claims_dir, "ocr")
        samples = [sample_id_from_transcript_path(claims_dir, f, "ocr") for f in ocr_files]

    if args.tiers and not args.sample:
        samples = [
            s
            for s in samples
            if any(s.startswith(f"{tier}_") for tier in args.tiers)
        ]
    
    if not samples:
        print("No OCR files found. Run ocr_claims_pdfs.py first.")
        return
    
    print("=" * 70)
    print("OCR vs GOLDEN VALIDATION")
    print("=" * 70)
    print()
    
    results = []
    total_records = 0
    
    for sample in samples:
        result = validate_sample(sample, claims_dir, verbose=args.verbose)
        
        if result is None:
            continue
        
        if "error" in result:
            print(f"⚠ {sample}: {result['error']}")
            continue
        
        results.append(result)
        
        overall_cov = result["overall_coverage"]
        
        # Determine status emoji
        if overall_cov >= 0.95:
            status = "✓"
        elif overall_cov >= 0.80:
            status = "~"
        else:
            status = "✗"
        
        print(f"{status} {sample}")
        if result["record_kind"] == "generic_records":
            parts = []
            for key, value in result["coverage"].items():
                if value["total"] == 0:
                    continue
                label = key.replace("_", " ").title()
                parts.append(f"{label}: {value['coverage']:5.1%} ({value['missing']} missing)")
            print(f"    Records: {result['num_claims']:4d}  |  " + "  |  ".join(parts))
        else:
            print(f"    Claims: {result['num_claims']:4d}  |  "
                  f"Incident: {result['incident_coverage']:5.1%} ({result['incident_missing']} missing)  |  "
                  f"Reference: {result['reference_coverage']:5.1%} ({result['reference_missing']} missing)")

        affected = result["affected"]
        if affected["affected_records"]:
            print(
                f"    Affected records: {affected['affected_records']}/"
                f"{result['num_claims']} ({affected['affected_record_rate']:5.1%})  |  "
                f"Identifier field support: {affected['identifier_field_coverage']:5.1%}"
            )
        
        if args.verbose and result.get("missing_incident_ids"):
            print(f"    Missing incidents: {', '.join(result['missing_incident_ids'][:5])}")
        if args.verbose and result.get("missing_reference_ids"):
            print(f"    Missing references: {', '.join(result['missing_reference_ids'][:5])}")
        if args.verbose and result.get("missing_identifiers"):
            for key, missing in result["missing_identifiers"].items():
                print(f"    Missing {key}: {', '.join(missing[:5])}")
        
        total_records += result["num_claims"]
    
    if results:
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        
        avg_overall = sum(r["overall_coverage"] for r in results) / len(results)
        
        print(f"Samples validated: {len(results)}")
        print(f"Total records: {total_records}")
        print(f"Average identifier coverage: {avg_overall:.1%}")
        total_affected_records = sum(r["affected"]["affected_records"] for r in results)
        total_identifier_pairs = sum(
            r["affected"]["tracked_identifier_field_pairs"] for r in results
        )
        total_supported_pairs = sum(
            r["affected"]["supported_identifier_field_pairs"] for r in results
        )
        affected_field_coverage = (
            total_supported_pairs / total_identifier_pairs if total_identifier_pairs else 1.0
        )
        print(f"Affected records: {total_affected_records}")
        print(f"Identifier field support: {affected_field_coverage:.1%}")
        
        # Count by coverage level
        high = sum(1 for r in results if r["overall_coverage"] >= 0.95)
        medium = sum(1 for r in results if 0.80 <= r["overall_coverage"] < 0.95)
        low = sum(1 for r in results if r["overall_coverage"] < 0.80)
        
        print(f"\nCoverage breakdown:")
        print(f"  ≥95%: {high} samples")
        print(f"  80-95%: {medium} samples")
        print(f"  <80%: {low} samples")


if __name__ == "__main__":
    main()
