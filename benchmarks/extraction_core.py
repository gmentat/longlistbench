#!/usr/bin/env python3
"""Regime-agnostic extraction primitives shared across all extraction regimes.

Holds the loss-run schema, JSON parsing/repair, schema validation, the shared
extraction prompt, provider client setup, and the per-provider call engines
(Gemini mode engine + OpenAI single-call). The regime modules
(`regime_oneshot`, `regime_chunked`, `regime_agentic`) build on top of this;
`evaluate_models` re-exports the pieces tests and the API regimes reference.
"""

import contextlib
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from models.loss_run import FinancialBreakdown, LossRunIncident

# Shared retry shim: use tenacity when available, otherwise no-op decorators.
try:
    from tenacity import RetryError, retry, stop_after_attempt, wait_exponential
except ModuleNotFoundError:
    RetryError = None

    def retry(*args, **kwargs):
        def decorator(fn):
            return fn
        return decorator

    def stop_after_attempt(*args, **kwargs):
        return None

    def wait_exponential(*args, **kwargs):
        return None


# ============================================================================
# Usage / cost / trace capture (uniform across all regimes)
# ============================================================================
# Token pricing in USD per 1M tokens (defaults = GPT-5.5 standard). Override via env.
PRICE_INPUT_PER_1M = float(os.getenv("LLB_PRICE_INPUT_PER_1M", "5.0"))
PRICE_CACHED_INPUT_PER_1M = float(os.getenv("LLB_PRICE_CACHED_INPUT_PER_1M", "0.5"))
PRICE_OUTPUT_PER_1M = float(os.getenv("LLB_PRICE_OUTPUT_PER_1M", "30.0"))


@dataclass
class CallUsage:
    """Accumulates token usage across the (possibly chunked) calls of one extraction."""
    requests: int = 0
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0

    def add(self, *, input_tokens=0, cached_input_tokens=0, output_tokens=0, requests=1):
        self.requests += requests
        self.input_tokens += int(input_tokens or 0)
        self.cached_input_tokens += int(cached_input_tokens or 0)
        self.output_tokens += int(output_tokens or 0)

    def cost_usd(self) -> float:
        uncached = max(self.input_tokens - self.cached_input_tokens, 0)
        return round(
            uncached / 1e6 * PRICE_INPUT_PER_1M
            + self.cached_input_tokens / 1e6 * PRICE_CACHED_INPUT_PER_1M
            + self.output_tokens / 1e6 * PRICE_OUTPUT_PER_1M,
            6,
        )

    def as_dict(self) -> dict:
        return {
            "requests": self.requests,
            "input_tokens": self.input_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
        }


# Module-global sink: visible to the extraction worker thread AND its chunk
# sub-threads. Correct for sequential-model runs (one extraction in flight).
_usage_lock = threading.Lock()
_usage_sink: "CallUsage | None" = None


@contextlib.contextmanager
def usage_capture():
    """Capture token usage recorded during the wrapped extraction.

    Yields a CallUsage that the run loop reads afterward. Assumes a single
    extraction is in flight (sequential models); not used for --parallel-models.
    """
    global _usage_sink
    accum = CallUsage()
    with _usage_lock:
        prev = _usage_sink
        _usage_sink = accum
    try:
        yield accum
    finally:
        with _usage_lock:
            _usage_sink = prev


def estimate_cost_usd(*, input_tokens=0, cached_input_tokens=0, output_tokens=0) -> float:
    """USD cost for the given token counts, using the shared PRICE_* rates."""
    u = CallUsage()
    u.add(
        input_tokens=input_tokens,
        cached_input_tokens=cached_input_tokens,
        output_tokens=output_tokens,
    )
    return u.cost_usd()


def record_usage(*, input_tokens=0, cached_input_tokens=0, output_tokens=0, requests=1):
    """Add token usage to the active capture sink (no-op if none active)."""
    with _usage_lock:
        if _usage_sink is not None:
            _usage_sink.add(
                input_tokens=input_tokens,
                cached_input_tokens=cached_input_tokens,
                output_tokens=output_tokens,
                requests=requests,
            )


def record_openai_usage(response) -> None:
    u = getattr(response, "usage", None)
    if u is None:
        return
    ptd = getattr(u, "prompt_tokens_details", None)
    record_usage(
        input_tokens=getattr(u, "prompt_tokens", 0) or 0,
        cached_input_tokens=(getattr(ptd, "cached_tokens", 0) or 0) if ptd is not None else 0,
        output_tokens=getattr(u, "completion_tokens", 0) or 0,
    )


def record_gemini_usage(response) -> None:
    u = getattr(response, "usage_metadata", None)
    if u is None:
        return
    record_usage(
        input_tokens=getattr(u, "prompt_token_count", 0) or 0,
        cached_input_tokens=getattr(u, "cached_content_token_count", 0) or 0,
        output_tokens=getattr(u, "candidates_token_count", 0) or 0,
    )


