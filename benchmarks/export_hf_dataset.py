#!/usr/bin/env python3
"""Package LongListBench as a Hugging Face datasets repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_REPO_ID = "kaydotai/LongListBench"
CONFIG_ORDER = ("core_claims", "claim_multihop", "policy_multihop")
CONFIG_DESCRIPTIONS = {
    "core_claims": "80 loss-run PDFs across easy, medium, hard, and extreme complexity regimes.",
    "claim_multihop": "3 loss-run PDFs where one incident record must be assembled from distant sections.",
    "policy_multihop": "3 commercial policy packets with heterogeneous policy records across BOP, WC, and CGL.",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sample_id(instance: dict[str, Any]) -> str:
    value = instance.get("id") or instance.get("instance_id")
    if not value:
        raise ValueError(f"Manifest instance is missing id: {instance}")
    return str(value)


def instance_domain(instance: dict[str, Any]) -> str:
    return str(instance.get("domain") or "claims")


def target_record_type(instance: dict[str, Any]) -> str:
    if instance.get("target_record_type"):
        return str(instance["target_record_type"])
    if instance_domain(instance) == "policy_review":
        return "policy_packet_item"
    return "loss_run_incident"


def target_field(instance: dict[str, Any]) -> str:
    return "records" if instance_domain(instance) == "policy_review" else "incidents"


def target_count(instance: dict[str, Any], ground_truth: list[Any]) -> int:
    for key in ("num_target_records", "num_policy_items", "num_claims"):
        value = instance.get(key)
        if isinstance(value, int):
            return value
    return len(ground_truth)


def page_count(instance: dict[str, Any]) -> int:
    for key in ("pdf_page_count", "pages_estimate"):
        value = instance.get(key)
        if isinstance(value, int):
            return value
    return 0


def config_for_instance(instance: dict[str, Any]) -> str:
    if instance_domain(instance) == "policy_review":
        return "policy_multihop"
    if instance.get("format") == "crosspage":
        return "claim_multihop"
    return "core_claims"


def resolve_artifact(dataset_dir: Path, instance: dict[str, Any], artifact: str) -> Path:
    files = instance.get("files") or {}
    relative = files.get(artifact)
    if not relative:
        raise ValueError(f"{sample_id(instance)} is missing files.{artifact}")
    path = dataset_dir / relative
    if not path.exists():
        raise FileNotFoundError(f"Missing {artifact} for {sample_id(instance)}: {path}")
    return path


def optional_transcript(dataset_dir: Path, instance: dict[str, Any], artifact: str) -> str:
    files = instance.get("files") or {}
    relative = files.get(artifact)
    if not relative:
        return ""
    path = dataset_dir / relative
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def row_for_instance(dataset_dir: Path, instance: dict[str, Any]) -> dict[str, Any]:
    sid = sample_id(instance)
    gt_path = resolve_artifact(dataset_dir, instance, "ground_truth")
    pdf_path = resolve_artifact(dataset_dir, instance, "pdf")
    ground_truth = read_json(gt_path)
    if not isinstance(ground_truth, list):
        raise ValueError(f"{sid} ground truth must be a list, got {type(ground_truth).__name__}")

    normalized_domain = instance_domain(instance)
    normalized_target_field = target_field(instance)
    metadata = {
        "manifest_instance": instance,
        "source_files": instance.get("files", {}),
        "ground_truth_sha256": sha256_file(gt_path),
        "pdf_sha256": sha256_file(pdf_path),
    }

    return {
        "document_id": sid,
        "domain": normalized_domain,
        "complexity_regime": str(instance.get("complexity_regime") or instance.get("difficulty") or ""),
        "difficulty": str(instance.get("difficulty") or ""),
        "document_format": str(instance.get("format") or ""),
        "num_pages": page_count(instance),
        "target_field": normalized_target_field,
        "target_record_type": target_record_type(instance),
        "target_count": target_count(instance, ground_truth),
        "problems": list(instance.get("problems") or []),
        "transcript_conditions": list(instance.get("transcripts_available") or []),
        "pdf": {"path": f"{sid}.pdf", "bytes": pdf_path.read_bytes()},
        "ground_truth": canonical_json({normalized_target_field: ground_truth}),
        "metadata": canonical_json(metadata),
        "canonical_transcript": optional_transcript(dataset_dir, instance, "canonical_md"),
        "ocr_transcript": optional_transcript(dataset_dir, instance, "ocr_md"),
    }


def build_config_rows(dataset_dir: Path) -> dict[str, list[dict[str, Any]]]:
    manifest = read_json(dataset_dir / "manifest.json")
    rows_by_config: dict[str, list[dict[str, Any]]] = {name: [] for name in CONFIG_ORDER}
    for instance in manifest["instances"]:
        rows_by_config[config_for_instance(instance)].append(row_for_instance(dataset_dir, instance))
    return rows_by_config


def summarize_rows(rows_by_config: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for config_name in CONFIG_ORDER:
        rows = rows_by_config.get(config_name, [])
        page_counts = [row["num_pages"] for row in rows]
        target_counts = [row["target_count"] for row in rows]
        domains = Counter(row["domain"] for row in rows)
        summary[config_name] = {
            "rows": len(rows),
            "targets": sum(target_counts),
            "min_pages": min(page_counts) if page_counts else 0,
            "max_pages": max(page_counts) if page_counts else 0,
            "domains": dict(sorted(domains.items())),
        }
    return summary


def write_parquet_export(rows_by_config: dict[str, list[dict[str, Any]]], output_dir: Path) -> None:
    try:
        from datasets import Dataset, Features, Pdf, Sequence, Value
    except ImportError as exc:
        raise SystemExit(
            "Missing Hugging Face export dependencies. "
            "Install them with: python -m pip install -r benchmarks/requirements-hf.txt"
        ) from exc

    features = Features(
        {
            "document_id": Value("string"),
            "domain": Value("string"),
            "complexity_regime": Value("string"),
            "difficulty": Value("string"),
            "document_format": Value("string"),
            "num_pages": Value("int32"),
            "target_field": Value("string"),
            "target_record_type": Value("string"),
            "target_count": Value("int32"),
            "problems": Sequence(Value("string")),
            "transcript_conditions": Sequence(Value("string")),
            "pdf": Pdf(decode=False),
            "ground_truth": Value("string"),
            "metadata": Value("string"),
            "canonical_transcript": Value("string"),
            "ocr_transcript": Value("string"),
        }
    )

    for config_name in CONFIG_ORDER:
        rows = rows_by_config.get(config_name, [])
        if not rows:
            continue
        config_dir = output_dir / "data" / config_name
        config_dir.mkdir(parents=True, exist_ok=True)
        dataset = Dataset.from_list(rows, features=features)
        dataset.to_parquet(config_dir / "test-00000-of-00001.parquet")


def write_metadata_files(dataset_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir = output_dir / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dataset_dir / "manifest.json", metadata_dir / "manifest.json")

    schema_dir = output_dir / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)
    for schema_path in sorted((dataset_dir / "schemas").glob("*.schema.json")):
        shutil.copy2(schema_path, schema_dir / schema_path.name)


def dataset_card(repo_id: str, summary: dict[str, dict[str, Any]]) -> str:
    config_yaml = "\n".join(
        [
            f"- config_name: {config_name}\n"
            "  data_files:\n"
            "  - split: test\n"
            f"    path: data/{config_name}/test-*.parquet"
            for config_name in CONFIG_ORDER
        ]
    )
    config_rows = "\n".join(
        [
            "| {name} | {description} | {rows} | {targets} | {min_pages}-{max_pages} |".format(
                name=config_name,
                description=CONFIG_DESCRIPTIONS[config_name],
                **summary[config_name],
            )
            for config_name in CONFIG_ORDER
        ]
    )

    total_rows = sum(item["rows"] for item in summary.values())
    total_targets = sum(item["targets"] for item in summary.values())

    return f"""---
