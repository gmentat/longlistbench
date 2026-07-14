import json
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import re
from typing import Any

try:
    from .models.loss_run import LossRunIncident
except ImportError:
    from models.loss_run import LossRunIncident


_DATE_FIELDS = {"date_of_loss", "date_reported"}
_OPTIONAL_STR_FIELDS = {
    "cause_code",
    "unit_number",
    "agency",
    "driver_name",
    "adjuster_notes",
}
_BREAKDOWN_KEYS = {"bi", "pd", "lae", "ded"}
_BREAKDOWN_FIELDS = {"reserve", "paid", "recovered", "total_incurred"}
_GENERIC_RECORD_TYPE_FIELD = "record_type"
_GENERIC_MATCH_EXCLUDED_FIELDS = {
    _GENERIC_RECORD_TYPE_FIELD,
    "record_id",
    "applies_to_record_id",
    "lob",
    "policy_number",
    "policy_period",
    "named_insured",
}
_GENERIC_SCORE_EXCLUDED_FIELDS = {
    _GENERIC_RECORD_TYPE_FIELD,
    "record_id",
    "applies_to_record_id",
    "lob",
    "policy_number",
    "policy_period",
    "named_insured",
}
_GENERIC_SIGNATURE_FIELDS = [
    "item_id",
    "incident_number",
    "policy_number",
    "coverage",
    "coverage_part",
    "limit_type",
    "form_number",
    "form_title",
    "location_number",
    "building_number",
    "class_code",
    "state",
    "premises_address",
]
_MAX_MATCH_PAIR_FANOUT = 250
_MAX_MATCH_CANDIDATES = 5_000_000
_REGION_CODES = {
    "alabama": "al",
    "alaska": "ak",
    "alberta": "ab",
    "arizona": "az",
    "arkansas": "ar",
    "british columbia": "bc",
    "california": "ca",
    "colorado": "co",
    "connecticut": "ct",
    "delaware": "de",
    "district of columbia": "dc",
    "florida": "fl",
    "georgia": "ga",
    "hawaii": "hi",
    "idaho": "id",
    "illinois": "il",
    "indiana": "in",
    "iowa": "ia",
    "kansas": "ks",
    "kentucky": "ky",
    "louisiana": "la",
    "maine": "me",
    "manitoba": "mb",
    "maryland": "md",
    "massachusetts": "ma",
    "michigan": "mi",
    "minnesota": "mn",
    "mississippi": "ms",
    "missouri": "mo",
    "montana": "mt",
    "nebraska": "ne",
    "nevada": "nv",
    "new brunswick": "nb",
    "new hampshire": "nh",
    "new jersey": "nj",
    "new mexico": "nm",
    "new york": "ny",
    "newfoundland and labrador": "nl",
    "newfoundland": "nl",
    "north carolina": "nc",
    "north dakota": "nd",
    "northwest territories": "nt",
    "nova scotia": "ns",
    "nunavut": "nu",
    "ohio": "oh",
    "oklahoma": "ok",
    "ontario": "on",
    "oregon": "or",
    "pennsylvania": "pa",
    "prince edward island": "pe",
    "puerto rico": "pr",
    "quebec": "qc",
    "rhode island": "ri",
    "saskatchewan": "sk",
    "south carolina": "sc",
    "south dakota": "sd",
    "tennessee": "tn",
    "texas": "tx",
    "utah": "ut",
    "vermont": "vt",
    "virginia": "va",
    "washington": "wa",
    "washington dc": "dc",
    "west virginia": "wv",
    "wisconsin": "wi",
    "wyoming": "wy",
    "yukon": "yt",
}
_LOB_CODES = {
    "bpp": "bop",
    "businessowners": "bop",
    "businessowners policy": "bop",
    "business owners policy": "bop",
    "commercial general liability": "cgl",
    "workers compensation": "wc",
    "workers compensation and employers liability": "wc",
    "workers' compensation": "wc",
    "workers' compensation and employers liability": "wc",
}


