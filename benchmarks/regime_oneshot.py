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
        _extract_with_gemini_mode,
        _openai_extract_once,
        retry,
        stop_after_attempt,
        wait_exponential,
    )
except ImportError:
    from extraction_core import (
        _extract_with_gemini_mode,
        _openai_extract_once,
        retry,
        stop_after_attempt,
        wait_exponential,
    )

# A whole-document one-shot call must emit every incident, so it needs a much
# larger output budget than a single chunk (8192 would truncate immediately).
_DEFAULT_ONESHOT_MAX_OUTPUT_TOKENS = 32000


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=4, min=10, max=120))
def extract_with_gemini_oneshot(client, ocr_text: str, model_id: str) -> list[dict]:
    """Extract claims using Gemini in full-context one-shot mode."""
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
