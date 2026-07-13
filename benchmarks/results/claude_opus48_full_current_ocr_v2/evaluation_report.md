# Multi-Model Evaluation Report

Generated: 2026-07-13 19:00:34 UTC
Evaluation mode: `subscription_cli`
Dataset manifest SHA-256: `f0fbc3c3bb8a524cf2a8785c00d1adb6a7ecf8e04efee5dd5e47f6dec3851bbe`
Git SHA: `4ffdcc9ff786f442a8a23b019d7fa81023026dc7`; dirty: `True`

## Overall Results

| Model | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|---------------------|--------------------|----------------|----------------|------|---------|--------|----------|------------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 85.8% | 11/36 (30.6%) | 98.7% | 98.5% | 33450 | 36 | 0 | 27569 | N/A |

The primary score is exact-record recall: a target counts only when every normalized field in one predicted record matches one ground-truth record. Complete-document success additionally requires the predicted and ground-truth record multisets to be identical. Record order is not scored. Field-pair F1 remains a secondary diagnostic.

## Strict Completeness by Evaluation Role

| Model | Structural Challenge | Scale Control |
|---|---|---|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 57.3% | 99.3% |

## Strict Completeness by Difficulty Tier

| Model | Core Operations | Claim Multihop | Policy Packets |
|---|---|---|---|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 89.8% | 98.7% | 0.0% |

## Strict Completeness by Document Format

| Model | Production Like Pdf | Crosspage |
|---|---|---|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 89.8% | 4.9% |

## Strict Completeness by Complexity Regime

| Model | Ifta Mileage By Vehicle | Ifta Multisection Return Packet | Ifta Return Schedule Details | Ifta Tax Return Summary | Driver Mvr Request And Roster | Loss Run External | Vehicle Schedule Spreadsheet Export | Ifta Tax Return Inquiry Detail | Driver Schedule Spreadsheet Export | Claim Crosspage Multihop | Policy Multi Hop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.1% | 99.9% | 63.9% | 99.9% | 0.0% | 93.9% | 99.9% | 99.8% | 99.4% | 98.7% | 0.0% |

## Strict Completeness by Key Stressor

| Model | Ocr Layout Condition | Cross Section Join | Long Range Evidence | Heterogeneous Record List | Multi Column | Merged Cells | Multi Row | Duplicates | Distractor Sections | Repeated Keys | Large Doc | High Density Long List | Page Breaks | Businessowners Policy | Claimant Lookup | Class Code Payroll Rating | Coded Values | Commercial General Liability | Continuation Notes | Cross Page Join | Distractor Forms | Distractor Locations | Experience Mod And Schedule Rating | Exposure Rating Rows | Form Endorsement Links | Inherited Context | Layout Randomization | Limits Forms Exclusions | Location Scoped Coverage | Longer List | Many To One Policy | Material Clause Extraction | Mixed Layout | Mixed Prose Tables | Multiple Tables | Natural Long Range Join | Non Sequential Identifiers | Non Target Rows | Ocr Condition | Production Like Layout | Sparse Driver Fields | Split Records | Summary Distractors | Variable Policy Sections | Workers Compensation Policy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.9% | 99.9% | 4.9% | 0.0% | 4.9% | 97.4% | 86.6% | 37.3% | 37.3% | 99.9% | 89.2% | 89.8% | 85.8% | 0.0% | 96.0% | 0.0% | 100.0% | 0.0% | 93.9% | 98.7% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 76.1% | 84.3% | 0.0% | 0.0% | 100.0% | 96.0% | 0.0% | 100.0% | 98.7% | 86.7% | 4.9% | 98.7% | 76.1% | 85.8% | 89.8% | 93.9% | 76.0% | 93.9% | 93.9% | 0.0% |

## Strict Completeness by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | N/A | 85.8% |

## Detailed Results

### driver_mvr_packet_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 0.0% | no | 87.9% | 268 | 150.8s |

### driver_mvr_packet_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 0.0% | no | 88.3% | 508 | 221.6s |

### driver_mvr_packet_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 0.0% | no | 88.4% | 508 | 146.1s |

### driver_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.4% | no | 99.9% | 500 | 120.2s |

### ifta_mileage_by_vehicle_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 1159 | 392.5s |

### ifta_mileage_by_vehicle_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2143 | 673.9s |

### ifta_mileage_by_vehicle_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2195 | 807.1s |

### ifta_mileage_by_vehicle_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2239 | 736.8s |

### ifta_mileage_by_vehicle_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.4% | no | 99.7% | 2365 | 558.9s |

### ifta_mileage_by_vehicle_006 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2434 | 630.3s |

### ifta_mileage_by_vehicle_007 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 94.2% | no | 98.1% | 2445 | 679.7s |

### ifta_mileage_by_vehicle_008 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2571 | 598.3s |

### ifta_multisection_return_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 335 | 299.7s |

### ifta_multisection_return_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 100.0% | 461 | 434.1s |

### ifta_return_schedule_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 63.7% | no | 97.0% | 558 | 1492.8s |

### ifta_return_schedule_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 64.1% | no | 97.1% | 962 | 1668.7s |

### ifta_return_schedule_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 64.1% | no | 97.2% | 1047 | 1103.9s |

### ifta_return_schedule_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 64.7% | no | 97.2% | 1061 | 1820.4s |

### ifta_return_schedule_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 62.9% | no | 97.1% | 1115 | 1300.8s |

### ifta_tax_inquiry_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 99.9% | 649 | 245.6s |

### ifta_tax_inquiry_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 99.9% | 649 | 264.2s |

### ifta_tax_summary_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 760 | 354.1s |

### ifta_tax_summary_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 760 | 507.4s |

### ifta_tax_summary_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 760 | 620.6s |

### ifta_tax_summary_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 760 | 1912.3s |

### loss_run_external_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 98.3% | no | 99.9% | 300 | 1074.6s |

### loss_run_external_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 91.7% | no | 99.7% | 300 | 940.2s |

### loss_run_external_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 91.7% | no | 99.5% | 301 | 899.7s |

### mixed_040_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 40 | 603.3s |

### mixed_cgl_040_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 0.0% | no | 99.5% | 619 | 2007.0s |

### multihop_012_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 12 | 347.5s |

### multihop_025_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 96.0% | no | 99.7% | 25 | 432.2s |

### multihop_bop_012_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 0.0% | no | 99.7% | 360 | 1285.6s |

### multihop_wc_025_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 0.0% | no | 100.0% | 510 | 829.5s |

### vehicle_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 800 | 512.9s |

### vehicle_schedule_sparse_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 800 | 895.6s |
