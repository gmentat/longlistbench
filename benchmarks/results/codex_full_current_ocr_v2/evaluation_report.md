# Multi-Model Evaluation Report

Generated: 2026-07-21 11:19:40 UTC
Evaluation mode: `offline_replay`
Dataset manifest SHA-256: `ccf1881c256e9b5a2f575e73061d6fd40cfe763dc446bc873fc63cedd0019133`
Git SHA: `02c9dd1a9d570c7d8b6df11850ac09eda10a8033`; dirty: `False`

## Overall Results

| Model | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|---------------------|--------------------|----------------|----------------|------|---------|--------|----------|------------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 94.5% | 4/32 (12.5%) | 98.8% | 98.6% | 29599 | 32 | 0 | N/A | N/A |

The primary score is exact-record recall: a target counts only when every normalized field in one predicted record matches one ground-truth record. Complete-document success additionally requires the predicted and ground-truth record multisets to be identical. Record order is not scored. Field-pair F1 remains a secondary diagnostic.

## Strict Completeness by Evaluation Role

| Model | Structural Challenge | Scale Control |
|---|---|---|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 82.0% | 99.5% |

## Strict Completeness by Difficulty Tier

| Model | Core Operations | Claim Multihop | Policy Packets |
|---|---|---|---|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 94.7% | 0.0% | 95.5% |

## Strict Completeness by Document Format

| Model | Production Like Pdf | Crosspage |
|---|---|---|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 94.7% | 90.3% |

## Strict Completeness by Complexity Regime

| Model | Ifta Mileage By Vehicle | Ifta Multisection Return Packet | Ifta Return Schedule Details | Ifta Tax Return Summary | Driver Mvr Request And Roster | Loss Run External | Vehicle Schedule Spreadsheet Export | Ifta Tax Return Inquiry Detail | Driver Schedule Spreadsheet Export | Claim Crosspage Multihop | Policy Multi Hop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.4% | 99.6% | 55.1% | 99.5% | 98.1% | 86.3% | 100.0% | 100.0% | 99.8% | 0.0% | 95.5% |

## Strict Completeness by Key Stressor

| Model | Ocr Layout Condition | Cross Section Join | Long Range Evidence | Heterogeneous Record List | Multi Column | Merged Cells | Multi Row | Duplicates | Distractor Sections | Repeated Keys | Large Doc | High Density Long List | Page Breaks | Businessowners Policy | Claimant Lookup | Class Code Payroll Rating | Coded Values | Commercial General Liability | Continuation Notes | Cross Page Join | Distractor Forms | Distractor Locations | Experience Mod And Schedule Rating | Exposure Rating Rows | Form Endorsement Links | Inherited Context | Layout Randomization | Limits Forms Exclusions | Location Scoped Coverage | Longer List | Many To One Policy | Material Clause Extraction | Mixed Layout | Mixed Prose Tables | Multiple Tables | Natural Long Range Join | Non Sequential Identifiers | Non Target Rows | Ocr Condition | Production Like Layout | Sparse Driver Fields | Split Records | Summary Distractors | Variable Policy Sections | Workers Compensation Policy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.6% | 99.6% | 90.3% | 95.5% | 90.3% | 93.5% | 98.2% | 80.3% | 88.8% | 99.6% | 94.4% | 94.7% | 94.5% | 82.6% | 0.0% | 99.8% | 0.0% | 100.0% | 86.3% | 0.0% | 100.0% | 100.0% | 99.8% | 100.0% | 82.6% | 86.0% | 83.8% | 100.0% | 82.6% | 0.0% | 0.0% | 95.5% | 0.0% | 0.0% | 94.7% | 90.3% | 0.0% | 86.0% | 94.5% | 94.7% | 86.3% | 86.7% | 86.3% | 86.3% | 99.8% |

## Strict Completeness by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| Codex GPT-5.5 (CLI Agentic, xhigh) | N/A | 94.5% |

## Detailed Results

### driver_mvr_packet_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 96.9% | no | 98.1% | 268 | N/A |

### driver_mvr_packet_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 98.4% | no | 99.0% | 508 | N/A |

### driver_mvr_packet_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 98.4% | no | 99.0% | 508 | N/A |

### driver_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.8% | no | 100.0% | 500 | N/A |

### ifta_mileage_by_vehicle_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.6% | no | 99.9% | 1159 | N/A |

### ifta_mileage_by_vehicle_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 96.5% | no | 99.6% | 2143 | N/A |

### ifta_mileage_by_vehicle_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.8% | no | 100.0% | 2195 | N/A |

### ifta_mileage_by_vehicle_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2239 | N/A |

### ifta_mileage_by_vehicle_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.7% | no | 99.9% | 2379 | N/A |

### ifta_mileage_by_vehicle_006 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2434 | N/A |

### ifta_mileage_by_vehicle_007 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.8% | no | 100.0% | 2445 | N/A |

### ifta_mileage_by_vehicle_008 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | no | 100.0% | 2571 | N/A |

### ifta_multisection_return_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.7% | no | 100.0% | 335 | N/A |

### ifta_multisection_return_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.6% | no | 100.0% | 461 | N/A |

### ifta_return_schedule_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 95.9% | no | 98.4% | 558 | N/A |

### ifta_return_schedule_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 95.3% | no | 98.5% | 962 | N/A |

### ifta_return_schedule_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 0.0% | no | 90.3% | 1115 | N/A |

### ifta_tax_inquiry_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | no | 98.9% | 665 | N/A |

### ifta_tax_inquiry_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | no | 98.9% | 665 | N/A |

### ifta_tax_summary_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.3% | no | 99.9% | 760 | N/A |

### ifta_tax_summary_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.6% | no | 100.0% | 760 | N/A |

### loss_run_external_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 88.7% | no | 99.4% | 300 | N/A |

### loss_run_external_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 89.3% | no | 99.5% | 300 | N/A |

### loss_run_external_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 81.0% | no | 99.2% | 300 | N/A |

### mixed_040_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 0.0% | no | 95.7% | 40 | N/A |

### mixed_cgl_040_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | no | 94.8% | 648 | N/A |

### multihop_012_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 0.0% | no | 93.8% | 12 | N/A |

### multihop_025_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 0.0% | no | 95.7% | 25 | N/A |

### multihop_bop_012_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 82.6% | no | 98.0% | 349 | N/A |

### multihop_wc_025_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 99.8% | no | 100.0% | 438 | N/A |

### vehicle_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 800 | N/A |

### vehicle_schedule_sparse_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.5 (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 800 | N/A |
