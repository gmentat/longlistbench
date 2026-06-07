# Multi-Model Evaluation Report

Generated: 2026-06-07 13:06:06

## Overall Results

| Model | Weighted F1 | Weighted Recall | Weighted Precision | Macro F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|-------------|-----------------|--------------------|----------|------|---------|--------|----------|------------|
| GPT-5.5 (Auto-chunked) | 85.4% | 80.2% | 91.2% | 87.7% | 6828 | 80 | 0 | 0 | $0.0000 |

Primary scores use corpus-level micro aggregation over all field-value pairs, so larger incident lists contribute proportionally more evidence than smaller documents.

## Results by Difficulty Tier

| Model | Easy | Medium | Hard | Extreme |
|-------|------|--------|------|---------|
| GPT-5.5 (Auto-chunked) | 91.3% | 92.6% | 82.1% | 84.6% |

## Results by Document Format

| Model | Detailed | Table |
|-------|----------|-------|
| GPT-5.5 (Auto-chunked) | 75.5% | 94.0% |

## Results by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| GPT-5.5 (Auto-chunked) | N/A | 85.4% |

## Detailed Results

### easy_10_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 90.8% | 90.8% | 90.8% | 10 | 0.0s |

### easy_10_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 90.6% | 90.6% | 90.6% | 10 | 0.0s |

### easy_10_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 91.7% | 91.7% | 91.7% | 10 | 0.0s |

### easy_10_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 98.3% | 98.3% | 98.3% | 10 | 0.0s |

### easy_10_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 91.4% | 91.4% | 91.4% | 10 | 0.0s |

### easy_10_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 92.8% | 92.8% | 92.8% | 10 | 0.0s |

### easy_10_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 85.7% | 81.8% | 90.0% | 10 | 0.0s |

### easy_10_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 87.1% | 87.1% | 87.1% | 11 | 0.0s |

### easy_10_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 87.3% | 83.3% | 91.7% | 10 | 0.0s |

### easy_10_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 90.5% | 86.4% | 95.0% | 10 | 0.0s |

### easy_10_006_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 91.7% | 91.7% | 91.7% | 10 | 0.0s |

### easy_10_006_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 91.7% | 91.7% | 91.7% | 10 | 0.0s |

### easy_10_007_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 96.9% | 96.9% | 96.9% | 10 | 0.0s |

### easy_10_007_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 99.7% | 99.7% | 99.7% | 10 | 0.0s |

### easy_10_008_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 96.7% | 96.7% | 96.7% | 10 | 0.0s |

### easy_10_008_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 90.3% | 90.3% | 90.3% | 10 | 0.0s |

### easy_10_009_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 90.9% | 90.9% | 90.9% | 11 | 0.0s |

### easy_10_009_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 84.1% | 80.3% | 88.3% | 10 | 0.0s |

### easy_10_010_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 91.7% | 91.7% | 91.7% | 11 | 0.0s |

### easy_10_010_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 92.9% | 88.6% | 97.5% | 10 | 0.0s |

### easy_10_011_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 96.7% | 96.7% | 96.7% | 10 | 0.0s |

### easy_10_011_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 92.8% | 92.8% | 92.8% | 10 | 0.0s |

### easy_10_012_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 91.7% | 91.7% | 91.7% | 10 | 0.0s |

### easy_10_012_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 92.2% | 92.2% | 92.2% | 10 | 0.0s |

### easy_10_013_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 91.7% | 91.7% | 91.7% | 10 | 0.0s |

### easy_10_013_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 99.7% | 99.7% | 99.7% | 10 | 0.0s |

### easy_10_014_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 92.6% | 88.4% | 97.2% | 10 | 0.0s |

### easy_10_014_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 84.9% | 81.1% | 89.2% | 10 | 0.0s |

### easy_10_015_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 86.8% | 82.8% | 91.1% | 10 | 0.0s |

### easy_10_015_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 81.0% | 77.3% | 85.0% | 10 | 0.0s |

### extreme_100_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 62.9% | 49.8% | 85.3% | 292 | 0.0s |

### extreme_100_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 93.4% | 93.8% | 93.1% | 504 | 0.0s |

### extreme_100_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 79.0% | 72.7% | 86.5% | 420 | 0.0s |

### extreme_100_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 94.4% | 94.8% | 93.9% | 505 | 0.0s |

