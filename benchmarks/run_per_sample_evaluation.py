#!/usr/bin/env python3
"""Run LongListBench evaluation one sample per subprocess.

This wrapper exists because provider SDK calls can block inside a worker thread.
Running each sample as its own process lets us enforce a real timeout, resume
completed predictions, and keep per-sample logs/reports for audit.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from .dataset_layout import (
        default_dataset_dir,
        ground_truth_path,
        iter_transcript_paths,
        sample_id_from_transcript_path,
    )
except ImportError:
    from dataset_layout import (
        default_dataset_dir,
        ground_truth_path,
        iter_transcript_paths,
        sample_id_from_transcript_path,
    )


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


def prediction_exists(output_dir: Path, sample: str, transcript: str, model: str) -> bool:
    expected = output_dir / f"{sample}_{transcript}_{model}_predicted.json"
    legacy = output_dir / f"{sample}_{model}_predicted.json" if transcript == "ocr" else None
    return expected.exists() and expected.stat().st_size > 0 or bool(
        legacy and legacy.exists() and legacy.stat().st_size > 0
    )


def run_sample(
    *,
    sample: str,
    model: str,
    transcript: str,
    output_dir: Path,
    timeout_seconds: int,
    no_resume: bool,
) -> tuple[str, int | str]:
    logs_dir = output_dir / "logs"
    reports_dir = output_dir / "per_sample_reports"
    logs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    if not no_resume and prediction_exists(output_dir, sample, transcript, model):
        return sample, "skip"

    log_path = logs_dir / f"{sample}_{transcript}_{model}.log"
    cmd = [
        sys.executable,
        "benchmarks/evaluate_models.py",
        "--models",
        model,
        "--samples",
        sample,
        "--transcripts",
        transcript,
        "--output-dir",
        str(output_dir),
    ]
    if no_resume:
        cmd.append("--no-resume")

    with log_path.open("w", encoding="utf-8") as log_file:
        try:
            completed = subprocess.run(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            report_path = output_dir / "evaluation_report.json"
            if report_path.exists():
                shutil.copy2(report_path, reports_dir / f"{sample}_{transcript}_{model}.json")
                try:
                    report = json.loads(report_path.read_text(encoding="utf-8"))
                    errors = [
                        item.get("error")
                        for item in report.get("detailed_results", [])
                        if item.get("sample") == sample and item.get("model") == model
                    ]
                    if any(errors):
                        return sample, "model_error"
                except Exception:
                    pass
            return sample, completed.returncode
        except subprocess.TimeoutExpired:
            log_file.write(f"\nTIMEOUT after {timeout_seconds}s\n")
            return sample, "timeout"


def write_final_offline_report(
    output_dir: Path,
    models: list[str],
    transcript: str,
    samples: list[str] | None,
) -> int:
    cmd = [
        sys.executable,
        "benchmarks/evaluate_models.py",
        "--offline",
        "--models",
        *models,
        "--transcripts",
        transcript,
        "--output-dir",
        str(output_dir),
    ]
    if samples:
        cmd.extend(["--samples", *samples])
    completed = subprocess.run(cmd, check=False)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run evaluation one sample per subprocess")
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--transcript", default="ocr", choices=["ocr", "canonical"])
    parser.add_argument("--samples", nargs="+", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=1200)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()

    dataset_dir = default_dataset_dir()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    samples = discover_samples(dataset_dir, args.transcript, args.samples)

    statuses: list[tuple[str, str, int | str]] = []
    total = len(samples) * len(args.models)
    index = 0
    for sample in samples:
        for model in args.models:
            index += 1
            print(f"[{index}/{total}] {model} {sample}", flush=True)
            sample_id, status = run_sample(
                sample=sample,
                model=model,
                transcript=args.transcript,
                output_dir=output_dir,
                timeout_seconds=args.timeout_seconds,
                no_resume=args.no_resume,
            )
            statuses.append((model, sample_id, status))
            print(f"  -> {status}", flush=True)

    status_path = output_dir / "per_sample_status.tsv"
    status_path.write_text(
        "model\tsample\tstatus\n"
        + "\n".join(f"{model}\t{sample}\t{status}" for model, sample, status in statuses)
        + "\n",
        encoding="utf-8",
    )
    return write_final_offline_report(output_dir, args.models, args.transcript, args.samples)


if __name__ == "__main__":
    raise SystemExit(main())
