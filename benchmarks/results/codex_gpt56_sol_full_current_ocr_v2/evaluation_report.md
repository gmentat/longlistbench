# Multi-Model Evaluation Report

Generated: 2026-07-21 11:19:22 UTC
Evaluation mode: `offline_replay`
Dataset manifest SHA-256: `ccf1881c256e9b5a2f575e73061d6fd40cfe763dc446bc873fc63cedd0019133`
Git SHA: `02c9dd1a9d570c7d8b6df11850ac09eda10a8033`; dirty: `False`

## Overall Results

| Model | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|---------------------|--------------------|----------------|----------------|------|---------|--------|----------|------------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 97.9% | 8/32 (25.0%) | 99.4% | 99.4% | 29599 | 32 | 0 | N/A | N/A |

The primary score is exact-record recall: a target counts only when every normalized field in one predicted record matches one ground-truth record. Complete-document success additionally requires the predicted and ground-truth record multisets to be identical. Record order is not scored. Field-pair F1 remains a secondary diagnostic.

## Strict Completeness by Evaluation Role

| Model | Structural Challenge | Scale Control |
|---|---|---|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 93.8% | 99.5% |

## Strict Completeness by Difficulty Tier

| Model | Core Operations | Claim Multihop | Policy Packets |
|---|---|---|---|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.0% | 98.7% | 73.3% |

## Strict Completeness by Document Format

| Model | Production Like Pdf | Crosspage |
|---|---|---|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.0% | 74.7% |

## Strict Completeness by Complexity Regime

| Model | Ifta Mileage By Vehicle | Ifta Multisection Return Packet | Ifta Return Schedule Details | Ifta Tax Return Summary | Driver Mvr Request And Roster | Loss Run External | Vehicle Schedule Spreadsheet Export | Ifta Tax Return Inquiry Detail | Driver Schedule Spreadsheet Export | Claim Crosspage Multihop | Policy Multi Hop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.4% | 99.6% | 95.5% | 99.5% | 99.4% | 97.3% | 100.0% | 99.9% | 99.8% | 98.7% | 73.3% |

## Strict Completeness by Key Stressor

| Model | Ocr Layout Condition | Cross Section Join | Long Range Evidence | Heterogeneous Record List | Multi Column | Merged Cells | Multi Row | Duplicates | Distractor Sections | Repeated Keys | Large Doc | High Density Long List | Page Breaks | Businessowners Policy | Claimant Lookup | Class Code Payroll Rating | Coded Values | Commercial General Liability | Continuation Notes | Cross Page Join | Distractor Forms | Distractor Locations | Experience Mod And Schedule Rating | Exposure Rating Rows | Form Endorsement Links | Inherited Context | Layout Randomization | Limits Forms Exclusions | Location Scoped Coverage | Longer List | Many To One Policy | Material Clause Extraction | Mixed Layout | Mixed Prose Tables | Multiple Tables | Natural Long Range Join | Non Sequential Identifiers | Non Target Rows | Ocr Condition | Production Like Layout | Sparse Driver Fields | Split Records | Summary Distractors | Variable Policy Sections | Workers Compensation Policy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.6% | 99.6% | 74.7% | 73.3% | 74.7% | 96.7% | 97.7% | 93.1% | 83.5% | 99.6% | 97.8% | 99.0% | 97.9% | 80.8% | 100.0% | 100.0% | 100.0% | 47.9% | 97.3% | 98.7% | 47.9% | 47.9% | 100.0% | 47.9% | 80.8% | 95.0% | 98.3% | 47.9% | 80.8% | 97.5% | 100.0% | 73.3% | 97.5% | 98.7% | 98.1% | 74.7% | 98.7% | 95.0% | 97.9% | 99.0% | 97.3% | 94.9% | 97.3% | 97.3% | 100.0% |

## Strict Completeness by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | N/A | 97.9% |

## Detailed Results

### driver_mvr_packet_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 260 | N/A |

### driver_mvr_packet_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 98.4% | no | 99.0% | 508 | N/A |

### driver_mvr_packet_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 500 | N/A |

### driver_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.8% | no | 100.0% | 500 | N/A |

### ifta_mileage_by_vehicle_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.6% | no | 99.9% | 1159 | N/A |

### ifta_mileage_by_vehicle_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 96.5% | no | 99.6% | 2143 | N/A |

### ifta_mileage_by_vehicle_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.8% | no | 100.0% | 2195 | N/A |

### ifta_mileage_by_vehicle_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2239 | N/A |

### ifta_mileage_by_vehicle_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.7% | no | 99.9% | 2379 | N/A |

### ifta_mileage_by_vehicle_006 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2434 | N/A |

### ifta_mileage_by_vehicle_007 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.8% | no | 100.0% | 2445 | N/A |

### ifta_mileage_by_vehicle_008 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 100.0% | no | 100.0% | 2571 | N/A |

### ifta_multisection_return_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.7% | no | 100.0% | 335 | N/A |

### ifta_multisection_return_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.6% | no | 100.0% | 461 | N/A |

### ifta_return_schedule_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 95.9% | no | 98.4% | 558 | N/A |

### ifta_return_schedule_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 95.3% | no | 98.5% | 962 | N/A |

### ifta_return_schedule_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 95.5% | no | 98.5% | 1115 | N/A |

### ifta_tax_inquiry_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 100.0% | no | 98.9% | 665 | N/A |

### ifta_tax_inquiry_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.8% | no | 99.9% | 649 | N/A |

### ifta_tax_summary_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.3% | no | 99.9% | 760 | N/A |

### ifta_tax_summary_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 99.6% | no | 100.0% | 760 | N/A |

### loss_run_external_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 96.3% | no | 99.8% | 300 | N/A |

### loss_run_external_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 97.7% | no | 99.8% | 300 | N/A |

### loss_run_external_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 98.0% | no | 99.8% | 300 | N/A |

### mixed_040_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 97.5% | no | 99.9% | 40 | N/A |

### mixed_cgl_040_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 47.9% | no | 93.2% | 581 | N/A |

### multihop_012_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 12 | N/A |

### multihop_025_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 25 | N/A |

### multihop_bop_012_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 80.8% | no | 97.3% | 354 | N/A |

### multihop_wc_025_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 100.0% | no | 97.9% | 484 | N/A |

### vehicle_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 800 | N/A |

### vehicle_schedule_sparse_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Codex GPT-5.6-Sol (CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 800 | N/A |
