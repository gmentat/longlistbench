# LongListBench Data

This directory contains the released synthetic benchmark artifacts.

## Contents

- `manifest.json` is the source of truth for the 34 released PDFs.
- `pdfs/` contains rendered source PDFs.
- `html/` contains the HTML sources used to render the PDFs.
- `ground_truth/` contains one JSON target list per PDF.
- `transcripts/ocr_gemini/` contains OCR transcripts for every PDF.
- `metadata/` contains per-sample metadata and evidence notes.
- `index.html`, `index.json`, and `index.csv` provide browsable indexes.

## Scale

- 34 PDFs.
- 32,654 target records.
- 28 core commercial operations PDFs with 31,088 records.
- 3 claim multi-hop PDFs with 77 records.
- 3 policy PDFs with 1,489 records.

OCR validation passes on all 34 PDFs. The current transcripts have 100.0% average identifier coverage, 99.9% tracked identifier-field support, and 39 target records with at least one tracked identifier missing from OCR.

## Complexity Stressors

Each instance records cross-cutting stressors in its `problems` metadata. The current release tracks the original generator stressors (`page_breaks`, `multi_row`, `duplicates`, `large_doc`, `multiple_tables`, `multi_column`, `merged_cells`) plus release-specific tags such as `ocr_condition`, `long_range_evidence`, and `heterogeneous_record_list`.

These tags are visible in `manifest.json`, per-sample files under `metadata/`, `index.csv`, `index.json`, and the browsable `index.html`. They are intentionally not printed inside the PDFs, because visible benchmark labels would make the documents less realistic.

To audit the mapping visually, open `index.html`, choose a sample, and compare the `problems` column with the linked PDF or HTML source. Examples:

| Family | Stressors visible in the PDF/HTML |
|---|---|
| `ifta_mileage_by_vehicle` | Long page-spanning unit sections, inherited unit headers, source notes inside jurisdiction rows. |
| `loss_run_external` | Merged description rows, continuation notes, summary cards, no-claims tables, and policy-period sections. |
| `claim_crosspage_multihop` | Claim schedules separated from policy, driver, claimant, cause-code, and ledger evidence by many pages. |
| `policy_multihop_*` | Heterogeneous policy records across declarations, schedules, forms, endorsements, premium pages, and clause prose. |

All visible names, identifiers, values, and document content are synthetic. Private production PDFs were used only as structural layout references and are not included in this repository.
