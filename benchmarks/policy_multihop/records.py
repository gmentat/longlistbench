"""Deterministic synthetic ground-truth records for policy packets."""

from __future__ import annotations

import random
from typing import Any

from .config import PolicyMultiHopCaseConfig
from .util import money, stable_seed


INSURED_STEMS = [
    "Orchard Vale Market Group",
    "Copperline Fitness Works",
    "Larkspur Equipment Rental",
    "Morrowfield Studio Collective",
    "Silverfen Property Holdings",
    "Juniper Gate Learning Center",
    "Blue Kettle Food Service",
    "Pinecrest Print Cooperative",
    "Cinderbrook Repair Studio",
    "Summit Lantern Contractors",
]

PRODUCERS = [
    ("Trestle Oak Risk Services", "PX-48271"),
    ("Brindle Coast Coverage Group", "PX-73916"),
    ("Mica Ridge Commercial Advisors", "PX-27405"),
    ("Lumen Field Brokerage", "PX-61844"),
]

STREETS = [
    "1186 Alder Spur",
    "52 Brickyard Loop",
    "736 Hawthorn Trace",
    "319 Stonewell Court",
    "68 Saffron Works",
    "914 Millrace Parkway",
    "27 Lantern Hill Road",
    "564 Quarry Gate",
    "19 Briar Harbor",
    "429 Ironvale Terrace",
]

CITIES = [
    ("New Haven", "CT", "06510"),
    ("Providence", "RI", "02903"),
    ("Portland", "ME", "04101"),
    ("Burlington", "VT", "05401"),
    ("Worcester", "MA", "01608"),
    ("Dover", "NH", "03820"),
]

BOP_COVERAGES = [
    ("Building", "BPF 00 13", "Businessowners Coverage Form", "Replacement Cost"),
    ("Business Personal Property", "BPF 00 13", "Businessowners Coverage Form", "Replacement Cost"),
    ("Business Income and Extra Expense", "BPF 04 39", "Business Income and Extra Expense", "Actual Loss Sustained"),
    ("Equipment Breakdown", "BPF 04 62", "Equipment Breakdown Coverage", "Replacement Cost"),
    ("Employee Dishonesty", "BPF 15 18", "Employee Dishonesty Optional Coverage", "Blanket Limit"),
    ("Accounts Receivable", "BPF 04 26", "Accounts Receivable Coverage", "Scheduled Limit"),
    ("Outdoor Property", "BPF 04 28", "Outdoor Property Extension", "Replacement Cost"),
    ("Water Back-Up", "BPF 04 91", "Water Back-Up and Sump Overflow", "Scheduled Limit"),
    ("Hired and Non-Owned Auto", "BPF 04 47", "Hired Auto and Non-Owned Auto Liability", "Liability Limit"),
    ("Additional Insured by Contract", "BPF 12 09", "Additional Insured - Contract", "Status Grant"),
    ("PFAS Exclusion", "BPF 14 19", "PFAS Exclusion", "Exclusion Applies"),
    ("Ordinary Payroll Limitation", "BPF 04 67", "Ordinary Payroll Limitation", "90 Days"),
]

BOP_CLASSES = [
    ("0542", "Retail stores - food and beverage"),
    ("0967", "Office and professional services"),
    ("1843", "Repair or service shop"),
    ("4167", "Restaurant or cafe"),
    ("5531", "Contractor - interior finishing"),
    ("7391", "Property management"),
]

WC_CLASSES = [
    ("CT", "8810", "Clerical office employees"),
    ("CT", "8017", "Retail store - all employees"),
    ("MA", "8742", "Outside salespersons"),
    ("MA", "5190", "Electrical wiring within buildings"),
    ("RI", "9082", "Restaurant NOC"),
    ("ME", "3632", "Machine shop NOC"),
    ("NH", "9015", "Building operations by owner"),
    ("VT", "5606", "Contractor executive supervisor"),
]