def record_anthropic_usage(response) -> None:
    u = getattr(response, "usage", None)
    if u is None:
        return
    record_usage(
        input_tokens=getattr(u, "input_tokens", 0) or 0,
        cached_input_tokens=getattr(u, "cache_read_input_tokens", 0) or 0,
        output_tokens=getattr(u, "output_tokens", 0) or 0,
    )


def traces_enabled() -> bool:
    """Debug flag: write per-call/per-run traces when LLB_CAPTURE_TRACES=1."""
    return os.getenv("LLB_CAPTURE_TRACES", "0") == "1"


def trace_dir() -> Path:
    return Path(os.getenv("LLB_TRACE_DIR", str(Path(__file__).resolve().parents[1] / ".traces")))


_trace_lock = threading.Lock()


def record_trace(filename: str, entry: dict) -> None:
    """Append one JSON record to <trace_dir>/<filename> (only when traces enabled)."""
    if not traces_enabled():
        return
    try:
        d = trace_dir()
        d.mkdir(parents=True, exist_ok=True)
        line = json.dumps(entry, default=str)
        with _trace_lock:
            with (d / filename).open("a", encoding="utf-8") as f:
                f.write(line + "\n")
    except Exception:
        pass


# ============================================================================
# Provider client setup
# ============================================================================

def setup_gemini():
    """Configure Gemini API."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment")
    import google.genai as genai
    return genai.Client(api_key=api_key)


def setup_openai():
    """Configure OpenAI API."""
    from openai import OpenAI
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")
    return OpenAI(api_key=api_key)


def setup_anthropic():
    """Configure Anthropic API."""
    import anthropic
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")
    return anthropic.Anthropic(api_key=api_key)


# ============================================================================
# Schema + shared prompt
# ============================================================================

class LossRunExtraction(BaseModel):
    incidents: list[LossRunIncident]


_LOSS_RUN_FIELDS = set(LossRunIncident.model_fields.keys())
_BREAKDOWN_FIELDS = set(FinancialBreakdown.model_fields.keys())
_BREAKDOWN_KEYS = {"bi", "pd", "lae", "ded"}

_LOSS_RUN_EXTRACTION_SCHEMA_JSON = json.dumps(
    LossRunExtraction.model_json_schema(),
    indent=2,
    ensure_ascii=False,
)


EXTRACTION_PROMPT = """Extract all incident records from the following document.

Requirements:
- Return ALL incidents you can find in the document.
- Each incident MUST include ALL fields in the schema.
- When a value is unknown:
  - For required string fields, use "" (empty string), not null.
  - For optional fields, use null.
  - For list fields, use [].
  - For numeric fields, use 0.0.
- Output MUST be valid JSON that conforms to the schema.

Schema (JSON Schema):
{schema_json}

Output JSON shape:
{{
  "incidents": [ ... ]
}}

