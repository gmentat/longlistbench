#!/usr/bin/env python3
"""Multi-model evaluation script for the LongListBench benchmark."""

import argparse
import contextlib
import inspect
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from .evaluation_metrics import (
        evaluate_extraction,
        evaluate_record_extraction,
        normalize_record_predictions,
        uses_record_evaluator,
    )
except ImportError:
    from evaluation_metrics import (
        evaluate_extraction,
        evaluate_record_extraction,
        normalize_record_predictions,
        uses_record_evaluator,
    )

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

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

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


if load_dotenv is not None:
    _REPO_ROOT = Path(__file__).resolve().parents[1]
    load_dotenv(_REPO_ROOT / ".env")
    load_dotenv(Path(__file__).parent / ".env")

# ============================================================================
# Model registry
# ============================================================================

@dataclass
class ModelConfig:
    name: str
    provider: str
    model_id: str
    setup_fn: Callable
    extract_fn: Callable


# ============================================================================
# Extraction regimes — shared core + one module per regime
# ============================================================================
try:
    from .extraction_core import (
        EXTRACTION_PROMPT,
        LossRunExtraction,
        _BREAKDOWN_FIELDS,
        _BREAKDOWN_KEYS,
        _LOSS_RUN_EXTRACTION_SCHEMA_JSON,
        _LOSS_RUN_FIELDS,
        _repair_truncated_json,
        _validate_and_normalize_predictions,
        _validate_incident_dict_is_complete,
        parse_json_response,
        setup_anthropic,
        setup_gemini,
        setup_openai,
        usage_capture,
    )
    from .regime_oneshot import extract_with_gemini_oneshot, extract_with_openai_oneshot
    from .regime_chunked import (
        extract_with_anthropic,
        extract_with_gemini,
        extract_with_openai,
    )
    from .regime_agentic import extract_with_openai_agent, setup_openai_agent
except ImportError:
    from extraction_core import (
        EXTRACTION_PROMPT,
        LossRunExtraction,
        _BREAKDOWN_FIELDS,
        _BREAKDOWN_KEYS,
        _LOSS_RUN_EXTRACTION_SCHEMA_JSON,
        _LOSS_RUN_FIELDS,
        _repair_truncated_json,
        _validate_and_normalize_predictions,
        _validate_incident_dict_is_complete,
        parse_json_response,
        setup_anthropic,
        setup_gemini,
        setup_openai,
        usage_capture,
    )
    from regime_oneshot import extract_with_gemini_oneshot, extract_with_openai_oneshot
    from regime_chunked import (
        extract_with_anthropic,
        extract_with_gemini,
        extract_with_openai,
    )
    from regime_agentic import extract_with_openai_agent, setup_openai_agent



MODELS = {
    'gemini': ModelConfig(
        name='Gemini Pro Preview',
        provider='Google',
        model_id=os.getenv('GEMINI_MODEL_ID', 'gemini-3.1-pro-preview'),
        setup_fn=setup_gemini,
        extract_fn=extract_with_gemini,
    ),
    'gemini_oneshot': ModelConfig(
        name='Gemini Pro Preview (One-shot)',
        provider='Google',
        model_id=os.getenv('GEMINI_ONESHOT_MODEL_ID', os.getenv('GEMINI_MODEL_ID', 'gemini-3.1-pro-preview')),
        setup_fn=setup_gemini,
        extract_fn=extract_with_gemini_oneshot,
    ),
    # Alias for backwards compatibility
    'gemini25': ModelConfig(
        name='Gemini Pro Preview',
        provider='Google',
        model_id=os.getenv('GEMINI_25_MODEL_ID', os.getenv('GEMINI_MODEL_ID', 'gemini-3.1-pro-preview')),
        setup_fn=setup_gemini,
        extract_fn=extract_with_gemini,
    ),
    'gpt52': ModelConfig(
        name='GPT-5.2',
        provider='OpenAI',
        model_id='gpt-5.2',
        setup_fn=setup_openai,
        extract_fn=extract_with_openai,
    ),
    'gpt4': ModelConfig(
        name='GPT-4o',
        provider='OpenAI',
        model_id='gpt-4o',
        setup_fn=setup_openai,
        extract_fn=extract_with_openai,
    ),
    'claude': ModelConfig(
        name='Claude Sonnet 4',
        provider='Anthropic',
        model_id='claude-sonnet-4-20250514',
        setup_fn=setup_anthropic,
        extract_fn=extract_with_anthropic,
    ),
    # GPT-5.5 across all three regimes (one model, three extraction strategies).
    'gpt55_oneshot': ModelConfig(
        name='GPT-5.5 (One-shot)',
        provider='OpenAI',
        model_id=os.getenv('GPT55_MODEL_ID', 'gpt-5.5'),
        setup_fn=setup_openai,
        extract_fn=extract_with_openai_oneshot,
    ),
    'gpt55_chunked': ModelConfig(
        name='GPT-5.5 (Auto-chunked)',
        provider='OpenAI',
        model_id=os.getenv('GPT55_MODEL_ID', 'gpt-5.5'),
        setup_fn=setup_openai,
        extract_fn=extract_with_openai,
    ),
    'gpt55_agent': ModelConfig(
        name='GPT-5.5 (Agentic Sandbox)',
        provider='OpenAI',
        model_id=os.getenv('GPT55_AGENT_MODEL_ID', 'gpt-5.5'),
        setup_fn=setup_openai_agent,
        extract_fn=extract_with_openai_agent,
    ),
}


# ============================================================================
# Evaluation Logic
# ============================================================================

# ============================================================================
# Main Evaluation Runner
# ============================================================================

@dataclass
class EvaluationResult:
    model: str
    sample: str
    tier: str
    format: str
    metrics: dict
    extraction_time: float
    error: str = None
    transcript: str = "ocr"
    tokens: dict = None
    cost_usd: float = None