CGL_CLASSES = [
    ("10010", "Mercantile - food or beverage stores", "Gross sales"),
    ("41670", "Restaurants - with sales of alcoholic beverages", "Gross sales"),
    ("16916", "Contractors - subcontracted work", "Cost of work"),
    ("91560", "Concrete construction", "Payroll"),
    ("97047", "Property owners - commercial buildings", "Area"),
    ("61217", "Buildings or premises - office", "Area"),
    ("18435", "Auto repair or service shops", "Gross sales"),
    ("47103", "Printing operations", "Payroll"),
]

MATERIALITY = ["Material", "Potentially Material", "Administrative", "No Material Change"]

CLAUSE_TYPES_BY_LOB: dict[str, tuple[tuple[str, str], ...]] = {
    "BOP": (
        ("Scheduled Premises Limitation", "limitation"),
        ("Limit And Deductible Application", "condition"),
        ("Valuation Records Requirement", "condition"),
        ("Endorsement Priority", "condition"),
    ),
    "WC": (
        ("Remuneration Audit", "condition"),
        ("State Classification Control", "condition"),
        ("Officer And Subcontractor Treatment", "limitation"),
        ("Premium Revision Basis", "condition"),
    ),
    "CGL": (
        ("Classification And Territory Limitation", "limitation"),
        ("Aggregate Limit Application", "condition"),
        ("Additional Insured Contract Gate", "condition"),
        ("Exclusion And Endorsement Priority", "exclusion"),
    ),
}


def case_profile(config: PolicyMultiHopCaseConfig, rng: random.Random) -> dict[str, str]:
    stem = INSURED_STEMS[rng.randrange(len(INSURED_STEMS))]
    city, state, zip_code = CITIES[rng.randrange(len(CITIES))]
    street = STREETS[rng.randrange(len(STREETS))]
    suffix = 600000 + rng.randrange(300000)
    effective_year = 2026
    if config.lob == "BOP":
        carrier = rng.choice(["Cobalt Pine Indemnity", "Larkspur Mutual", "Morrowfield Casualty"])
        prefix = "QB"
        lob_display = "Businessowners Policy"
    elif config.lob == "WC":
        carrier = rng.choice(["Argent Birch Employers", "Coppervale Regional", "Norridge Workguard"])
        prefix = "YW"
        lob_display = "Workers Compensation and Employers Liability"
    else:
        carrier = rng.choice(["Juniper Crown Casualty", "Cobalt Pine Indemnity", "Northline Underwriters"])
        prefix = "LG"
        lob_display = "Commercial General Liability"
    producer_name, producer_code = rng.choice(PRODUCERS)

    return {
        "named_insured": f"{stem}, LLC",
        "mailing_address": f"{street}, {city}, {state} {zip_code}",
        "producer_name": producer_name,
        "producer_code": producer_code,
        "carrier": carrier,
        "lob": config.lob,
        "lob_display": lob_display,
        "policy_number": f"{prefix}{suffix + 37}",
        "policy_period": f"04/01/{effective_year} - 04/01/{effective_year + 1}",
    }


def address_for(idx: int, rng: random.Random) -> str:
    city, state, zip_code = CITIES[(idx + rng.randrange(len(CITIES))) % len(CITIES)]
    street = STREETS[(idx + rng.randrange(len(STREETS))) % len(STREETS)]
    return f"{street}, {city}, {state} {zip_code}"


