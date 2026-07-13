# Multi-Model Evaluation Report

Generated: 2026-07-13 13:10:01 UTC
Evaluation mode: `subscription_cli`
Dataset manifest SHA-256: `efb19fba854d881aa6c010d736efa0ddf153890ad4b9b564a21b5e7ac3ea61b4`
Git SHA: `20021bb19097628cb48313bb84c2e9f4b7ac8954`; dirty: `False`

## Overall Results

| Model | Exact-record recall | Complete documents | Field micro-F1 | Field macro-F1 | Rows | Samples | Errors | Time (s) | Cost (USD) |
|-------|---------------------|--------------------|----------------|----------------|------|---------|--------|----------|------------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 90.6% | 15/36 (41.7%) | 98.9% | 98.7% | 33450 | 36 | 0 | 17601 | N/A |

The primary score is exact-record recall: a target counts only when every normalized field in one predicted record matches one ground-truth record. Complete-document success additionally requires the predicted and ground-truth record multisets to be identical. Record order is not scored. Field-pair F1 remains a secondary diagnostic.

## Strict Completeness by Evaluation Role

| Model | Structural Challenge | Scale Control |
|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 71.2% | 99.8% |

## Strict Completeness by Difficulty Tier

| Model | Core Operations | Claim Multihop | Policy Packets |
|---|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 90.5% | 100.0% | 92.5% |

## Strict Completeness by Document Format

| Model | Production Like Pdf | Crosspage |
|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 90.5% | 92.9% |

## Strict Completeness by Complexity Regime

| Model | Ifta Mileage By Vehicle | Ifta Multisection Return Packet | Ifta Return Schedule Details | Ifta Tax Return Summary | Driver Mvr Request And Roster | Loss Run External | Vehicle Schedule Spreadsheet Export | Ifta Tax Return Inquiry Detail | Driver Schedule Spreadsheet Export | Claim Crosspage Multihop | Policy Multi Hop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | 99.9% | 64.6% | 99.9% | 1.9% | 99.2% | 100.0% | 99.8% | 99.4% | 100.0% | 92.5% |

## Strict Completeness by Key Stressor

| Model | Ocr Layout Condition | Cross Section Join | Long Range Evidence | Heterogeneous Record List | Multi Column | Merged Cells | Multi Row | Duplicates | Distractor Sections | Repeated Keys | Large Doc | High Density Long List | Page Breaks | Businessowners Policy | Claimant Lookup | Class Code Payroll Rating | Coded Values | Commercial General Liability | Continuation Notes | Cross Page Join | Distractor Forms | Distractor Locations | Experience Mod And Schedule Rating | Exposure Rating Rows | Form Endorsement Links | Inherited Context | Layout Randomization | Limits Forms Exclusions | Location Scoped Coverage | Longer List | Many To One Policy | Material Clause Extraction | Mixed Layout | Mixed Prose Tables | Multiple Tables | Natural Long Range Join | Non Sequential Identifiers | Non Target Rows | Ocr Condition | Production Like Layout | Sparse Driver Fields | Split Records | Summary Distractors | Variable Policy Sections | Workers Compensation Policy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.9% | 99.9% | 92.9% | 92.5% | 92.9% | 99.6% | 93.7% | 95.2% | 95.2% | 99.9% | 94.1% | 90.5% | 90.6% | 95.0% | 100.0% | 99.2% | 100.0% | 85.6% | 99.2% | 100.0% | 85.6% | 85.6% | 99.2% | 85.6% | 95.0% | 86.4% | 84.6% | 85.6% | 95.0% | 100.0% | 100.0% | 92.5% | 100.0% | 100.0% | 90.6% | 92.9% | 100.0% | 86.4% | 90.6% | 90.5% | 99.2% | 86.4% | 99.2% | 99.2% | 99.2% |

## Strict Completeness by Transcript Condition

| Model | Canonical | OCR |
|-------|-----------|-----|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | N/A | 90.6% |

## Detailed Results

### driver_mvr_packet_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 3.1% | no | 89.2% | 260 | 98.3s |

### driver_mvr_packet_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 1.6% | no | 89.1% | 500 | 103.5s |

### driver_mvr_packet_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 1.6% | no | 89.1% | 500 | 117.8s |

### driver_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.4% | no | 99.9% | 500 | 95.8s |

### ifta_mileage_by_vehicle_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 1159 | 230.1s |

### ifta_mileage_by_vehicle_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2143 | 508.7s |

### ifta_mileage_by_vehicle_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2195 | 477.5s |

### ifta_mileage_by_vehicle_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2239 | 617.6s |

### ifta_mileage_by_vehicle_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2379 | 671.3s |

### ifta_mileage_by_vehicle_006 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2434 | 617.3s |

### ifta_mileage_by_vehicle_007 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 98.5% | no | 99.8% | 2445 | 810.4s |

### ifta_mileage_by_vehicle_008 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 2571 | 758.8s |

### ifta_multisection_return_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 335 | 277.6s |

### ifta_multisection_return_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 100.0% | 461 | 277.0s |

### ifta_return_schedule_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 63.7% | no | 97.0% | 558 | 575.2s |

### ifta_return_schedule_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 67.7% | no | 98.6% | 998 | 878.1s |

### ifta_return_schedule_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 64.1% | no | 97.2% | 1047 | 669.0s |

### ifta_return_schedule_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 64.7% | no | 97.2% | 1061 | 770.5s |

### ifta_return_schedule_005 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 62.9% | no | 97.1% | 1115 | 671.2s |

### ifta_tax_inquiry_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 99.9% | 649 | 152.9s |

### ifta_tax_inquiry_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.8% | no | 99.9% | 649 | 112.8s |

### ifta_tax_summary_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 760 | 322.0s |

### ifta_tax_summary_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 760 | 306.3s |

### ifta_tax_summary_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 760 | 391.8s |

### ifta_tax_summary_004 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.9% | no | 100.0% | 760 | 542.3s |

### loss_run_external_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.0% | no | 99.9% | 300 | 657.7s |

### loss_run_external_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.3% | no | 99.9% | 300 | 859.4s |

### loss_run_external_003 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.3% | no | 99.8% | 301 | 797.2s |

### mixed_040_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 40 | 403.9s |

### mixed_cgl_040_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 85.6% | no | 99.2% | 619 | 1090.2s |

### multihop_012_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 12 | 306.1s |

### multihop_025_001_crosspage (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 25 | 355.6s |

### multihop_bop_012_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 95.0% | no | 99.7% | 360 | 764.7s |

### multihop_wc_025_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 99.2% | no | 99.9% | 510 | 769.2s |

### vehicle_schedule_sparse_001 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 800 | 226.3s |

### vehicle_schedule_sparse_002 (ocr)

| Model | Exact records | Complete | Field F1 | Predicted | Time |
|-------|---------------|----------|----------|-----------|------|
| Claude Fable 5 (Claude Code CLI Agentic, xhigh) | 100.0% | yes | 100.0% | 800 | 317.0s |
