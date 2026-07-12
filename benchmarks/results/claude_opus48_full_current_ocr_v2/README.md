# Released Claude OCR Baseline

This directory contains the saved predictions and recomputable report for the LongListBench 2.0 Claude baseline.

## Protocol

- Input: one released Gemini OCR transcript per run.
- Extractor: Claude Code CLI invoking `claude-opus-4-8` with `--effort xhigh` on July 12, 2026. `run_metadata.json` records the CLI version observed when metadata was finalized; it is not asserted as a per-call version.
- Authentication: Claude Max subscription. The CLI's per-run dollar values are API-equivalent estimates, not billed API cost.
- Isolation: each run used a temporary document workspace, and a macOS sandbox denied the benchmark repository. The prompt prohibited other host files. This was repository isolation, not a host-wide filesystem allowlist. Ground truth, target values and counts, and generator code were not copied into the workspace. Claude Code safe mode disabled project instructions, skills, plugins, hooks, and MCP servers.
- Contract: claim runs received the published claim schema. Generic-record runs received the public output shape plus sample-specific field names and record groups derived from the ground-truth schema structure. They did not receive field values.
- Tools: the agent could inspect the transcript, write temporary parsing code, validate its output, and save JSON.
- Scoring: predictions were replayed through the repository evaluator against `data/ground_truth/`, with documented string, date, decimal, and domain-label canonicalization.

The runner verified that every extraction call reported `claude-opus-4-8`. Claude Code also reported a small Haiku 4.5 routing call; the extraction model remained Opus 4.8.

## Result

| Documents | Target records | Errors | Exact-record recall | Complete documents | Field micro-F1 |
|---:|---:|---:|---:|---:|---:|
| 36 | 33,450 | 0 | 86.9% | 13/36 (36.1%) | 98.6% |

Exact-record recall requires every normalized target field to match. Complete-document success requires an identical record multiset with no missing or extra records; source order is not scored.

## Artifacts

- `*_predicted.json`: 36 saved per-document predictions.
- `evaluation_report.json`: machine-readable aggregate and per-document metrics.
- `evaluation_report.md`: human-readable report.
- `per_sample_status.tsv`: run completion status.
- `run_metadata.json`: requested/observed models, effort, CLI version, duration, token usage, and API-equivalent cost estimate for each document.

Debug logs are intentionally excluded because they contain verbose agent reasoning and are not needed to recompute the scores.

## Reproduce

From the repository root, with Claude Code authenticated to a subscription:

```bash
uv run python benchmarks/run_claude_cli_evaluation.py \
  --output-dir benchmarks/results/claude_opus48_full_current_ocr_v2 \
  --workers 4 \
  --timeout-seconds 3600
```

## Verify

```bash
uv run python benchmarks/check_evaluation_report.py \
  --results-dir benchmarks/results/claude_opus48_full_current_ocr_v2
```
