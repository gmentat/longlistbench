# Multi-Model Evaluation Report

Generated: 2026-06-22 21:18:31 UTC

## Overall Results

| Model | Weighted F1 | Weighted Recall | Weighted Precision | Macro F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|-------------|-----------------|--------------------|----------|------|---------|--------|----------|------------|
| GPT-5.5 (Agentic Sandbox) | 97.3% | 97.7% | 96.9% | 97.0% | 422 | 6 | 0 | 1842 | $9.0117 |

Primary scores use corpus-level micro aggregation over all field-value pairs, so larger incident lists contribute proportionally more evidence than smaller documents.

## Results by Difficulty Tier

| Model | Multihop | Mixed |
|---|---|---|
| GPT-5.5 (Agentic Sandbox) | 96.5% | 98.0% |

## Results by Document Format

| Model | Crosspage |
|---|---|
| GPT-5.5 (Agentic Sandbox) | 97.3% |

## Results by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| GPT-5.5 (Agentic Sandbox) | N/A | 97.3% |

## Detailed Results

### mixed_040_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 98.9% | 98.9% | 98.9% | 40 | 265.2s |

### mixed_cgl_040_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 97.6% | 97.6% | 97.6% | 184 | 486.6s |

### multihop_012_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.3% | 99.3% | 99.3% | 12 | 188.3s |

### multihop_025_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.0% | 99.0% | 99.0% | 25 | 175.2s |

### multihop_bop_012_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 90.0% | 95.0% | 85.5% | 53 | 317.0s |

### multihop_wc_025_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 97.0% | 97.0% | 97.0% | 113 | 410.1s |
