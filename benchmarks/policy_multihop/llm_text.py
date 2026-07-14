"""Gemini-assisted policy prose generation."""

from __future__ import annotations

import hashlib
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args: Any, **_kwargs: Any) -> bool:
        return False

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

from .config import PolicyMultiHopCaseConfig


PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
PROMPT_FILES = {
    "system": "policy_writer_system.md",
    "common": "policy_page_bank.md",
    "BOP": "bop_examples.md",
    "WC": "wc_examples.md",
    "CGL": "cgl_examples.md",
}

PAGE_KINDS = ("policy_form", "coverage_form", "notice", "amendatory", "billing", "endorsement")
DEFAULT_GEMINI_MODEL = "gemini-3.1-pro-preview"
DEFAULT_THINKING_LEVEL = "high"
GEMINI_API_KEY_ENV_VARS = ("VERTEX_AI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY")
ORDINARY_PAGE_COUNTS = {"policy_form": 16, "notice": 4, "amendatory": 4, "billing": 4}
ORDINARY_PAGE_BATCH_SIZE = 4
MIN_ORDINARY_PARAGRAPHS = 26
MIN_ORDINARY_WORDS = 540
MAX_ORDINARY_WORDS = 740

FORBIDDEN_PHRASE_REWRITES = {
    r"\bwe will pay those sums that the insured becomes legally obligated to pay\b": (
        "covered liability amounts for which the insured is responsible may be handled"
    ),
    r"\bwe will pay those sums\b": "covered amounts may be handled",
    r"\blegally obligated to pay\b": "responsible for under applicable law",
    r"\bwe will pay for direct physical loss of or damage to\b": (
        "the policy addresses covered physical damage involving"
    ),
    r"\bdirect physical loss of or damage to\b": "covered physical damage involving",
    r"\bcovered cause of loss\b": "covered loss event",
    r"\bthe most we will pay\b": "the applicable ceiling for payment",
    r"\bthe company will pay\b": "the company may apply payment for",
    r"\bcompany will pay\b": "company may apply payment for",
    r"\bright and duty to defend\b": "defense obligation",
    r"\ball other terms and conditions remain unchanged\b": (
        "unmodified policy provisions continue to apply"
    ),
    r"\bcompetent appraiser\b": "qualified appraiser",
    r"\bmechanics\b": "operation",
}


@dataclass(frozen=True)
class PolicyTextBank:
    """Reusable LLM-generated prose drafts for synthetic policy pages."""

    case_id: str
    generator: str
    model: str
    thinking_level: str | None
    prompt_files: tuple[str, ...]
    page_bank: dict[str, list[dict[str, Any]]]

    def pages(self, kind: str) -> list[dict[str, Any]]:
        return self.page_bank.get(kind) or []

    def metadata(self) -> dict[str, Any]:
        return {
            "generator": self.generator,
            "model": self.model,
            "thinking_level": self.thinking_level,
            "prompt_files": list(self.prompt_files),
            "page_kinds": {kind: len(self.page_bank.get(kind, [])) for kind in PAGE_KINDS},
        }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def _prompt_file_list(lob: str) -> tuple[str, ...]:
    return (
        PROMPT_FILES["system"],
        PROMPT_FILES["common"],
        PROMPT_FILES[lob],
    )