def generate_bop_items(config: PolicyMultiHopCaseConfig, profile: dict[str, str], base_seed: int) -> list[dict[str, Any]]:
    rng = random.Random(stable_seed(base_seed, config.id, config.seed_offset))
    items: list[dict[str, Any]] = []
    premises: list[tuple[str, str, str, str, str]] = []
    for idx, (location_number, building_number) in enumerate(
        [("001", "001"), ("002", "001"), ("001", "002"), ("002", "002")]
    ):
        class_code, class_desc = BOP_CLASSES[(idx + rng.randrange(len(BOP_CLASSES))) % len(BOP_CLASSES)]
        premises.append((location_number, building_number, address_for(idx, rng), class_code, class_desc))
    for idx in range(config.num_items):
        coverage, form_number, form_title, valuation = BOP_COVERAGES[idx % len(BOP_COVERAGES)]
        location_number, building_number, premises_address, class_code, class_desc = premises[idx % len(premises)]
        limit = 50_000 + (idx % 10) * 25_000 + rng.choice([0, 10_000, 25_000])
        deductible = rng.choice([500, 1_000, 2_500, 5_000, 10_000])
        premium = 145 + idx * 31 + rng.randrange(0, 130)
        endorsement = f"BP-EN-{idx + 1:03d}" if idx % 3 != 1 else ""
        items.append(
            {
                "item_id": f"BOP-{idx + 1:04d}",
                "lob": "BOP",
                "policy_number": profile["policy_number"],
                "named_insured": profile["named_insured"],
                "policy_period": profile["policy_period"],
                "coverage": coverage,
                "location_number": location_number,
                "building_number": building_number,
                "premises_address": premises_address,
                "limit": money(limit),
                "deductible": money(deductible),
                "valuation": valuation,
                "coinsurance": rng.choice(["80%", "90%", "Agreed Value"]),
                "business_income_basis": rng.choice(["Actual Loss Sustained", "12 Months", "Ordinary Payroll 90 Days"]),
                "class_code": class_code,
                "classification": class_desc,
                "form_number": form_number,
                "form_title": form_title,
                "edition_date": rng.choice(["01 20", "06 21", "12 23", "04 24"]),
                "endorsement_number": endorsement,
                "endorsement_effective_date": f"{(idx % 12) + 1:02d}/15/2026" if endorsement else "",
                "premium": money(premium),
                "materiality": MATERIALITY[(idx + rng.randrange(len(MATERIALITY))) % len(MATERIALITY)],
            }
        )
    return items


def generate_wc_items(config: PolicyMultiHopCaseConfig, profile: dict[str, str], base_seed: int) -> list[dict[str, Any]]:
    rng = random.Random(stable_seed(base_seed, config.id, config.seed_offset))
    items: list[dict[str, Any]] = []
    exp_mod = f"{rng.choice([0.87, 0.92, 0.98, 1.04, 1.11]):.2f}"
    schedule_credit = rng.choice(["-5%", "-2%", "0%", "+3%"])
    for idx in range(config.num_items):
        state, class_code, classification = WC_CLASSES[idx % len(WC_CLASSES)]
        payroll = 42_000 + idx * 11_500 + rng.randrange(0, 9_000)
        manual_rate = rng.choice([0.18, 0.27, 0.42, 0.74, 1.15, 2.86, 4.35, 6.22])
        premium = int((payroll / 100) * manual_rate)
        endorsement = f"WC-EN-{idx + 1:03d}" if idx % 4 in {0, 3} else ""
        items.append(
            {
                "item_id": f"WC-{idx + 1:04d}",
                "lob": "WC",
                "policy_number": profile["policy_number"],
                "named_insured": profile["named_insured"],
                "policy_period": profile["policy_period"],
                "state": state,
                "class_code": class_code,
                "classification": classification,
                "annual_payroll": money(payroll),
                "manual_rate": f"{manual_rate:.2f}",
                "estimated_premium": money(premium),
                "experience_mod": exp_mod,
                "schedule_credit_debit": schedule_credit,
                "governing_class": "Yes" if idx == 0 else "No",
                "location_number": str((idx % 5) + 1),
                "premium_basis": "Payroll per $100 remuneration",
                "form_number": rng.choice(["WC 00 00 00 C", "WC 00 00 01 A", "WC 00 03 13", "WC 04 03 06"]),
                "form_title": rng.choice(
                    [
                        "Workers Compensation and Employers Liability Policy",
                        "Information Page",
                        "Waiver of Our Right to Recover",
                        "Voluntary Compensation Endorsement",
                    ]
                ),
                "edition_date": rng.choice(["01 15", "04 21", "07 23"]),
                "endorsement_number": endorsement,
                "endorsement_effective_date": f"{(idx % 12) + 1:02d}/01/2026" if endorsement else "",
                "materiality": MATERIALITY[(idx + rng.randrange(len(MATERIALITY))) % len(MATERIALITY)],
            }
        )
    return items


