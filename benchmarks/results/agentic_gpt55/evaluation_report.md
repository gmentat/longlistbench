# Multi-Model Evaluation Report

Generated: 2026-06-06 20:44:56

## Overall Results

| Model | Weighted F1 | Weighted Recall | Weighted Precision | Macro F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|-------------|-----------------|--------------------|----------|------|---------|--------|----------|------------|
| GPT-5.5 (Agentic Sandbox) | 90.6% | 89.7% | 91.4% | 94.4% | 6828 | 80 | 0 | 8874 | $32.6481 |

Primary scores use corpus-level micro aggregation over all field-value pairs, so larger incident lists contribute proportionally more evidence than smaller documents.

## Results by Difficulty Tier

| Model | Easy | Medium | Hard | Extreme |
|-------|------|--------|------|---------|
| GPT-5.5 (Agentic Sandbox) | 97.0% | 95.2% | 91.4% | 89.4% |

## Results by Document Format

| Model | Detailed | Table |
|-------|----------|-------|
| GPT-5.5 (Agentic Sandbox) | 87.9% | 93.2% |

## Results by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| GPT-5.5 (Agentic Sandbox) | N/A | 90.6% |

## Detailed Results

### easy_10_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.4% | 99.4% | 99.4% | 10 | 48.9s |

### easy_10_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.6% | 95.6% | 95.6% | 10 | 190.4s |

### easy_10_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 100.0% | 100.0% | 100.0% | 10 | 68.3s |

### easy_10_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.7% | 99.7% | 99.7% | 10 | 47.5s |

### easy_10_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.7% | 99.7% | 99.7% | 10 | 54.2s |

### easy_10_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.4% | 99.4% | 99.4% | 10 | 68.6s |

### easy_10_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 93.7% | 89.4% | 98.3% | 10 | 67.9s |

### easy_10_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.5% | 99.5% | 99.5% | 11 | 68.4s |

### easy_10_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 97.2% | 97.2% | 97.2% | 11 | 51.9s |

### easy_10_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 93.9% | 89.6% | 98.6% | 10 | 68.4s |

### easy_10_006_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 100.0% | 100.0% | 100.0% | 10 | 51.1s |

### easy_10_006_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.3% | 95.3% | 95.3% | 10 | 70.6s |

### easy_10_007_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.7% | 99.7% | 99.7% | 10 | 49.2s |

### easy_10_007_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.7% | 99.7% | 99.7% | 10 | 68.4s |

### easy_10_008_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.4% | 99.4% | 99.4% | 10 | 44.5s |

### easy_10_008_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 98.6% | 98.6% | 98.6% | 10 | 54.9s |

### easy_10_009_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 100.0% | 100.0% | 100.0% | 11 | 35.9s |

### easy_10_009_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 91.3% | 87.1% | 95.8% | 10 | 40.4s |

### easy_10_010_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.2% | 90.9% | 100.0% | 10 | 37.8s |

### easy_10_010_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.2% | 90.9% | 100.0% | 10 | 101.8s |

### easy_10_011_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.4% | 99.4% | 99.4% | 10 | 52.9s |

### easy_10_011_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 100.0% | 100.0% | 100.0% | 10 | 53.4s |

### easy_10_012_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 100.0% | 100.0% | 100.0% | 10 | 52.4s |

### easy_10_012_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 98.6% | 98.6% | 98.6% | 10 | 103.5s |

### easy_10_013_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 100.0% | 100.0% | 100.0% | 10 | 54.9s |

### easy_10_013_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 96.7% | 96.7% | 96.7% | 10 | 105.4s |

### easy_10_014_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.2% | 90.9% | 100.0% | 10 | 903.9s |

### easy_10_014_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 82.8% | 82.8% | 82.8% | 11 | 49.3s |

### easy_10_015_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 99.5% | 99.5% | 99.5% | 11 | 96.8s |

### easy_10_015_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 87.6% | 87.6% | 87.6% | 11 | 61.5s |

### extreme_100_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 89.1% | 88.6% | 89.5% | 495 | 105.9s |

### extreme_100_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 97.3% | 97.3% | 97.3% | 500 | 65.5s |

### extreme_100_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 84.7% | 84.3% | 85.1% | 495 | 108.7s |

### extreme_100_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 96.8% | 96.8% | 96.8% | 500 | 91.9s |