def _normalize_date(value: Any) -> str:
    if value is None:
        return ""
    s = " ".join(str(value).strip().split())
    if not s:
        return ""
    for fmt in (
        "%m/%d/%Y",
        "%m/%d/%y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m-%d-%Y",
    ):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%m/%d/%Y")
        except ValueError:
            continue
    return s


def normalize_incident_number(incident_num: str) -> str:
    if not incident_num:
        return ""
    incident_num = str(incident_num).strip()
    for prefix in ["Incident #", "Incident#", "Incident ", "#", "INC"]:
        if incident_num.casefold().startswith(prefix.casefold()):
            incident_num = incident_num[len(prefix):]
    return incident_num.strip().casefold()


def _norm_str(v: Any, *, optional: bool) -> Any:
    if v is None:
        return None
    s = str(v).strip()
    if optional and s == "":
        return None
    return s.casefold()


def _norm_description(v: Any) -> str:
    return str(_norm_str(v, optional=False)).rstrip(".").strip()


def _norm_unit_number(v: Any) -> Any:
    s = _norm_str(v, optional=True)
    if s is None:
        return None
    match = re.search(r"(\d{5,})$", s)
    return match.group(1) if match else s


def _norm_float(v: Any) -> float:
    try:
        f = float(v)
    except Exception:
        f = 0.0
    f = round(f, 2)
    if f == -0.0:
        f = 0.0
    return f


def _normalize_region(value: Any) -> Any:
    normalized = _norm_str(value, optional=True)
    if normalized is None:
        return None
    parenthetical = re.search(r"\(([a-z]{2})\)\s*$", normalized)
    if parenthetical:
        return parenthetical.group(1)
    return _REGION_CODES.get(normalized, normalized)


def _canonicalize_incident(item: dict) -> dict:
    obj = LossRunIncident.model_validate(item).model_dump(mode="json")

    for k, v in list(obj.items()):
        if k in _BREAKDOWN_KEYS:
            if not isinstance(v, dict):
                v = {}
            b: dict[str, Any] = {}
            for bf in _BREAKDOWN_FIELDS:
                b[bf] = _norm_float(v.get(bf, 0.0))
            obj[k] = b
        elif k == "claimants":
            if not isinstance(v, list):
                v = []
            cleaned = [str(x).strip().casefold() for x in v if str(x).strip()]
            obj[k] = sorted(cleaned)
        elif k in _DATE_FIELDS:
            obj[k] = _normalize_date(v)
        elif k == "description":
            obj[k] = _norm_description(v)
        elif k == "unit_number":
            obj[k] = _norm_unit_number(v)
        elif k in {"policy_state", "loss_state"}:
            obj[k] = _normalize_region(v)
        elif isinstance(v, str) or v is None:
            obj[k] = _norm_str(v, optional=(k in _OPTIONAL_STR_FIELDS))
        else:
            obj[k] = v

    return obj


