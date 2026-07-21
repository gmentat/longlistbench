#!/usr/bin/env python3
"""Build the static LongListBench leaderboard Space from saved evaluation reports."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

DEFAULT_REPO_ID = "kaydotai/LongListBench-Leaderboard"
REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = Path(__file__).resolve().parent / "results"
RELEASE_VERSION = "v" + (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_OUTPUT = REPO_ROOT / "dist" / "huggingface" / "leaderboard_space"

RUNS = (
    ("codex_gpt56_sol_full_current_ocr_v2", "codex_gpt56_sol", "Codex CLI", "GPT-5.6-Sol"),
    ("claude_opus48_full_current_ocr_v2", "claude_opus48", "Claude Code", "Claude Opus 4.8"),
    ("claude_fable5_full_current_ocr_v2", "claude_fable5", "Claude Code", "Claude Fable 5"),
    ("codex_full_current_ocr_v2", "codex_gpt55", "Codex CLI", "GPT-5.5"),
)
SPACE_FILENAMES = ("README.md", "index.html", "leaderboard_data.json")


def load_runs(results_dir: Path) -> tuple[list[dict], dict]:
    models = []
    dataset_meta: dict = {}
    expected_manifest: str | None = None
    expected_shape: tuple[int, int] | None = None
    for run_dir, key, harness, model_name in RUNS:
        report = json.loads((results_dir / run_dir / "evaluation_report.json").read_text(encoding="utf-8"))
        meta = json.loads((results_dir / run_dir / "run_metadata.json").read_text(encoding="utf-8"))
        stats = report["model_stats"][key]
        manifest = report["dataset"]["manifest_sha256"]
        shape = (stats["total_samples"], stats["total_rows"])
        if expected_manifest is None:
            expected_manifest = manifest
            expected_shape = shape
            dataset_meta = report["dataset"]
        elif manifest != expected_manifest or shape != expected_shape:
            raise ValueError(
                f"{run_dir} targets a different dataset: "
                f"manifest={manifest}, shape={shape}; "
                f"expected manifest={expected_manifest}, shape={expected_shape}"
            )
        models.append({
            "key": key,
            "harness": harness,
            "model": model_name,
            "requested_model": meta["requested_model"],
            "effort": meta["effort"],
            "cli_version": meta["cli_version_observed_at_metadata_write"],
            "run_date": meta["generated_at"][:10],
            "stats": stats,
        })
    return models, dataset_meta


def pct(value: float, digits: int = 1) -> str:
    return f"{100 * value:.{digits}f}"


def build_data(models: list[dict], dataset_meta: dict) -> dict:
    rows = []
    for m in models:
        s = m["stats"]
        roles = s["by_evaluation_role"]
        rows.append({
            "config": f"{m['harness']}, {m['model']} ({m['effort']})",
            "harness": m["harness"],
            "model": m["model"],
            "requested_model": m["requested_model"],
            "effort": m["effort"],
            "cli_version": m["cli_version"],
            "run_date": m["run_date"],
            "exact_record_recall": s["exact_record_recall"],
            "exact_record_precision": s["exact_record_precision"],
            "exact_record_f1": s["exact_record_f1"],
            "complete_documents": s["complete_documents"],
            "total_samples": s["total_samples"],
            "complete_document_rate": s["complete_document_rate"],
            "weighted_f1": s["weighted_f1"],
            "weighted_recall": s["weighted_recall"],
            "structural_exact_recall": roles["structural_challenge"]["exact_record_recall"],
            "scale_control_exact_recall": roles["scale_control"]["exact_record_recall"],
            "gold_records": s["total_rows"],
            "exact_record_matches": s["total_exact_record_matches"],
            "errors": s["errors"],
            "by_tier": s["by_tier"],
            "by_family": s["by_complexity_regime"],
            "by_stressor": s["by_stressor"],
        })
    rows.sort(key=lambda r: r["exact_record_recall"], reverse=True)
    return {
        "benchmark": "LongListBench",
        "version": RELEASE_VERSION,
        "dataset": dataset_meta,
        "protocol": (
            "Agentic CLI extraction from OCR transcripts "
            "(repository-denied sandbox, same task prompt for all runs)"
        ),
        "results": rows,
    }


def build_html(data: dict) -> str:
    rows_html = []
    for i, r in enumerate(data["results"], 1):
        rows_html.append(
            "<tr>"
            f"<td class='rank'>{i}</td>"
            f"<td class='cfg'><span class='model'>{r['model']}</span>"
            f"<span class='sub'>{r['harness']} · {r['effort']} · {r['run_date']}</span></td>"
            f"<td class='num prim'>{pct(r['exact_record_recall'])}</td>"
            f"<td class='num'>{r['complete_documents']}/{r['total_samples']}</td>"
            f"<td class='num'>{pct(r['structural_exact_recall'])}</td>"
            f"<td class='num'>{pct(r['scale_control_exact_recall'])}</td>"
            f"<td class='num'>{pct(r['weighted_f1'])}</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base target="_blank">
<title>LongListBench Leaderboard</title>
<style>
:root {{
  --bg: #ffffff; --fg: #1a1d23; --dim: #6b7280; --line: #e5e7eb;
  --card: #f8fafc; --accent: #4f46e5; --head: #f1f5f9;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #0f1117; --fg: #e5e7eb; --dim: #9ca3af; --line: #272b35;
    --card: #161922; --accent: #818cf8; --head: #1b1f2a;
  }}
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--fg);
  font: 15px/1.55 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
.wrap {{ max-width: 880px; margin: 0 auto; padding: 44px 24px 56px; }}
h1 {{ font-size: 26px; margin: 0 0 4px; letter-spacing: -0.01em; }}
p.lede {{ color: var(--dim); margin: 0 0 14px; max-width: 68ch; }}
.links {{ margin: 0 0 26px; display: flex; gap: 10px; flex-wrap: wrap; }}
.links a {{ color: var(--accent); text-decoration: none; font-size: 14px;
  border: 1px solid var(--line); border-radius: 999px; padding: 5px 14px; background: var(--card); }}
.links a:hover {{ border-color: var(--accent); }}
.tablebox {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: var(--card); }}
table {{ border-collapse: collapse; width: 100%; font-size: 14.5px; }}
th, td {{ padding: 11px 14px; text-align: left; border-top: 1px solid var(--line); white-space: nowrap; }}
thead th {{ border-top: none; background: var(--head); color: var(--dim); font-weight: 600;
  font-size: 12.5px; text-transform: uppercase; letter-spacing: 0.04em; }}
td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
td.prim {{ font-weight: 700; color: var(--accent); font-size: 15.5px; }}
td.rank {{ color: var(--dim); width: 2ch; }}
td.cfg .model {{ font-weight: 600; display: block; }}
td.cfg .sub {{ color: var(--dim); font-size: 12px; display: block; }}
.metrics {{ color: var(--dim); font-size: 13px; margin: 10px 2px 0; max-width: 78ch; }}
.submit {{ margin-top: 36px; border: 1px solid var(--line); border-radius: 10px;
  background: var(--card); padding: 16px 20px; }}
.submit h2 {{ font-size: 16px; margin: 0 0 8px; }}
.submit p {{ margin: 6px 0; font-size: 14px; color: var(--dim); }}
.submit a {{ color: var(--accent); }}
code {{ background: var(--bg); border: 1px solid var(--line); border-radius: 4px; padding: 1px 5px; font-size: 12.5px; }}
footer {{ margin-top: 28px; color: var(--dim); font-size: 12.5px; }}
footer a {{ color: var(--accent); }}
</style>
</head>
<body>
<div class="wrap">
<h1>LongListBench Leaderboard</h1>
<p class="lede">Complete document-to-list extraction from long business PDFs — 32 documents,
29,599 target records, OCR-conditioned agentic protocol.</p>
<div class="links">
<a href="https://huggingface.co/datasets/kaydotai/LongListBench">🤗 Dataset</a>
<a href="https://github.com/kaydotai/longlistbench">GitHub</a>
</div>

<div class="tablebox"><table>
<thead><tr><th></th><th>Configuration</th><th class="num">Exact recall</th>
<th class="num">Complete docs</th><th class="num">Structural</th><th class="num">Scale ctrl</th>
<th class="num">Field F1</th></tr></thead>
<tbody>
{''.join(rows_html)}
</tbody>
</table></div>
<p class="metrics"><b>Exact recall</b>: share of gold records reproduced exactly (primary metric).
<b>Complete docs</b>: documents with the full record list reproduced perfectly.
<b>Structural / Scale ctrl</b>: exact recall on structurally hard documents vs. long simple lists.
<b>Field F1</b>: partial-credit field overlap (secondary).</p>

<div class="submit">
<h2>Submit a result</h2>
<p>1. Run your system on the <a href="https://huggingface.co/datasets/kaydotai/LongListBench">dataset</a>
({RELEASE_VERSION}) and score it with the
<a href="https://github.com/kaydotai/longlistbench/blob/{RELEASE_VERSION}/benchmarks/evaluation_metrics.py">reference evaluator</a>
(see the <a href="https://github.com/kaydotai/longlistbench#readme">README</a> for runner scripts).</p>
<p>2. Open a pull request or issue on
<a href="https://github.com/kaydotai/longlistbench">GitHub</a> — or a discussion in this Space's
<a href="https://huggingface.co/spaces/kaydotai/LongListBench-Leaderboard/discussions">Community tab</a> —
with your <code>evaluation_report.json</code>, <code>run_metadata.json</code>, and per-sample predictions.</p>
<p>3. Verified results (scores must reproduce from the saved predictions) are added here.</p>
</div>

<footer>Dataset {RELEASE_VERSION}. Per-tier, per-family, and per-stressor slices are in the
<a href="leaderboard_data.json">raw JSON</a>.</footer>
</div>
</body>
</html>
"""


