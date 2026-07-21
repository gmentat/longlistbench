#!/usr/bin/env python3
"""Run repository-denied Claude Code extraction and score saved predictions.

This runner deliberately reuses the Codex CLI runner's workspace and field
contract construction. The temporary workspace contains the OCR transcript,
field contract, prompt, and output directory. A macOS profile denies repository
access, and the prompt prohibits external files; this is not a host-wide
filesystem allowlist.
"""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

try:
    from .dataset_layout import default_dataset_dir
    from .evaluate_models import MODELS, generate_report, run_evaluation_from_saved_predictions
    from .run_codex_cli_evaluation import (
        discover_samples,
        _all_statuses_succeeded,
        _bind_prediction_provenance,
        _build_workspace_provenance,
        _metadata_denied_path_labels,
        _resume_metadata_matches,
        load_prediction,
        normalize_record_predictions,
        prepare_workspace,
        sandbox_profile,
        _validate_and_normalize_predictions,
    )
except ImportError:
    from dataset_layout import default_dataset_dir
    from evaluate_models import MODELS, generate_report, run_evaluation_from_saved_predictions
    from run_codex_cli_evaluation import (
        discover_samples,
        _all_statuses_succeeded,
        _bind_prediction_provenance,
        _build_workspace_provenance,
        _metadata_denied_path_labels,
        _resume_metadata_matches,
        load_prediction,
        normalize_record_predictions,
        prepare_workspace,
        sandbox_profile,
        _validate_and_normalize_predictions,
    )


DEFAULT_MODEL_KEY = "claude_opus48"
DEFAULT_CLAUDE_MODEL = "claude-opus-4-8"
DEFAULT_CLAUDE_EFFORT = "xhigh"
RUN_METADATA_FILE = "run_metadata.json"


def prediction_path(output_dir: Path, sample: str, transcript: str, model_key: str) -> Path:
    return output_dir / f"{sample}_{transcript}_{model_key}_predicted.json"


def _parse_result_payload(log: str) -> dict:
    """Parse Claude Code's JSON result, tolerating warning lines before it."""
    stripped = log.strip()
    if not stripped:
        raise ValueError("Claude Code returned no result")
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        payload = None
        for line in reversed(stripped.splitlines()):
            try:
                candidate = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, dict) and candidate.get("type") == "result":
                payload = candidate
                break
        if payload is None:
            raise ValueError("Claude Code did not return a JSON result object")

    if not isinstance(payload, dict) or payload.get("type") != "result":
        raise ValueError("Claude Code returned an unexpected result object")
    if payload.get("is_error") or payload.get("subtype") != "success":
        raise ValueError(f"Claude Code failed: {payload.get('result') or payload.get('subtype')}")
    return payload


def _metadata_from_payload(payload: dict, requested_model: str, effort: str) -> dict:
    model_usage = payload.get("modelUsage") or {}
    observed_models = sorted(model_usage)
    matching_models = [
        model
        for model in observed_models
        if model == requested_model or model.startswith(f"{requested_model}[")
    ]
    if not matching_models:
        raise ValueError(
            f"Requested {requested_model}, but Claude Code reported {observed_models or 'no model'}"
        )

    input_tokens = 0
    cached_input_tokens = 0
    cache_creation_input_tokens = 0
    output_tokens = 0
    for usage in model_usage.values():
        input_tokens += int(usage.get("inputTokens") or 0)
        cached_input_tokens += int(usage.get("cacheReadInputTokens") or 0)
        cache_creation_input_tokens += int(usage.get("cacheCreationInputTokens") or 0)
        output_tokens += int(usage.get("outputTokens") or 0)

    duration_ms = payload.get("duration_ms")
    return {
        "requested_model": requested_model,
        "matching_inference_models": matching_models,
        "observed_models": observed_models,
        "effort": effort,
        "duration_seconds": float(duration_ms) / 1000 if duration_ms is not None else None,
        "tokens": {
            "requests": int(payload.get("num_turns") or 0),
            "input_tokens": input_tokens + cached_input_tokens + cache_creation_input_tokens,
            "cached_input_tokens": cached_input_tokens,
            "cache_creation_input_tokens": cache_creation_input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens
            + cached_input_tokens
            + cache_creation_input_tokens
            + output_tokens,
        },
        # Claude Code reports an API-equivalent estimate even on a subscription.
        "estimated_api_cost_usd": payload.get("total_cost_usd"),
    }