### extreme_100_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 71.0% | 59.8% | 87.4% | 342 | 0.0s |

### extreme_100_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 94.3% | 94.7% | 93.9% | 504 | 0.0s |

### extreme_100_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 85.5% | 85.1% | 85.9% | 495 | 0.0s |

### extreme_100_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 93.9% | 94.3% | 93.6% | 504 | 0.0s |

### extreme_100_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 66.6% | 54.7% | 85.0% | 322 | 0.0s |

### extreme_100_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 94.2% | 94.7% | 93.6% | 506 | 0.0s |

### hard_50_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 88.9% | 86.5% | 91.5% | 52 | 0.0s |

### hard_50_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 96.0% | 95.1% | 96.9% | 54 | 0.0s |

### hard_50_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 87.4% | 83.4% | 91.8% | 50 | 0.0s |

### hard_50_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 91.4% | 91.4% | 91.4% | 55 | 0.0s |

### hard_50_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 87.2% | 83.3% | 91.6% | 50 | 0.0s |

### hard_50_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 97.8% | 97.8% | 97.8% | 55 | 0.0s |

### hard_50_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 90.2% | 88.6% | 91.9% | 53 | 0.0s |

### hard_50_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 96.7% | 96.7% | 96.7% | 55 | 0.0s |

### hard_50_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 6.4% | 3.3% | 91.7% | 2 | 0.0s |

### hard_50_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 94.1% | 94.1% | 94.1% | 55 | 0.0s |

### hard_50_006_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 30.6% | 18.3% | 91.7% | 11 | 0.0s |

### hard_50_006_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 96.0% | 96.0% | 96.0% | 55 | 0.0s |

### hard_50_007_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 55.7% | 40.0% | 91.7% | 24 | 0.0s |

### hard_50_007_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 95.4% | 95.4% | 95.4% | 55 | 0.0s |

### hard_50_008_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 6.4% | 3.3% | 91.7% | 2 | 0.0s |

### hard_50_008_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 92.6% | 94.3% | 91.0% | 57 | 0.0s |

### medium_25_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 93.5% | 90.0% | 97.2% | 25 | 0.0s |

### medium_25_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 90.7% | 89.0% | 92.4% | 26 | 0.0s |

### medium_25_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 91.7% | 91.7% | 91.7% | 25 | 0.0s |

### medium_25_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 96.6% | 96.6% | 96.6% | 25 | 0.0s |

### medium_25_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 88.1% | 84.9% | 91.7% | 25 | 0.0s |

### medium_25_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 95.6% | 97.3% | 93.8% | 28 | 0.0s |

### medium_25_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 93.5% | 90.0% | 97.2% | 25 | 0.0s |

### medium_25_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 97.2% | 95.4% | 99.0% | 26 | 0.0s |

### medium_25_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 97.2% | 97.2% | 97.2% | 27 | 0.0s |

### medium_25_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 95.6% | 95.6% | 95.6% | 27 | 0.0s |

### medium_25_006_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 91.7% | 91.7% | 91.7% | 25 | 0.0s |

### medium_25_006_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 91.7% | 91.7% | 91.7% | 25 | 0.0s |

### medium_25_007_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 88.1% | 84.9% | 91.7% | 25 | 0.0s |

### medium_25_007_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 95.7% | 95.7% | 95.7% | 27 | 0.0s |

### medium_25_008_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 88.1% | 84.9% | 91.7% | 25 | 0.0s |

### medium_25_008_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 95.5% | 93.7% | 97.3% | 26 | 0.0s |

### medium_25_009_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 88.1% | 84.9% | 91.7% | 25 | 0.0s |

### medium_25_009_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 93.1% | 93.1% | 93.1% | 27 | 0.0s |

### medium_25_010_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 97.2% | 97.2% | 97.2% | 25 | 0.0s |

### medium_25_010_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 90.5% | 92.3% | 88.8% | 26 | 0.0s |

### medium_25_011_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 93.5% | 90.0% | 97.2% | 25 | 0.0s |

### medium_25_011_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 95.6% | 97.3% | 93.8% | 28 | 0.0s |

### medium_25_012_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 88.1% | 84.9% | 91.7% | 25 | 0.0s |

### medium_25_012_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Auto-chunked) | 85.8% | 85.8% | 85.8% | 27 | 0.0s |