def _flatten_pairs(incident_id: str, obj: dict) -> list[str]:
    pairs: list[str] = []
    for k, v in obj.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                if k in _BREAKDOWN_KEYS and kk in _BREAKDOWN_FIELDS and _norm_float(vv) == 0.0:
                    continue
                pairs.append(
                    json.dumps(
                        [incident_id, f"{k}.{kk}", vv],
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                )
        else:
            pairs.append(
                json.dumps(
                    [incident_id, k, v],
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
    return pairs


def _exact_record_metrics(exact_matches: int, gold_count: int, predicted_count: int) -> dict[str, Any]:
    """Summarize strict normalized-record recovery independently of field overlap."""
    recall = exact_matches / gold_count if gold_count > 0 else float(predicted_count == 0)
    precision = exact_matches / predicted_count if predicted_count > 0 else float(gold_count == 0)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "exact_record_recall": recall,
        "exact_record_precision": precision,
        "exact_record_f1": f1,
        "complete_document": exact_matches == gold_count == predicted_count,
    }


def evaluate_extraction(predicted: list[dict], ground_truth: list[dict]) -> dict[str, Any]:
    """Evaluate claim incident extraction keyed by unique normalized incident numbers.

    Missing incident numbers are scored as side-specific unmatched rows rather than
    collapsed into a shared empty bucket.
    """
    gt_count = len(ground_truth)
    pred_count = len(predicted)

    gt_by_id: dict[str, list[str]] = {}
    pred_by_id: dict[str, list[str]] = {}
    gt_pairs: list[str] = []
    pred_pairs: list[str] = []

    for idx, item in enumerate(ground_truth):
        obj = _canonicalize_incident(item)
        inc = normalize_incident_number(obj.get("incident_number", ""))
        if not inc:
            inc = f"<missing_ground_truth_incident_number:{idx}>"
        gt_by_id.setdefault(inc, []).append(json.dumps(obj, sort_keys=True, separators=(",", ":")))
        gt_pairs.extend(_flatten_pairs(inc, obj))

    for idx, item in enumerate(predicted):
        obj = _canonicalize_incident(item)
        inc = normalize_incident_number(obj.get("incident_number", ""))
        if not inc:
            inc = f"<missing_predicted_incident_number:{idx}>"
        pred_by_id.setdefault(inc, []).append(json.dumps(obj, sort_keys=True, separators=(",", ":")))
        pred_pairs.extend(_flatten_pairs(inc, obj))

    gt_ids = set(gt_by_id.keys())
    pred_ids = set(pred_by_id.keys())
    missing_ids = sorted(gt_ids - pred_ids)
    extra_ids = sorted(pred_ids - gt_ids)

    exact_record_matches = 0
    for inc in sorted(gt_ids & pred_ids):
        exact_record_matches += sum(
            (Counter(gt_by_id.get(inc, [])) & Counter(pred_by_id.get(inc, []))).values()
        )

    gt_pairs_counter = Counter(gt_pairs)
    pred_pairs_counter = Counter(pred_pairs)
    found_pairs = sum((gt_pairs_counter & pred_pairs_counter).values())

    total_gt_pairs = sum(gt_pairs_counter.values())
    total_pred_pairs = sum(pred_pairs_counter.values())

    recall = found_pairs / total_gt_pairs if total_gt_pairs > 0 else 0.0
    precision = found_pairs / total_pred_pairs if total_pred_pairs > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "ground_truth_count": gt_count,
        "predicted_count": pred_count,
        "found": found_pairs,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "missing": len(missing_ids),
        "extra": len(extra_ids),
        "missing_ids": missing_ids,
        "extra_ids": extra_ids,
        "exact_record_matches": exact_record_matches,
        **_exact_record_metrics(exact_record_matches, gt_count, pred_count),
        "total_gold_field_pairs": total_gt_pairs,
        "total_pred_field_pairs": total_pred_pairs,
    }


def _normalize_decimal_string(value: str) -> str:
    value = value.strip()
    negative = False
    if re.fullmatch(r"\(\s*\$?-?[\d,]+(?:\.\d+)?\s*\)", value):
        negative = True
        value = value.strip()[1:-1].strip()
    if value.startswith("-"):
        negative = True
        value = value[1:].strip()
    try:
        d = Decimal(value.replace(",", "").replace("$", "").strip())
    except InvalidOperation:
        return value
    if negative:
        d = -abs(d)
    normalized = format(d.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized or "0"


def _normalize_generic_scalar(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return _normalize_decimal_string(str(value))
    if isinstance(value, float):
        f = round(value, 6)
        if f == -0.0:
            f = 0.0
        return _normalize_decimal_string(str(f))

    s = " ".join(str(value).strip().split())
    if not s:
        return None

    for fmt in (
        "%m/%d/%Y",
        "%m/%d/%y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m-%d-%Y",
    ):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%m/%d/%Y")
        except ValueError:
            continue

    if "%" in s:
        return re.sub(r"\s+", "", s).casefold()
    decimal_like = bool(re.fullmatch(r"-?\$?\d[\d,]*(?:\.\d+)?", s))
    parenthesized_decimal = bool(re.fullmatch(r"\(\s*\$?-?\d[\d,]*(?:\.\d+)?\s*\)", s))
    if decimal_like or parenthesized_decimal:
        return _normalize_decimal_string(s)
    return s.casefold()


def _canonicalize_generic_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(k): _canonicalize_generic_value(v)
            for k, v in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, list):
        values = [_canonicalize_generic_value(v) for v in value]
        return sorted(values, key=lambda v: json.dumps(v, sort_keys=True, separators=(",", ":")))
    return _normalize_generic_scalar(value)


def _canonicalize_record(item: dict) -> dict:
    canonical: dict[str, Any] = {}
    for k, v in sorted(item.items(), key=lambda item: str(item[0])):
        value = _normalize_generic_field(str(k), _canonicalize_generic_value(v))
        if value is None:
            continue
        canonical[str(k)] = value
    return canonical


def _normalize_generic_field(field: str, value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if field == "vehicle":
        return re.sub(r"^unit\s+", "", value).strip()
    if field == "schedule":
        return re.sub(r"^quarter\s+return\b", "quarterly return", value).strip()
    if field in {"jurisdiction", "state", "policy_state", "loss_state"}:
        return _normalize_region(value)
    if field == "fuel_type":
        parenthetical = re.search(r"\(([a-z0-9-]+)\)\s*$", value)
        if parenthetical:
            return parenthetical.group(1)
        if value == "diesel":
            return "di"
    if field == "lob":
        return _LOB_CODES.get(value, value)
    if field == "policy_period":
        dates = re.findall(
            r"(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})",
            value,
        )
        if len(dates) == 2:
            return f"{_normalize_date(dates[0])} - {_normalize_date(dates[1])}"
    if field == "clause_scope":
        value = re.sub(r"^applies\s+within\s+", "", value).strip()
        return value.split(";", 1)[0].strip()
    return value


def uses_record_evaluator(ground_truth: list[dict]) -> bool:
    if any(isinstance(item, dict) and _GENERIC_RECORD_TYPE_FIELD in item for item in ground_truth):
        return True
    if not ground_truth:
        return False
    dict_rows = [item for item in ground_truth if isinstance(item, dict)]
    if not dict_rows:
        return False
    return not any("incident_number" in item for item in dict_rows)


def normalize_record_predictions(raw: object) -> list[dict]:
    if isinstance(raw, dict) and isinstance(raw.get("records"), list):
        raw = raw["records"]
    if not isinstance(raw, list):
        raise ValueError("Predicted output must be a JSON list of records or an object with a records list")

    normalized: list[dict] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"Record at index {idx} must be an object")
        normalized.append(dict(item))
    return normalized


def _flatten_record_value(field: str, value: Any, out: list[str]) -> None:
    if value is None:
        return
    if isinstance(value, dict):
        for k, v in sorted(value.items(), key=lambda item: str(item[0])):
            _flatten_record_value(f"{field}.{k}", v, out)
        return
    if isinstance(value, list):
        for v in value:
            _flatten_record_value(field, v, out)
        return
    out.append(json.dumps([field, value], sort_keys=True, separators=(",", ":")))


def _record_field_pairs(record: dict, *, exclude_fields: set[str]) -> list[str]:
    pairs: list[str] = []
    for field, value in record.items():
        if field in exclude_fields:
            continue
        _flatten_record_value(field, value, pairs)
    return pairs


def _record_type(record: dict) -> str:
    value = record.get(_GENERIC_RECORD_TYPE_FIELD)
    if value is None:
        return "<missing_record_type>"
    return str(value).strip() or "<missing_record_type>"


def _record_signature(record: dict) -> str:
    parts = [_record_type(record)]
    for field in _GENERIC_SIGNATURE_FIELDS:
        value = record.get(field)
        if value is None:
            continue
        parts.append(f"{field}={value}")
        if len(parts) >= 7:
            break
    if len(parts) > 1:
        return " | ".join(parts)
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
    return f"{parts[0]} | sha1={digest}"


def _greedy_match_records(gt_records: list[dict], pred_records: list[dict]) -> list[tuple[int, int]]:
    gt_match_pairs = [
        Counter(_record_field_pairs(record, exclude_fields=_GENERIC_MATCH_EXCLUDED_FIELDS))
        for record in gt_records
    ]
    pred_match_pairs = [
        Counter(_record_field_pairs(record, exclude_fields=_GENERIC_MATCH_EXCLUDED_FIELDS))
        for record in pred_records
    ]
    gt_score_pairs = [
        Counter(_record_field_pairs(record, exclude_fields=_GENERIC_SCORE_EXCLUDED_FIELDS))
        for record in gt_records
    ]
    pred_score_pairs = [
        Counter(_record_field_pairs(record, exclude_fields=_GENERIC_SCORE_EXCLUDED_FIELDS))
        for record in pred_records
    ]

    pred_pair_index: dict[str, list[tuple[int, int]]] = {}
    for pred_idx, pred_pairs in enumerate(pred_match_pairs):
        for pair, count in pred_pairs.items():
            pred_pair_index.setdefault(pair, []).append((pred_idx, count))

    candidate_match_scores: dict[tuple[int, int], int] = {}
    for gt_idx, gt_pairs in enumerate(gt_match_pairs):
        for pair, gt_count in gt_pairs.items():
            pred_entries = pred_pair_index.get(pair)
            if not pred_entries:
                continue
            if len(pred_entries) > _MAX_MATCH_PAIR_FANOUT:
                continue
            for pred_idx, pred_count in pred_entries:
                candidate_match_scores[(gt_idx, pred_idx)] = (
                    candidate_match_scores.get((gt_idx, pred_idx), 0) + min(gt_count, pred_count)
                )
                if len(candidate_match_scores) > _MAX_MATCH_CANDIDATES:
                    raise ValueError(
                        "Too many candidate record matches; use a narrower prediction set or add discriminating fields"
                    )

    candidates: list[tuple[int, int, int, int]] = []
    for (gt_idx, pred_idx), match_score in candidate_match_scores.items():
        score_pairs = sum((gt_score_pairs[gt_idx] & pred_score_pairs[pred_idx]).values())
        candidates.append((match_score, score_pairs, gt_idx, pred_idx))

    candidates.sort(reverse=True)
    matched_gt: set[int] = set()
    matched_pred: set[int] = set()
    matches: list[tuple[int, int]] = []
    for _match_score, _score_pairs, gt_idx, pred_idx in candidates:
        if gt_idx in matched_gt or pred_idx in matched_pred:
            continue
        matched_gt.add(gt_idx)
        matched_pred.add(pred_idx)
        matches.append((gt_idx, pred_idx))
    return matches


def evaluate_record_extraction(predicted: list[dict], ground_truth: list[dict]) -> dict[str, Any]:
    """Evaluate heterogeneous record lists without relying on hidden record IDs."""
    gt_records = [_canonicalize_record(item) for item in ground_truth]
    pred_records = [_canonicalize_record(item) for item in predicted]

    gt_pairs_by_record = [
        Counter(_record_field_pairs(record, exclude_fields=_GENERIC_SCORE_EXCLUDED_FIELDS))
        for record in gt_records
    ]
    pred_pairs_by_record = [
        Counter(_record_field_pairs(record, exclude_fields=_GENERIC_SCORE_EXCLUDED_FIELDS))
        for record in pred_records
    ]

    found_pairs = 0
    matched_gt: set[int] = set()
    matched_pred: set[int] = set()
    matched_pairs = _greedy_match_records(gt_records, pred_records)

    by_record_type: dict[str, dict[str, Any]] = {}
    for idx, record in enumerate(gt_records):
        record_type = _record_type(record)
        stats = by_record_type.setdefault(
            record_type,
            {
                "ground_truth_count": 0,
                "predicted_count": 0,
                "matched_records": 0,
                "found": 0,
                "total_gold_field_pairs": 0,
                "total_pred_field_pairs": 0,
            },
        )
        stats["ground_truth_count"] += 1
        stats["total_gold_field_pairs"] += sum(gt_pairs_by_record[idx].values())

    for gt_idx, pred_idx in matched_pairs:
        matched_gt.add(gt_idx)
        matched_pred.add(pred_idx)
        overlap = gt_pairs_by_record[gt_idx] & pred_pairs_by_record[pred_idx]
        pair_count = sum(overlap.values())
        found_pairs += pair_count

        record_type = _record_type(gt_records[gt_idx])
        stats = by_record_type.setdefault(
            record_type,
            {
                "ground_truth_count": 0,
                "predicted_count": 0,
                "matched_records": 0,
                "found": 0,
                "total_gold_field_pairs": 0,
                "total_pred_field_pairs": 0,
            },
        )
        stats["predicted_count"] += 1
        stats["matched_records"] += 1
        stats["found"] += pair_count
        stats["total_pred_field_pairs"] += sum(pred_pairs_by_record[pred_idx].values())

    for idx, record in enumerate(pred_records):
        if idx in matched_pred:
            continue
        record_type = _record_type(record)
        stats = by_record_type.setdefault(
            record_type,
            {
                "ground_truth_count": 0,
                "predicted_count": 0,
                "matched_records": 0,
                "found": 0,
                "total_gold_field_pairs": 0,
                "total_pred_field_pairs": 0,
            },
        )
        stats["predicted_count"] += 1
        stats["total_pred_field_pairs"] += sum(pred_pairs_by_record[idx].values())

    for stats in by_record_type.values():
        stats["missing"] = stats["ground_truth_count"] - stats["matched_records"]
        stats["extra"] = stats["predicted_count"] - stats["matched_records"]
        type_gold_pairs = stats["total_gold_field_pairs"]
        type_pred_pairs = stats["total_pred_field_pairs"]
        type_recall = stats["found"] / type_gold_pairs if type_gold_pairs > 0 else 0.0
        type_precision = stats["found"] / type_pred_pairs if type_pred_pairs > 0 else 0.0
        stats["recall"] = type_recall
        stats["precision"] = type_precision
        stats["f1"] = (
            2 * type_precision * type_recall / (type_precision + type_recall)
            if (type_precision + type_recall) > 0
            else 0.0
        )

    gt_pairs_total = sum(sum(pairs.values()) for pairs in gt_pairs_by_record)
    pred_pairs_total = sum(sum(pairs.values()) for pairs in pred_pairs_by_record)
    recall = found_pairs / gt_pairs_total if gt_pairs_total > 0 else 0.0
    precision = found_pairs / pred_pairs_total if pred_pairs_total > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    exact_record_matches = sum(
        (
            Counter(json.dumps(r, sort_keys=True, separators=(",", ":")) for r in gt_records)
            & Counter(json.dumps(r, sort_keys=True, separators=(",", ":")) for r in pred_records)
        ).values()
    )

    missing_ids = [_record_signature(gt_records[i]) for i in sorted(set(range(len(gt_records))) - matched_gt)]
    extra_ids = [_record_signature(pred_records[i]) for i in sorted(set(range(len(pred_records))) - matched_pred)]

    return {
        "ground_truth_count": len(gt_records),
        "predicted_count": len(pred_records),
        "found": found_pairs,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "missing": len(missing_ids),
        "extra": len(extra_ids),
        "missing_ids": missing_ids,
        "extra_ids": extra_ids,
        "exact_record_matches": exact_record_matches,
        **_exact_record_metrics(exact_record_matches, len(gt_records), len(pred_records)),
        "total_gold_field_pairs": gt_pairs_total,
        "total_pred_field_pairs": pred_pairs_total,
        "by_record_type": by_record_type,
    }