def generate_cgl_items(config: PolicyMultiHopCaseConfig, profile: dict[str, str], base_seed: int) -> list[dict[str, Any]]:
    rng = random.Random(stable_seed(base_seed, config.id, config.seed_offset))
    limit_types = [
        ("Each Occurrence", 1_000_000),
        ("General Aggregate", 2_000_000),
        ("Products-Completed Operations Aggregate", 2_000_000),
        ("Personal and Advertising Injury", 1_000_000),
        ("Damage to Premises Rented to You", 100_000),
        ("Medical Expense", 5_000),
    ]
    forms = [
        ("CG 00 01", "Commercial General Liability Coverage Form"),
        ("CG 20 10", "Additional Insured - Owners, Lessees or Contractors"),
        ("CG 20 37", "Additional Insured - Completed Operations"),
        ("CG 21 06", "Exclusion - Access or Disclosure of Confidential Information"),
        ("CG 21 67", "Fungi or Bacteria Exclusion"),
        ("CG 24 26", "Amendment of Insured Contract Definition"),
        ("CG 24 04", "Waiver of Transfer of Rights of Recovery"),
    ]
    exclusions = [
        "PFAS Exclusion",
        "Silica or Silica-Related Dust Exclusion",
        "Data Privacy Violation Exclusion",
        "Employment-Related Practices Exclusion",
        "Designated Professional Services Exclusion",
    ]
    items: list[dict[str, Any]] = []
    for idx in range(config.num_items):
        class_code, classification, exposure_basis = CGL_CLASSES[idx % len(CGL_CLASSES)]
        limit_type, limit = limit_types[idx % len(limit_types)]
        form_number, form_title = forms[idx % len(forms)]
        exposure = 75_000 + idx * 13_500 + rng.randrange(0, 20_000)
        rate = rng.choice([0.112, 0.184, 0.245, 0.392, 0.515, 0.744])
        premium = int((exposure / 1000) * rate * 100)
        endorsement = f"GL-EN-{idx + 1:03d}" if idx % 5 in {0, 2, 4} else ""
        items.append(
            {
                "item_id": f"CGL-{idx + 1:04d}",
                "lob": "CGL",
                "policy_number": profile["policy_number"],
                "named_insured": profile["named_insured"],
                "policy_period": profile["policy_period"],
                "coverage_part": "Commercial General Liability",
                "limit_type": limit_type,
                "limit": money(limit),
                "class_code": class_code,
                "classification": classification,
                "location_number": str((idx % 6) + 1),
                "territory": rng.choice(["001", "003", "007", "012"]),
                "exposure_basis": exposure_basis,
                "exposure": f"{exposure:,}",
                "rate": f"{rate:.3f}",
                "premium": money(max(premium, 95)),
                "products_completed_ops_rate": f"{rate * rng.choice([0.18, 0.24, 0.31]):.3f}",
                "form_number": form_number,
                "form_title": form_title,
                "edition_date": rng.choice(["04 13", "12 19", "09 21", "01 24"]),
                "exclusion_name": exclusions[idx % len(exclusions)],
                "endorsement_number": endorsement,
                "endorsement_effective_date": f"{(idx % 12) + 1:02d}/20/2026" if endorsement else "",
                "materiality": MATERIALITY[(idx + rng.randrange(len(MATERIALITY))) % len(MATERIALITY)],
            }
        )
    return items


def generate_policy_items(config: PolicyMultiHopCaseConfig, profile: dict[str, str], base_seed: int) -> list[dict[str, Any]]:
    if config.lob == "BOP":
        return generate_bop_items(config, profile, base_seed)
    if config.lob == "WC":
        return generate_wc_items(config, profile, base_seed)
    return generate_cgl_items(config, profile, base_seed)


