#!/usr/bin/env python3
"""Run repository-denied Codex CLI extraction and score saved predictions.

Each sample is copied into a temporary workspace containing only:
- document_ocr.md
- field_contract.md
- prompt.md

The Codex process is wrapped in a macOS sandbox profile that denies read/write
access to this repository. The prompt also prohibits using files outside the
temporary workspace. This is repository isolation, not a host-wide filesystem
allowlist. The runner validates the output and saves the normalized prediction.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

try:
    from .dataset_layout import (
        default_dataset_dir,
        ground_truth_path,
        iter_transcript_paths,
        sample_id_from_transcript_path,
        transcript_path,
    )
    from .evaluate_models import MODELS, generate_report, run_evaluation_from_saved_predictions
    from .evaluation_metrics import normalize_record_predictions, uses_record_evaluator
    from .extraction_core import (
        _LOSS_RUN_EXTRACTION_SCHEMA_JSON,
        _validate_and_normalize_predictions,
        build_record_extraction_contract,
        parse_json_response,
    )
except ImportError:
    from dataset_layout import (
        default_dataset_dir,
        ground_truth_path,
        iter_transcript_paths,
        sample_id_from_transcript_path,
        transcript_path,
    )
    from evaluate_models import MODELS, generate_report, run_evaluation_from_saved_predictions
    from evaluation_metrics import normalize_record_predictions, uses_record_evaluator
    from extraction_core import (
        _LOSS_RUN_EXTRACTION_SCHEMA_JSON,
        _validate_and_normalize_predictions,
        build_record_extraction_contract,
        parse_json_response,
    )


DEFAULT_MODEL_KEY = "codex_gpt55"
DEFAULT_CODEX_MODEL = "gpt-5.5"
DEFAULT_REASONING_EFFORT = "xhigh"
RUN_METADATA_FILE = "run_metadata.json"
OUTPUT_FILE_RECORDS = Path("output/records.json")
OUTPUT_FILE_INCIDENTS = Path("output/incidents.json")


def discover_samples(dataset_dir: Path, transcript: str, requested: list[str] | None) -> list[str]:
    if requested:
        return requested
    samples: list[tuple[int, str]] = []
    for path in iter_transcript_paths(dataset_dir, transcript):
        if path.stat().st_size <= 0:
            continue
        sample = sample_id_from_transcript_path(dataset_dir, path, transcript)
        gt_path = ground_truth_path(dataset_dir, sample)
        if gt_path.exists():
            try:
                target_count = len(json.loads(gt_path.read_text(encoding="utf-8")))
            except Exception:
                target_count = 0
            samples.append((target_count, sample))
    return [sample for _count, sample in sorted(set(samples))]


def prediction_path(output_dir: Path, sample: str, transcript: str, model_key: str) -> Path:
    return output_dir / f"{sample}_{transcript}_{model_key}_predicted.json"


def build_incident_contract() -> str:
    return "\n".join(
        [
            "Output JSON shape:",
            '{ "incidents": [ ... ] }',
            "",
            "Extract every claim/loss-run incident record visible in the document.",
            "Every incident must include all fields in the JSON Schema below.",
            "Use empty strings, nulls, empty lists, or 0.0 for unknown values according to the schema.",
            "",
            "JSON Schema:",
            _LOSS_RUN_EXTRACTION_SCHEMA_JSON,
        ]
    )


def build_prompt(output_file: Path) -> str:
    return f"""You are dispatched as a subagent for a specific extraction task; skip superpowers skills.

Your workspace contains:
- document_ocr.md: OCR transcript of one benchmark PDF.
- field_contract.md: the target output shape and allowed fields.

The official ground truth is not present. Do not use files outside this workspace.

Task:
Extract the complete target list from document_ocr.md according to field_contract.md.
Write valid JSON to {output_file.as_posix()}.

You may inspect the document, write temporary scripts, and verify counts. Before finishing:
- Confirm the JSON parses.
- Spot-check beginning, middle, and end records against the OCR.
- Ensure field names match field_contract.md exactly.
- Ensure every target row or target record type requested by the contract is represented.