_QUICK_SAMPLES = [
    "loss_run_external_002",
    "ifta_mileage_by_vehicle_008",
    "multihop_025_001_crosspage",
    "mixed_cgl_040_001",
]


@dataclass(frozen=True)
class EvaluationInput:
    sample: str
    tier: str
    format: str
    transcript: str


def _transcript_input_path(claims_dir: Path, sample: str, transcript: str) -> Path:
    return transcript_path(claims_dir, sample, transcript)


def _prediction_output_path(output_dir: Path, sample: str, transcript: str, model_key: str) -> Path:
    return output_dir / f"{sample}_{transcript}_{model_key}_predicted.json"


def _legacy_prediction_output_path(output_dir: Path, sample: str, transcript: str, model_key: str) -> Path | None:
    if transcript != "ocr":
        return None
    return output_dir / f"{sample}_{model_key}_predicted.json"


def _metadata_key(sample: str | None, transcript: str | None, model: str | None) -> tuple[str, str, str] | None:
    if not sample or not model:
        return None
    return (sample, transcript or "ocr", model)


def _remember_saved_result_metadata(
    lookup: dict[tuple[str, str, str], dict],
    entry: dict,
) -> None:
    if entry.get("error"):
        return
    key = _metadata_key(entry.get("sample"), entry.get("transcript", "ocr"), entry.get("model"))
    if key is None:
        return

    metadata = lookup.setdefault(key, {})
    extraction_time = entry.get("extraction_time")
    if "extraction_time" not in metadata and extraction_time is not None:
        try:
            t = float(extraction_time)
            if t > 0:
                metadata["extraction_time"] = t
        except (TypeError, ValueError):
            pass

    if "tokens" not in metadata and entry.get("tokens") is not None:
        metadata["tokens"] = entry.get("tokens")
    if "cost_usd" not in metadata and entry.get("cost_usd") is not None:
        metadata["cost_usd"] = entry.get("cost_usd")


def _load_saved_result_metadata(
    *,
    output_dir: Path,
    previous_report_path: Path | None = None,
) -> dict[tuple[str, str, str], dict]:
    """Recover timing/token/cost metadata from existing reports when predictions are reused."""
    lookup: dict[tuple[str, str, str], dict] = {}
    current_report_path = output_dir / "evaluation_report.json"

    report_paths: list[Path] = [current_report_path]
    if previous_report_path is not None:
        try:
            if previous_report_path.resolve() != current_report_path.resolve():
                report_paths.append(previous_report_path)
        except Exception:
            report_paths.append(previous_report_path)

    for report_path in report_paths:
        if report_path.exists():
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
                for entry in report.get("detailed_results", []):
                    _remember_saved_result_metadata(lookup, entry)
            except Exception:
                pass

    try:
        repo_root = Path(__file__).resolve().parent.parent
        rel_report_path = current_report_path.resolve().relative_to(repo_root)
        head_json = subprocess.check_output(
            [
                "git",
                "-C",
                str(repo_root),
                "show",
                f"HEAD:{rel_report_path.as_posix()}",
            ],
            text=True,
        )
        head_report = json.loads(head_json)
        for entry in head_report.get("detailed_results", []):
            _remember_saved_result_metadata(lookup, entry)
    except Exception:
        pass

    return lookup


def _discover_evaluation_inputs(
    *,
    claims_dir: Path,
    samples: list[str] | None,
    tiers: list[str] | None,
    formats: list[str] | None,
    transcripts: list[str] | None,
) -> list[EvaluationInput]:
    transcript_list = transcripts or ["ocr"]
    out: list[EvaluationInput] = []

    if samples is None:
        sample_names = set()
        for transcript in transcript_list:
            for transcript_path in iter_transcript_paths(claims_dir, transcript):
                if transcript_path.stat().st_size <= 0:
                    continue
                sample = sample_id_from_transcript_path(claims_dir, transcript_path, transcript)
                json_file = ground_truth_path(claims_dir, sample)
                if not json_file.exists():
                    continue
                tier, fmt = get_sample_info(sample)
                if (tiers is None or tier in tiers) and (formats is None or fmt in formats):
                    sample_names.add(sample)
        ordered_samples = sorted(sample_names)
    else:
        ordered_samples = list(samples)

    for sample in ordered_samples:
        tier, fmt = get_sample_info(sample)
        if tiers is not None and tier not in tiers:
            continue
        if formats is not None and fmt not in formats:
            continue
        for transcript in transcript_list:
            transcript_path = _transcript_input_path(claims_dir, sample, transcript)
            json_file = ground_truth_path(claims_dir, sample)
            if transcript_path.exists() and transcript_path.stat().st_size > 0 and json_file.exists():
                out.append(EvaluationInput(sample=sample, tier=tier, format=fmt, transcript=transcript))

    return out


def get_sample_info(sample_name: str) -> tuple[str, str]:
    """Extract tier and format from sample name."""
    if sample_name.startswith(
        (
            "driver_mvr_packet_",
            "driver_schedule_sparse_",
            "ifta_",
            "loss_run_external_",
            "vehicle_schedule_sparse_",
        )
    ):
        return "core_operations", "production_like_pdf"
    if sample_name.startswith(("multihop_bop_", "multihop_wc_", "mixed_cgl_")):
        return "policy_packets", "crosspage"
    if sample_name.startswith(("multihop_", "mixed_")):
        return "claim_multihop", "crosspage"

    parts = sample_name.split('_')
    tier = parts[0]
    fmt = parts[-1]
    return tier, fmt


def _validate_predictions_for_ground_truth(raw: object, ground_truth: list[dict]) -> list[dict]:
    if uses_record_evaluator(ground_truth):
        return normalize_record_predictions(raw)
    return _validate_and_normalize_predictions(raw)


