#!/usr/bin/env python3
"""Organize LongListBench artifacts into the public dataset layout."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .dataset_layout import (
        artifact_path,
        artifact_relative_path,
        ensure_organized_dataset_dirs,
        record_count_summary,
    )
except ImportError:
    from dataset_layout import (
        artifact_path,
        artifact_relative_path,
        ensure_organized_dataset_dirs,
        record_count_summary,
    )


_SAMPLE_SUFFIXES = {
    "ground_truth": ".json",
    "pdf": ".pdf",
    "html": ".html",
    "canonical": "_canonical.md",
    "ocr": "_ocr.md",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _copy_or_move(src: Path, dst: Path, *, move: bool) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if move:
        shutil.move(str(src), str(dst))
    else:
        shutil.copy2(src, dst)


def _instance_files(dataset_dir: Path, sample_id: str) -> dict[str, Any]:
    files = {
        "ground_truth": artifact_relative_path(dataset_dir, sample_id, "ground_truth"),
        "pdf": artifact_relative_path(dataset_dir, sample_id, "pdf"),
        "html": artifact_relative_path(dataset_dir, sample_id, "html"),
        "canonical_md": artifact_relative_path(dataset_dir, sample_id, "canonical"),
        "ocr_md": artifact_relative_path(dataset_dir, sample_id, "ocr"),
    }
    for key, artifact in [
        ("json_size_bytes", "ground_truth"),
        ("pdf_size_bytes", "pdf"),
        ("html_size_bytes", "html"),
        ("canonical_size_bytes", "canonical"),
        ("ocr_size_bytes", "ocr"),
    ]:
        path = artifact_path(dataset_dir, sample_id, artifact)
        files[key] = path.stat().st_size if path.exists() else 0
    return files


def _normalize_instance(dataset_dir: Path, instance: dict[str, Any]) -> dict[str, Any]:
    sample_id = instance["id"]
    out = dict(instance)
    out["files"] = _instance_files(dataset_dir, sample_id)
    out.setdefault("complexity_regime", out.get("difficulty"))
    out.setdefault("document_count", 1)
    out.setdefault("evidence_pattern", "single_document")
    return out


def organize_flat_claims(source_dir: Path, dataset_dir: Path, *, move: bool) -> dict[str, Any]:
    """Move or copy the original flat claims directory into ``dataset_dir``."""
    ensure_organized_dataset_dirs(dataset_dir)
    source_manifest = _read_json(source_dir / "metadata.json")
    instances: list[dict[str, Any]] = []

    for instance in source_manifest.get("instances", []):
        sample_id = instance["id"]
        _copy_or_move(source_dir / f"{sample_id}.json", artifact_path(dataset_dir, sample_id, "ground_truth"), move=move)
        _copy_or_move(source_dir / f"{sample_id}.pdf", artifact_path(dataset_dir, sample_id, "pdf"), move=move)
        _copy_or_move(source_dir / f"{sample_id}.html", artifact_path(dataset_dir, sample_id, "html"), move=move)
        _copy_or_move(source_dir / f"{sample_id}_canonical.md", artifact_path(dataset_dir, sample_id, "canonical"), move=move)
        _copy_or_move(source_dir / f"{sample_id}_ocr.md", artifact_path(dataset_dir, sample_id, "ocr"), move=move)

        normalized = _normalize_instance(dataset_dir, instance)
        _write_json(artifact_path(dataset_dir, sample_id, "metadata"), normalized)
        instances.append(normalized)

    manifest = dict(source_manifest)
    manifest["layout"] = {
        "type": "modality_separated",
        "pdfs": "pdfs/{sample_id}.pdf",
        "html": "html/{sample_id}.html",
        "ground_truth": "ground_truth/{sample_id}.json",
        "canonical_transcripts": "transcripts/canonical/{sample_id}.md",
        "ocr_transcripts": "transcripts/ocr_gemini/{sample_id}.md",
        "metadata": "metadata/{sample_id}.json",
    }
    manifest["organized_at"] = datetime.now(timezone.utc).isoformat()
    manifest["instances"] = instances
    manifest["total_instances"] = len(instances)
    manifest.update(record_count_summary(instances))
    manifest["complexity_regimes"] = sorted(
        {str(instance.get("complexity_regime")) for instance in instances if instance.get("complexity_regime")}
    )

    _write_json(dataset_dir / "manifest.json", manifest)
    _write_json(dataset_dir / "metadata.json", manifest)

    for index_name in ["index.json", "index.csv", "index.html"]:
        _copy_or_move(source_dir / index_name, dataset_dir / index_name, move=move)

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Organize flat LongListBench claims artifacts into data/")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).parent / "claims",
        help="Flat source directory (default: benchmarks/claims)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Organized dataset directory (default: data)",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move files instead of copying them",
    )
    args = parser.parse_args()

    manifest = organize_flat_claims(args.source, args.output, move=args.move)
    print(f"Organized {manifest['total_instances']} samples in {args.output}")


if __name__ == "__main__":
    main()