Do not include explanations in the JSON file.
"""


def prepare_workspace(
    *,
    dataset_dir: Path,
    sample: str,
    transcript: str,
    workspace_root: Path,
) -> tuple[Path, Path, bool]:
    workspace = Path(tempfile.mkdtemp(prefix=f"{sample}_", dir=workspace_root)).resolve()
    (workspace / "output").mkdir(parents=True, exist_ok=True)

    ocr = transcript_path(dataset_dir, sample, transcript).read_text(encoding="utf-8")
    ground_truth = json.loads(ground_truth_path(dataset_dir, sample).read_text(encoding="utf-8"))
    expects_records = uses_record_evaluator(ground_truth)
    output_file = OUTPUT_FILE_RECORDS if expects_records else OUTPUT_FILE_INCIDENTS
    contract = (
        build_record_extraction_contract(ground_truth)
        if expects_records
        else build_incident_contract()
    )

    (workspace / "document_ocr.md").write_text(ocr, encoding="utf-8")
    (workspace / "field_contract.md").write_text(contract, encoding="utf-8")
    (workspace / "prompt.md").write_text(build_prompt(output_file), encoding="utf-8")
    return workspace, output_file, expects_records


def sandbox_profile(repo_root: Path, extra_denied_paths: list[Path] | None = None) -> str:
    denied_paths = {repo_root.resolve()}
    denied_paths.update(path.resolve() for path in extra_denied_paths or [])
    deny_rules = " ".join(
        f'(deny file-read* file-write* (subpath "{path}"))'
        for path in sorted(denied_paths, key=str)
    )
    return f'(version 1) (allow default) {deny_rules}'


def _all_statuses_succeeded(statuses: list[tuple[str, int | str]]) -> bool:
    return bool(statuses) and all(status in (0, "skip") for _sample, status in statuses)


def run_codex(
    workspace: Path,
    repo_root: Path,
    timeout_seconds: int,
    model: str,
    effort: str,
    extra_denied_paths: list[Path] | None = None,
) -> tuple[int | str, str]:
    prompt = (workspace / "prompt.md").read_text(encoding="utf-8")
    cmd = [
        "sandbox-exec",
        "-p",
        sandbox_profile(repo_root, extra_denied_paths),
        "codex",
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "-m",
        model,
        "-c",
        f'model_reasoning_effort="{effort}"',
        "--cd",
        str(workspace),
        "--dangerously-bypass-approvals-and-sandbox",
        prompt,
    ]
    env = dict(os.environ)
    env["NO_COLOR"] = "1"
    try:
        completed = subprocess.run(
            cmd,
            cwd="/tmp",
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return completed.returncode, completed.stdout
    except subprocess.TimeoutExpired as exc:
        return "timeout", (exc.stdout or "") + f"\nTIMEOUT after {timeout_seconds}s\n"


def load_prediction(workspace: Path, output_file: Path, expects_records: bool) -> list[dict]:
    path = workspace / output_file
    if not path.exists():
        raise FileNotFoundError(f"Agent did not write {output_file.as_posix()}")
    raw_text = path.read_text(encoding="utf-8")
    raw = parse_json_response(raw_text)
    return normalize_record_predictions(raw) if expects_records else _validate_and_normalize_predictions(raw)


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
    model_key: str,
    model: str,
    effort: str,
    extra_denied_paths: list[Path],
) -> tuple[str, int | str]:
    pred_path = prediction_path(output_dir, sample, transcript, model_key)
    if pred_path.exists() and pred_path.stat().st_size > 0 and not no_resume:
        return sample, "skip"

    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    workspace, output_file, expects_records = prepare_workspace(
        dataset_dir=dataset_dir,
        sample=sample,
        transcript=transcript,
        workspace_root=workspace_root,
    )
    try:
        status, log = run_codex(
            workspace,
            repo_root,
            timeout_seconds,
            model,
            effort,
            extra_denied_paths,
        )
        (logs_dir / f"{sample}_{transcript}_{model_key}.log").write_text(
            log,
            encoding="utf-8",
        )
        if status == 0:
            predicted = load_prediction(workspace, output_file, expects_records)
            pred_path.write_text(json.dumps(predicted, indent=2), encoding="utf-8")
        return sample, status
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def _codex_cli_version() -> str | None:
    try:
        return subprocess.check_output(
            ["codex", "--version"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _write_run_metadata(
    *,
    output_dir: Path,
    transcript: str,
    model_key: str,
    requested_model: str,
    effort: str,
    statuses: list[tuple[str, int | str]],
    extra_denied_paths: list[Path] | None = None,
) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runner": Path(__file__).name,
        "model_key": model_key,
        "requested_model": requested_model,
        "effort": effort,
        "transcript": transcript,
        "cli_version_observed_at_metadata_write": _codex_cli_version(),
        "authentication": "Codex subscription; credentials are not stored",
        "additional_denied_paths": [
            str(path.resolve()) for path in extra_denied_paths or []
        ],
        "sample_statuses": {sample: status for sample, status in statuses},
    }
    (output_dir / RUN_METADATA_FILE).write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repository-denied Codex CLI extraction")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--transcript", default="ocr", choices=["ocr", "canonical"])
    parser.add_argument("--samples", nargs="+", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--workspace-root", default="/tmp/longlistbench-codex-workspaces")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--workers", type=int, default=1, help="Number of samples to run in parallel")
    parser.add_argument("--model-key", default=DEFAULT_MODEL_KEY, help="Offline scorer model key")
    parser.add_argument("--model", default=DEFAULT_CODEX_MODEL, help="Codex model slug")
    parser.add_argument("--effort", default=DEFAULT_REASONING_EFFORT, help="Codex reasoning effort")
    parser.add_argument(
        "--deny-path",
        action="append",
        default=[],
        help="Additional host path to deny to the Codex process; may be repeated",
    )
    args = parser.parse_args()

    if shutil.which("sandbox-exec") is None:
        raise SystemExit("sandbox-exec is required for repository-denied Codex CLI runs")
    if args.model_key not in MODELS:
        raise SystemExit(f"Unknown offline scorer model key: {args.model_key}")

    repo_root = Path(__file__).resolve().parents[1]
    dataset_dir = default_dataset_dir()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    workspace_root = Path(args.workspace_root)
    workspace_root.mkdir(parents=True, exist_ok=True)
    extra_denied_paths = [Path(path) for path in args.deny_path]

    samples = discover_samples(dataset_dir, args.transcript, args.samples)
    statuses: list[tuple[str, int | str]] = []
    worker_count = max(1, args.workers)
    if worker_count == 1:
        for index, sample in enumerate(samples, start=1):
            print(f"[{index}/{len(samples)}] {args.model_key} {sample}", flush=True)
            sample_id, status = run_sample(
                dataset_dir=dataset_dir,
                repo_root=repo_root,
                output_dir=output_dir,
                workspace_root=workspace_root,
                sample=sample,
                transcript=args.transcript,
                timeout_seconds=args.timeout_seconds,
                no_resume=args.no_resume,
                model_key=args.model_key,
                model=args.model,
                effort=args.effort,
                extra_denied_paths=extra_denied_paths,
            )
            statuses.append((sample_id, status))
            print(f"  -> {status}", flush=True)
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
                    model_key=args.model_key,
                    model=args.model,
                    effort=args.effort,
                    extra_denied_paths=extra_denied_paths,
                )
                future_to_sample[future] = sample

            for future in as_completed(future_to_sample):
                sample = future_to_sample[future]
                try:
                    sample_id, status = future.result()
                except Exception as exc:
                    sample_id, status = sample, f"error: {exc}"
                statuses.append((sample_id, status))
                print(f"[DONE] {args.model_key} {sample_id} -> {status}", flush=True)

        status_order = {sample: index for index, sample in enumerate(samples)}
        statuses.sort(key=lambda item: status_order.get(item[0], len(status_order)))

    (output_dir / "per_sample_status.tsv").write_text(
        "sample\tstatus\n" + "\n".join(f"{sample}\t{status}" for sample, status in statuses) + "\n",
        encoding="utf-8",
    )
    _write_run_metadata(
        output_dir=output_dir,
        transcript=args.transcript,
        model_key=args.model_key,
        requested_model=args.model,
        effort=args.effort,
        statuses=statuses,
        extra_denied_paths=extra_denied_paths,
    )
    results = run_evaluation_from_saved_predictions(
        models=[args.model_key],
        samples=args.samples,
        transcripts=[args.transcript],
        output_dir=output_dir,
    )
    generate_report(results, output_dir)
    return 0 if _all_statuses_succeeded(statuses) else 1


if __name__ == "__main__":
    raise SystemExit(main())
