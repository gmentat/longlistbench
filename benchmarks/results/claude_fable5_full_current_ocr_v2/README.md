# Released Fable 5 OCR Baseline

This directory contains the saved predictions and recomputable current LongListBench report for Fable 5.

## Protocol

- Input: one released Gemini OCR transcript per extraction.
- Extractor: Claude Code CLI invoking `claude-fable-5` at xhigh effort. The 29 unchanged inputs use the July 14, 2026 run (`2.1.209`); the corrected driver/MVR family was rerun July 21 (`2.1.216`).
- Authentication: Claude subscription. Dollar values in `run_metadata.json` are API-equivalent estimates, not billed subscription cost.
- Isolation: each extraction used a temporary workspace, and a macOS sandbox denied the benchmark repository. Ground truth, target values and counts, and generator code were absent. Claude Code safe mode disabled project instructions, skills, plugins, hooks, and MCP servers.
- Contract: claim runs received the published claim schema. Other runs received the public output shape plus sample-specific field names and record groups, but no field values or target counts.
- Tools: the agent could inspect the transcript, write temporary parsing code, validate its output, and save JSON.
- Scoring: predictions were replayed through the repository evaluator with the documented normalization rules.

Every extraction reported `claude-fable-5` in model usage. Claude Code also reported auxiliary Haiku 4.5 routing, so this is a Claude Code/Fable 5 protocol baseline rather than a raw-model measurement.

## Result

| Documents | Target records | Errors | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 |
|---:|---:|---:|---:|---:|---:|---:|
| 32 | 29,599 | 0 | 95.1% | 9/32 (28.1%) | 96.8% | 93.6% |

Exact-record recall requires every normalized target field to match. Complete-document success requires an identical record multiset with no missing or extra records; source order is not scored.

## Artifacts

- `*_predicted.json`: 32 saved per-document predictions.
- `evaluation_report.json`: machine-readable aggregate and per-document metrics.
- `evaluation_report.md`: human-readable report.
- `per_sample_status.tsv`: merged release status (`attest` for reused predictions and `0` for corrected inputs rerun successfully).
- `run_metadata.json`: requested and observed models, effort, CLI version, transcript and contract fingerprints, prediction hashes, duration, token usage, and API-equivalent cost estimates for all samples.

Debug logs are excluded because they contain verbose agent traces and are not needed to recompute the scores.

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
  --results-dir benchmarks/results/claude_fable5_full_current_ocr_v2 \
  --require-full-corpus
```