pretty_name: LongListBench
language:
- en
license: mit
tags:
- synthetic
- pdf
- ocr
- document-ai
- information-extraction
- structured-extraction
- long-list-extraction
- long-range-evidence
- insurance
configs:
{config_yaml}
---

# LongListBench

LongListBench is a synthetic PDF benchmark for extracting long lists of structured records from semi-structured insurance documents. It is designed around three stressors that are common in production document extraction: many target records, complex layouts, and evidence that can be separated by long page distances.

The dataset contains {total_rows} PDF documents and {total_targets} target records. All visible document content is synthetic and does not contain real customer PII.

## Configs

| Config | Description | Documents | Target records | Page range |
|---|---|---:|---:|---:|
{config_rows}

## Columns

- `document_id`: Stable sample identifier.
- `domain`: `claims` or `policy_review`.
- `complexity_regime`: High-level regime used by the generator.
- `difficulty`: Generator tier, such as `easy`, `medium`, `hard`, `extreme`, `multihop`, or `mixed`.
- `document_format`: Rendered layout family.
- `num_pages`: Page count recorded by the generator.
- `target_field`: Top-level JSON field to evaluate, either `incidents` or `records`.
- `target_record_type`: Primary schema for the expected output.
- `target_count`: Number of target records in `ground_truth`.
- `problems`: Complexity tags for the document.
- `transcript_conditions`: Available transcript conditions, usually `canonical` and sometimes `ocr`.
- `pdf`: Embedded PDF bytes.
- `ground_truth`: JSON string containing the expected records under `target_field`.
- `metadata`: JSON string with source manifest metadata, file hashes, evidence maps, and generation details.
- `canonical_transcript`: Clean transcript derived from the generated document structure.
- `ocr_transcript`: Gemini OCR transcript when available, otherwise an empty string.