def _evaluate_predictions_for_ground_truth(predicted: list[dict], ground_truth: list[dict]) -> dict:
    if uses_record_evaluator(ground_truth):
        return evaluate_record_extraction(predicted, ground_truth)
    return evaluate_extraction(predicted, ground_truth)


def _record_label_for_ground_truth(ground_truth: list[dict]) -> str:
    return "records" if uses_record_evaluator(ground_truth) else "claims"


def _call_extract_fn(
    extract_fn: Callable,
    client: object,
    transcript_text: str,
    model_id: str,
    *,
    ground_truth: list[dict],
    sample: str,
) -> object:
    """Call an extraction function, passing benchmark context when supported."""
    try:
        params = inspect.signature(extract_fn).parameters
    except (TypeError, ValueError):
        params = {}

    kwargs = {}
    if "ground_truth" in params:
        kwargs["ground_truth"] = ground_truth
    if "sample" in params:
        kwargs["sample"] = sample
    return extract_fn(client, transcript_text, model_id, **kwargs)


def run_evaluation(
    models: list[str],
    samples: list[str] = None,
    tiers: list[str] = None,
    formats: list[str] = None,
    transcripts: list[str] = None,
    claims_dir: Path = None,
    output_dir: Path = None,
    parallel_models: bool = False,
    model_workers: int | None = None,
    resume: bool = True,
) -> list[EvaluationResult]:
    """Run evaluation across specified models and samples."""
    
    if claims_dir is None:
        claims_dir = default_dataset_dir()
    if output_dir is None:
        output_dir = Path(__file__).parent / "results" / "scratch"
    
    output_dir.mkdir(parents=True, exist_ok=True)

    eval_inputs = _discover_evaluation_inputs(
        claims_dir=claims_dir,
        samples=samples,
        tiers=tiers,
        formats=formats,
        transcripts=transcripts,
    )

    preview = [f"{entry.sample} ({entry.transcript})" for entry in eval_inputs[:5]]
    print(f"Evaluating {len(eval_inputs)} sample/transcript inputs across {len(models)} models")
    print(f"Samples: {', '.join(preview)}{'...' if len(eval_inputs) > 5 else ''}")
    print()
    
    # Setup models
    clients = {}
    for model_key in models:
        if model_key not in MODELS:
            print(f"⚠ Unknown model: {model_key}")
            continue
        config = MODELS[model_key]
        try:
            print(f"Setting up {config.name}...")
            clients[model_key] = config.setup_fn()
            print(f"  ✓ {config.name} ready")
        except Exception as e:
            print(f"  ✗ {config.name} failed: {e}")
    
    print()

    results = []

    active_models = [m for m in models if m in clients]
    total_pairs = len(eval_inputs) * len(active_models)
    if resume and total_pairs > 0:
        existing_pairs = 0
        for entry in eval_inputs:
            for model_key in active_models:
                pred_path = _prediction_output_path(output_dir, entry.sample, entry.transcript, model_key)
                legacy_path = _legacy_prediction_output_path(output_dir, entry.sample, entry.transcript, model_key)
                if pred_path.exists() and pred_path.stat().st_size > 0:
                    existing_pairs += 1
                elif legacy_path is not None and legacy_path.exists() and legacy_path.stat().st_size > 0:
                    existing_pairs += 1
        print(f"Resume enabled: {existing_pairs}/{total_pairs} prediction files already exist")
        print()

    if not parallel_models:
        parallel_models = os.getenv("LLB_PARALLEL_MODELS", "0") == "1"

    if model_workers is None:
        model_workers = int(os.getenv("LLB_MODEL_WORKERS", str(len(models))))
    model_workers = max(1, int(model_workers))
    saved_metadata = _load_saved_result_metadata(output_dir=output_dir)

    gemini_rate_lock = threading.Lock()
    gemini_next_allowed_time = 0.0

    def _gemini_rate_limit() -> None:
        nonlocal gemini_next_allowed_time
        with gemini_rate_lock:
            now = time.time()
            if now < gemini_next_allowed_time:
                time.sleep(gemini_next_allowed_time - now)
            gemini_next_allowed_time = time.time() + 5.0
    
    pair_index = 0

    for sample_idx, entry in enumerate(eval_inputs, start=1):
        print(f"{'='*70}")
        print(f"Sample: {entry.sample} [{entry.transcript}] ({sample_idx}/{len(eval_inputs)})")
        print(f"{'='*70}")

        transcript_path = _transcript_input_path(claims_dir, entry.sample, entry.transcript)
        json_path = ground_truth_path(claims_dir, entry.sample)

        transcript_text = transcript_path.read_text(encoding='utf-8')
        with open(json_path) as f:
            ground_truth = json.load(f)
        
        record_label = _record_label_for_ground_truth(ground_truth)
        print(f"  Ground truth: {len(ground_truth)} {record_label}")
        print(f"  {entry.transcript} text: {len(transcript_text):,} characters")
        print()

        def _eval_one_model(model_key: str) -> EvaluationResult:
            config = MODELS[model_key]
            client = clients[model_key]

            if model_key.startswith("gemini"):
                _gemini_rate_limit()

            start_time = time.time()
            error = None
            predicted: list[dict] = []
            usage_accum = None
            try:
                extract_timeout_s = float(os.getenv("LLB_EXTRACT_TIMEOUT_SECONDS", "1800"))
                heartbeat_s = float(os.getenv("LLB_EXTRACT_HEARTBEAT_SECONDS", "30"))

                def _do_extract() -> object:
                    return _call_extract_fn(
                        config.extract_fn,
                        client,
                        transcript_text,
                        config.model_id,
                        ground_truth=ground_truth,
                        sample=entry.sample,
                    )

                # Token/cost capture uses a module-global sink, so it's only correct
                # when one extraction is in flight (sequential models). Skip it under
                # --parallel-models to avoid cross-model attribution.
                _capture = contextlib.nullcontext() if parallel_models else usage_capture()
                with ThreadPoolExecutor(max_workers=1) as _ex, _capture as usage_accum:
                    _fut = _ex.submit(_do_extract)
                    raw_predicted: object
                    while True:
                        remaining = extract_timeout_s - (time.time() - start_time)
                        if remaining <= 0:
                            raise FuturesTimeoutError()
                        try:
                            raw_predicted = _fut.result(timeout=min(heartbeat_s, remaining))
                            break
                        except FuturesTimeoutError:
                            elapsed = time.time() - start_time
                            print(
                                f"    … still extracting ({elapsed:.0f}s/{extract_timeout_s:.0f}s)",
                                flush=True,
                            )
                predicted = _validate_predictions_for_ground_truth(raw_predicted, ground_truth)
            except FuturesTimeoutError:
                error = f"TimeoutError: extraction exceeded {os.getenv('LLB_EXTRACT_TIMEOUT_SECONDS', '1800')}s"
            except Exception as e:
                if RetryError is not None and isinstance(e, RetryError) and getattr(e, "last_attempt", None) is not None:
                    underlying = e.last_attempt.exception()
                    error = f"{type(underlying).__name__}: {underlying}"
                else:
                    error = str(e)

            extraction_time = time.time() - start_time
            tokens = usage_accum.as_dict() if usage_accum and usage_accum.requests else None
            cost_usd = usage_accum.cost_usd() if usage_accum and usage_accum.requests else None

            if not error:
                metrics = _evaluate_predictions_for_ground_truth(predicted, ground_truth)
                pred_path = _prediction_output_path(output_dir, entry.sample, entry.transcript, model_key)
                with open(pred_path, "w") as f:
                    json.dump(predicted, f, indent=2)
            else:
                metrics = _evaluate_predictions_for_ground_truth([], ground_truth)

            return EvaluationResult(
                model=model_key,
                sample=entry.sample,
                tier=entry.tier,
                format=entry.format,
                metrics=metrics,
                extraction_time=extraction_time,
                error=error,
                transcript=entry.transcript,
                tokens=tokens,
                cost_usd=cost_usd,
            )

        if not parallel_models or len(active_models) <= 1:
            for model_key in active_models:
                pair_index += 1
                config = MODELS[model_key]
                pred_path = _prediction_output_path(output_dir, entry.sample, entry.transcript, model_key)
                legacy_path = _legacy_prediction_output_path(output_dir, entry.sample, entry.transcript, model_key)
                existing_pred_path = pred_path if pred_path.exists() and pred_path.stat().st_size > 0 else legacy_path
                if resume and existing_pred_path is not None and existing_pred_path.exists() and existing_pred_path.stat().st_size > 0:
                    try:
                        raw_predicted = json.loads(existing_pred_path.read_text(encoding="utf-8"))
                        predicted = _validate_predictions_for_ground_truth(raw_predicted, ground_truth)
                        metrics = _evaluate_predictions_for_ground_truth(predicted, ground_truth)
                        metadata = saved_metadata.get((entry.sample, entry.transcript, model_key), {})
                        r = EvaluationResult(
                            model=model_key,
                            sample=entry.sample,
                            tier=entry.tier,
                            format=entry.format,
                            metrics=metrics,
                            extraction_time=metadata.get("extraction_time", 0.0),
                            error=None,
                            transcript=entry.transcript,
                            tokens=metadata.get("tokens"),
                            cost_usd=metadata.get("cost_usd"),
                        )
                        print(f"  [{config.name}] Pair {pair_index}/{total_pairs} SKIP")
                    except Exception as e:
                        print(f"  [{config.name}] Pair {pair_index}/{total_pairs} RUN (invalid existing prediction: {e})")
                        print(f"    → extracting…", flush=True)
                        r = _eval_one_model(model_key)
                else:
                    print(f"  [{config.name}] Pair {pair_index}/{total_pairs} RUN")
                    print(f"    → extracting…", flush=True)
                    r = _eval_one_model(model_key)

                if r.error:
                    print(f"    ✗ Error: {r.error}")
                else:
                    m = r.metrics
                    print(f"    Predicted: {m['predicted_count']} {record_label}")
                    print(f"    Recall: {m['recall']:.1%}  Precision: {m['precision']:.1%}  F1: {m['f1']:.1%}")
                    print(f"    Time: {r.extraction_time:.1f}s")
                    if r.cost_usd is not None:
                        t = r.tokens or {}
                        print(f"    Cost: ${r.cost_usd:.4f}  Tokens(in/out): {t.get('input_tokens', 0):,}/{t.get('output_tokens', 0):,}")
                    if m.get('missing', 0) > 0:
                        print(f"    ⚠ Missing: {m['missing']}")
                    if m.get('extra', 0) > 0:
                        print(f"    ⚠ Extra: {m['extra']}")
                results.append(r)
                print()
        else:
            with ThreadPoolExecutor(max_workers=min(model_workers, len(active_models))) as ex:
                future_map = {}
                skipped: list[EvaluationResult] = []
                for model_key in active_models:
                    pair_index += 1
                    config = MODELS[model_key]
                    pred_path = _prediction_output_path(output_dir, entry.sample, entry.transcript, model_key)
                    legacy_path = _legacy_prediction_output_path(output_dir, entry.sample, entry.transcript, model_key)
                    existing_pred_path = pred_path if pred_path.exists() and pred_path.stat().st_size > 0 else legacy_path
                    if resume and existing_pred_path is not None and existing_pred_path.exists() and existing_pred_path.stat().st_size > 0:
                        try:
                            raw_predicted = json.loads(existing_pred_path.read_text(encoding="utf-8"))
                            predicted = _validate_predictions_for_ground_truth(raw_predicted, ground_truth)
                            metrics = _evaluate_predictions_for_ground_truth(predicted, ground_truth)
                            metadata = saved_metadata.get((entry.sample, entry.transcript, model_key), {})
                            skipped.append(
                                EvaluationResult(
                                    model=model_key,
                                    sample=entry.sample,
                                    tier=entry.tier,
                                    format=entry.format,
                                    metrics=metrics,
                                    extraction_time=metadata.get("extraction_time", 0.0),
                                    error=None,
                                    transcript=entry.transcript,
                                    tokens=metadata.get("tokens"),
                                    cost_usd=metadata.get("cost_usd"),
                                )
                            )
                            print(f"  [{config.name}] Pair {pair_index}/{total_pairs} SKIP")
                        except Exception as e:
                            print(
                                f"  [{config.name}] Pair {pair_index}/{total_pairs} RUN (invalid existing prediction: {e})"
                            )
                            print(f"    → extracting…", flush=True)
                            future_map[ex.submit(_eval_one_model, model_key)] = model_key
                    else:
                        print(f"  [{config.name}] Pair {pair_index}/{total_pairs} RUN")
                        print(f"    → extracting…", flush=True)
                        future_map[ex.submit(_eval_one_model, model_key)] = model_key

                for r in skipped:
                    results.append(r)
                    m = r.metrics
                    config = MODELS[r.model]
                    print(f"  [{config.name}]")
                    print(f"    Predicted: {m['predicted_count']} {record_label}")
                    print(f"    Recall: {m['recall']:.1%}  Precision: {m['precision']:.1%}  F1: {m['f1']:.1%}")
                    print(f"    Time: {r.extraction_time:.1f}s")
                    if r.cost_usd is not None:
                        t = r.tokens or {}
                        print(f"    Cost: ${r.cost_usd:.4f}  Tokens(in/out): {t.get('input_tokens', 0):,}/{t.get('output_tokens', 0):,}")
                    if m.get('missing', 0) > 0:
                        print(f"    ⚠ Missing: {m['missing']}")
                    if m.get('extra', 0) > 0:
                        print(f"    ⚠ Extra: {m['extra']}")
                    print()

                for fut in as_completed(future_map):
                    r = fut.result()
                    config = MODELS[r.model]
                    print(f"  [{config.name}]")
                    if r.error:
                        print(f"    ✗ Error: {r.error}")
                    else:
                        m = r.metrics
                        print(f"    Predicted: {m['predicted_count']} {record_label}")
                        print(f"    Recall: {m['recall']:.1%}  Precision: {m['precision']:.1%}  F1: {m['f1']:.1%}")
                        print(f"    Time: {r.extraction_time:.1f}s")
                        if m.get('missing', 0) > 0:
                            print(f"    ⚠ Missing: {m['missing']}")
                        if m.get('extra', 0) > 0:
                            print(f"    ⚠ Extra: {m['extra']}")
                    results.append(r)
                    print()
        
        # Rate limiting between samples
        time.sleep(1)
    
    return results


