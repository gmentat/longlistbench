"""Shared helpers for policy benchmark generation."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


def dataset_version() -> str:
    version = None
    try:
        pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
        if pyproject.exists():
            text = pyproject.read_text(encoding="utf-8")
            match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
            if match:
                version = match.group(1)
    except Exception:
        pass
    return version or "1.0.0"


def stable_seed(base_seed: int, case_id: str, offset: int) -> int:
    digest = hashlib.sha256(f"{base_seed}:{case_id}:{offset}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def count_pdf_pages(pdf_path: Path) -> int | None:
    if not pdf_path.exists():
        return None
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


def money(value: int) -> str:
    return f"${value:,.0f}"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