## Usage

```python
from datasets import load_dataset

ds = load_dataset("{repo_id}", "core_claims", split="test")
row = ds[0]

pdf_bytes = row["pdf"]["bytes"]
ground_truth = row["ground_truth"]
metadata = row["metadata"]
```

Available configs:

```python
for config in ["core_claims", "claim_multihop", "policy_multihop"]:
    ds = load_dataset("{repo_id}", config, split="test")
    print(config, len(ds), sum(row["target_count"] for row in ds))
```

## Evaluation

The repository includes an evaluator that runs one-shot and agentic extraction modes over canonical or OCR transcripts and scores field-level extraction quality against the ground truth. See `benchmarks/evaluate_models.py` in the source repository.

The `ground_truth` column is stored as a JSON string so consumers can choose their own extraction schema enforcement. Claims rows use `{{"incidents": [...]}}`; policy rows use `{{"records": [...]}}`.

## Provenance and Limitations

The documents are synthetic. Policy packets are structurally inspired by commercial insurance policy workflows, but names, values, prose, and identifiers are generated fixtures. OCR transcripts are included only where OCR has been run and accepted for the released data.

This benchmark is intended for measuring long-list and long-range-evidence extraction behavior. It is not a substitute for evaluation on a private production corpus.

## Citation

If you use this dataset, cite the LongListBench repository and paper draft.
"""


def write_dataset_card(output_dir: Path, repo_id: str, summary: dict[str, dict[str, Any]]) -> None:
    (output_dir / "README.md").write_text(dataset_card(repo_id, summary), encoding="utf-8")


def upload_to_hub(output_dir: Path, repo_id: str) -> None:
    try:
        from huggingface_hub import HfApi
    except ImportError as exc:
        raise SystemExit(
            "Missing huggingface_hub. Install with: python -m pip install -r benchmarks/requirements-hf.txt"
        ) from exc

    api = HfApi()
    api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)
    api.upload_folder(repo_id=repo_id, repo_type="dataset", folder_path=output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data"), help="Input data directory.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/huggingface/longlistbench"),
        help="Output directory for the Hugging Face dataset package.",
    )
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help="Target Hugging Face dataset repo ID.")
    parser.add_argument("--overwrite", action="store_true", help="Remove the output directory before writing.")
    parser.add_argument("--upload", action="store_true", help="Upload the generated package to Hugging Face Hub.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_dir = args.input
    output_dir = args.output

    if args.overwrite and output_dir.exists():
        shutil.rmtree(output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"Output directory is not empty: {output_dir}. Use --overwrite.")

    rows_by_config = build_config_rows(dataset_dir)
    summary = summarize_rows(rows_by_config)
    write_parquet_export(rows_by_config, output_dir)
    write_metadata_files(dataset_dir, output_dir)
    write_dataset_card(output_dir, args.repo_id, summary)

    print(json.dumps({"output": str(output_dir), "repo_id": args.repo_id, "configs": summary}, indent=2))
    if args.upload:
        upload_to_hub(output_dir, args.repo_id)


if __name__ == "__main__":
    main()