README = f"""---
title: LongListBench Leaderboard
emoji: 📊
colorFrom: indigo
colorTo: blue
sdk: static
pinned: false
license: mit
short_description: Extraction results on LongListBench (32 PDFs, 29.6k records)
---

# LongListBench Leaderboard

Leaderboard for [LongListBench](https://huggingface.co/datasets/kaydotai/LongListBench) —
complete document-to-list extraction from long business PDFs.

## Submitting a result

1. Run your system on the dataset and score it with the
   [reference evaluator](https://github.com/kaydotai/longlistbench/blob/{RELEASE_VERSION}/benchmarks/evaluation_metrics.py).
2. Open a PR or issue on [GitHub](https://github.com/kaydotai/longlistbench) — or a discussion in
   this Space's Community tab — with your `evaluation_report.json`, `run_metadata.json`, and
   per-sample predictions.
3. Results are verified (scores must reproduce from the saved predictions) and added.

`leaderboard_data.json` holds the full numbers, including per-tier, per-family, and per-stressor slices.

This Space is generated by
[`benchmarks/export_leaderboard_space.py`](https://github.com/kaydotai/longlistbench/blob/main/benchmarks/export_leaderboard_space.py)
from the saved evaluation reports in the repository.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR, help="Directory holding run result folders.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output directory for the Space files.")
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help="Target Hugging Face Space repo ID.")
    parser.add_argument("--overwrite", action="store_true", help="Replace a non-empty output directory.")
    parser.add_argument("--upload", action="store_true", help="Upload the generated Space to Hugging Face Hub.")
    return parser.parse_args()


def prepare_output(output: Path, *, overwrite: bool) -> None:
    if output.is_file() or output.is_symlink():
        if not overwrite:
            raise FileExistsError(f"output path already exists: {output}; pass --overwrite to replace it")
        output.unlink()
    elif output.exists() and any(output.iterdir()):
        if not overwrite:
            raise FileExistsError(f"output directory is not empty: {output}; pass --overwrite to replace it")
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    models, dataset_meta = load_runs(args.results_dir)
    data = build_data(models, dataset_meta)
    prepare_output(args.output, overwrite=args.overwrite)
    (args.output / "leaderboard_data.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (args.output / "index.html").write_text(build_html(data), encoding="utf-8")
    (args.output / "README.md").write_text(README, encoding="utf-8")
    print(f"Wrote {args.output}")
    for path in sorted(args.output.iterdir()):
        print(f"  {path.name} ({path.stat().st_size} bytes)")
    if args.upload:
        from huggingface_hub import HfApi

        api = HfApi()
        api.create_repo(args.repo_id, repo_type="space", space_sdk="static", exist_ok=True)
        result = api.upload_folder(
            folder_path=str(args.output),
            repo_id=args.repo_id,
            repo_type="space",
            allow_patterns=list(SPACE_FILENAMES),
        )
        print(f"Uploaded: {result.commit_url}")


if __name__ == "__main__":
    main()