Document:
{ocr_text}
"""


# ============================================================================
# JSON parsing / repair
# ============================================================================

def _repair_truncated_json(raw: str) -> dict | None:
    """Salvage complete incidents from truncated JSON output.

    When the LLM hits the output-token limit the JSON is cut mid-object.
    This helper finds the last complete incident object in the array and
    returns a valid partial result.
    """
    idx = raw.find('"incidents"')
    if idx == -1:
        return None
    arr_start = raw.find("[", idx)
    if arr_start == -1:
        return None

    # Walk the array region tracking brace depth while respecting JSON strings
    # so that braces inside string values (e.g. descriptions) are ignored.
    search_region = raw[arr_start:]
    last_good = -1
    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(search_region):
        if escape:
            escape = False
            continue
        if ch == "\\":
            if in_string:
                escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                last_good = i
    if last_good == -1:
        return None

    repaired = '{"incidents": ' + search_region[: last_good + 1] + "]}"
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        return None


def parse_json_response(response_text: str) -> Any:
    """Parse JSON from LLM response, handling markdown code blocks."""
    text = response_text.strip()

    code_block_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if code_block_match is not None:
        text = code_block_match.group(1).strip()

    def _repair_common_json_issues(s: str) -> str:
        s = s.strip()
        s = re.sub(r",\s*([}\]])", r"\1", s)
        s = re.sub(r"}\s*{", r"},{", s)
        s = re.sub(r"\]\s*\[", r"],[", s)
        s = re.sub(r'"\s*(?="[^"]*"\s*:)', '",', s)
        s = re.sub(r'\b(true|false|null)\b\s*(?="[^"]*"\s*:)', r"\1,", s)
        s = re.sub(r'(\d+(?:\.\d+)?|\]|\})\s*(?="[^"]*"\s*:)', r"\1,", s)
        return s

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start_candidates = [p for p in (text.find('{'), text.find('[')) if p != -1]
        if not start_candidates:
            raise
        start = min(start_candidates)
        end_obj = text.rfind('}')
        end_arr = text.rfind(']')
        end = max(end_obj, end_arr)
        if end <= start:
            raise

        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            try:
                repaired = _repair_common_json_issues(candidate)
                return json.loads(repaired)
            except json.JSONDecodeError:
                pass

        # Last resort: salvage complete incidents from truncated JSON
        salvaged = _repair_truncated_json(text)
        if salvaged is not None:
            return salvaged
        raise json.JSONDecodeError("Could not parse JSON response", text, 0)


# ============================================================================
# Schema validation
# ============================================================================

def _validate_incident_dict_is_complete(incident: dict) -> None:
    extra = set(incident.keys()) - _LOSS_RUN_FIELDS
    if extra:
        raise ValueError(f"Incident has unexpected fields: {sorted(extra)}")

    missing = _LOSS_RUN_FIELDS - set(incident.keys())
    if missing:
        raise ValueError(f"Incident missing required fields: {sorted(missing)}")

    for breakdown_key in _BREAKDOWN_KEYS:
        if breakdown_key not in incident:
            raise ValueError(f"Incident missing required field: {breakdown_key}")
        breakdown = incident.get(breakdown_key)
        if not isinstance(breakdown, dict):
            raise ValueError(f"Incident field '{breakdown_key}' must be an object")

        b_extra = set(breakdown.keys()) - _BREAKDOWN_FIELDS
        if b_extra:
            raise ValueError(
                f"Incident.{breakdown_key} has unexpected fields: {sorted(b_extra)}"
            )

        b_missing = _BREAKDOWN_FIELDS - set(breakdown.keys())
        if b_missing:
            raise ValueError(
                f"Incident.{breakdown_key} missing required fields: {sorted(b_missing)}"
            )


def _validate_and_normalize_predictions(raw: object) -> list[dict]:
    if isinstance(raw, BaseModel):
        raw = raw.model_dump(mode="json")

    incidents: object
    if isinstance(raw, dict):
        if "incidents" not in raw:
            raise ValueError("Model output must include key 'incidents' (list)")
        extra_top_level = set(raw.keys()) - {"incidents"}
        if extra_top_level:
            raise ValueError(
                f"Model output has unexpected top-level keys: {sorted(extra_top_level)}"
            )
        incidents = raw.get("incidents")
    elif isinstance(raw, list):
        incidents = raw
    else:
        raise ValueError("Model output must be either a list of incidents or an object with key 'incidents'")

    if not isinstance(incidents, list):
        raise ValueError("Model output 'incidents' must be a list")

    normalized: list[dict] = []
    for idx, item in enumerate(incidents):
        if not isinstance(item, dict):
            raise ValueError(f"Incident at index {idx} must be an object")
        _validate_incident_dict_is_complete(item)
        try:
            model_obj = LossRunIncident.model_validate(item)
        except ValidationError as e:
            raise ValueError(f"Incident at index {idx} failed schema validation: {e}") from e
        normalized.append(model_obj.model_dump(mode="json"))

    return normalized


# ============================================================================
# Chunking helpers (shared by the chunked regime + Gemini engine)
# ============================================================================

_DEFAULT_GEMINI_CHUNK_MAX_INPUT_TOKENS = 12000


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=2, max=30))
def _count_gemini_tokens(client, model_id: str, text: str) -> int:
    response = client.models.count_tokens(model=model_id, contents=text)
    total_tokens = getattr(response, "total_tokens", None)
    if total_tokens is None:
        raise ValueError("Gemini count_tokens response did not include total_tokens")
    return int(total_tokens)


def _split_ocr_into_token_chunks(
    client,
    model_id: str,
    ocr_text: str,
    *,
    max_chunk_tokens: int,
) -> list[str]:
    if not ocr_text:
        return []

    chunks: list[str] = []
    start = 0
    text_len = len(ocr_text)
    while start < text_len:
        lo = start + 1
        hi = text_len
        best_end = start + 1

        while lo <= hi:
            mid = (lo + hi) // 2
            candidate = ocr_text[start:mid]
            if _count_gemini_tokens(client, model_id, candidate) <= max_chunk_tokens:
                best_end = mid
                lo = mid + 1
            else:
                hi = mid - 1

        chunks.append(ocr_text[start:best_end])
        start = best_end

    return chunks


def _split_text_into_char_chunks(
    text: str,
    *,
    max_chunk_chars: int = 60000,
) -> list[str]:
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(text_len, start + max_chunk_chars)
        chunks.append(text[start:end])
        start = end
    return chunks


def _should_chunk_by_chars(text: str, *, max_chunk_chars: int = 60000) -> bool:
    return len(text) > max_chunk_chars


def _concatenate_incident_lists(incidents: list[list[dict]]) -> list[dict]:
    combined: list[dict] = []
    for chunk_list in incidents:
        combined.extend(chunk_list)
    return combined


# ============================================================================
# Provider call engines (used by the regime modules)
# ============================================================================

def _extract_with_gemini_mode(
    client,
    ocr_text: str,
    model_id: str,
    *,
    allow_chunking: bool,
    structured_output: bool,
) -> list[dict]:
    """Gemini engine shared by the one-shot and chunked regimes."""
    from google.genai import types

    def _extract_chunk(chunk_text: str) -> list[dict]:
        prompt = EXTRACTION_PROMPT.format(
            ocr_text=chunk_text,
            schema_json=_LOSS_RUN_EXTRACTION_SCHEMA_JSON,
        )
        thinking_config = None
        if "flash" in model_id:
            thinking_config = types.ThinkingConfig(thinking_budget=0)

        config_kwargs = {
            "temperature": 0,
            "maxOutputTokens": 8192,
            "thinking_config": thinking_config,
        }
        if structured_output:
            config_kwargs["responseMimeType"] = "application/json"
            config_kwargs["responseSchema"] = LossRunExtraction

        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        record_gemini_usage(response)
        record_trace("gemini_calls.jsonl", {"model": model_id, "input_chars": len(chunk_text)})
        if structured_output:
            parsed = getattr(response, "parsed", None)
            raw = parsed if parsed is not None else parse_json_response(response.text)
        else:
            raw = parse_json_response(response.text)
        return _validate_and_normalize_predictions(raw)

    if not allow_chunking:
        return _extract_chunk(ocr_text)

    max_chunk_tokens = int(
        os.getenv("LLB_GEMINI_CHUNK_MAX_INPUT_TOKENS", str(_DEFAULT_GEMINI_CHUNK_MAX_INPUT_TOKENS))
    )
    if _count_gemini_tokens(client, model_id, ocr_text) <= max_chunk_tokens:
        return _extract_chunk(ocr_text)

    chunks = _split_ocr_into_token_chunks(
        client,
        model_id,
        ocr_text,
        max_chunk_tokens=max_chunk_tokens,
    )
    max_workers = int(os.getenv("LLB_GEMINI_CHUNK_WORKERS", "2"))
    per_chunk: list[list[dict]] = [None] * len(chunks)
    if max_workers <= 1 or len(chunks) <= 1:
        for i, chunk in enumerate(chunks):
            per_chunk[i] = _extract_chunk(chunk)
    else:
        with ThreadPoolExecutor(max_workers=min(max_workers, len(chunks))) as ex:
            futures = [ex.submit(_extract_chunk, chunk) for chunk in chunks]
            for i, fut in enumerate(futures):
                per_chunk[i] = fut.result()
    return _concatenate_incident_lists(per_chunk)


def _openai_supports_custom_temperature(model_id: str) -> bool:
    """Reasoning-family models (gpt-5.x, o-series) only allow the default temperature."""
    m = model_id.lower()
    return not (
        m.startswith("gpt-5")
        or m.startswith("o1")
        or m.startswith("o3")
        or m.startswith("o4")
    )


def _openai_extract_once(
    client,
    text: str,
    model_id: str,
    *,
    max_output_tokens: int = 8192,
) -> list[dict]:
    """One OpenAI call on a single text blob → validated incidents.

    Used per-chunk by the chunked regime and once (with a large output budget)
    by the one-shot regime. Structured-parse first, JSON-mode fallback.
    """
    prompt = EXTRACTION_PROMPT.format(
        ocr_text=text,
        schema_json=_LOSS_RUN_EXTRACTION_SCHEMA_JSON,
    )
    # gpt-5.x / o-series reject temperature=0; omit it so they use the default.
    common_kwargs: dict = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": max_output_tokens,
    }
    if _openai_supports_custom_temperature(model_id):
        common_kwargs["temperature"] = 0
    try:
        response = client.beta.chat.completions.parse(
            response_format=LossRunExtraction,
            **common_kwargs,
        )
        record_openai_usage(response)
        parsed = getattr(response.choices[0].message, "parsed", None)
        if parsed is not None:
            raw = parsed
        else:
            raw = parse_json_response(response.choices[0].message.content)
    except Exception:
        # Some models do not support the structured parse endpoint; fall back to JSON mode.
        response = client.chat.completions.create(
            response_format={"type": "json_object"},
            **common_kwargs,
        )
        record_openai_usage(response)
        raw = parse_json_response(response.choices[0].message.content)
    record_trace("openai_calls.jsonl", {
        "model": model_id,
        "input_chars": len(text),
        "max_output_tokens": max_output_tokens,
    })
    return _validate_and_normalize_predictions(raw)
