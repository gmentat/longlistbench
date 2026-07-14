# LongListBench Data

This directory contains the released synthetic benchmark artifacts.

The intended task is per-document extraction: a system receives one PDF or OCR transcript and the target schema/field contract, then returns the complete target list for that document. Structured operations files are useful controls for scale, OCR preservation, and row completeness. Claim and policy packets are the harder regimes because fields must be joined across distant sections and, for policies, across heterogeneous record types.

## Contents

- `manifest.json` is the source of truth for the 32 released PDFs.
- `pdfs/` contains rendered source PDFs.
- `html/` contains the HTML sources used to render the PDFs.
- `ground_truth/` contains one JSON target list per PDF.
- `transcripts/ocr_gemini/` contains OCR transcripts for every PDF.
- `metadata/` contains per-sample metadata and evidence notes.
- `index.html`, `index.json`, and `index.csv` provide browsable indexes.

## Scale

- 32 PDFs and 1,773 pages.
- 29,599 target records.
- 26 core commercial operations PDFs with 28,178 records.
- 3 claim multi-hop PDFs with 77 records.
- 3 policy PDFs with 1,344 records.

All 32 PDFs have Gemini OCR transcripts. The current transcripts have 99.9% average identifier coverage, 99.9% tracked identifier-field support, and 17 target records with at least one tracked identifier missing from OCR. An audited numeric-fidelity baseline records 56 genuine OCR misses among 76,968 checked numeric fields (0.073%); CI verifies that exact miss set rather than silently correcting the OCR output.

## Complexity Stressors

Each instance records cross-cutting stressors in its `problems` metadata. The current release tracks the original generator stressors (`page_breaks`, `multi_row`, `duplicates`, `large_doc`, `multiple_tables`, `multi_column`, `merged_cells`) plus release-specific tags such as `ocr_condition`, `ocr_layout_condition`, `long_range_evidence`, `cross_section_join`, `repeated_keys`, and `heterogeneous_record_list`.

These tags are visible in `manifest.json`, per-sample files under `metadata/`, `index.csv`, `index.json`, and the browsable `index.html`. They are intentionally not printed inside the PDFs, because visible benchmark labels would make the documents less realistic.

To audit the mapping visually, open `index.html`, choose a sample, and compare the `problems` column with the linked PDF or HTML source. Examples:

| Family | Stressors visible in the PDF/HTML |
|---|---|
| `ifta_mileage_by_vehicle` | Long page-spanning unit sections, inherited unit headers, source notes inside jurisdiction rows. |
| `ifta_multisection_return_packet` | Return headers, Schedule A distance/gallon pages, and dense Jurisdictions tax-detail tables must be joined; OCR preserves visual layout rather than clean CSV rows. |
| `loss_run_external` | Merged description rows, continuation notes, summary cards, no-claims tables, and policy-period sections. |
| `claim_crosspage_multihop` | Claim schedules separated from policy, driver, claimant, cause-code, and ledger evidence by many pages. |
| `policy_multihop_*` | Heterogeneous policy records across declarations, schedules, forms, endorsements, premium pages, and clause prose. |

All visible names, identifiers, values, and document content are synthetic. Private production PDFs were used only as structural layout references and are not included in this repository.
