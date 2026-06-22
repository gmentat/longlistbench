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
        target_fields = sorted(set(row["target_field"] for row in rows))
        summary[config_name] = {
            "rows": len(rows),
            "targets": sum(target_counts),
            "min_targets": min(target_counts) if target_counts else 0,
            "max_targets": max(target_counts) if target_counts else 0,
            "min_pages": min(page_counts) if page_counts else 0,
            "max_pages": max(page_counts) if page_counts else 0,
            "domains": dict(sorted(domains.items())),
            "target_fields": target_fields,
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
            "| `{name}` | {description} | `{target_field}` | {rows} | {min_targets}-{max_targets} | {targets} | {min_pages}-{max_pages} |".format(
                name=config_name,
                description=CONFIG_DESCRIPTIONS[config_name],
                target_field="`, `".join(summary[config_name]["target_fields"]),
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
- document-extraction
- benchmark
- synthetic
- pdf
- ocr
- document-ai
- information-extraction
- structured-extraction
- long-list-extraction
- long-array
- large-array
- long-range-evidence
- insurance
size_categories:
- n<1K
configs:
{config_yaml}
---

# LongListBench

LongListBench is a synthetic benchmark for measuring **long-list structured extraction** from insurance PDFs: the task of extracting every item in a large repeating record set, without dropping records, merging neighboring records, inventing extras, or losing fields when the document has complex layout, OCR noise, or evidence spread across distant pages.

Most document-extraction benchmarks emphasize document-level header fields. LongListBench focuses on the production failure mode that appears once the target is a long list: recall and precision degrade as the model must preserve many records, normalize repeated fields, and sometimes join values from sections separated by dozens or hundreds of pages.

The dataset contains {total_rows} PDF documents and {total_targets} target records. All visible document content is synthetic and does not contain real customer PII.

## Configs and Data Viewer

| Config | Description | Target field | Documents | Records/doc range | Target records | Page range |
|---|---|---|---:|---:|---:|---:|
{config_rows}

Pick one config when loading:

```python
from datasets import load_dataset

ds = load_dataset("{repo_id}", "core_claims", split="test")
# or "claim_multihop", or "policy_multihop"
print(ds)  # each row is one PDF document
```

## Columns

| Column | Type | Description |
|---|---|---|
| `document_id` | string | Stable sample identifier, e.g. `easy_10_001_detailed` or `multihop_bop_012_001`. |
| `domain` | string | `claims` or `policy_review`. |
| `complexity_regime` | string | Generator regime, such as `easy`, `hard`, `policy_multi_hop`, or `multihop`. |
| `difficulty` | string | Published difficulty tier: `easy`, `medium`, `hard`, `extreme`, `multihop`, or `mixed`. |
| `document_format` | string | Rendered layout family, currently `detailed`, `table`, or `crosspage`. |
| `num_pages` | int32 | Page count recorded by the generator. |
| `target_field` | string | Name of the top-level list to extract: `incidents` for claim rows, `records` for policy rows. |
| `target_record_type` | string | Primary schema family: `loss_run_incident` or `policy_packet_item`. |
| `target_count` | int32 | Number of target records in `ground_truth`. |
| `problems` | list[string] | Complexity tags for the document, e.g. `multi_row`, `merged_cells`, `long_range_evidence`. |
| `transcript_conditions` | list[string] | Available transcript conditions. All rows include `canonical`; accepted OCR rows include `ocr`. |
| `pdf` | Pdf | Embedded source PDF bytes. |
| `ground_truth` | string | JSON string containing the expected records under `target_field`. |
| `metadata` | string | JSON string with manifest metadata, file hashes, evidence maps, generation details, and source artifact paths. |
| `canonical_transcript` | string | Clean transcript derived from the generated document structure. |
| `ocr_transcript` | string | OCR transcript when available, otherwise an empty string. |

`ground_truth` is the complete schema-shaped object for the extraction target. Claims rows use `{{"incidents": [...]}}`; policy rows use `{{"records": [...]}}`.

## Usage

```python
import json
from datasets import load_dataset
from datasets import Pdf

ds = load_dataset("{repo_id}", "claim_multihop", split="test")

# The Pdf feature may decode through pdfplumber on access. Disable decoding
# when you only need bytes, transcripts, or ground truth.
ds = ds.cast_column("pdf", Pdf(decode=False))

row = ds[0]
gt = json.loads(row["ground_truth"])
records = gt[row["target_field"]]
assert len(records) == row["target_count"]

with open(f"{{row['document_id']}}.pdf", "wb") as f:
    f.write(row["pdf"]["bytes"])
```

## Canonical Scoring

The source repository includes the reference evaluator in `benchmarks/evaluation_metrics.py`. Scores are computed over field-value pairs, not just record counts.

### Method

1. **Shape.** Run your extractor on each PDF or transcript and return an object matching `ground_truth`: `{{"incidents": [...]}}` for claims or `{{"records": [...]}}` for policy packets. A bare list is also accepted by the repository evaluator.
2. **Claims matching.** Claim rows are keyed by normalized `incident_number`. Dates are normalized to `MM/DD/YYYY`, claimant lists are sorted, and financial breakdowns are rounded to cents. Each flattened `(incident_number, field_path, value)` tuple is one scored field-value pair.
3. **Policy matching.** Policy rows are heterogeneous. The evaluator groups records by `record_type`, greedily matches records using overlapping non-global field pairs, then scores flattened field-value pairs. Hidden row identifiers are not required.
4. **Metrics.** Recall is `found_gold_field_pairs / total_gold_field_pairs`. Precision is `found_field_pairs / total_pred_field_pairs`. F1 is the harmonic mean. Missing records reduce recall; extra predicted fields or records reduce precision.
5. **Aggregation.** Reports include per-document metrics plus corpus-level micro scores over all field-value pairs. Always report `predicted_count` beside F1 because long-list failures often show up as truncation or over-extraction.

Official scoring uses the repository evaluator. The following compact scorer is self-contained and useful for smoke checks; it follows the same field-pair precision/recall idea, but the repository implementation adds stricter date/decimal canonicalization and policy-record matching details.

```python
import json
from collections import Counter
from datasets import load_dataset

def flatten(value, prefix=""):
    if isinstance(value, dict):
        pairs = []
        for key, child in sorted(value.items()):
            name = f"{{prefix}}.{{key}}" if prefix else str(key)
            pairs.extend(flatten(child, name))
        return pairs
    if isinstance(value, list):
        pairs = []
        for child in value:
            pairs.extend(flatten(child, prefix))
        return pairs
    return [(prefix, "" if value is None else str(value).strip())]

def row_key(row, target_field):
    if target_field == "incidents":
        return str(row.get("incident_number", "")).strip().lstrip("#")
    signature_fields = [
        "record_type", "item_id", "coverage", "coverage_part", "form_number",
        "location_number", "building_number", "class_code", "state",
    ]
    return "|".join(str(row.get(field, "")).strip() for field in signature_fields)

def field_pairs(obj, target_field):
    rows = obj[target_field] if isinstance(obj, dict) else obj
    pairs = Counter()
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = row_key(row, target_field)
        pairs.update((key, field, value) for field, value in flatten(row))
    return pairs

def score_document(pred, gold, target_field):
    pred_pairs = field_pairs(pred, target_field)
    gold_pairs = field_pairs(gold, target_field)
    found = sum((pred_pairs & gold_pairs).values())
    recall = found / sum(gold_pairs.values()) if gold_pairs else 0.0
    precision = found / sum(pred_pairs.values()) if pred_pairs else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {{"f1": f1, "recall": recall, "precision": precision}}

config = "claim_multihop"
ds = load_dataset("{repo_id}", config, split="test")

for row in ds.remove_columns("pdf"):
    gold = json.loads(row["ground_truth"])
    pred = my_predictions[row["document_id"]]
    metrics = score_document(pred, gold, row["target_field"])
    print(row["document_id"], metrics["f1"], metrics["recall"], metrics["precision"])
```

## Schemas

Extraction schemas are published as standalone JSON Schema files under [`schemas/`](./schemas):

- [`schemas/loss_run_incident.schema.json`](./schemas/loss_run_incident.schema.json) - `incidents[]` for claim loss-run rows, including incident identifiers, policy fields, claimant/driver fields, dates, coverage fields, and nested financial breakdowns.
- [`schemas/policy_packet_item.schema.json`](./schemas/policy_packet_item.schema.json) - `records[]` for policy packet rows. Records are heterogeneous and may represent locations, coverages, forms, endorsements, exclusions, rating rows, or premium items depending on `record_type`.

These schemas describe the public extraction target. The ground truth in each row is generated from the same schema family.

## Transcript Conditions

The benchmark can be evaluated from different transcript conditions without changing the underlying PDF:

- `canonical_transcript`: clean text derived from the generated HTML/document structure.
- `ocr_transcript`: OCR text generated from rendered PDF page images when available.

All documents include canonical transcripts. The released multi-hop rows include OCR transcripts; core rows may have an empty `ocr_transcript` unless OCR has been generated for those PDFs.

## Provenance

The documents are synthetic. Each sample is produced by a reproducible generation pipeline:

1. Deterministic fixtures create the schema-shaped ground truth.
2. Layout generators project the records into claim schedules, tables, rosters, ledgers, declarations, forms, endorsements, rating schedules, and policy conditions.
3. HTML/CSS rendering produces the source PDF and a clean canonical transcript.
4. Optional Gemini OCR over rendered page images produces an OCR transcript for rows where OCR has been run and accepted.

Policy packets are structurally inspired by commercial insurance policy workflows, but names, values, prose, and identifiers are generated fixtures.

No real insureds, claimants, policies, financial accounts, or customer documents are represented. Real documents were used only as structural references for layout and packet organization.

## Limitations

LongListBench is intended for measuring long-list, layout, OCR, and long-range-evidence extraction behavior. It is not a substitute for evaluation on a private production corpus. Synthetic documents can underrepresent the visual and linguistic diversity of real carrier packets, and OCR transcripts are included only for rows where the OCR path has been run and reviewed.

## License

[MIT](https://github.com/kaydotai/longlistbench/blob/main/LICENSE). The documents and ground truth are synthetic and released with the repository under this license.

## Citation

```bibtex
@misc{{fedoruk2026longlistbench,
  title        = {{LongListBench: A Benchmark for Long-List Entity Extraction Under Layout and OCR Noise}},
  author       = {{Fedoruk, Anton and Shchoholiev, Serhii and Mehta, Akhil}},
  year         = {{2026}},
  version      = {{1.0.2}},
  howpublished = {{\\url{{https://github.com/kaydotai/longlistbench}}}}
}}
```
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
