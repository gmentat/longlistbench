"""Dataset artifact path helpers.

LongListBench publishes artifacts in a modality-separated layout under
``data/`` while a few tests and older scratch workflows still use the original
flat layout. Keep path resolution in one place so evaluation code does not
need to know which layout it is reading.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_DIR = Path(__file__).resolve().parent
DATASET_DIR = REPO_ROOT / "data"
LEGACY_CLAIMS_DIR = BENCHMARKS_DIR / "claims"

_TRANSCRIPT_DIRS = {
    "canonical": Path("transcripts") / "canonical",
    "ocr": Path("transcripts") / "ocr_gemini",
}

_FLAT_TRANSCRIPT_SUFFIXES = {
    "canonical": "_canonical.md",
    "ocr": "_ocr.md",
}


def default_dataset_dir() -> Path:
    """Return the preferred dataset root for CLI defaults."""
    return DATASET_DIR if DATASET_DIR.exists() else LEGACY_CLAIMS_DIR


def is_organized_dataset(dataset_dir: Path) -> bool:
    """Return True when ``dataset_dir`` uses the public modality layout."""
    return (
        (dataset_dir / "pdfs").is_dir()
        and (dataset_dir / "ground_truth").is_dir()
        and (dataset_dir / "transcripts").is_dir()
    )


def ensure_organized_dataset_dirs(dataset_dir: Path) -> None:
    """Create the public dataset subdirectories."""
    for relative in [
        "pdfs",
        "html",
        "ground_truth",
        "metadata",
        "schemas",
        "transcripts/canonical",
        "transcripts/ocr_gemini",
    ]:
        (dataset_dir / relative).mkdir(parents=True, exist_ok=True)


def manifest_path(dataset_dir: Path) -> Path:
    """Return the suite manifest path, supporting the legacy metadata filename."""
    path = dataset_dir / "manifest.json"
    if path.exists() or is_organized_dataset(dataset_dir):
        return path
    return dataset_dir / "metadata.json"


def artifact_path(dataset_dir: Path, sample_id: str, artifact: str) -> Path:
    """Resolve an artifact path for either organized or legacy-flat data."""
    if is_organized_dataset(dataset_dir):
        if artifact == "pdf":
            return dataset_dir / "pdfs" / f"{sample_id}.pdf"
        if artifact == "html":
            return dataset_dir / "html" / f"{sample_id}.html"
        if artifact == "ground_truth":
            return dataset_dir / "ground_truth" / f"{sample_id}.json"
        if artifact == "metadata":
            return dataset_dir / "metadata" / f"{sample_id}.json"
        if artifact in _TRANSCRIPT_DIRS:
            return dataset_dir / _TRANSCRIPT_DIRS[artifact] / f"{sample_id}.md"
        raise ValueError(f"Unknown artifact kind: {artifact}")

    if artifact == "pdf":
        return dataset_dir / f"{sample_id}.pdf"
    if artifact == "html":
        return dataset_dir / f"{sample_id}.html"
    if artifact == "ground_truth":
        return dataset_dir / f"{sample_id}.json"
    if artifact == "metadata":
        return dataset_dir / f"{sample_id}_metadata.json"
    if artifact in _FLAT_TRANSCRIPT_SUFFIXES:
        return dataset_dir / f"{sample_id}{_FLAT_TRANSCRIPT_SUFFIXES[artifact]}"
    raise ValueError(f"Unknown artifact kind: {artifact}")


def artifact_relative_path(dataset_dir: Path, sample_id: str, artifact: str) -> str:
    """Return an artifact path relative to ``dataset_dir``."""
    return artifact_path(dataset_dir, sample_id, artifact).relative_to(dataset_dir).as_posix()


def transcript_path(dataset_dir: Path, sample_id: str, transcript: str) -> Path:
    """Resolve a canonical or OCR transcript path."""
    return artifact_path(dataset_dir, sample_id, transcript)


def ground_truth_path(dataset_dir: Path, sample_id: str) -> Path:
    """Resolve a sample ground-truth JSON path."""
    return artifact_path(dataset_dir, sample_id, "ground_truth")


def iter_transcript_paths(dataset_dir: Path, transcript: str) -> list[Path]:
    """List transcript files for a transcript condition."""
    if is_organized_dataset(dataset_dir):
        folder = dataset_dir / _TRANSCRIPT_DIRS[transcript]
        return sorted(folder.glob("*.md")) if folder.exists() else []
    suffix = _FLAT_TRANSCRIPT_SUFFIXES[transcript]
    return sorted(dataset_dir.glob(f"*{suffix}"))


def sample_id_from_transcript_path(dataset_dir: Path, path: Path, transcript: str) -> str:
    """Recover the sample ID from a transcript artifact path."""
    if is_organized_dataset(dataset_dir):
        return path.stem
    suffix = _FLAT_TRANSCRIPT_SUFFIXES[transcript]
    return path.name[: -len(suffix)]


def collect_pdf_paths(dataset_dir: Path, *, recursive: bool = False) -> list[Path]:
    """Collect PDFs from either the organized or legacy dataset layout."""
    if is_organized_dataset(dataset_dir):
        pdf_root = dataset_dir / "pdfs"
        return sorted(pdf_root.rglob("*.pdf") if recursive else pdf_root.glob("*.pdf"))
    return sorted(dataset_dir.rglob("*.pdf") if recursive else dataset_dir.glob("*.pdf"))


def target_record_count(instance: dict[str, Any]) -> int:
    """Return the number of scored target records for a manifest instance."""
    for key in ("num_target_records", "num_policy_items", "num_claims"):
        value = instance.get(key)
        if value is not None:
            return int(value)
    return 0


def record_count_summary(instances: list[dict[str, Any]]) -> dict[str, int]:
    """Summarize claim, policy, and total target-record counts."""
    total_claims = 0
    total_policy_items = 0

    for instance in instances:
        count = target_record_count(instance)
        if instance.get("domain") == "policy_review" or instance.get("num_policy_items") is not None:
            total_policy_items += count
        else:
            total_claims += count

    return {
        "total_claims": total_claims,
        "total_policy_items": total_policy_items,
        "total_target_records": total_claims + total_policy_items,
    }
