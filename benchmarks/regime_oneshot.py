#!/usr/bin/env python3
"""One-shot full-context extraction regime.

Submits the entire OCR in a single model call (no chunking); truncated JSON is
salvaged by `parse_json_response`. Gemini uses the shared mode engine; OpenAI
uses a single `_openai_extract_once` call with a large output-token budget.
"""

import os
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from .extraction_core import (
        build_record_extraction_prompt,
        _extract_with_gemini_mode,
        _openai_extract_once,
        gemini_thinking_config,
        parse_json_response,
        record_gemini_usage,
        record_trace,
        retry,
        stop_after_attempt,
        wait_exponential,
    )
    from .evaluation_metrics import normalize_record_predictions, uses_record_evaluator
except ImportError:
    from extraction_core import (
        build_record_extraction_prompt,
        _extract_with_gemini_mode,
        _openai_extract_once,
        gemini_thinking_config,
        parse_json_response,
        record_gemini_usage,
        record_trace,
        retry,
        stop_after_attempt,
        wait_exponential,
    )
    from evaluation_metrics import normalize_record_predictions, uses_record_evaluator

# A whole-document one-shot call must emit every incident in a single response.
# Default to the model's hard output ceiling (GPT-5.5 = 128K) so generation stops
# only when the model decides (or hits the model's own maximum), never an
# artificial cap of ours. Override via LLB_ONESHOT_MAX_OUTPUT_TOKENS.
_DEFAULT_ONESHOT_MAX_OUTPUT_TOKENS = 128000
_DEFAULT_GEMINI_ONESHOT_MAX_OUTPUT_TOKENS = 65536


def _extract_records_with_gemini_oneshot(
    client,
    ocr_text: str,
    model_id: str,
    ground_truth: list[dict],
) -> list[dict]:
    """Extract generic records using Gemini in full-context one-shot mode."""
    from google.genai import types

    prompt = build_record_extraction_prompt(ocr_text, ground_truth)
    thinking_config = gemini_thinking_config(model_id)

    max_output_tokens = int(
        os.getenv(
            "LLB_GEMINI_ONESHOT_MAX_OUTPUT_TOKENS",
            str(_DEFAULT_GEMINI_ONESHOT_MAX_OUTPUT_TOKENS),
        )
    )
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            maxOutputTokens=max_output_tokens,
            thinking_config=thinking_config,
            responseMimeType="application/json",
        ),
    )
    record_gemini_usage(response)
    record_trace(
        "gemini_calls.jsonl",
        {
            "model": model_id,
            "input_chars": len(ocr_text),
            "max_output_tokens": max_output_tokens,
            "mode": "generic_oneshot",
        },
    )
    if not response.text:
        finish_reason = None
        if getattr(response, "candidates", None):
            finish_reason = getattr(response.candidates[0], "finish_reason", None)
        raise ValueError(f"Gemini returned no text (finish_reason={finish_reason})")
    return normalize_record_predictions(parse_json_response(response.text))


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=4, min=10, max=120))
def extract_with_gemini_oneshot(
    client,
    ocr_text: str,
    model_id: str,
    *,
    ground_truth: list[dict] | None = None,
    sample: str | None = None,
) -> list[dict]:
    """Extract claims using Gemini in full-context one-shot mode."""
    if ground_truth and uses_record_evaluator(ground_truth):
        return _extract_records_with_gemini_oneshot(client, ocr_text, model_id, ground_truth)
    return _extract_with_gemini_mode(
        client, ocr_text, model_id, allow_chunking=False, structured_output=False
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=60))
def extract_with_openai_oneshot(client, ocr_text: str, model_id: str) -> list[dict]:
    """Extract claims using OpenAI in full-context one-shot mode (single call)."""
    max_output_tokens = int(
        os.getenv("LLB_ONESHOT_MAX_OUTPUT_TOKENS", str(_DEFAULT_ONESHOT_MAX_OUTPUT_TOKENS))
    )
    return _openai_extract_once(
        client, ocr_text, model_id, max_output_tokens=max_output_tokens
    )
