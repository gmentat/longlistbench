# Multi-Model Evaluation Report

Generated: 2026-07-01 06:15:31 UTC
Dataset manifest SHA-256: `971e26def302810c9f87cc4eda36336c2ff82f54990f2d08aa00e3445ce4e2bc`
Git SHA: `f9f8538a230bd786b6de97b99f4cfa775f9c8899`; dirty: `True`

## Overall Results

| Model | Weighted F1 | Weighted Recall | Weighted Precision | Macro F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|-------------|-----------------|--------------------|----------|------|---------|--------|----------|------------|
| Codex GPT-5.5 (CLI Agentic) | 97.7% | 96.8% | 98.7% | 96.7% | 33450 | 36 | 0 | 0 | $0.0000 |

Primary scores use corpus-level micro aggregation over all field-value pairs, so larger incident lists contribute proportionally more evidence than smaller documents.

## Results by Difficulty Tier

| Model | Core Operations | Claim Multihop | Policy Packets |
|---|---|---|---|
| Codex GPT-5.5 (CLI Agentic) | 98.1% | 97.1% | 92.8% |

## Results by Document Format

| Model | Production Like Pdf | Crosspage |
|---|---|---|
| Codex GPT-5.5 (CLI Agentic) | 98.1% | 93.2% |

## Results by Complexity Regime

| Model | Ifta Mileage By Vehicle | Ifta Multisection Return Packet | Ifta Return Schedule Details | Ifta Tax Return Summary | Driver Mvr Request And Roster | Loss Run External | Vehicle Schedule Spreadsheet Export | Ifta Tax Return Inquiry Detail | Driver Schedule Spreadsheet Export | Claim Crosspage Multihop | Policy Multi Hop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 91.1% | 97.7% | 99.7% | 89.1% | 97.2% | 100.0% | 99.4% | 87.7% | 97.1% | 92.8% |

## Results by Key Stressor

| Model | Ocr Layout Condition | Cross Section Join | Long Range Evidence | Heterogeneous Record List | Multi Column | Merged Cells | Multi Row | Duplicates | Distractor Sections | Repeated Keys | Large Doc | High Density Long List | Page Breaks | Businessowners Policy | Claimant Lookup | Class Code Payroll Rating | Coded Values | Commercial General Liability | Continuation Notes | Cross Page Join | Distractor Forms | Distractor Locations | Experience Mod And Schedule Rating | Exposure Rating Rows | Form Endorsement Links | Inherited Context | Layout Randomization | Limits Forms Exclusions | Location Scoped Coverage | Longer List | Many To One Policy | Material Clause Extraction | Mixed Layout | Mixed Prose Tables | Multiple Tables | Natural Long Range Join | Non Sequential Identifiers | Non Target Rows | Ocr Condition | Production Like Layout | Sparse Driver Fields | Split Records | Summary Distractors | Variable Policy Sections | Workers Compensation Policy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex GPT-5.5 (CLI Agentic) | 91.1% | 91.1% | 93.2% | 92.8% | 93.2% | 97.9% | 97.2% | 94.8% | 94.8% | 91.1% | 98.1% | 98.1% | 97.7% | 89.9% | 100.0% | 91.1% | 95.8% | 95.6% | 97.2% | 97.1% | 95.6% | 95.6% | 91.1% | 95.6% | 89.9% | 97.1% | 98.4% | 95.6% | 89.9% | 95.8% | 100.0% | 92.8% | 95.8% | 97.1% | 97.9% | 93.2% | 97.1% | 97.1% | 97.7% | 98.1% | 97.2% | 97.1% | 97.2% | 97.2% | 91.1% |

## Results by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| Codex GPT-5.5 (CLI Agentic) | N/A | 97.7% |

## Detailed Results

### driver_mvr_packet_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 89.2% | 80.6% | 100.0% | 260 | 0.0s |

### driver_mvr_packet_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 89.1% | 80.3% | 100.0% | 500 | 0.0s |

### driver_mvr_packet_003 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 89.1% | 80.3% | 100.0% | 500 | 0.0s |

### driver_schedule_sparse_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 87.7% | 87.7% | 87.7% | 500 | 0.0s |

### ifta_mileage_by_vehicle_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 1159 | 0.0s |

### ifta_mileage_by_vehicle_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 2143 | 0.0s |

### ifta_mileage_by_vehicle_003 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 2195 | 0.0s |

### ifta_mileage_by_vehicle_004 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 2239 | 0.0s |

### ifta_mileage_by_vehicle_005 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 2379 | 0.0s |

### ifta_mileage_by_vehicle_006 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 2434 | 0.0s |

### ifta_mileage_by_vehicle_007 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 99.8% | 99.7% | 100.0% | 2445 | 0.0s |

### ifta_mileage_by_vehicle_008 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 2571 | 0.0s |

### ifta_multisection_return_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 87.5% | 87.5% | 87.5% | 335 | 0.0s |

### ifta_multisection_return_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 93.7% | 93.7% | 93.7% | 461 | 0.0s |

### ifta_return_schedule_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 96.8% | 94.0% | 99.9% | 558 | 0.0s |

### ifta_return_schedule_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 98.5% | 97.2% | 99.8% | 998 | 0.0s |

### ifta_return_schedule_003 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 97.2% | 94.6% | 99.9% | 1047 | 0.0s |

### ifta_return_schedule_004 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 98.4% | 97.2% | 99.5% | 1105 | 0.0s |

### ifta_return_schedule_005 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 97.1% | 94.4% | 100.0% | 1115 | 0.0s |

### ifta_tax_inquiry_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 99.9% | 99.8% | 100.0% | 649 | 0.0s |

### ifta_tax_inquiry_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 98.8% | 98.8% | 98.9% | 649 | 0.0s |

### ifta_tax_summary_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 760 | 0.0s |

### ifta_tax_summary_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 98.7% | 98.7% | 98.7% | 760 | 0.0s |

### ifta_tax_summary_003 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 760 | 0.0s |

### ifta_tax_summary_004 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 760 | 0.0s |

### loss_run_external_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 95.6% | 95.8% | 95.4% | 300 | 0.0s |

### loss_run_external_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 99.6% | 99.9% | 99.2% | 300 | 0.0s |

### loss_run_external_003 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 96.5% | 97.0% | 96.1% | 301 | 0.0s |

### mixed_040_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 95.8% | 95.8% | 95.8% | 40 | 0.0s |

### mixed_cgl_040_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 95.6% | 95.4% | 95.9% | 619 | 0.0s |

### multihop_012_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 95.8% | 95.8% | 95.8% | 12 | 0.0s |

### multihop_025_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 25 | 0.0s |

### multihop_bop_012_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 89.9% | 89.9% | 89.9% | 360 | 0.0s |

### multihop_wc_025_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 91.1% | 91.1% | 91.1% | 510 | 0.0s |

### vehicle_schedule_sparse_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 800 | 0.0s |

### vehicle_schedule_sparse_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic) | 100.0% | 100.0% | 100.0% | 800 | 0.0s |