def run_evaluation_from_saved_predictions(
    models: list[str],
    samples: list[str] = None,
    tiers: list[str] = None,
    formats: list[str] = None,
    transcripts: list[str] = None,
    claims_dir: Path = None,
    output_dir: Path = None,
    previous_report_path: Path = None,
) -> list[EvaluationResult]:
    if claims_dir is None:
        claims_dir = default_dataset_dir()
    if output_dir is None:
        output_dir = Path(__file__).parent / "results" / "scratch"

    output_dir.mkdir(parents=True, exist_ok=True)

    eval_inputs = _discover_evaluation_inputs(
        claims_dir=claims_dir,
        samples=samples,
        tiers=tiers,
        formats=formats,
        transcripts=transcripts,
    )

    saved_metadata = _load_saved_result_metadata(
        output_dir=output_dir,
        previous_report_path=previous_report_path,
    )

    results: list[EvaluationResult] = []

    for entry in eval_inputs:
        json_path = ground_truth_path(claims_dir, entry.sample)
        with open(json_path) as f:
            ground_truth = json.load(f)

        for model_key in models:
            if model_key not in MODELS:
                continue

            pred_path = _prediction_output_path(output_dir, entry.sample, entry.transcript, model_key)
            legacy_path = _legacy_prediction_output_path(output_dir, entry.sample, entry.transcript, model_key)
            existing_pred_path = pred_path if pred_path.exists() else legacy_path
            error = None
            predicted: list[dict] = []
            if existing_pred_path is not None and existing_pred_path.exists():
                try:
                    raw_predicted = json.loads(existing_pred_path.read_text(encoding="utf-8"))
                    predicted = _validate_predictions_for_ground_truth(raw_predicted, ground_truth)
                except Exception as e:
                    error = f"Failed to load predicted JSON: {e}"
            else:
                error = f"Missing predicted file: {pred_path.name}"

            if not error:
                metrics = _evaluate_predictions_for_ground_truth(predicted, ground_truth)
            else:
                metrics = _evaluate_predictions_for_ground_truth([], ground_truth)

            metadata = saved_metadata.get((entry.sample, entry.transcript, model_key), {})

            results.append(
                EvaluationResult(
                    model=model_key,
                    sample=entry.sample,
                    tier=entry.tier,
                    format=entry.format,
                    metrics=metrics,
                    extraction_time=metadata.get("extraction_time", 0.0),
                    error=error,
                    transcript=entry.transcript,
                    tokens=metadata.get("tokens"),
                    cost_usd=metadata.get("cost_usd"),
                )
            )

    return results


