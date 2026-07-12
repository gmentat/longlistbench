# Released Codex OCR Baseline

This directory contains the saved predictions and recomputable report for the LongListBench 2.0 baseline reported in the paper and Hugging Face dataset card.

## Protocol

- Input: one released Gemini OCR transcript per run.
- Extractor: Codex CLI invoking `gpt-5.5` with `model_reasoning_effort="xhigh"` on July 1, 2026.
- Isolation: each run used a temporary document workspace, and a macOS sandbox denied the benchmark repository. The prompt prohibited other host files. This was repository isolation, not a host-wide filesystem allowlist. Ground truth, target values and counts, and generator code were not copied into the workspace.
- Contract: claim runs received the published claim schema. Generic-record runs received the public output shape plus the sample-specific field names and record groups derived from the ground-truth schema structure. They did not receive field values.
- Tools: the agent could inspect the transcript, write temporary parsing code, validate its output, and save JSON.
- Scoring: predictions were replayed through the repository evaluator against `data/ground_truth/`, with documented string, date, decimal, and domain-label canonicalization.

The report records the current evaluator and manifest provenance. The predictions are the original saved model outputs; reports can be regenerated without rerunning Codex.

## Result

| Documents | Target records | Errors | Exact-record recall | Complete documents | Field micro-F1 |
|---:|---:|---:|---:|---:|---:|
| 36 | 33,450 | 0 | 89.5% | 12/36 (33.3%) | 98.7% |

Exact-record recall requires every normalized target field to match. Complete-document success requires an identical record multiset with no missing or extra records; source order is not scored.

## Artifacts

- `*_predicted.json`: 36 saved per-document predictions.
- `evaluation_report.json`: machine-readable aggregate and per-document metrics.
- `evaluation_report.md`: human-readable report.
- `per_sample_status.tsv`: run completion status.

Token, cost, and latency telemetry was not retained for this subscription-backed run, so the report records those totals as `null` rather than zero.

## Verify

From the repository root:

```bash
.venv/bin/python benchmarks/check_evaluation_report.py \
  --results-dir benchmarks/results/codex_full_current_ocr_v2
```