def _base_record(item: dict[str, Any], record_type: str, record_id: str) -> dict[str, Any]:
    return {
        "record_type": record_type,
        "record_id": record_id,
        "lob": item["lob"],
        "policy_number": item["policy_number"],
        "named_insured": item["named_insured"],
        "policy_period": item["policy_period"],
    }


def _primary_record(config: PolicyMultiHopCaseConfig, item: dict[str, Any]) -> dict[str, Any]:
    record = dict(item)
    record.pop("materiality", None)
    record.update(_base_record(item, config.target_record_type, item["item_id"]))
    return record


def _form_record(item: dict[str, Any]) -> dict[str, Any]:
    record = _base_record(item, "policy_form_item", f"FORM-{item['item_id']}")
    schedule_source = item.get("endorsement_number") or "Policy jacket"
    if item["lob"] == "BOP" and item.get("endorsement_number"):
        schedule_source = "Endorsement attached"
    record.update(
        {
            "item_id": item["item_id"],
            "applies_to_record_id": item["item_id"],
            "form_number": item["form_number"],
            "edition_date": item["edition_date"],
            "form_title": item["form_title"],
            "schedule_source": schedule_source,
        }
    )
    if item["lob"] == "BOP":
        return record
    if item["lob"] == "CGL":
        record["exclusion_name"] = item.get("exclusion_name", "")
    return record


def _endorsement_record(item: dict[str, Any]) -> dict[str, Any] | None:
    endorsement_number = item.get("endorsement_number")
    if not endorsement_number:
        return None
    record = _base_record(item, "policy_endorsement_item", endorsement_number)
    record.update(
        {
            "item_id": item["item_id"],
            "applies_to_record_id": item["item_id"],
            "endorsement_number": endorsement_number,
            "endorsement_effective_date": item.get("endorsement_effective_date", ""),
            "form_number": item["form_number"],
            "form_title": item["form_title"],
            "edition_date": item["edition_date"],
            "materiality": item["materiality"],
        }
    )
    if item["lob"] == "BOP":
        record.update(
            {
                "coverage": item["coverage"],
                "location_number": item["location_number"],
                "building_number": item["building_number"],
                "limit": item["limit"],
                "deductible": item["deductible"],
            }
        )
    elif item["lob"] == "WC":
        record.update(
            {
                "state": item["state"],
                "class_code": item["class_code"],
                "classification": item["classification"],
                "annual_payroll": item["annual_payroll"],
                "estimated_premium": item["estimated_premium"],
            }
        )
    else:
        record.update(
            {
                "class_code": item["class_code"],
                "classification": item["classification"],
                "location_number": item["location_number"],
                "exclusion_name": item["exclusion_name"],
                "limit_type": item["limit_type"],
                "limit": item["limit"],
            }
        )
    return record


def _premium_record(item: dict[str, Any]) -> dict[str, Any]:
    record = _base_record(item, "policy_premium_item", f"PREM-{item['item_id']}")
    record.update(
        {
            "item_id": item["item_id"],
            "applies_to_record_id": item["item_id"],
            "premium": item.get("premium") or item.get("estimated_premium", ""),
            "premium_basis": item.get("premium_basis") or item.get("exposure_basis") or item.get("coverage", ""),
            "class_code": item.get("class_code", ""),
            "location_number": item.get("location_number", ""),
        }
    )
    if item["lob"] == "WC":
        record.update(
            {
                "state": item["state"],
                "annual_payroll": item["annual_payroll"],
                "manual_rate": item["manual_rate"],
                "experience_mod": item["experience_mod"],
                "schedule_credit_debit": item["schedule_credit_debit"],
            }
        )
    elif item["lob"] == "CGL":
        record.update(
            {
                "exposure": item["exposure"],
                "rate": item["rate"],
                "products_completed_ops_rate": item["products_completed_ops_rate"],
            }
        )
    else:
        record.update(
            {
                "coverage": item["coverage"],
                "location_number": item["location_number"],
                "building_number": item["building_number"],
                "limit": item["limit"],
            }
        )
    return record