def generate_report(results: list[EvaluationResult], output_path: Path):
    """Generate summary report in JSON and Markdown formats."""

    model_order: list[str] = []
    for r in results:
        if r.model not in model_order:
            model_order.append(r.model)
    
    # Aggregate by model
    model_stats = {}
    for r in results:
        if r.model not in model_stats:
            model_stats[r.model] = {
                'total_samples': 0,
                'total_f1': 0,
                'total_recall': 0,
                'total_precision': 0,
                'total_found': 0,
                'total_gold_field_pairs': 0,
                'total_pred_field_pairs': 0,
                'total_rows': 0,
                'errors': 0,
                'total_cost_usd': 0.0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_extraction_time': 0.0,
                'by_tier': {},
                'by_format': {},
                'by_transcript': {},
            }

        stats = model_stats[r.model]
        stats['total_samples'] += 1
        stats['total_f1'] += r.metrics['f1']
        stats['total_recall'] += r.metrics['recall']
        stats['total_precision'] += r.metrics['precision']
        stats['total_found'] += r.metrics.get('found', 0)
        stats['total_gold_field_pairs'] += r.metrics.get('total_gold_field_pairs', 0)
        stats['total_pred_field_pairs'] += r.metrics.get('total_pred_field_pairs', 0)
        stats['total_rows'] += r.metrics.get('ground_truth_count', 0)
        stats['total_cost_usd'] += r.cost_usd or 0.0
        stats['total_extraction_time'] += r.extraction_time or 0.0
        if r.tokens:
            stats['total_input_tokens'] += r.tokens.get('input_tokens', 0)
            stats['total_output_tokens'] += r.tokens.get('output_tokens', 0)
        if r.error:
            stats['errors'] += 1
        
        # By tier
        if r.tier not in stats['by_tier']:
            stats['by_tier'][r.tier] = {
                'count': 0,
                'rows': 0,
                'f1_sum': 0,
                'recall_sum': 0,
                'found_sum': 0,
                'gold_pairs_sum': 0,
                'pred_pairs_sum': 0,
            }
        stats['by_tier'][r.tier]['count'] += 1
        stats['by_tier'][r.tier]['rows'] += r.metrics.get('ground_truth_count', 0)
        stats['by_tier'][r.tier]['f1_sum'] += r.metrics['f1']
        stats['by_tier'][r.tier]['recall_sum'] += r.metrics['recall']
        stats['by_tier'][r.tier]['found_sum'] += r.metrics.get('found', 0)
        stats['by_tier'][r.tier]['gold_pairs_sum'] += r.metrics.get('total_gold_field_pairs', 0)
        stats['by_tier'][r.tier]['pred_pairs_sum'] += r.metrics.get('total_pred_field_pairs', 0)
        
        # By format
        if r.format not in stats['by_format']:
            stats['by_format'][r.format] = {
                'count': 0,
                'rows': 0,
                'f1_sum': 0,
                'recall_sum': 0,
                'found_sum': 0,
                'gold_pairs_sum': 0,
                'pred_pairs_sum': 0,
            }
        stats['by_format'][r.format]['count'] += 1
        stats['by_format'][r.format]['rows'] += r.metrics.get('ground_truth_count', 0)
        stats['by_format'][r.format]['f1_sum'] += r.metrics['f1']
        stats['by_format'][r.format]['recall_sum'] += r.metrics['recall']
        stats['by_format'][r.format]['found_sum'] += r.metrics.get('found', 0)
        stats['by_format'][r.format]['gold_pairs_sum'] += r.metrics.get('total_gold_field_pairs', 0)
        stats['by_format'][r.format]['pred_pairs_sum'] += r.metrics.get('total_pred_field_pairs', 0)

        # By transcript condition
        if r.transcript not in stats['by_transcript']:
            stats['by_transcript'][r.transcript] = {
                'count': 0,
                'rows': 0,
                'f1_sum': 0,
                'recall_sum': 0,
                'found_sum': 0,
                'gold_pairs_sum': 0,
                'pred_pairs_sum': 0,
            }
        stats['by_transcript'][r.transcript]['count'] += 1
        stats['by_transcript'][r.transcript]['rows'] += r.metrics.get('ground_truth_count', 0)
        stats['by_transcript'][r.transcript]['f1_sum'] += r.metrics['f1']
        stats['by_transcript'][r.transcript]['recall_sum'] += r.metrics['recall']
        stats['by_transcript'][r.transcript]['found_sum'] += r.metrics.get('found', 0)
        stats['by_transcript'][r.transcript]['gold_pairs_sum'] += r.metrics.get('total_gold_field_pairs', 0)
        stats['by_transcript'][r.transcript]['pred_pairs_sum'] += r.metrics.get('total_pred_field_pairs', 0)
    
    # Compute averages
    for model, stats in model_stats.items():
        n = stats['total_samples']
        stats['avg_f1'] = stats['total_f1'] / n if n > 0 else 0
        stats['avg_recall'] = stats['total_recall'] / n if n > 0 else 0
        stats['avg_precision'] = stats['total_precision'] / n if n > 0 else 0
        total_found = stats['total_found']
        total_gold = stats['total_gold_field_pairs']
        total_pred = stats['total_pred_field_pairs']
        stats['weighted_recall'] = total_found / total_gold if total_gold > 0 else 0
        stats['weighted_precision'] = total_found / total_pred if total_pred > 0 else 0
        stats['weighted_f1'] = (
            2 * stats['weighted_precision'] * stats['weighted_recall'] / (stats['weighted_precision'] + stats['weighted_recall'])
            if (stats['weighted_precision'] + stats['weighted_recall']) > 0 else 0
        )
        
        for tier_stats in stats['by_tier'].values():
            c = tier_stats['count']
            tier_stats['avg_f1'] = tier_stats['f1_sum'] / c if c > 0 else 0
            tier_stats['avg_recall'] = tier_stats['recall_sum'] / c if c > 0 else 0
            gold_pairs = tier_stats['gold_pairs_sum']
            pred_pairs = tier_stats['pred_pairs_sum']
            found_sum = tier_stats['found_sum']
            tier_stats['weighted_recall'] = found_sum / gold_pairs if gold_pairs > 0 else 0
            tier_stats['weighted_precision'] = found_sum / pred_pairs if pred_pairs > 0 else 0
            tier_stats['weighted_f1'] = (
                2 * tier_stats['weighted_precision'] * tier_stats['weighted_recall'] / (tier_stats['weighted_precision'] + tier_stats['weighted_recall'])
                if (tier_stats['weighted_precision'] + tier_stats['weighted_recall']) > 0 else 0
            )
        
        for fmt_stats in stats['by_format'].values():
            c = fmt_stats['count']
            fmt_stats['avg_f1'] = fmt_stats['f1_sum'] / c if c > 0 else 0
            fmt_stats['avg_recall'] = fmt_stats['recall_sum'] / c if c > 0 else 0
            gold_pairs = fmt_stats['gold_pairs_sum']
            pred_pairs = fmt_stats['pred_pairs_sum']
            found_sum = fmt_stats['found_sum']
            fmt_stats['weighted_recall'] = found_sum / gold_pairs if gold_pairs > 0 else 0
            fmt_stats['weighted_precision'] = found_sum / pred_pairs if pred_pairs > 0 else 0
            fmt_stats['weighted_f1'] = (
                2 * fmt_stats['weighted_precision'] * fmt_stats['weighted_recall'] / (fmt_stats['weighted_precision'] + fmt_stats['weighted_recall'])
                if (fmt_stats['weighted_precision'] + fmt_stats['weighted_recall']) > 0 else 0
            )

        for transcript_stats in stats['by_transcript'].values():
            c = transcript_stats['count']
            transcript_stats['avg_f1'] = transcript_stats['f1_sum'] / c if c > 0 else 0
            transcript_stats['avg_recall'] = transcript_stats['recall_sum'] / c if c > 0 else 0
            gold_pairs = transcript_stats['gold_pairs_sum']
            pred_pairs = transcript_stats['pred_pairs_sum']
            found_sum = transcript_stats['found_sum']
            transcript_stats['weighted_recall'] = found_sum / gold_pairs if gold_pairs > 0 else 0
            transcript_stats['weighted_precision'] = found_sum / pred_pairs if pred_pairs > 0 else 0
            transcript_stats['weighted_f1'] = (
                2 * transcript_stats['weighted_precision'] * transcript_stats['weighted_recall'] / (transcript_stats['weighted_precision'] + transcript_stats['weighted_recall'])
                if (transcript_stats['weighted_precision'] + transcript_stats['weighted_recall']) > 0 else 0
            )
    
    # Save JSON report
    report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'model_stats': model_stats,
        'detailed_results': [
            {
                'model': r.model,
                'sample': r.sample,
                'tier': r.tier,
                'format': r.format,
                'transcript': r.transcript,
                'metrics': r.metrics,
                'extraction_time': r.extraction_time,
                'tokens': r.tokens,
                'cost_usd': r.cost_usd,
                'error': r.error,
            }
            for r in results
        ],
    }
    
    json_path = output_path / 'evaluation_report.json'
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate Markdown report
    md_lines = [
        "# Multi-Model Evaluation Report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "",
        "## Overall Results",
        "",
        "| Model | Weighted F1 | Weighted Recall | Weighted Precision | Macro F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |",
        "|-------|-------------|-----------------|--------------------|----------|------|---------|--------|----------|------------|",
    ]

    def _format_weighted_pct(group_stats: dict | None) -> str:
        if not group_stats or group_stats.get("count", 0) == 0:
            return "N/A"
        return f"{group_stats['weighted_f1']:.1%}"

    def _observed_group_keys(stats_key: str, preferred_order: list[str]) -> list[str]:
        observed: set[str] = set()
        for model_key in model_order:
            if model_key in model_stats:
                observed.update(model_stats[model_key].get(stats_key, {}).keys())
        return [
            *[key for key in preferred_order if key in observed],
            *sorted(observed - set(preferred_order)),
        ]

    def _label_group_key(key: str) -> str:
        return key.replace("_", " ").title()

    def _append_group_table(title: str, stats_key: str, preferred_order: list[str]) -> None:
        group_keys = _observed_group_keys(stats_key, preferred_order)
        if not group_keys:
            return

        headers = ["Model", *[_label_group_key(key) for key in group_keys]]
        md_lines.extend(
            [
                "",
                title,
                "",
                "| " + " | ".join(headers) + " |",
                "|" + "|".join(["---"] * len(headers)) + "|",
            ]
        )

        for model_key in model_order:
            if model_key in model_stats:
                s = model_stats[model_key]
                name = MODELS[model_key].name
                scores = [
                    _format_weighted_pct(s[stats_key].get(key)) for key in group_keys
                ]
                md_lines.append(f"| {name} | {' | '.join(scores)} |")

    for model_key in model_order:
        if model_key in model_stats:
            s = model_stats[model_key]
            name = MODELS[model_key].name
            md_lines.append(
                f"| {name} | {s['weighted_f1']:.1%} | {s['weighted_recall']:.1%} | "
                f"{s['weighted_precision']:.1%} | {s['avg_f1']:.1%} | {s['total_rows']} | {s['total_samples']} | {s['errors']} | "
                f"{s.get('total_extraction_time', 0):.0f} | ${s.get('total_cost_usd', 0):.4f} |"
            )
    
    md_lines.extend([
        "",
        "Primary scores use corpus-level micro aggregation over all field-value pairs, so larger incident lists contribute proportionally more evidence than smaller documents.",
    ])

    _append_group_table(
        "## Results by Difficulty Tier",
        "by_tier",
        [
            "core_operations",
            "claim_multihop",
            "policy_packets",
            "easy",
            "medium",
            "hard",
            "extreme",
            "multihop",
            "mixed",
        ],
    )
    _append_group_table(
        "## Results by Document Format",
        "by_format",
        ["production_like_pdf", "crosspage", "detailed", "table"],
    )

    md_lines.extend([
        "",
        "## Results by Transcript Condition",
        "",
        "| Model | Canonical | OCR |",
        "|-------|-----------|-----|",
    ])

    for model_key in model_order:
        if model_key in model_stats:
            s = model_stats[model_key]
            name = MODELS[model_key].name
            canonical = _format_weighted_pct(s["by_transcript"].get("canonical"))
            ocr = _format_weighted_pct(s["by_transcript"].get("ocr"))
            md_lines.append(f"| {name} | {canonical} | {ocr} |")
    
    md_lines.extend([
        "",
        "## Detailed Results",
        "",
    ])
    
    # Group by sample
    samples_seen: set[tuple[str, str]] = set()
    for r in results:
        sample_key = (r.sample, r.transcript)
        if sample_key not in samples_seen:
            samples_seen.add(sample_key)
            md_lines.append(f"### {r.sample} ({r.transcript})")
            md_lines.append("")
            md_lines.append("| Model | F1 | Recall | Precision | Predicted | Time |")
            md_lines.append("|-------|-----|--------|-----------|-----------|------|")
            
            for r2 in results:
                if r2.sample == r.sample and r2.transcript == r.transcript:
                    name = MODELS[r2.model].name
                    m = r2.metrics
                    if r2.error:
                        md_lines.append(f"| {name} | ERROR | - | - | - | - |")
                    else:
                        md_lines.append(
                            f"| {name} | {m['f1']:.1%} | {m['recall']:.1%} | "
                            f"{m['precision']:.1%} | {m['predicted_count']} | {r2.extraction_time:.1f}s |"
                        )
            
            md_lines.append("")
    
    md_path = output_path / 'evaluation_report.md'
    with open(md_path, 'w') as f:
        f.write('\n'.join(md_lines))
    
    print(f"\nReports saved to:")
    print(f"  - {json_path}")
    print(f"  - {md_path}")


