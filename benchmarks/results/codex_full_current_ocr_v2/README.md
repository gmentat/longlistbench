# Released GPT-5.5 OCR Baseline

This directory contains the saved predictions and recomputable current LongListBench report for GPT-5.5.

## Protocol

- Input: one released Gemini OCR transcript per extraction.
- Extractor: Codex CLI invoking `gpt-5.5` at xhigh reasoning effort. The 29 unchanged inputs use the July 14, 2026 run (`0.144.4`); the corrected driver/MVR family was rerun July 21 (`0.144.6`).
- Authentication: Codex subscription; credentials are not stored.
- Isolation: each extraction used a temporary workspace. A macOS sandbox denied the benchmark repository and additional parent paths; ground truth, target values and counts, and generator code were absent.
- Contract: claim runs received the published claim schema. Other runs received the public output shape plus sample-specific field names and record groups, but no field values or target counts.
- Tools: the agent could inspect the transcript, write temporary parsing code, validate its output, and save JSON.
- Scoring: predictions were replayed through the repository evaluator with the documented normalization rules.

## Result

| Documents | Target records | Errors | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 |
|---:|---:|---:|---:|---:|---:|---:|
| 32 | 29,599 | 0 | 94.5% | 4/32 (12.5%) | 98.8% | 98.6% |

Exact-record recall requires every normalized target field to match. Complete-document success requires an identical record multiset with no missing or extra records; source order is not scored.

## Artifacts

- `*_predicted.json`: 32 saved per-document predictions.
- `evaluation_report.json`: machine-readable aggregate and per-document metrics.
- `evaluation_report.md`: human-readable report.
- `per_sample_status.tsv`: merged release status (`attest` for reused predictions and `0` for corrected inputs rerun successfully).
- `run_metadata.json`: requested and observed model, effort, CLI version, transcript and contract fingerprints, and prediction hashes for all samples.

## Reproduce

```bash
python benchmarks/run_codex_cli_evaluation.py \
  --output-dir benchmarks/results/codex_full_current_ocr_v2 \
  --model-key codex_gpt55 \
  --model gpt-5.5 \
  --effort xhigh \
  --workers 4 \
  --timeout-seconds 3600
```

## Verify

```bash
python benchmarks/check_evaluation_report.py \
  --results-dir benchmarks/results/codex_full_current_ocr_v2 \
  --require-full-corpus
```