### extreme_100_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 91.3% | 90.9% | 91.8% | 495 | 63.5s |

### extreme_100_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 85.9% | 85.9% | 85.9% | 500 | 69.1s |

### extreme_100_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 65.8% | 65.5% | 66.1% | 495 | 65.1s |

### extreme_100_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 98.4% | 98.4% | 98.4% | 500 | 97.3s |

### extreme_100_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 94.5% | 94.5% | 94.5% | 500 | 456.4s |

### extreme_100_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 90.5% | 90.5% | 90.5% | 500 | 66.7s |

### hard_50_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.2% | 90.9% | 100.0% | 50 | 80.1s |

### hard_50_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 93.0% | 88.8% | 97.7% | 50 | 61.1s |

### hard_50_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.0% | 90.7% | 99.7% | 50 | 32.8s |

### hard_50_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 93.3% | 89.1% | 98.0% | 50 | 87.5s |

### hard_50_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 85.4% | 81.6% | 89.7% | 50 | 73.1s |

### hard_50_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 91.7% | 87.6% | 96.3% | 50 | 60.6s |

### hard_50_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.2% | 90.9% | 100.0% | 50 | 429.2s |

### hard_50_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 81.4% | 77.7% | 85.4% | 50 | 151.6s |

### hard_50_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.0% | 90.7% | 99.8% | 50 | 44.4s |

### hard_50_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 92.6% | 88.4% | 97.3% | 50 | 62.2s |

### hard_50_006_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.2% | 90.9% | 100.0% | 50 | 95.0s |

### hard_50_006_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 86.2% | 82.3% | 90.6% | 50 | 53.1s |

### hard_50_007_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.2% | 90.9% | 100.0% | 50 | 90.3s |

### hard_50_007_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 85.4% | 81.6% | 89.7% | 50 | 66.4s |

### hard_50_008_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 94.7% | 90.4% | 99.4% | 50 | 50.2s |

### hard_50_008_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 87.0% | 87.0% | 87.0% | 55 | 79.3s |

### medium_25_001_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 96.2% | 92.6% | 100.0% | 25 | 66.1s |

### medium_25_001_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.0% | 91.5% | 98.8% | 25 | 683.6s |

### medium_25_002_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 100.0% | 100.0% | 100.0% | 25 | 37.2s |

### medium_25_002_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 88.7% | 88.7% | 88.7% | 25 | 85.3s |

### medium_25_003_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 96.2% | 92.6% | 100.0% | 25 | 47.0s |

### medium_25_003_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 93.7% | 90.2% | 97.4% | 25 | 96.1s |

### medium_25_004_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 96.2% | 92.6% | 100.0% | 25 | 43.3s |

### medium_25_004_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 85.3% | 82.1% | 88.7% | 25 | 109.9s |

### medium_25_005_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 96.2% | 92.6% | 100.0% | 25 | 119.8s |

### medium_25_005_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 96.0% | 92.5% | 99.9% | 25 | 55.8s |

### medium_25_006_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 100.0% | 100.0% | 100.0% | 25 | 110.3s |

### medium_25_006_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 88.1% | 88.1% | 88.1% | 25 | 94.7s |

### medium_25_007_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 100.0% | 100.0% | 100.0% | 27 | 49.6s |

### medium_25_007_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 94.2% | 90.7% | 98.0% | 25 | 64.5s |

### medium_25_008_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 96.2% | 92.6% | 100.0% | 25 | 61.4s |

### medium_25_008_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 91.2% | 91.2% | 91.2% | 27 | 70.9s |

### medium_25_009_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 96.2% | 92.6% | 100.0% | 25 | 72.3s |

### medium_25_009_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 95.5% | 92.0% | 99.3% | 25 | 1047.3s |

### medium_25_010_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 100.0% | 100.0% | 100.0% | 25 | 36.4s |

### medium_25_010_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 93.1% | 93.1% | 93.1% | 25 | 118.9s |

### medium_25_011_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 96.2% | 92.6% | 100.0% | 25 | 42.6s |

### medium_25_011_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 100.0% | 100.0% | 100.0% | 27 | 58.8s |

### medium_25_012_detailed (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 96.2% | 92.6% | 100.0% | 25 | 63.4s |

### medium_25_012_table (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| GPT-5.5 (Agentic Sandbox) | 94.6% | 91.0% | 98.3% | 25 | 109.4s |
