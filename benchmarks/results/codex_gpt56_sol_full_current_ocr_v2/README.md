# Released GPT-5.6-Sol OCR Baseline

This directory contains the saved predictions and recomputable report for the LongListBench 2.1 GPT-5.6-Sol baseline.

## Protocol

- Input: one released Gemini OCR transcript per run.
- Extractor: Codex CLI `0.144.4` invoking `gpt-5.6-sol` with xhigh reasoning on July 14, 2026.
- Authentication: Codex subscription; credentials are not stored.
- Isolation: each run used a temporary document workspace. A macOS sandbox denied the benchmark repository and additional parent paths; ground truth, target values and counts, and generator code were absent.
- Contract: claim runs received the published claim schema. Other runs received the public output shape plus sample-specific field names and record groups, but no field values or target counts.
- Tools: the agent could inspect the transcript, write temporary parsing code, validate its output, and save JSON.
- Scoring: predictions were replayed through the repository evaluator with the documented normalization rules.

## Result

| Documents | Target records | Errors | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 |
|---:|---:|---:|---:|---:|---:|---:|
| 32 | 29,599 | 0 | 93.5% | 6/32 (18.8%) | 98.7% | 98.3% |

Exact-record recall requires every normalized target field to match. Complete-document success requires an identical record multiset with no missing or extra records; source order is not scored.

## Artifacts

- `*_predicted.json`: 32 saved per-document predictions.
- `evaluation_report.json`: machine-readable aggregate and per-document metrics.
- `evaluation_report.md`: human-readable report.
- `per_sample_status.tsv`: run completion status.
- `run_metadata.json`: requested model, effort, CLI version, transcript condition, and per-sample statuses.

## Reproduce

```bash
python benchmarks/run_codex_cli_evaluation.py \
  --output-dir benchmarks/results/codex_gpt56_sol_full_current_ocr_v2 \
  --model-key codex_gpt56_sol \
  --model gpt-5.6-sol \
  --effort xhigh \
  --workers 4 \
  --timeout-seconds 3600
```

## Verify

```bash
python benchmarks/check_evaluation_report.py \
  --results-dir benchmarks/results/codex_gpt56_sol_full_current_ocr_v2
```
