# Multi-Model Evaluation Report

Generated: 2026-06-21 18:43:00 UTC

## Overall Results

| Model | Weighted F1 | Weighted Recall | Weighted Precision | Macro F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|-------------|-----------------|--------------------|----------|------|---------|--------|----------|------------|
| GPT-5.5 (Agentic Sandbox) | 92.9% | 93.3% | 92.6% | 92.8% | 422 | 6 | 0 | 1842 | $9.0117 |

Primary scores use corpus-level micro aggregation over all field-value pairs, so larger incident lists contribute proportionally more evidence than smaller documents.

## Results by Difficulty Tier

| Model | Multihop | Mixed |
|---|---|---|
| GPT-5.5 (Agentic Sandbox) | 91.5% | 94.2% |

## Results by Document Format

| Model | Crosspage |
|---|---|
| GPT-5.5 (Agentic Sandbox) | 92.9% |

## Results by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| GPT-5.5 (Agentic Sandbox) | N/A | 92.9% |

## Detailed Results

### multihop_012_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.5% | 99.5% | 99.5% | 12 | 188.3s |

### multihop_025_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.3% | 99.3% | 99.3% | 25 | 175.2s |

### mixed_040_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.3% | 99.3% | 99.3% | 40 | 265.2s |

### multihop_bop_012_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 76.4% | 80.5% | 72.6% | 53 | 317.0s |

### multihop_wc_025_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 90.9% | 90.9% | 90.9% | 113 | 410.1s |

### mixed_cgl_040_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 91.5% | 91.5% | 91.5% | 184 | 486.6s |
