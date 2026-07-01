# Multi-Model Evaluation Report

Generated: 2026-07-01 12:04:51 UTC
Evaluation mode: `offline_replay`
Dataset manifest SHA-256: `c19d98bc6de8d1def3b155f991c973e5a35e8df7fee9d2a9457e89356f6dd943`
Git SHA: `78751b8a69b3bfc318814e5a8f50b6d06ec81bad`; dirty: `False`

## Overall Results

| Model | Weighted F1 | Weighted Recall | Weighted Precision | Macro F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|-------------|-----------------|--------------------|----------|------|---------|--------|----------|------------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 97.7% | 96.8% | 98.7% | 96.7% | 33450 | 36 | 0 | N/A | N/A |

Primary scores use corpus-level micro aggregation over all field-value pairs, so larger incident lists contribute proportionally more evidence than smaller documents.

## Results by Difficulty Tier

| Model | Core Operations | Claim Multihop | Policy Packets |
|---|---|---|---|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 98.1% | 97.1% | 92.8% |

## Results by Document Format

| Model | Production Like Pdf | Crosspage |
|---|---|---|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 98.1% | 93.2% |

## Results by Complexity Regime

| Model | Ifta Mileage By Vehicle | Ifta Multisection Return Packet | Ifta Return Schedule Details | Ifta Tax Return Summary | Driver Mvr Request And Roster | Loss Run External | Vehicle Schedule Spreadsheet Export | Ifta Tax Return Inquiry Detail | Driver Schedule Spreadsheet Export | Claim Crosspage Multihop | Policy Multi Hop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 91.1% | 97.7% | 99.7% | 89.1% | 97.2% | 100.0% | 99.4% | 87.7% | 97.1% | 92.8% |

## Results by Key Stressor

| Model | Ocr Layout Condition | Cross Section Join | Long Range Evidence | Heterogeneous Record List | Multi Column | Merged Cells | Multi Row | Duplicates | Distractor Sections | Repeated Keys | Large Doc | High Density Long List | Page Breaks | Businessowners Policy | Claimant Lookup | Class Code Payroll Rating | Coded Values | Commercial General Liability | Continuation Notes | Cross Page Join | Distractor Forms | Distractor Locations | Experience Mod And Schedule Rating | Exposure Rating Rows | Form Endorsement Links | Inherited Context | Layout Randomization | Limits Forms Exclusions | Location Scoped Coverage | Longer List | Many To One Policy | Material Clause Extraction | Mixed Layout | Mixed Prose Tables | Multiple Tables | Natural Long Range Join | Non Sequential Identifiers | Non Target Rows | Ocr Condition | Production Like Layout | Sparse Driver Fields | Split Records | Summary Distractors | Variable Policy Sections | Workers Compensation Policy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 91.1% | 91.1% | 93.2% | 92.8% | 93.2% | 97.9% | 97.2% | 94.8% | 94.8% | 91.1% | 98.1% | 98.1% | 97.7% | 89.9% | 100.0% | 91.1% | 95.8% | 95.6% | 97.2% | 97.1% | 95.6% | 95.6% | 91.1% | 95.6% | 89.9% | 97.1% | 98.4% | 95.6% | 89.9% | 95.8% | 100.0% | 92.8% | 95.8% | 97.1% | 97.9% | 93.2% | 97.1% | 97.1% | 97.7% | 98.1% | 97.2% | 97.1% | 97.2% | 97.2% | 91.1% |

## Results by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| Codex GPT-5.5 (CLI Agentic, xhigh) | N/A | 97.7% |

## Detailed Results

### driver_mvr_packet_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 89.2% | 80.6% | 100.0% | 260 | N/A |

### driver_mvr_packet_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 89.1% | 80.3% | 100.0% | 500 | N/A |

### driver_mvr_packet_003 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 89.1% | 80.3% | 100.0% | 500 | N/A |

### driver_schedule_sparse_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 87.7% | 87.7% | 87.7% | 500 | N/A |

### ifta_mileage_by_vehicle_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 1159 | N/A |

### ifta_mileage_by_vehicle_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 2143 | N/A |

### ifta_mileage_by_vehicle_003 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 2195 | N/A |

### ifta_mileage_by_vehicle_004 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 2239 | N/A |

### ifta_mileage_by_vehicle_005 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 2379 | N/A |

### ifta_mileage_by_vehicle_006 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 2434 | N/A |

### ifta_mileage_by_vehicle_007 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.8% | 99.7% | 100.0% | 2445 | N/A |

### ifta_mileage_by_vehicle_008 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 2571 | N/A |

### ifta_multisection_return_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 87.5% | 87.5% | 87.5% | 335 | N/A |

### ifta_multisection_return_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 93.7% | 93.7% | 93.7% | 461 | N/A |

### ifta_return_schedule_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 96.8% | 94.0% | 99.9% | 558 | N/A |

### ifta_return_schedule_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 98.5% | 97.2% | 99.8% | 998 | N/A |

### ifta_return_schedule_003 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 97.2% | 94.6% | 99.9% | 1047 | N/A |

### ifta_return_schedule_004 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 98.4% | 97.2% | 99.5% | 1105 | N/A |

### ifta_return_schedule_005 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 97.1% | 94.4% | 100.0% | 1115 | N/A |

### ifta_tax_inquiry_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.9% | 99.8% | 100.0% | 649 | N/A |

### ifta_tax_inquiry_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 98.8% | 98.8% | 98.9% | 649 | N/A |

### ifta_tax_summary_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 760 | N/A |

### ifta_tax_summary_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 98.7% | 98.7% | 98.7% | 760 | N/A |

### ifta_tax_summary_003 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 760 | N/A |

### ifta_tax_summary_004 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 760 | N/A |

### loss_run_external_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 95.6% | 95.8% | 95.4% | 300 | N/A |

### loss_run_external_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.6% | 99.9% | 99.2% | 300 | N/A |

### loss_run_external_003 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 96.5% | 97.0% | 96.1% | 301 | N/A |

### mixed_040_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 95.8% | 95.8% | 95.8% | 40 | N/A |

### mixed_cgl_040_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 95.6% | 95.4% | 95.9% | 619 | N/A |

### multihop_012_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 95.8% | 95.8% | 95.8% | 12 | N/A |

### multihop_025_001_crosspage (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 25 | N/A |

### multihop_bop_012_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 89.9% | 89.9% | 89.9% | 360 | N/A |

### multihop_wc_025_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 91.1% | 91.1% | 91.1% | 510 | N/A |

### vehicle_schedule_sparse_001 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 800 | N/A |

### vehicle_schedule_sparse_002 (ocr)

| Model | F1 | Recall | Precision | Predicted | Time |
|-------|-----|--------|-----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | 100.0% | 100.0% | 800 | N/A |
