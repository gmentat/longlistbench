# Released Fable 5 OCR Baseline

This directory contains the saved predictions and recomputable report for the LongListBench 2.0 Fable 5 baseline.

## Protocol

- Input: one released Gemini OCR transcript per run.
- Extractor: Claude Code CLI `2.1.207` invoking `claude-fable-5` with `--effort xhigh` on July 13, 2026.
- Authentication: Claude subscription. Dollar values in `run_metadata.json` are API-equivalent estimates, not billed subscription cost.
- Isolation: each run used a temporary document workspace, and a macOS sandbox denied the benchmark repository. The prompt prohibited other host files. This was repository isolation, not a host-wide filesystem allowlist. Ground truth, target values and counts, and generator code were not copied into the workspace. Claude Code safe mode disabled project instructions, skills, plugins, hooks, and MCP servers.
- Contract: claim runs received the published claim schema. Generic-record runs received the public output shape plus sample-specific field names and record groups derived from ground-truth object structure. They did not receive field values.
- Tools: the agent could inspect the transcript, write temporary parsing code, validate its output, and save JSON.
- Scoring: predictions were replayed through the repository evaluator against `data/ground_truth/`, with documented string, date, decimal, and domain-label canonicalization.

Every run reported `claude-fable-5` in model usage. Claude Code also reported auxiliary Haiku 4.5 routing, so this is a Claude Code/Fable 5 protocol baseline rather than a raw-model measurement.

## Result

| Documents | Target records | Errors | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 |
|---:|---:|---:|---:|---:|---:|---:|
| 36 | 33,450 | 0 | 90.6% | 15/36 (41.7%) | 98.9% | 98.7% |

Exact-record recall requires every normalized target field to match. Complete-document success requires an identical record multiset with no missing or extra records; source order is not scored.

## Artifacts

- `*_predicted.json`: 36 saved per-document predictions.
- `evaluation_report.json`: machine-readable aggregate and per-document metrics.
- `evaluation_report.md`: human-readable report.
- `per_sample_status.tsv`: run completion status.
- `run_metadata.json`: requested and observed models, effort, CLI version, duration, token usage, and API-equivalent cost estimate for each document.

Debug logs are intentionally excluded because they contain verbose agent traces and are not needed to recompute the scores.

## Reproduce

```bash
python benchmarks/run_claude_cli_evaluation.py \
  --output-dir benchmarks/results/claude_fable5_full_current_ocr_v2 \
  --model-key claude_fable5 \
  --model claude-fable-5 \
  --effort xhigh \
  --workers 4 \
  --timeout-seconds 3600
```

## Verify

```bash
python benchmarks/check_evaluation_report.py \
  --results-dir benchmarks/results/claude_fable5_full_current_ocr_v2
```