def _clause_scope(item: dict[str, Any]) -> str:
    if item["lob"] == "BOP":
        return f"Location {item['location_number']}, Building {item['building_number']}, {item['coverage']}"
    if item["lob"] == "WC":
        return f"{item['state']} class {item['class_code']}, Location {item['location_number']}"
    return f"Location {item['location_number']}, class {item['class_code']}, territory {item['territory']}"


def _clause_text(item: dict[str, Any], clause_title: str) -> str:
    if item["lob"] == "BOP":
        scope = _clause_scope(item)
        if clause_title == "Scheduled Premises Limitation":
            return (
                f"This provision applies only to {scope} when {item['form_number']} edition "
                f"{item['edition_date']} is attached to the policy."
            )
        if clause_title == "Limit And Deductible Application":
            return (
                f"The scheduled limit of {item['limit']} and deductible of {item['deductible']} "
                f"apply to {item['coverage']} at the described premises."
            )
        if clause_title == "Valuation Records Requirement":
            return (
                f"The insured must keep records supporting the {item['valuation']} valuation basis, "
                f"{item['coinsurance']} coinsurance entry, and {item['business_income_basis']} business income basis."
            )
        return (
            f"If schedules conflict for {scope}, the endorsement or form entry with the later effective date "
            f"controls the affected coverage."
        )
    if item["lob"] == "WC":
        scope = _clause_scope(item)
        if clause_title == "Remuneration Audit":
            return (
                f"The annual payroll of {item['annual_payroll']} for {scope} is an estimate and is subject "
                f"to audit after the policy period."
            )
        if clause_title == "State Classification Control":
            return (
                f"The {item['state']} classification {item['class_code']} controls the rating basis for "
                f"{item['classification']} unless a state amendatory endorsement changes it."
            )
        if clause_title == "Officer And Subcontractor Treatment":
            return (
                f"Officer, member, volunteer, leased-worker, and subcontractor treatment for {scope} must be "
                f"read with the attached forms schedule."
            )
        return (
            f"The estimated premium of {item['estimated_premium']} is calculated from rate {item['manual_rate']}, "
            f"experience modification {item['experience_mod']}, and schedule rating {item['schedule_credit_debit']}."
        )
    scope = _clause_scope(item)
    if clause_title == "Classification And Territory Limitation":
        return (
            f"The {item['classification']} operation applies at {scope} only when the declarations show "
            f"the same exposure basis."
        )
    if clause_title == "Aggregate Limit Application":
        return (
            f"The {item['limit_type']} limit of {item['limit']} applies with the Commercial General Liability "
            f"coverage part and does not increase another aggregate."
        )
    if clause_title == "Additional Insured Contract Gate":
        return (
            f"Additional insured status for {scope} applies only when the contract requirement and attached "
            f"form {item['form_number']} are both satisfied."
        )
    return (
        f"The {item['exclusion_name']} provision and form {item['form_number']} edition {item['edition_date']} "
        f"control before any conflicting summary entry for {scope}."
    )


def build_policy_clause_records_for_item(item: dict[str, Any]) -> list[dict[str, Any]]:
    """Return material clause records that are rendered as prose in the policy packet."""
    clauses: list[dict[str, Any]] = []
    for index, (clause_title, clause_type) in enumerate(CLAUSE_TYPES_BY_LOB[item["lob"]], start=1):
        record = _base_record(item, "policy_clause_item", f"CL-{item['item_id']}-{index:02d}")
        clause_text = _clause_text(item, clause_title)
        record.update(
            {
                "form_number": item["form_number"],
                "edition_date": item["edition_date"],
                "form_title": item["form_title"],
                "clause_title": clause_title,
                "clause_type": clause_type,
                "clause_scope": _clause_scope(item),
                "clause_text": clause_text,
            }
        )
        if item["lob"] == "BOP":
            record.update(
                {
                    "coverage": item["coverage"],
                    "location_number": item["location_number"],
                    "building_number": item["building_number"],
                    "limit": item["limit"],
                    "deductible": item["deductible"],
                }
            )
        elif item["lob"] == "WC":
            record.update(
                {
                    "state": item["state"],
                    "class_code": item["class_code"],
                    "classification": item["classification"],
                    "annual_payroll": item["annual_payroll"],
                    "estimated_premium": item["estimated_premium"],
                }
            )
        else:
            record.update(
                {
                    "class_code": item["class_code"],
                    "classification": item["classification"],
                    "location_number": item["location_number"],
                    "territory": item["territory"],
                    "exclusion_name": item["exclusion_name"],
                    "limit_type": item["limit_type"],
                    "limit": item["limit"],
                }
            )
        clauses.append(record)
    return clauses


