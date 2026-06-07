# Multi-Model Evaluation Report

Generated: 2026-06-07 13:06:04

## Overall Results

| Model | Weighted F1 | Weighted Recall | Weighted Precision | Macro F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|-------------|-----------------|--------------------|----------|------|---------|--------|----------|------------|
| GPT-5.5 (One-shot) | 29.9% | 17.8% | 94.4% | 71.0% | 6828 | 80 | 0 | 0 | $0.0000 |

Primary scores use corpus-level micro aggregation over all field-value pairs, so larger incident lists contribute proportionally more evidence than smaller documents.

## Results by Difficulty Tier

| Model | Easy | Medium | Hard | Extreme |
|-------|------|--------|------|---------|
| GPT-5.5 (One-shot) | 91.2% | 93.1% | 56.5% | 0.0% |

## Results by Document Format

| Model | Detailed | Table |
|-------|----------|-------|
| GPT-5.5 (One-shot) | 32.1% | 27.6% |

## Results by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| GPT-5.5 (One-shot) | N/A | 29.9% |

## Detailed Results

### easy_10_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 90.8% | 90.8% | 90.8% | 10 | 0.0s |

### easy_10_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.4% | 91.4% | 91.4% | 10 | 0.0s |

### easy_10_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.7% | 91.7% | 91.7% | 10 | 0.0s |

### easy_10_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 96.9% | 96.9% | 96.9% | 10 | 0.0s |

### easy_10_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.4% | 91.4% | 91.4% | 10 | 0.0s |

### easy_10_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 94.7% | 94.7% | 94.7% | 10 | 0.0s |

### easy_10_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 85.7% | 81.8% | 90.0% | 10 | 0.0s |

### easy_10_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 93.4% | 89.1% | 98.1% | 10 | 0.0s |

### easy_10_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.7% | 91.7% | 91.7% | 11 | 0.0s |

### easy_10_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 92.6% | 88.4% | 97.2% | 10 | 0.0s |

### easy_10_006_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.7% | 91.7% | 91.7% | 10 | 0.0s |

### easy_10_006_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 89.7% | 89.7% | 89.7% | 10 | 0.0s |

### easy_10_007_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.4% | 91.4% | 91.4% | 10 | 0.0s |

### easy_10_007_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 99.7% | 99.7% | 99.7% | 10 | 0.0s |

### easy_10_008_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 96.7% | 96.7% | 96.7% | 10 | 0.0s |

### easy_10_008_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.7% | 91.7% | 91.7% | 10 | 0.0s |

### easy_10_009_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.7% | 91.7% | 91.7% | 11 | 0.0s |

### easy_10_009_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 84.1% | 80.3% | 88.3% | 10 | 0.0s |

### easy_10_010_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 87.3% | 83.3% | 91.7% | 10 | 0.0s |

### easy_10_010_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 92.6% | 88.4% | 97.2% | 10 | 0.0s |

### easy_10_011_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.1% | 91.1% | 91.1% | 10 | 0.0s |

### easy_10_011_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 94.4% | 94.4% | 94.4% | 10 | 0.0s |

### easy_10_012_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.7% | 91.7% | 91.7% | 10 | 0.0s |

### easy_10_012_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 96.4% | 96.4% | 96.4% | 10 | 0.0s |

### easy_10_013_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.7% | 91.7% | 91.7% | 10 | 0.0s |

### easy_10_013_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 96.9% | 96.9% | 96.9% | 10 | 0.0s |

### easy_10_014_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 87.3% | 83.3% | 91.7% | 10 | 0.0s |

### easy_10_014_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 83.3% | 87.1% | 79.9% | 12 | 0.0s |

### easy_10_015_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 86.8% | 82.8% | 91.1% | 10 | 0.0s |

### easy_10_015_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 81.0% | 77.3% | 85.0% | 10 | 0.0s |

### extreme_100_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### extreme_100_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### extreme_100_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### extreme_100_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### extreme_100_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### extreme_100_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### extreme_100_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### extreme_100_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### extreme_100_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### extreme_100_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### hard_50_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 87.3% | 83.3% | 91.7% | 50 | 0.0s |

### hard_50_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### hard_50_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 29.1% | 17.2% | 94.4% | 10 | 0.0s |

### hard_50_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### hard_50_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 87.3% | 83.3% | 91.7% | 50 | 0.0s |

### hard_50_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 94.8% | 90.5% | 99.5% | 50 | 0.0s |

### hard_50_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 87.3% | 83.3% | 91.7% | 50 | 0.0s |

### hard_50_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### hard_50_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### hard_50_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 35.6% | 21.7% | 99.3% | 12 | 0.0s |

### hard_50_006_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 87.3% | 83.3% | 91.7% | 50 | 0.0s |

### hard_50_006_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### hard_50_007_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 15.3% | 8.3% | 91.7% | 5 | 0.0s |

### hard_50_007_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 0.0% | 0.0% | 0.0% | 0 | 0.0s |

### hard_50_008_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 87.3% | 83.3% | 91.7% | 50 | 0.0s |

### hard_50_008_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 95.2% | 90.9% | 99.9% | 50 | 0.0s |

### medium_25_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 88.1% | 84.9% | 91.7% | 25 | 0.0s |

### medium_25_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 96.0% | 92.5% | 99.9% | 25 | 0.0s |

### medium_25_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.7% | 91.7% | 91.7% | 25 | 0.0s |

### medium_25_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 100.0% | 100.0% | 100.0% | 25 | 0.0s |

### medium_25_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 93.5% | 90.0% | 97.2% | 25 | 0.0s |

### medium_25_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 95.9% | 92.4% | 99.8% | 25 | 0.0s |

### medium_25_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 88.1% | 84.9% | 91.7% | 25 | 0.0s |

### medium_25_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 96.2% | 92.6% | 100.0% | 25 | 0.0s |

### medium_25_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 93.5% | 90.0% | 97.2% | 25 | 0.0s |

### medium_25_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 89.4% | 86.1% | 93.0% | 25 | 0.0s |

### medium_25_006_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.7% | 91.7% | 91.7% | 25 | 0.0s |

### medium_25_006_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 100.0% | 100.0% | 100.0% | 25 | 0.0s |

### medium_25_007_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 88.1% | 84.9% | 91.7% | 25 | 0.0s |

### medium_25_007_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 93.2% | 93.2% | 93.2% | 27 | 0.0s |

### medium_25_008_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 88.1% | 84.9% | 91.7% | 25 | 0.0s |

### medium_25_008_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 96.2% | 92.6% | 100.0% | 25 | 0.0s |

### medium_25_009_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 93.5% | 90.0% | 97.2% | 25 | 0.0s |

### medium_25_009_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 99.8% | 99.8% | 99.8% | 27 | 0.0s |

### medium_25_010_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 91.7% | 91.7% | 91.7% | 25 | 0.0s |

### medium_25_010_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 99.8% | 99.8% | 99.8% | 25 | 0.0s |

### medium_25_011_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 93.5% | 90.0% | 97.2% | 25 | 0.0s |

### medium_25_011_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 89.3% | 86.0% | 92.9% | 25 | 0.0s |

### medium_25_012_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 88.1% | 84.9% | 91.7% | 25 | 0.0s |

### medium_25_012_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (One-shot) | 89.4% | 86.1% | 93.0% | 25 | 0.0s |
