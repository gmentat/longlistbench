"""Gemini-assisted policy prose generation."""

from __future__ import annotations

import hashlib
import json
import os
import re
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
                ):
                    if raw.get(key):
                        page[key] = _sanitize_policy_text(raw[key])
                pages.append(page)
        normalized[kind] = pages
    return normalized


def _build_user_prompt(config: PolicyMultiHopCaseConfig, profile: dict[str, str], items: list[dict[str, Any]]) -> str:
    common_prompt = _read_prompt(PROMPT_FILES["common"])
    lob_prompt = _read_prompt(PROMPT_FILES[config.lob])
    coverage_form_records = []
    if config.lob == "BOP":
        coverage_form_records = [
            {
                "coverage": item["coverage"],
                "form_number": item["form_number"],
                "form_title": item["form_title"],
                "edition_date": item["edition_date"],
                "location_number": item["location_number"],
                "building_number": item["building_number"],
                "limit": item["limit"],
                "deductible": item["deductible"],
                "valuation": item["valuation"],
                "coinsurance": item["coinsurance"],
                "business_income_basis": item["business_income_basis"],
                "class_code": item["class_code"],
                "classification": item["classification"],
            }
            for item in items
        ]
    payload = {
        "case_id": config.id,
        "line_of_business": config.lob,
        "policy_profile": profile,
        "target_record_type": config.target_record_type,
        "target_record_count": len(items),
        "schema_fields": sorted({key for item in items for key in item}),
        "sample_records": items[: min(4, len(items))],
        "coverage_form_records": coverage_form_records,
        "complexity_tags": list(config.complexity_tags),
        "join_requirements": list(config.join_requirements),
    }
    return (
        f"{common_prompt}\n\n"
        f"{lob_prompt}\n\n"
        "Use the following synthetic policy facts as factual anchors. "
        "Do not replace them or invent contradictory values.\n\n"
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
    client = genai.Client(api_key=_gemini_api_key())
    system_prompt = _read_prompt(PROMPT_FILES["system"])
    response = client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.55,
            response_mime_type="application/json",
            thinking_config=_thinking_config(thinking_level),
        ),
        contents=[_build_user_prompt(config, profile, items)],
    )
    raw_text = response.text or ""
    try:
        page_bank = _normalize_page_bank(json.loads(_strip_json_fence(raw_text)))
    except json.JSONDecodeError as exc:
        bad_path = cache_path.with_suffix(".bad.txt")
        bad_path.write_text(raw_text, encoding="utf-8")
        raise RuntimeError(f"Gemini returned invalid JSON for {config.id}; saved raw output to {bad_path}") from exc

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