def main():
    parser = argparse.ArgumentParser(description='Multi-model evaluation for LongListBench')
    parser.add_argument('--models', nargs='+', default=['gpt55_oneshot'],
                       choices=['gemini', 'gemini_oneshot', 'gemini25', 'gpt52', 'gpt4', 'claude',
                                'gpt55_oneshot', 'gpt55_chunked', 'gpt55_agent'],
                       help='Models to evaluate (default: gpt55_oneshot)')
    parser.add_argument('--output-dir', default=None,
                       help='Directory to write predictions and evaluation reports (default: benchmarks/results/scratch)')
    parser.add_argument('--tiers', nargs='+', default=None,
                       choices=['easy', 'medium', 'hard', 'extreme', 'multihop', 'mixed',
                                'core_operations', 'claim_multihop', 'policy_packets'],
                       help='Difficulty tiers to test (default: all)')
    parser.add_argument('--formats', nargs='+', default=None,
                       choices=['detailed', 'table', 'crosspage', 'production_like_pdf'],
                       help='Document formats to test (default: all)')
    parser.add_argument('--transcripts', nargs='+', default=['ocr'],
                       choices=['canonical', 'ocr'],
                       help='Transcript conditions to test (default: ocr)')
    parser.add_argument('--samples', nargs='+', default=None,
                       help='Specific samples to test (default: all available)')
    parser.add_argument('--quick', action='store_true',
                       help='Quick test with representative current-release samples')
    parser.add_argument('--offline', action='store_true',
                       help='Regenerate reports from saved *_predicted.json files (no API calls)')
    parser.add_argument('--previous-report', default=None,
                       help='Optional path to an evaluation_report.json to reuse extraction_time values from')
    parser.add_argument('--parallel-models', action='store_true',
                       help='Run all selected models in parallel for each sample')
    parser.add_argument('--model-workers', type=int, default=None,
                       help='Max number of parallel model workers (default: len(models) or LLB_MODEL_WORKERS)')
    parser.add_argument('--no-resume', action='store_true',
                       help='Do not reuse existing *_predicted.json files; always rerun extractions')
    
    args = parser.parse_args()
    
    # Quick mode: representative current-release samples.
    if args.quick:
        args.samples = list(_QUICK_SAMPLES)
    
    print("="*70)
    print("MULTI-MODEL EVALUATION: LongListBench Benchmark")
    print("="*70)
    print()
    print(f"Models: {', '.join(args.models)}")
    print(f"Tiers: {args.tiers or 'all'}")
    print(f"Formats: {args.formats or 'all'}")
    print(f"Transcripts: {args.transcripts or 'all'}")
    print()
    
    if args.offline: 
        previous_report_path = Path(args.previous_report) if args.previous_report else None
        output_dir = Path(args.output_dir) if args.output_dir else (Path(__file__).parent / "results" / "scratch")
        results = run_evaluation_from_saved_predictions(
            models=args.models,
            samples=args.samples,
            tiers=args.tiers,
            formats=args.formats,
            transcripts=args.transcripts,
            output_dir=output_dir,
            previous_report_path=previous_report_path,
        )
    else:
        output_dir = Path(args.output_dir) if args.output_dir else (Path(__file__).parent / "results" / "scratch")
        results = run_evaluation(
            models=args.models,
            samples=args.samples,
            tiers=args.tiers,
            formats=args.formats,
            transcripts=args.transcripts,
            output_dir=output_dir,
            parallel_models=args.parallel_models,
            model_workers=args.model_workers,
            resume=(not args.no_resume),
        )
    
    # Generate reports
    generate_report(results, output_dir)
    
    print()
    print("="*70)
    print("EVALUATION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