def _prompt_digest(
    model: str,
    thinking_level: str,
    config: PolicyMultiHopCaseConfig,
    profile: dict[str, str],
    items: list[dict[str, Any]],
) -> str:
    prompt_text = "\n\n".join(_read_prompt(name) for name in _prompt_file_list(config.lob))
    payload = {
        "model": model,
        "thinking_level": thinking_level,
        "case_id": config.id,
        "lob": config.lob,
        "prompt_text": prompt_text,
        "profile": profile,
        "items": items,
        "schema_fields": sorted({key for item in items for key in item}),
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def _cache_path(
    cache_dir: Path,
    model: str,
    thinking_level: str,
    config: PolicyMultiHopCaseConfig,
    profile: dict[str, str],
    items: list[dict[str, Any]],
) -> Path:
    digest = _prompt_digest(model, thinking_level, config, profile, items)
    safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", model)
    return cache_dir / f"{config.id}.{safe_model}.{digest}.json"


def _strip_json_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def _parse_json_response(text: str) -> dict[str, Any]:
    stripped = _strip_json_fence(text)
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        if exc.msg != "Extra data":
            raise
        parsed, end = json.JSONDecoder().raw_decode(stripped)
        trailing = stripped[end:].strip()
        if trailing and not re.fullmatch(r"[\[\]{},\s]+", trailing):
            raise
    if not isinstance(parsed, dict):
        raise ValueError("Gemini JSON response must be an object")
    return parsed


def _sanitize_policy_text(text: str) -> str:
    clean = str(text).strip()
    clean = clean.replace("**", "")
    clean = re.sub(r"^\s*[-*]\s+", "", clean)
    for pattern, replacement in FORBIDDEN_PHRASE_REWRITES.items():
        clean = re.sub(pattern, replacement, clean, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", clean).strip()


def _normalize_page_bank(data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    normalized: dict[str, list[dict[str, Any]]] = {}
    for kind in PAGE_KINDS:
        pages: list[dict[str, Any]] = []
        raw_pages = data.get(kind) or []
        if not isinstance(raw_pages, list):
            raw_pages = []
        for raw in raw_pages:
            if not isinstance(raw, dict):
                continue
            title = _sanitize_policy_text(raw.get("title") or kind.replace("_", " ").title())
            form_id = _sanitize_policy_text(raw.get("form_id") or kind.upper())
            paragraphs = raw.get("paragraphs") or []
            if not isinstance(paragraphs, list):
                paragraphs = [str(paragraphs)]
            clean_paragraphs = [_sanitize_policy_text(paragraph) for paragraph in paragraphs if str(paragraph).strip()]
            if clean_paragraphs:
                page = {"title": title, "form_id": form_id, "paragraphs": clean_paragraphs}
                for key in (
                    "coverage",
                    "form_number",
                    "form_title",
                    "edition_date",
                    "location_number",
                    "building_number",
                    "subject_key",
                ):
                    if raw.get(key):
                        page[key] = _sanitize_policy_text(raw[key])
                pages.append(page)
        normalized[kind] = pages
    return normalized


def _bop_coverage_form_records(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    seen_coverage_forms: set[tuple[str, str]] = set()
    for item in items:
        key = (str(item["coverage"]), str(item["form_number"]))
        if key in seen_coverage_forms:
            continue
        seen_coverage_forms.add(key)
        records.append(
            {
                "coverage": str(item["coverage"]),
                "form_number": str(item["form_number"]),
                "form_title": str(item["form_title"]),
                "edition_date": str(item["edition_date"]),
                "limit": str(item["limit"]),
                "deductible": str(item["deductible"]),
                "valuation": str(item["valuation"]),
                "coinsurance": str(item["coinsurance"]),
                "business_income_basis": str(item["business_income_basis"]),
                "class_code": str(item["class_code"]),
                "classification": str(item["classification"]),
            }
        )
    return records


def _endorsement_subjects(config: PolicyMultiHopCaseConfig, items: list[dict[str, Any]]) -> list[dict[str, str]]:
    subjects: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        if not item.get("endorsement_number"):
            continue
        if config.lob == "BOP":
            subject_key = str(item["coverage"])
        elif config.lob == "WC":
            subject_key = str(item["form_title"])
        else:
            subject_key = str(item["exclusion_name"])
        if subject_key in seen:
            continue
        seen.add(subject_key)
        subjects.append(
            {
                "subject_key": subject_key,
                "form_number": str(item["form_number"]),
                "form_title": str(item["form_title"]),
                "line_of_business": str(item["lob"]),
            }
        )
    return subjects


def _build_user_prompt(
    config: PolicyMultiHopCaseConfig,
    profile: dict[str, str],
    items: list[dict[str, Any]],
    *,
    coverage_form_records: list[dict[str, str]] | None = None,
    endorsement_subjects: list[dict[str, str]] | None = None,
    generation_scope: str = "full",
    requested_page_counts: dict[str, int] | None = None,
    batch_focus: str | None = None,
) -> str:
    common_prompt = _read_prompt(PROMPT_FILES["common"])
    lob_prompt = _read_prompt(PROMPT_FILES[config.lob])
    if coverage_form_records is None:
        coverage_form_records = _bop_coverage_form_records(items) if config.lob == "BOP" else []
    if endorsement_subjects is None:
        endorsement_subjects = _endorsement_subjects(config, items)
    if requested_page_counts is None:
        requested_page_counts = {}
    payload = {
        "case_id": config.id,
        "line_of_business": config.lob,
        "policy_profile": profile,
        "target_record_type": config.target_record_type,
        "target_record_count": len(items),
        "schema_fields": sorted({key for item in items for key in item}),
        "sample_records": items[: min(4, len(items))],
        "coverage_form_records": coverage_form_records,
        "endorsement_subjects": endorsement_subjects,
        "requested_page_counts": {
            kind: int(requested_page_counts.get(kind, 0)) for kind in PAGE_KINDS
        },
        "batch_focus": batch_focus,
        "complexity_tags": list(config.complexity_tags),
        "join_requirements": list(config.join_requirements),
    }
    if generation_scope == "requested_batch":
        scope_instruction = (
            "Generation scope override: the requested_page_counts object supersedes all default counts in "
            "the shared prompt. Return exactly that many drafts for each key and empty arrays for keys whose "
            "requested count is zero. Keep every draft distinct. For endorsement drafts, return exactly one "
            "draft per supplied endorsement_subjects entry and preserve subject_key exactly."
        )
    elif generation_scope == "policy_bank":
        scope_instruction = (
            "Generation scope override: return the requested policy_form, notice, amendatory, billing, "
            "and endorsement arrays, but return an empty coverage_form array. Coverage forms are generated "
            "in separate bounded requests."
        )
    elif generation_scope == "coverage_only":
        scope_instruction = (
            "Generation scope override: return exactly one coverage_form draft for every "
            "coverage_form_records entry and return empty arrays for policy_form, notice, amendatory, "
            "billing, and endorsement. Preserve each coverage and form metadata value exactly."
        )
    else:
        scope_instruction = "Generate every requested page-bank section."
    return (
        f"{common_prompt}\n\n"
        f"{lob_prompt}\n\n"
        f"{scope_instruction}\n\n"
        "Use the following synthetic policy facts as structural anchors. "
        "Only coverage_form drafts may repeat values from sample_records. Ordinary drafts must remain "
        "policy-level and must not mention a sampled item ID, location, class code, exposure, payroll, "
        "premium, limit, or endorsement date. Do not invent contradictory values.\n\n"
        f"{json.dumps(payload, indent=2, ensure_ascii=False)}"
    )


def _load_cached_bank(path: Path) -> PolicyTextBank:
    data = json.loads(path.read_text(encoding="utf-8"))
    return PolicyTextBank(
        case_id=str(data["case_id"]),
        generator=str(data.get("generator", "gemini")),
        model=str(data.get("model", "")),
        thinking_level=data.get("thinking_level"),
        prompt_files=tuple(data.get("prompt_files", [])),
        page_bank=_normalize_page_bank(data.get("page_bank", {})),
    )


def _gemini_api_key() -> str:
    for env_var in GEMINI_API_KEY_ENV_VARS:
        api_key = os.getenv(env_var)
        if api_key and api_key not in {"your-api-key-here", "your-gemini-api-key"}:
            return api_key
    names = ", ".join(GEMINI_API_KEY_ENV_VARS)
    raise RuntimeError(f"{names} is not set; cannot generate policy prose with Gemini.")


def _thinking_config(thinking_level: str):
    if types is None:
        return None
    normalized = thinking_level.strip().lower()
    if normalized in {"", "none", "off", "disabled"}:
        return None
    if normalized == "auto":
        return types.ThinkingConfig(thinking_budget=-1)
    enum_name = normalized.upper()
    enum_value = getattr(types.ThinkingLevel, enum_name, None)
    if enum_value is None:
        valid = ", ".join(level.lower() for level in ("minimal", "low", "medium", "high", "auto", "none"))
        raise ValueError(f"Unsupported Gemini thinking level '{thinking_level}'. Use one of: {valid}.")
    return types.ThinkingConfig(thinking_level=enum_value)


def _request_gemini_page_bank(
    *,
    model: str,
    thinking_level: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    part_path: Path,
    force: bool,
) -> dict[str, list[dict[str, Any]]]:
    if part_path.exists() and not force:
        return _normalize_page_bank(json.loads(part_path.read_text(encoding="utf-8")))
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.55,
            response_mime_type="application/json",
            thinking_config=_thinking_config(thinking_level),
            max_output_tokens=16384,
        ),
        contents=[user_prompt],
    )
    raw_text = response.text or ""
    try:
        page_bank = _normalize_page_bank(_parse_json_response(raw_text))
    except json.JSONDecodeError as exc:
        bad_path = part_path.with_suffix(".bad.txt")
        bad_path.write_text(raw_text, encoding="utf-8")
        raise RuntimeError(f"Gemini returned invalid JSON; saved raw output to {bad_path}") from exc
    part_path.write_text(json.dumps(page_bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return page_bank


def _validate_bop_coverage_bank(
    pages: list[dict[str, Any]],
    expected_records: list[dict[str, str]],
) -> None:
    expected = {(record["coverage"], record["form_number"]) for record in expected_records}
    actual = {(str(page.get("coverage", "")), str(page.get("form_number", ""))) for page in pages}
    if actual != expected or len(pages) != len(expected_records):
        raise RuntimeError(
            f"Gemini BOP coverage batch mismatch: expected {sorted(expected)}, received {sorted(actual)}"
        )
    sparse = []
    for page in pages:
        paragraphs = page.get("paragraphs", [])
        word_count = sum(len(str(paragraph).split()) for paragraph in paragraphs)
        if len(paragraphs) < 26 or word_count < 650:
            sparse.append((page.get("coverage"), len(paragraphs), word_count))
    if sparse:
        raise RuntimeError(f"Gemini returned sparse BOP coverage forms: {sparse}")


def _validate_requested_page_bank(
    page_bank: dict[str, list[dict[str, Any]]],
    requested_counts: dict[str, int],
    *,
    label: str,
) -> None:
    mismatches = {
        kind: (requested_counts.get(kind, 0), len(page_bank.get(kind, [])))
        for kind in PAGE_KINDS
        if len(page_bank.get(kind, [])) != requested_counts.get(kind, 0)
    }
    if mismatches:
        raise RuntimeError(f"Gemini page-bank count mismatch for {label}: {mismatches}")

    invalid_density: list[tuple[str, int, int, int]] = []
    for kind in ("policy_form", "notice", "amendatory", "billing", "endorsement"):
        for page_index, page in enumerate(page_bank.get(kind, []), start=1):
            paragraphs = page.get("paragraphs", [])
            word_count = sum(len(str(paragraph).split()) for paragraph in paragraphs)
            if (
                len(paragraphs) < MIN_ORDINARY_PARAGRAPHS
                or word_count < MIN_ORDINARY_WORDS
                or word_count > MAX_ORDINARY_WORDS
            ):
                invalid_density.append((kind, page_index, len(paragraphs), word_count))
    if invalid_density:
        raise RuntimeError(
            f"Gemini returned policy pages outside the density bounds for {label}: {invalid_density}"
        )


def _request_batched_policy_bank(
    config: PolicyMultiHopCaseConfig,
    profile: dict[str, str],
    items: list[dict[str, Any]],
    *,
    model: str,
    thinking_level: str,
    system_prompt: str,
    api_key: str,
    cache_path: Path,
    force: bool,
) -> dict[str, list[dict[str, Any]]]:
    requests: list[tuple[str, dict[str, int], list[dict[str, str]], str]] = []
    policy_focuses = (
        "definitions, coverage scope, limits, and conditions",
        "duties after loss, defense, cooperation, and claim administration",
        "records, audit, classification, valuation, and premium",
        "cancellation, transfer, territory, state provisions, and conflicting forms",
    )
    for start in range(0, ORDINARY_PAGE_COUNTS["policy_form"], ORDINARY_PAGE_BATCH_SIZE):
        count = min(ORDINARY_PAGE_BATCH_SIZE, ORDINARY_PAGE_COUNTS["policy_form"] - start)
        requests.append(
            (
                f"policy-form-{start // ORDINARY_PAGE_BATCH_SIZE + 1}",
                {"policy_form": count},
                [],
                policy_focuses[start // ORDINARY_PAGE_BATCH_SIZE],
            )
        )
    for kind in ("notice", "amendatory", "billing"):
        requests.append((kind, {kind: ORDINARY_PAGE_COUNTS[kind]}, [], f"distinct {kind} forms"))

    all_endorsement_subjects = _endorsement_subjects(config, items)
    for start in range(0, len(all_endorsement_subjects), ORDINARY_PAGE_BATCH_SIZE):
        subjects = all_endorsement_subjects[start:start + ORDINARY_PAGE_BATCH_SIZE]
        requests.append(
            (
                f"endorsement-{start // ORDINARY_PAGE_BATCH_SIZE + 1}",
                {"endorsement": len(subjects)},
                subjects,
                "issued endorsement language for only the supplied subjects",
            )
        )

    generated_parts: dict[str, dict[str, list[dict[str, Any]]]] = {}
    with ThreadPoolExecutor(max_workers=min(4, len(requests))) as executor:
        futures = {}
        for label, counts, subjects, focus in requests:
            normalized_counts = {kind: int(counts.get(kind, 0)) for kind in PAGE_KINDS}
            future = executor.submit(
                _request_gemini_page_bank,
                model=model,
                thinking_level=thinking_level,
                system_prompt=system_prompt,
                user_prompt=_build_user_prompt(
                    config,
                    profile,
                    items,
                    coverage_form_records=[],
                    endorsement_subjects=subjects,
                    generation_scope="requested_batch",
                    requested_page_counts=normalized_counts,
                    batch_focus=focus,
                ),
                api_key=api_key,
                part_path=cache_path.with_name(f"{cache_path.stem}.{label}.json"),
                force=force,
            )
            futures[future] = (label, normalized_counts)
        for future in as_completed(futures):
            label, counts = futures[future]
            part = future.result()
            _validate_requested_page_bank(part, counts, label=label)
            generated_parts[label] = part

    page_bank = {kind: [] for kind in PAGE_KINDS}
    for label, _counts, _subjects, _focus in requests:
        part = generated_parts[label]
        for kind in PAGE_KINDS:
            page_bank[kind].extend(part[kind])
    expected_counts = {
        **ORDINARY_PAGE_COUNTS,
        "endorsement": len(all_endorsement_subjects),
    }
    _validate_requested_page_bank(page_bank, expected_counts, label="combined policy bank")
    return page_bank


def generate_gemini_policy_text_bank(
    config: PolicyMultiHopCaseConfig,
    profile: dict[str, str],
    items: list[dict[str, Any]],
    *,
    model: str,
    cache_dir: Path,
    thinking_level: str = DEFAULT_THINKING_LEVEL,
    force: bool = False,
) -> PolicyTextBank:
    """Generate or load reusable synthetic policy prose with Gemini."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = _cache_path(cache_dir, model, thinking_level, config, profile, items)
    if cache_path.exists() and not force:
        return _load_cached_bank(cache_path)

    if genai is None or types is None:
        raise RuntimeError("google-genai is not installed; run `pip install -r benchmarks/requirements.txt`.")

    load_dotenv(_repo_root() / ".env")
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    api_key = _gemini_api_key()
    system_prompt = _read_prompt(PROMPT_FILES["system"])
    page_bank = _request_batched_policy_bank(
        config,
        profile,
        items,
        model=model,
        thinking_level=thinking_level,
        system_prompt=system_prompt,
        api_key=api_key,
        cache_path=cache_path,
        force=force,
    )
    if config.lob == "BOP":
        coverage_records = _bop_coverage_form_records(items)
        chunks = [coverage_records[start:start + 3] for start in range(0, len(coverage_records), 3)]
        requests: list[tuple[str, str, Path]] = []
        for index, chunk in enumerate(chunks, start=1):
            requests.append(
                (
                    f"coverage-{index}",
                    _build_user_prompt(
                        config,
                        profile,
                        items,
                        coverage_form_records=chunk,
                        generation_scope="coverage_only",
                    ),
                    cache_path.with_name(f"{cache_path.stem}.coverage-{index}.json"),
                )
            )
        generated_parts: dict[str, dict[str, list[dict[str, Any]]]] = {}
        with ThreadPoolExecutor(max_workers=min(4, len(requests))) as executor:
            futures = {
                executor.submit(
                    _request_gemini_page_bank,
                    model=model,
                    thinking_level=thinking_level,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    api_key=api_key,
                    part_path=part_path,
                    force=force,
                ): label
                for label, user_prompt, part_path in requests
            }
            for future in as_completed(futures):
                generated_parts[futures[future]] = future.result()
        page_bank["coverage_form"] = []
        for index, chunk in enumerate(chunks, start=1):
            coverage_pages = generated_parts[f"coverage-{index}"]["coverage_form"]
            _validate_bop_coverage_bank(coverage_pages, chunk)
            page_bank["coverage_form"].extend(coverage_pages)
        _validate_bop_coverage_bank(page_bank["coverage_form"], coverage_records)

    bank = PolicyTextBank(
        case_id=config.id,
        generator="gemini",
        model=model,
        thinking_level=thinking_level,
        prompt_files=_prompt_file_list(config.lob),
        page_bank=page_bank,
    )
    cache_path.write_text(
        json.dumps(
            {
                "case_id": bank.case_id,
                "generator": bank.generator,
                "model": bank.model,
                "thinking_level": thinking_level,
                "prompt_files": list(bank.prompt_files),
                "page_bank": bank.page_bank,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return bank