def _claude_cli_version() -> str | None:
    try:
        return subprocess.check_output(
            ["claude", "--version"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def run_claude(
    workspace: Path,
    repo_root: Path,
    timeout_seconds: int,
    model: str,
    effort: str,
    extra_denied_paths: list[Path] | None = None,
    runtime_version: str | None = None,
) -> tuple[int | str, str, dict | None]:
    cli_version = runtime_version or _claude_cli_version()
    prompt = (workspace / "prompt.md").read_text(encoding="utf-8")
    cmd = [
        "sandbox-exec",
        "-p",
        sandbox_profile(repo_root, extra_denied_paths),
        "claude",
        "-p",
        "--model",
        model,
        "--effort",
        effort,
        "--safe-mode",
        "--disable-slash-commands",
        "--no-chrome",
        "--no-session-persistence",
        "--dangerously-skip-permissions",
        "--tools",
        "Bash,Read,Write,Edit,Glob,Grep",
        "--output-format",
        "json",
        prompt,
    ]
    env = dict(os.environ)
    env["NO_COLOR"] = "1"
    try:
        completed = subprocess.run(
            cmd,
            cwd=workspace,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + f"\nTIMEOUT after {timeout_seconds}s\n"
        return "timeout", output, None

    if completed.returncode != 0:
        return completed.returncode, completed.stdout, None
    try:
        payload = _parse_result_payload(completed.stdout)
        metadata = _metadata_from_payload(payload, model, effort)
        metadata["claude_cli_version"] = cli_version
    except ValueError as exc:
        return f"invalid_result: {exc}", completed.stdout, None
    return 0, completed.stdout, metadata


def run_sample(
    *,
    dataset_dir: Path,
    repo_root: Path,
    output_dir: Path,
    workspace_root: Path,
    sample: str,
    transcript: str,
    timeout_seconds: int,
    no_resume: bool,
    attest_existing: bool,
    model_key: str,
    model: str,
    effort: str,
    runtime_version: str,
    existing_metadata: dict | None,
    metadata_cli_version: str | None,
    extra_denied_paths: list[Path],
) -> tuple[str, int | str, dict | None]:
    pred_path = prediction_path(output_dir, sample, transcript, model_key)
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    workspace, output_file, expects_records = prepare_workspace(
        dataset_dir=dataset_dir,
        sample=sample,
        transcript=transcript,
        workspace_root=workspace_root,
    )
    expected_provenance = _build_workspace_provenance(
        workspace=workspace,
        output_file=output_file,
        sample=sample,
        transcript=transcript,
        model_key=model_key,
        requested_model=model,
        effort=effort,
        dataset_manifest_path=dataset_dir / "manifest.json",
        runner_source_path=Path(__file__),
        runtime_version=runtime_version,
    )
    try:
        if not no_resume and _resume_metadata_matches(
            existing_metadata,
            expected_provenance,
            pred_path,
        ):
            return sample, "skip", existing_metadata

        if not no_resume and attest_existing and pred_path.is_file() and pred_path.stat().st_size > 0:
            log_path = logs_dir / f"{sample}_{transcript}_{model_key}.log"
            if not log_path.is_file():
                return sample, "invalid_attestation: missing Claude log", None
            try:
                payload = _parse_result_payload(log_path.read_text(encoding="utf-8"))
                metadata = _metadata_from_payload(payload, model, effort)
                raw_prediction = json.loads(pred_path.read_text(encoding="utf-8"))
                if expects_records:
                    normalize_record_predictions(raw_prediction)
                else:
                    _validate_and_normalize_predictions(raw_prediction)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                return sample, f"invalid_attestation: {exc}", None
            observed_cli_version = (
                existing_metadata.get("claude_cli_version")
                if isinstance(existing_metadata, dict)
                else None
            )
            cli_version_evidence = "per_sample"
            if not observed_cli_version:
                observed_cli_version = metadata_cli_version
                cli_version_evidence = "run_metadata_write"
            if not observed_cli_version:
                return sample, "invalid_attestation: missing Claude CLI version", None
            metadata["claude_cli_version"] = observed_cli_version
            metadata["claude_cli_version_evidence"] = cli_version_evidence
            attested_provenance = _build_workspace_provenance(
                workspace=workspace,
                output_file=output_file,
                sample=sample,
                transcript=transcript,
                model_key=model_key,
                requested_model=model,
                effort=effort,
                dataset_manifest_path=dataset_dir / "manifest.json",
                runner_source_path=Path(__file__),
                runtime_version=observed_cli_version,
            )
            metadata.update(_bind_prediction_provenance(attested_provenance, pred_path))
            return sample, "attest", metadata

        status, log, metadata = run_claude(
            workspace,
            repo_root,
            timeout_seconds,
            model,
            effort,
            extra_denied_paths,
            runtime_version,
        )
        (logs_dir / f"{sample}_{transcript}_{model_key}.log").write_text(
            log,
            encoding="utf-8",
        )
        if status == 0:
            predicted = load_prediction(workspace, output_file, expects_records)
            pred_path.write_text(json.dumps(predicted, indent=2), encoding="utf-8")
            metadata.update(_bind_prediction_provenance(expected_provenance, pred_path))
        return sample, status, metadata
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def _load_run_metadata_payload(output_dir: Path) -> dict:
    path = output_dir / RUN_METADATA_FILE
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_run_metadata(output_dir: Path) -> dict:
    return _load_run_metadata_payload(output_dir).get("samples") or {}


def _write_run_metadata(
    *,
    repo_root: Path,
    output_dir: Path,
    transcript: str,
    sample_metadata: dict[str, dict],
    model_key: str,
    requested_model: str,
    effort: str,
    extra_denied_paths: list[Path] | None = None,
    runtime_version: str | None = None,
) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runner": Path(__file__).name,
        "model_key": model_key,
        "requested_model": requested_model,
        "effort": effort,
        "transcript": transcript,
        "cli_version_observed_at_metadata_write": runtime_version or _claude_cli_version(),
        "authentication": "Claude subscription; credentials are not stored",
        "additional_denied_paths": _metadata_denied_path_labels(
            repo_root,
            extra_denied_paths,
        ),
        "samples": sample_metadata,
    }
    path = output_dir / RUN_METADATA_FILE
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repository-denied Claude Code CLI extraction")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--transcript", default="ocr", choices=["ocr", "canonical"])
    parser.add_argument("--samples", nargs="+", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--workspace-root", default="/tmp/longlistbench-claude-workspaces")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument(
        "--attest-existing",
        action="store_true",
        help="Attest legacy predictions only when their saved Claude result logs match the requested model",
    )
    parser.add_argument("--workers", type=int, default=1, help="Number of samples to run in parallel")
    parser.add_argument("--model-key", default=DEFAULT_MODEL_KEY, help="Offline scorer model key")
    parser.add_argument("--model", default=DEFAULT_CLAUDE_MODEL, help="Claude model slug")
    parser.add_argument("--effort", default=DEFAULT_CLAUDE_EFFORT, help="Claude effort level")
    parser.add_argument(
        "--deny-path",
        action="append",
        default=[],
        help="Additional host path to deny to the Claude process; may be repeated",
    )
    args = parser.parse_args()

    if shutil.which("sandbox-exec") is None:
        raise SystemExit("sandbox-exec is required for repository-denied Claude Code CLI runs")
    if shutil.which("claude") is None:
        raise SystemExit("claude is required for Claude Code CLI runs")
    if args.model_key not in MODELS:
        raise SystemExit(f"Unknown offline scorer model key: {args.model_key}")
    runtime_version = _claude_cli_version()
    if not runtime_version:
        raise SystemExit("Unable to determine Claude CLI version")

    repo_root = Path(__file__).resolve().parents[1]
    dataset_dir = default_dataset_dir()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    workspace_root = Path(args.workspace_root)
    workspace_root.mkdir(parents=True, exist_ok=True)
    extra_denied_paths = [Path(path) for path in args.deny_path]

    samples = discover_samples(dataset_dir, args.transcript, args.samples)
    statuses: list[tuple[str, int | str]] = []
    initial_run_metadata = _load_run_metadata_payload(output_dir)
    sample_metadata = dict(initial_run_metadata.get("samples") or {})
    metadata_cli_version = initial_run_metadata.get("cli_version_observed_at_metadata_write")
    worker_count = max(1, args.workers)

    def record_result(result: tuple[str, int | str, dict | None]) -> None:
        sample_id, status, metadata = result
        statuses.append((sample_id, status))
        if metadata is not None:
            sample_metadata[sample_id] = metadata
            _write_run_metadata(
                repo_root=repo_root,
                output_dir=output_dir,
                transcript=args.transcript,
                sample_metadata=sample_metadata,
                model_key=args.model_key,
                requested_model=args.model,
                effort=args.effort,
                runtime_version=runtime_version,
                extra_denied_paths=extra_denied_paths,
            )
        print(f"[DONE] {args.model_key} {sample_id} -> {status}", flush=True)

    if worker_count == 1:
        for index, sample in enumerate(samples, start=1):
            print(f"[{index}/{len(samples)}] {args.model_key} {sample}", flush=True)
            record_result(
                run_sample(
                    dataset_dir=dataset_dir,
                    repo_root=repo_root,
                    output_dir=output_dir,
                    workspace_root=workspace_root,
                    sample=sample,
                    transcript=args.transcript,
                    timeout_seconds=args.timeout_seconds,
                    no_resume=args.no_resume,
                    attest_existing=args.attest_existing,
                    model_key=args.model_key,
                    model=args.model,
                    effort=args.effort,
                    runtime_version=runtime_version,
                    existing_metadata=sample_metadata.get(sample),
                    metadata_cli_version=metadata_cli_version,
                    extra_denied_paths=extra_denied_paths,
                )
            )
    else:
        with ThreadPoolExecutor(max_workers=min(worker_count, len(samples) or 1)) as executor:
            future_to_sample = {}
            for index, sample in enumerate(samples, start=1):
                print(f"[{index}/{len(samples)}] {args.model_key} {sample} QUEUED", flush=True)
                future = executor.submit(
                    run_sample,
                    dataset_dir=dataset_dir,
                    repo_root=repo_root,
                    output_dir=output_dir,
                    workspace_root=workspace_root,
                    sample=sample,
                    transcript=args.transcript,
                    timeout_seconds=args.timeout_seconds,
                    no_resume=args.no_resume,
                    attest_existing=args.attest_existing,
                    model_key=args.model_key,
                    model=args.model,
                    effort=args.effort,
                    runtime_version=runtime_version,
                    existing_metadata=sample_metadata.get(sample),
                    metadata_cli_version=metadata_cli_version,
                    extra_denied_paths=extra_denied_paths,
                )
                future_to_sample[future] = sample

            for future in as_completed(future_to_sample):
                sample = future_to_sample[future]
                try:
                    record_result(future.result())
                except Exception as exc:
                    record_result((sample, f"error: {exc}", None))

    status_order = {sample: index for index, sample in enumerate(samples)}
    statuses.sort(key=lambda item: status_order.get(item[0], len(status_order)))
    (output_dir / "per_sample_status.tsv").write_text(
        "sample\tstatus\n"
        + "\n".join(f"{sample}\t{status}" for sample, status in statuses)
        + "\n",
        encoding="utf-8",
    )
    _write_run_metadata(
        repo_root=repo_root,
        output_dir=output_dir,
        transcript=args.transcript,
        sample_metadata=sample_metadata,
        model_key=args.model_key,
        requested_model=args.model,
        effort=args.effort,
        extra_denied_paths=extra_denied_paths,
        runtime_version=runtime_version,
    )

    results = run_evaluation_from_saved_predictions(
        models=[args.model_key],
        samples=args.samples,
        transcripts=[args.transcript],
        output_dir=output_dir,
    )
    for result in results:
        metadata = sample_metadata.get(result.sample) or {}
        result.extraction_time = metadata.get("duration_seconds")
        result.tokens = metadata.get("tokens")
    generate_report(results, output_dir, evaluation_mode="subscription_cli")
    return 0 if _all_statuses_succeeded(statuses) else 1


if __name__ == "__main__":
    raise SystemExit(main())
