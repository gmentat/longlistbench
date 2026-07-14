# Multi-Model Evaluation Report

Generated: 2026-07-14 20:37:23 UTC
Evaluation mode: `offline_replay`
Dataset manifest SHA-256: `5e40e8e07c58aa8882f1f4308fd338310ab19c65367ba9ab60b71050eb739140`
Git SHA: `f8d022fe4a10ce3d3d1a568161eb6a06692d7c8b`; dirty: `False`

## Overall Results

| Model | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|---------------------|--------------------|----------------|----------------|------|---------|--------|----------|------------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 90.9% | 6/32 (18.8%) | 96.1% | 92.6% | 29599 | 32 | 0 | N/A | N/A |

The primary score is exact-record recall: a target counts only when every normalized field in one predicted record matches one ground-truth record. Complete-document success additionally requires the predicted and ground-truth record multisets to be identical. Record order is not scored. Field-pair F1 remains a secondary diagnostic.

## Strict Completeness by Evaluation Role

| Model | Structural Challenge | Scale Control |
|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 69.3% | 99.5% |

## Strict Completeness by Difficulty Tier

| Model | Core Operations | Claim Multihop | Policy Packets |
|---|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 94.5% | 98.7% | 14.6% |

## Strict Completeness by Document Format

| Model | Production Like Pdf | Crosspage |
|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 94.5% | 19.1% |

## Strict Completeness by Complexity Regime

| Model | Ifta Mileage By Vehicle | Ifta Multisection Return Packet | Ifta Return Schedule Details | Ifta Tax Return Summary | Driver Mvr Request And Roster | Loss Run External | Vehicle Schedule Spreadsheet Export | Ifta Tax Return Inquiry Detail | Driver Schedule Spreadsheet Export | Claim Crosspage Multihop | Policy Multi Hop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.4% | 99.6% | 95.5% | 99.5% | 1.9% | 92.2% | 100.0% | 99.8% | 99.8% | 98.7% | 14.6% |

## Strict Completeness by Key Stressor

| Model | Ocr Layout Condition | Cross Section Join | Long Range Evidence | Heterogeneous Record List | Multi Column | Merged Cells | Multi Row | Duplicates | Distractor Sections | Repeated Keys | Large Doc | High Density Long List | Page Breaks | Businessowners Policy | Claimant Lookup | Class Code Payroll Rating | Coded Values | Commercial General Liability | Continuation Notes | Cross Page Join | Distractor Forms | Distractor Locations | Experience Mod And Schedule Rating | Exposure Rating Rows | Form Endorsement Links | Inherited Context | Layout Randomization | Limits Forms Exclusions | Location Scoped Coverage | Longer List | Many To One Policy | Material Clause Extraction | Mixed Layout | Mixed Prose Tables | Multiple Tables | Natural Long Range Join | Non Sequential Identifiers | Non Target Rows | Ocr Condition | Production Like Layout | Sparse Driver Fields | Split Records | Summary Distractors | Variable Policy Sections | Workers Compensation Policy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.6% | 99.6% | 19.1% | 14.6% | 19.1% | 95.2% | 88.3% | 73.4% | 47.5% | 99.6% | 94.9% | 94.5% | 90.9% | 18.6% | 100.0% | 13.7% | 100.0% | 12.8% | 92.2% | 98.7% | 12.8% | 12.8% | 13.7% | 12.8% | 18.6% | 87.0% | 98.3% | 12.8% | 18.6% | 97.5% | 100.0% | 14.6% | 97.5% | 98.7% | 91.8% | 19.1% | 98.7% | 87.0% | 90.9% | 94.5% | 92.2% | 86.9% | 92.2% | 92.2% | 13.7% |

## Strict Completeness by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | N/A | 90.9% |

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
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 1.6% | no | 87.3% | 483 | N/A |

### driver_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 100.0% | 500 | N/A |

### ifta_mileage_by_vehicle_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.6% | no | 99.9% | 1159 | N/A |

### ifta_mileage_by_vehicle_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 96.5% | no | 99.6% | 2143 | N/A |

### ifta_mileage_by_vehicle_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 100.0% | 2195 | N/A |

### ifta_mileage_by_vehicle_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2239 | N/A |

### ifta_mileage_by_vehicle_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.7% | no | 99.9% | 2379 | N/A |

### ifta_mileage_by_vehicle_006 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2434 | N/A |

### ifta_mileage_by_vehicle_007 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 100.0% | 2445 | N/A |

### ifta_mileage_by_vehicle_008 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | no | 100.0% | 2571 | N/A |

### ifta_multisection_return_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.7% | no | 100.0% | 335 | N/A |

### ifta_multisection_return_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.6% | no | 100.0% | 461 | N/A |

### ifta_return_schedule_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 95.9% | no | 98.4% | 558 | N/A |

### ifta_return_schedule_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 95.3% | no | 98.5% | 962 | N/A |

### ifta_return_schedule_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 95.5% | no | 98.5% | 1115 | N/A |

### ifta_tax_inquiry_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 99.9% | 649 | N/A |

### ifta_tax_inquiry_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 99.9% | 649 | N/A |

### ifta_tax_summary_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.3% | no | 99.9% | 760 | N/A |

### ifta_tax_summary_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.7% | no | 100.0% | 760 | N/A |

### loss_run_external_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 88.3% | no | 99.5% | 300 | N/A |

### loss_run_external_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 98.0% | no | 99.9% | 300 | N/A |

### loss_run_external_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 90.3% | no | 99.6% | 300 | N/A |

### mixed_040_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 97.5% | no | 99.9% | 40 | N/A |

### mixed_cgl_040_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 12.8% | no | 30.7% | 72 | N/A |

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
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 18.6% | no | 41.4% | 100 | N/A |

### multihop_wc_025_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 13.7% | no | 30.8% | 60 | N/A |

### vehicle_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 800 | N/A |

### vehicle_schedule_sparse_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 800 | N/A |
