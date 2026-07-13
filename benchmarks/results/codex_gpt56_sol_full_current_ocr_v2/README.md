# Released GPT-5.6-Sol OCR Baseline

This directory contains the saved predictions and recomputable report for the LongListBench 2.0 GPT-5.6-Sol baseline.

## Protocol

- Input: one released Gemini OCR transcript per run.
- Extractor: Codex CLI `0.144.1` invoking `gpt-5.6-sol` with `model_reasoning_effort="xhigh"` on July 13, 2026.
- Authentication: Codex subscription; credentials are not stored.
- Isolation: each run used a temporary document workspace, and a macOS sandbox denied the benchmark repository. The prompt prohibited other host files. This was repository isolation, not a host-wide filesystem allowlist. Ground truth, target values and counts, and generator code were not copied into the workspace.
- Contract: claim runs received the published claim schema. Generic-record runs received the public output shape plus sample-specific field names and record groups derived from ground-truth object structure. They did not receive field values.
- Tools: the agent could inspect the transcript, write temporary parsing code, validate its output, and save JSON.
- Scoring: predictions were replayed through the repository evaluator against `data/ground_truth/`, with documented string, date, decimal, and domain-label canonicalization.

The 36 local execution logs reported `gpt-5.6-sol` with xhigh reasoning. Logs are intentionally excluded because they contain verbose agent traces and are not needed to recompute the scores.

## Result

| Documents | Target records | Errors | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 |
|---:|---:|---:|---:|---:|---:|---:|
| 36 | 33,450 | 0 | 89.9% | 14/36 (38.9%) | 97.8% | 97.8% |

Exact-record recall requires every normalized target field to match. Complete-document success requires an identical record multiset with no missing or extra records; source order is not scored.

## Artifacts

- `*_predicted.json`: 36 saved per-document predictions.
- `evaluation_report.json`: machine-readable aggregate and per-document metrics.
- `evaluation_report.md`: human-readable report.
- `per_sample_status.tsv`: run completion status.
- `run_metadata.json`: requested model, effort, CLI version, transcript condition, and per-sample statuses.

Token, cost, and latency telemetry was not retained for this subscription-backed run.

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