def _location_record(item: dict[str, Any]) -> dict[str, Any]:
    if item["lob"] == "BOP":
        record_id = f"LOC-{item['location_number']}-BLDG-{item['building_number']}-{item['item_id']}"
        record = _base_record(item, "policy_location_item", record_id)
        record.update(
            {
                "item_id": item["item_id"],
                "applies_to_record_id": item["item_id"],
                "location_number": item["location_number"],
                "building_number": item["building_number"],
                "premises_address": item["premises_address"],
                "class_code": item["class_code"],
                "classification": item["classification"],
            }
        )
        return record
    if item["lob"] == "WC":
        record_id = f"LOC-{item['location_number']}-{item['state']}-{item['class_code']}-{item['item_id']}"
        record = _base_record(item, "policy_location_item", record_id)
        record.update(
            {
                "item_id": item["item_id"],
                "applies_to_record_id": item["item_id"],
                "location_number": item["location_number"],
                "state": item["state"],
                "class_code": item["class_code"],
                "classification": item["classification"],
                "governing_class": item["governing_class"],
            }
        )
        return record
    record_id = f"LOC-{item['location_number']}-{item['class_code']}-{item['territory']}-{item['item_id']}"
    record = _base_record(item, "policy_location_item", record_id)
    record.update(
        {
            "item_id": item["item_id"],
            "applies_to_record_id": item["item_id"],
            "location_number": item["location_number"],
            "territory": item["territory"],
            "class_code": item["class_code"],
            "classification": item["classification"],
            "exposure_basis": item["exposure_basis"],
        }
    )
    return record


def build_policy_target_records(
    config: PolicyMultiHopCaseConfig,
    primary_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return the heterogeneous list of policy records to extract.

    The benchmark remains a long-list extraction task: systems return one JSON
    list. Policy cases make that list heterogeneous by mixing scheduled
    coverage/class/exposure items with form rows, endorsement rows, premium rows,
    and location/classification rows from the same issued policy.
    """
    records: list[dict[str, Any]] = []
    for item in primary_items:
        records.append(_primary_record(config, item))
    for item in primary_items:
        records.append(_location_record(item))
    for item in primary_items:
        records.append(_form_record(item))
    for item in primary_items:
        endorsement = _endorsement_record(item)
        if endorsement:
            records.append(endorsement)
    for item in primary_items:
        records.append(_premium_record(item))
    for item in primary_items:
        records.extend(build_policy_clause_records_for_item(item))
    records = [_strip_document_record(record, lob=config.lob) for record in records]
    if config.lob == "BOP":
        records = _dedupe_policy_records(records)
    return records


def _strip_document_record(record: dict[str, Any], *, lob: str) -> dict[str, Any]:
    """Remove benchmark-only linkage fields from extraction targets."""
    hidden_fields = {
        "record_id",
        "applies_to_record_id",
    }
    if lob == "BOP":
        hidden_fields.update(
            {
                "item_id",
                "endorsement_number",
                "materiality",
            }
        )
        if record["record_type"] == "bop_coverage_item":
            hidden_fields.add("endorsement_effective_date")
    return {key: value for key, value in record.items() if key not in hidden_fields}


def _dedupe_policy_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[tuple[str, str], ...]] = set()
    for record in records:
        key = tuple(sorted((field, str(value)) for field, value in record.items()))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped
