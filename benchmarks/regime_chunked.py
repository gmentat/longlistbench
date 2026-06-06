#!/usr/bin/env python3
"""Auto-chunked extraction regime.

Splits long OCR into fixed-budget chunks, extracts each chunk independently
(in parallel), and concatenates the per-chunk incident lists. Gemini chunks by
token budget (via the shared mode engine); OpenAI/Anthropic chunk by characters.
"""

import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from .extraction_core import (
        EXTRACTION_PROMPT,
        _LOSS_RUN_EXTRACTION_SCHEMA_JSON,
        _concatenate_incident_lists,
        _extract_with_gemini_mode,
        _openai_extract_once,
        _should_chunk_by_chars,
        _split_text_into_char_chunks,
        _validate_and_normalize_predictions,
        parse_json_response,
        record_anthropic_usage,
        record_trace,
        retry,
        stop_after_attempt,
        wait_exponential,
    )
except ImportError:
    from extraction_core import (
        EXTRACTION_PROMPT,
        _LOSS_RUN_EXTRACTION_SCHEMA_JSON,
        _concatenate_incident_lists,
        _extract_with_gemini_mode,
        _openai_extract_once,
        _should_chunk_by_chars,
        _split_text_into_char_chunks,
        _validate_and_normalize_predictions,
        parse_json_response,
        record_anthropic_usage,
        record_trace,
        retry,
        stop_after_attempt,
        wait_exponential,
    )


def _run_char_chunked(ocr_text: str, extract_one, *, workers: int) -> list[dict]:
    """Shared char-chunk orchestration: split → extract each → concatenate."""
    if not _should_chunk_by_chars(ocr_text):
        return extract_one(ocr_text)

    chunks = _split_text_into_char_chunks(ocr_text)
    per_chunk: list[list[dict]] = [None] * len(chunks)
    if workers <= 1 or len(chunks) <= 1:
        for i, chunk in enumerate(chunks):
            per_chunk[i] = extract_one(chunk)
    else:
        with ThreadPoolExecutor(max_workers=min(workers, len(chunks))) as ex:
            futures = [ex.submit(extract_one, chunk) for chunk in chunks]
            for i, fut in enumerate(futures):
                per_chunk[i] = fut.result()
    return _concatenate_incident_lists(per_chunk)


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=4, min=10, max=120))
def extract_with_gemini(client, ocr_text: str, model_id: str) -> list[dict]:
    """Extract claims using Gemini with token-budget chunking."""
    return _extract_with_gemini_mode(
        client, ocr_text, model_id, allow_chunking=True, structured_output=True
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=60))
def extract_with_openai(client, ocr_text: str, model_id: str) -> list[dict]:
    """Extract claims using OpenAI with character chunking."""
    workers = int(os.getenv("LLB_OPENAI_CHUNK_WORKERS", "4"))
    return _run_char_chunked(
        ocr_text,
        lambda text: _openai_extract_once(client, text, model_id),
        workers=workers,
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=60))
def extract_with_anthropic(client, ocr_text: str, model_id: str) -> list[dict]:
    """Extract claims using Anthropic Claude with character chunking."""

    def _extract_chunk(chunk_text: str) -> list[dict]:
        prompt = EXTRACTION_PROMPT.format(
            ocr_text=chunk_text,
            schema_json=_LOSS_RUN_EXTRACTION_SCHEMA_JSON,
        )
        response = client.messages.create(
            model=model_id,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )
        record_anthropic_usage(response)
        record_trace("anthropic_calls.jsonl", {"model": model_id, "input_chars": len(chunk_text)})
        raw = parse_json_response(response.content[0].text)
        return _validate_and_normalize_predictions(raw)

    workers = int(os.getenv("LLB_ANTHROPIC_CHUNK_WORKERS", "2"))
    return _run_char_chunked(ocr_text, _extract_chunk, workers=workers)
