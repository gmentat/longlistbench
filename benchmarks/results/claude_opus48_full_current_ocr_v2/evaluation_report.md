# Multi-Model Evaluation Report

Generated: 2026-07-12 19:44:49 UTC
Evaluation mode: `offline_replay`
Dataset manifest SHA-256: `efb19fba854d881aa6c010d736efa0ddf153890ad4b9b564a21b5e7ac3ea61b4`
Git SHA: `5edf851fb3e89e30600e1600789a9b54b3290259`; dirty: `False`

## Overall Results

| Model | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|---------------------|--------------------|----------------|----------------|------|---------|--------|----------|------------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 86.9% | 13/36 (36.1%) | 98.6% | 98.2% | 33450 | 36 | 0 | N/A | N/A |

The primary score is exact-record recall: a target counts only when every normalized field in one predicted record matches one ground-truth record. Complete-document success additionally requires the predicted and ground-truth record multisets to be identical. Record order is not scored. Field-pair F1 remains a secondary diagnostic.

## Strict Completeness by Evaluation Role

| Model | Structural Challenge | Scale Control |
|---|---|---|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 60.7% | 99.3% |

## Strict Completeness by Difficulty Tier

| Model | Core Operations | Claim Multihop | Policy Packets |
|---|---|---|---|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 89.4% | 98.7% | 32.0% |

## Strict Completeness by Document Format

| Model | Production Like Pdf | Crosspage |
|---|---|---|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 89.4% | 35.2% |

## Strict Completeness by Complexity Regime

| Model | Ifta Mileage By Vehicle | Ifta Multisection Return Packet | Ifta Return Schedule Details | Ifta Tax Return Summary | Driver Mvr Request And Roster | Loss Run External | Vehicle Schedule Spreadsheet Export | Ifta Tax Return Inquiry Detail | Driver Schedule Spreadsheet Export | Claim Crosspage Multihop | Policy Multi Hop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.1% | 99.9% | 63.9% | 99.9% | 0.0% | 93.9% | 100.0% | 90.8% | 99.4% | 98.7% | 32.0% |

## Strict Completeness by Key Stressor

| Model | Ocr Layout Condition | Cross Section Join | Long Range Evidence | Heterogeneous Record List | Multi Column | Merged Cells | Multi Row | Duplicates | Distractor Sections | Repeated Keys | Large Doc | High Density Long List | Page Breaks | Businessowners Policy | Claimant Lookup | Class Code Payroll Rating | Coded Values | Commercial General Liability | Continuation Notes | Cross Page Join | Distractor Forms | Distractor Locations | Experience Mod And Schedule Rating | Exposure Rating Rows | Form Endorsement Links | Inherited Context | Layout Randomization | Limits Forms Exclusions | Location Scoped Coverage | Longer List | Many To One Policy | Material Clause Extraction | Mixed Layout | Mixed Prose Tables | Multiple Tables | Natural Long Range Join | Non Sequential Identifiers | Non Target Rows | Ocr Condition | Production Like Layout | Sparse Driver Fields | Split Records | Summary Distractors | Variable Policy Sections | Workers Compensation Policy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.9% | 99.9% | 35.2% | 32.0% | 35.2% | 92.0% | 88.7% | 56.7% | 56.7% | 99.9% | 90.3% | 89.4% | 86.9% | 0.0% | 96.0% | 93.3% | 100.0% | 0.0% | 93.9% | 98.7% | 0.0% | 0.0% | 93.3% | 0.0% | 0.0% | 78.7% | 83.3% | 0.0% | 0.0% | 100.0% | 96.0% | 32.0% | 100.0% | 98.7% | 87.8% | 35.2% | 98.7% | 78.7% | 86.9% | 89.4% | 93.9% | 78.6% | 93.9% | 93.9% | 93.3% |

## Strict Completeness by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | N/A | 86.9% |

## Detailed Results

### driver_mvr_packet_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 0.0% | no | 87.9% | 268 | N/A |

### driver_mvr_packet_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 0.0% | no | 88.3% | 508 | N/A |

### driver_mvr_packet_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 0.0% | no | 88.4% | 508 | N/A |

### driver_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.4% | no | 99.9% | 500 | N/A |

### ifta_mileage_by_vehicle_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 1159 | N/A |

### ifta_mileage_by_vehicle_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2143 | N/A |

### ifta_mileage_by_vehicle_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2195 | N/A |

### ifta_mileage_by_vehicle_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2239 | N/A |

### ifta_mileage_by_vehicle_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.4% | no | 99.7% | 2365 | N/A |

### ifta_mileage_by_vehicle_006 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2434 | N/A |

### ifta_mileage_by_vehicle_007 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 94.2% | no | 98.1% | 2445 | N/A |

### ifta_mileage_by_vehicle_008 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2571 | N/A |

### ifta_multisection_return_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 335 | N/A |

### ifta_multisection_return_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 100.0% | 461 | N/A |

### ifta_return_schedule_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 63.7% | no | 97.0% | 558 | N/A |

### ifta_return_schedule_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 64.1% | no | 97.1% | 962 | N/A |

### ifta_return_schedule_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 64.1% | no | 97.2% | 1047 | N/A |

### ifta_return_schedule_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 64.7% | no | 97.2% | 1061 | N/A |

### ifta_return_schedule_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 62.9% | no | 97.1% | 1115 | N/A |

### ifta_tax_inquiry_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 81.7% | no | 91.1% | 649 | N/A |

### ifta_tax_inquiry_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 99.9% | 649 | N/A |

### ifta_tax_summary_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 760 | N/A |

### ifta_tax_summary_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 760 | N/A |

### ifta_tax_summary_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 760 | N/A |

### ifta_tax_summary_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 760 | N/A |

### loss_run_external_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 98.3% | no | 99.9% | 300 | N/A |

### loss_run_external_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 91.7% | no | 99.7% | 300 | N/A |

### loss_run_external_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 91.7% | no | 99.5% | 301 | N/A |

### mixed_040_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 40 | N/A |

### mixed_cgl_040_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 0.0% | no | 99.0% | 619 | N/A |

### multihop_012_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 12 | N/A |

### multihop_025_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 96.0% | no | 99.7% | 25 | N/A |

### multihop_bop_012_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 0.0% | no | 99.7% | 360 | N/A |

### multihop_wc_025_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 93.3% | no | 99.7% | 510 | N/A |

### vehicle_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 800 | N/A |

### vehicle_schedule_sparse_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Opus 4.8 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 800 | N/A |
