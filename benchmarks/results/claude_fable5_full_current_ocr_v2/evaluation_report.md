# Multi-Model Evaluation Report

Generated: 2026-07-13 19:20:52 UTC
Evaluation mode: `offline_replay`
Dataset manifest SHA-256: `f0fbc3c3bb8a524cf2a8785c00d1adb6a7ecf8e04efee5dd5e47f6dec3851bbe`
Git SHA: `0a4f2cca9d5b5ecc88deb425e21517b373097925`; dirty: `False`

## Overall Results

| Model | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|---------------------|--------------------|----------------|----------------|------|---------|--------|----------|------------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 90.7% | 15/36 (41.7%) | 98.9% | 98.6% | 33450 | 36 | 0 | N/A | N/A |

The primary score is exact-record recall: a target counts only when every normalized field in one predicted record matches one ground-truth record. Complete-document success additionally requires the predicted and ground-truth record multisets to be identical. Record order is not scored. Field-pair F1 remains a secondary diagnostic.

## Strict Completeness by Evaluation Role

| Model | Structural Challenge | Scale Control |
|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 71.5% | 99.8% |

## Strict Completeness by Difficulty Tier

| Model | Core Operations | Claim Multihop | Policy Packets |
|---|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 90.4% | 100.0% | 96.8% |

## Strict Completeness by Document Format

| Model | Production Like Pdf | Crosspage |
|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 90.4% | 97.0% |

## Strict Completeness by Complexity Regime

| Model | Ifta Mileage By Vehicle | Ifta Multisection Return Packet | Ifta Return Schedule Details | Ifta Tax Return Summary | Driver Mvr Request And Roster | Loss Run External | Vehicle Schedule Spreadsheet Export | Ifta Tax Return Inquiry Detail | Driver Schedule Spreadsheet Export | Claim Crosspage Multihop | Policy Multi Hop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | 99.9% | 64.6% | 99.9% | 1.9% | 99.2% | 99.9% | 98.1% | 99.4% | 100.0% | 96.8% |

## Strict Completeness by Key Stressor

| Model | Ocr Layout Condition | Cross Section Join | Long Range Evidence | Heterogeneous Record List | Multi Column | Merged Cells | Multi Row | Duplicates | Distractor Sections | Repeated Keys | Large Doc | High Density Long List | Page Breaks | Businessowners Policy | Claimant Lookup | Class Code Payroll Rating | Coded Values | Commercial General Liability | Continuation Notes | Cross Page Join | Distractor Forms | Distractor Locations | Experience Mod And Schedule Rating | Exposure Rating Rows | Form Endorsement Links | Inherited Context | Layout Randomization | Limits Forms Exclusions | Location Scoped Coverage | Longer List | Many To One Policy | Material Clause Extraction | Mixed Layout | Mixed Prose Tables | Multiple Tables | Natural Long Range Join | Non Sequential Identifiers | Non Target Rows | Ocr Condition | Production Like Layout | Sparse Driver Fields | Split Records | Summary Distractors | Variable Policy Sections | Workers Compensation Policy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.9% | 99.9% | 97.0% | 96.8% | 97.0% | 98.5% | 94.0% | 97.8% | 97.8% | 99.9% | 94.2% | 90.4% | 90.7% | 100.0% | 100.0% | 100.0% | 100.0% | 92.4% | 99.2% | 100.0% | 92.4% | 92.4% | 100.0% | 92.4% | 100.0% | 86.7% | 84.4% | 92.4% | 100.0% | 100.0% | 100.0% | 96.8% | 100.0% | 100.0% | 90.6% | 97.0% | 100.0% | 86.7% | 90.7% | 90.4% | 99.2% | 86.7% | 99.2% | 99.2% | 100.0% |

## Strict Completeness by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | N/A | 90.7% |

## Detailed Results

### driver_mvr_packet_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 3.1% | no | 89.2% | 260 | N/A |

### driver_mvr_packet_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 1.6% | no | 89.1% | 500 | N/A |

### driver_mvr_packet_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 1.6% | no | 89.1% | 500 | N/A |

### driver_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.4% | no | 99.9% | 500 | N/A |

### ifta_mileage_by_vehicle_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 1159 | N/A |

### ifta_mileage_by_vehicle_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2143 | N/A |

### ifta_mileage_by_vehicle_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2195 | N/A |

### ifta_mileage_by_vehicle_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2239 | N/A |

### ifta_mileage_by_vehicle_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2379 | N/A |

### ifta_mileage_by_vehicle_006 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2434 | N/A |

### ifta_mileage_by_vehicle_007 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 98.5% | no | 99.8% | 2445 | N/A |

### ifta_mileage_by_vehicle_008 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2571 | N/A |

### ifta_multisection_return_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 335 | N/A |

### ifta_multisection_return_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 100.0% | 461 | N/A |

### ifta_return_schedule_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 63.7% | no | 97.0% | 558 | N/A |

### ifta_return_schedule_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 67.7% | no | 98.6% | 998 | N/A |

### ifta_return_schedule_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 64.1% | no | 97.2% | 1047 | N/A |

### ifta_return_schedule_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 64.7% | no | 97.2% | 1061 | N/A |

### ifta_return_schedule_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 62.9% | no | 97.1% | 1115 | N/A |

### ifta_tax_inquiry_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 99.9% | 649 | N/A |

### ifta_tax_inquiry_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 96.3% | no | 98.2% | 649 | N/A |

### ifta_tax_summary_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 760 | N/A |

### ifta_tax_summary_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 760 | N/A |

### ifta_tax_summary_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 760 | N/A |

### ifta_tax_summary_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 760 | N/A |

### loss_run_external_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.0% | no | 99.9% | 300 | N/A |

### loss_run_external_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.3% | no | 99.9% | 300 | N/A |

### loss_run_external_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.3% | no | 99.8% | 301 | N/A |

### mixed_040_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 40 | N/A |

### mixed_cgl_040_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 92.4% | no | 99.4% | 619 | N/A |

### multihop_012_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 12 | N/A |

### multihop_025_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 25 | N/A |

### multihop_bop_012_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 360 | N/A |

### multihop_wc_025_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 510 | N/A |

### vehicle_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 800 | N/A |

### vehicle_schedule_sparse_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 800 | N/A |
