# LongListBench

Benchmark for long-list entity extraction from complex semi-structured business PDFs, including dense layouts, OCR transcripts, and long-range cross-page evidence.

This benchmark was developed at [Kay.ai](https://kay.ai).

LongListBench evaluates complete per-document extraction: give a system one PDF or OCR transcript plus the target output contract, then measure exact records and fully complete documents. Structured operations families are scale and completeness controls; claim and policy packets add distant evidence, inherited context, and heterogeneous schemas.

## Quick Start

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
python -m pip install -r benchmarks/requirements.txt
python -m playwright install chromium

# Set API keys (only needed for OCR/evaluation runs)
cp .env.example .env

# Inspect the released dataset artifacts
open data/index.html

# Run OCR/evaluation only when regenerating transcripts or baselines
python benchmarks/ocr_claims_pdfs.py --model gemini-3.5-flash
```

## Reproducibility

Convenience targets are provided via the repository root `Makefile`:

```bash
make help

# Create venv + install deps + install Playwright Chromium
make setup

# Build dataset indexes from the current data/ directory
python benchmarks/build_instance_index.py --input data

# Build the paper
make paper
```

See [`benchmarks/README.md`](benchmarks/README.md) for benchmark documentation.

## Hugging Face Dataset Package

The repository can export a LongArray-style Hugging Face dataset package with one row per PDF, embedded PDF bytes, JSON ground truth, metadata, and available transcripts:

```bash
source .venv/bin/activate
python -m pip install -r benchmarks/requirements-hf.txt

make hf-export
```

By default this writes an ignored local package to `dist/huggingface/longlistbench/` for `kaydotai/LongListBench`. Override the target repo ID with:

```bash
HF_REPO_ID=your-org/your-dataset make hf-export
```

The exported Hugging Face configs are:

| Config | Contents |
|--------|----------|
| `core_operations` | 30 production-like commercial insurance and trucking-operation PDFs with dense repeated operations, IFTA, and loss-run records |
| `claim_multihop` | 3 claim PDFs requiring long-range cross-page joins |
| `policy_packets` | 3 long BOP, WC, and CGL policy packets requiring cross-page extraction |

Upload only after inspecting the generated package:

```bash
python benchmarks/export_hf_dataset.py \
  --input data \
  --output dist/huggingface/longlistbench \
  --repo-id kaydotai/LongListBench \
  --overwrite \
  --upload
```

## Versioning and Citation

- **Version**: see `VERSION`.
- **Citation metadata**: see `CITATION.cff`.

## Benchmark Overview

- **36 benchmark instances** across 13 production-like document families
- **33,450 target records** across commercial operations, claim, and policy extraction tasks
- **30 core operations PDFs** covering IFTA, driver/MVR, vehicle schedule, and loss-run layouts
- **3 policy PDFs** covering long BOP, WC, and CGL policy packets
- **3 claim cross-page PDFs**, with 3 of the policy PDFs also requiring long-range cross-page extraction
- **Ground truth annotations** in JSON format
- **OCR transcripts** generated from rendered PDF page images
- **OCR support validation**: 100.0% average identifier coverage, 99.9% tracked identifier-field support, 39 records with at least one tracked identifier missing from OCR, and 0 unrecoverable ground-truth numeric values at the default numeric-fidelity threshold
- **Synthetic visible values only**; private production documents were used only as visual layout references

## Dataset Layout

Released artifacts are organized by modality under `data/`:

```text
data/
  manifest.json
  pdfs/{sample_id}.pdf
  html/{sample_id}.html
  ground_truth/{sample_id}.json
  transcripts/ocr_gemini/{sample_id}.md
  metadata/{sample_id}.json
  schemas/*.schema.json
```

`data/manifest.json` is the source of truth for sample IDs, document families, artifact paths, transcript availability, and per-sample metadata.

### Document Families

| Family | PDFs | Target records |
|--------|-----:|---------------:|
| `ifta_mileage_by_vehicle` | 8 | 17,565 |
| `ifta_multisection_return_packet` | 2 | 796 |
| `ifta_return_schedule_details` | 5 | 4,923 |
| `ifta_tax_return_summary` | 4 | 3,040 |
| `driver_mvr_request_and_roster` | 3 | 1,260 |
| `loss_run_external` | 3 | 900 |
| `vehicle_schedule_spreadsheet_export` | 2 | 1,600 |
| `ifta_tax_return_inquiry_detail` | 2 | 1,300 |
| `driver_schedule_spreadsheet_export` | 1 | 500 |
| `claim_crosspage_multihop` | 3 | 77 |
| `policy_multihop_bop` | 1 | 360 |
| `policy_multihop_wc` | 1 | 510 |
| `policy_multihop_cgl` | 1 | 619 |

### Complexity Stressors

LongListBench defines 14 canonical cross-cutting stressors in each instance's `problems` metadata. The manifest contains 45 distinct problem tokens because it also retains finer domain and implementation tags for audit slices.

| Tag | Meaning |
|-----|---------|
| `page_breaks` | Target lists or supporting sections span page boundaries with repeated headers or inherited context. |
| `split_records` | One target record has fields in separate visual blocks, sections, or pages and must be assembled. |
| `multi_row` | One logical record contains wrapped notes, long descriptions, clause prose, or continuation rows. |
| `duplicates` | Duplicate or near-duplicate distractor material appears, usually as prior-term/archive sections rather than exact duplicate target rows. |
| `large_doc` | Documents contain hundreds to thousands of targets or enough pages to expose truncation/list-completeness failures. |
| `multiple_tables` | Target records are mixed with summaries, ledgers, support tables, schedules, or empty/no-claims tables. |
| `multi_column` | Two-column or form-like layouts stress reading order. |
| `merged_cells` | Tables use merged cells, section-spanning rows, or `colspan`/`rowspan` structure. |
| `ocr_condition` | Released transcripts are OCR output from rendered PDF page images. |
| `ocr_layout_condition` | OCR preserves visual spacing and reading order instead of converting tables into clean CSV-style rows. |
| `long_range_evidence` | Required fields must be joined from distant sections of the same PDF. |
| `cross_section_join` | A target record must be assembled from separately labeled sections, such as return summary, distance/gallon schedules, and liability schedules. |
| `repeated_keys` | Common keys such as states or jurisdictions repeat across sections or returns, so the key alone is insufficient for matching. |
| `heterogeneous_record_list` | One output list contains multiple schema families, especially in policy packets. |

These tags are present in `data/manifest.json`, `data/metadata/{sample_id}.json`, the browsable `data/index.html`, and the Hugging Face export.

The PDFs do not print these labels, but the stressors are visible in the document structure. This map gives representative pages to inspect; the full per-instance mapping is in the metadata.

| Stressor | Representative PDF/pages | What to check |
|----------|--------------------------|---------------|
| `page_breaks` | `ifta_mileage_by_vehicle_001`, pages 3-4 | Unit 118 spans two pages with the same unit header and jurisdiction rows split across the page boundary. |
| `split_records` | `ifta_multisection_return_001`, pages 1, 2, and 4 | One jurisdiction record combines return-header context, Schedule A mileage/gallons, and later tax-detail fields. |
| `multi_row` | `loss_run_external_001`, pages 1-2; `driver_mvr_packet_001`, page 10 | Claim rows include description/detail rows; driver records include roster/MVR detail blocks. |
| `duplicates` | `loss_run_external_001`, pages 1-2; `multihop_bop_012_001`, page 142 | Summary/no-claim rows and archived/prior-term sections create near-duplicate distractors. |
| `large_doc` | `ifta_mileage_by_vehicle_008`, whole PDF; `mixed_cgl_040_001`, whole PDF | Long files with 218 and 316 pages respectively, including thousands of operation rows or many policy records. |
| `multiple_tables` | `ifta_tax_inquiry_001`, page 1; `loss_run_external_001`, pages 1-2 | Target tables appear alongside support tables, empty tables, summaries, and section totals. |
| `multi_column` | `mixed_cgl_040_001`, pages 139-150; `multihop_wc_025_001`, pages 95-106 | Material policy provisions are laid out in two-column policy-form pages. |
| `merged_cells` | `loss_run_external_001`, page 1; `ifta_tax_inquiry_001`, page 1 | Section-spanning rows and wide description/status cells interrupt the tabular structure. |
| `ocr_condition` | Any PDF with `data/transcripts/ocr_gemini/{sample_id}.md`, for example `loss_run_external_001`, page 1 | The released text input is OCR output from rendered page images, not the HTML text layer. |
| `ocr_layout_condition` | `ifta_multisection_return_001`, pages 2 and 4 | OCR preserves the visual Schedule A table and dense Jurisdictions tax-detail table instead of a clean row table. |
| `long_range_evidence` | `multihop_012_001_crosspage`, pages 4, 36, 56, 57, 76; `mixed_040_001_crosspage`, pages 4, 86, 143, 144, 186 | A front claim row must be joined to driver, policy, cause-code, claimant, and ledger sections far apart in one PDF. |
| `cross_section_join` | `ifta_multisection_return_001`, pages 1, 2, 4 | Each jurisdiction row combines return header context, Schedule A mileage/gallon values, and Jurisdictions tax-detail values while ignoring adjustment/support rows. |
| `repeated_keys` | `ifta_multisection_return_001`, pages 2, 4, 8, 10 | The same jurisdiction codes recur across returns and sections, so state code alone is not a unique row key. |
| `heterogeneous_record_list` | `multihop_bop_012_001`, pages 26, 48, 94, 127, 142; `mixed_cgl_040_001`, pages 66-73 and 139-150 | One output list mixes locations/classifications, coverage items, forms, endorsements, premiums, and clause records. |

### Multi-Hop Extensions

The repository includes two single-document cross-page multi-hop suites in the same `data/` layout.

The claim multi-hop suite has 3 PDFs and 77 target incidents. These cases keep the same incident schema, but required fields are spread across distant sections of one long PDF. The primary claim schedule appears near the front; supporting rosters, policy registers, cause-code appendices, claimant indexes, and financial ledgers appear dozens to hundreds of pages later with dense distractor pages in between.

| Join key | Distant section |
|----------|-----------------|
| `policy_number` | Policy register |
| `unit_number` | Driver roster |
| `cause_code` | Cause classification appendix |
| `incident_number` | Claimant index and financial ledger |

The cross-page PDFs are:

| Sample | Pages | Target incidents |
|--------|-------|------------------|
| `multihop_012_001_crosspage` | 80 | 12 |
| `multihop_025_001_crosspage` | 136 | 25 |
| `mixed_040_001_crosspage` | 209 | 40 |

Join/evidence metadata is recorded in `data/metadata/{sample_id}.json`; the rendered documents do not expose benchmark instructions such as "join on" labels.

The policy suite has 3 commercial insurance policy PDFs and 1,489 target policy records. A policy packet is the contract document issued by an insurer; it combines declarations, covered locations or classifications, coverage limits and deductibles, rating or premium schedules, required forms, material policy clauses, and endorsements that modify the base policy. The samples cover Businessowners Policy (BOP), Workers Compensation (WC), and Commercial General Liability (CGL) schemas inspired by real policy-review workflows. The visible document content is synthetic, but the packet structure mirrors observed commercial policy packets.

Interpret the configs separately. `core_operations` contains high-density structured reports where deterministic row parsers or document-specific agent code can perform well; those files measure scale, OCR preservation, and output completeness. The multisection IFTA files within `core_operations` add OCR-layout preservation and cross-section joins. The claim and policy packet configs are the stronger complex packet cases, with inherited context, heterogeneous record types, distant supporting sections, and distractor material.

OCR support should be interpreted at the affected-record and field level, not only by unique identifier coverage. For example, a single missing repeated header can affect many rows that inherit that value. The current identifier validation reports 39 affected records across 33,450 total targets. The numeric-fidelity gate also checks that every ground-truth numeric value with absolute value at least 10 is recoverable from the released OCR transcript; the current release has 0 unrecoverable numeric values under that gate. These OCR support gates do not score extraction quality by themselves. The evaluator compares complete normalized records first and reports flattened field-value overlap as secondary partial credit, so recovering identifiers alone is insufficient.

| Sample | Pages | Target policy records |
|--------|-------|-----------------------|
| `multihop_bop_012_001` | 142 | 360 |
| `multihop_wc_025_001` | 194 | 510 |
| `mixed_cgl_040_001` | 316 | 619 |

## Saved Evaluation Artifacts

Saved reports under `benchmarks/results/` should be treated as local run artifacts unless their manifest hash matches the current `data/manifest.json`. After replacing layouts, rerun OCR and evaluation before citing current-layout or current-model baselines. The current released dataset includes OCR transcripts for every PDF.

The release includes four full-corpus repository-denied coding-agent runs under the same OCR input and field-contract protocol. Each result directory includes all 36 predictions and a report that can be checked offline.

| Agent | Documents | Target records | Errors | Exact-record recall | Complete documents | Field micro-F1 |
|---|---:|---:|---:|---:|---:|---:|
| Codex CLI `gpt-5.6-sol`, xhigh | 36 | 33,450 | 0 | 89.0% | 13/36 (36.1%) | 97.3% |
| Claude Code `claude-fable-5`, xhigh | 36 | 33,450 | 0 | 90.6% | 15/36 (41.7%) | 98.9% |
| Codex CLI `gpt-5.5`, xhigh | 36 | 33,450 | 0 | 89.5% | 12/36 (33.3%) | 98.7% |
| Claude Code `claude-opus-4-8`, xhigh | 36 | 33,450 | 0 | 86.9% | 13/36 (36.1%) | 98.6% |

The latest saved results are under `benchmarks/results/codex_gpt56_sol_full_current_ocr_v2/` and `benchmarks/results/claude_fable5_full_current_ocr_v2/`; the GPT-5.5 and Opus 4.8 comparison runs remain available beside them.

An exact record must match every normalized target field. Complete-document success requires the predicted and ground-truth record multisets to be identical, including duplicates and with no extra records. Record order is not scored. Field-pair F1 remains a secondary partial-credit diagnostic.

The evaluator uses a fixed document-family mapping for scale-test and structural-challenge roles:

| Evaluation role | Documents | Target records | GPT-5.6-Sol exact | Fable 5 exact | GPT-5.6-Sol complete | Fable 5 complete |
|---|---:|---:|---:|---:|---:|---:|
| Structural challenges | 21 | 10,745 | 66.4% | 71.2% | 4/21 (19.0%) | 4/21 (19.0%) |
| Scale tests | 15 | 22,705 | 99.7% | 99.8% | 9/15 (60.0%) | 11/15 (73.3%) |

Strict exact-record recall for the latest models, labeled by the extraction problem each family emphasizes:

| Extraction problem | Documents | Target records | GPT-5.6-Sol | Fable 5 |
|---|---:|---:|---:|---:|
| Sparse record enrichment (driver/MVR) | 3 | 1,260 | 1.9% | 1.9% |
| Long-range claim joins | 3 | 77 | 100.0% | 100.0% |
| Split return schedules | 5 | 4,923 | 58.5% | 64.6% |
| Mixed row/detail loss runs | 3 | 900 | 98.6% | 99.2% |
| Tax inquiry detail tables | 2 | 1,300 | 99.8% | 99.8% |
| Heterogeneous policy records | 3 | 1,489 | 78.7% | 92.5% |
| Cross-section return joins | 2 | 796 | 99.9% | 99.9% |
| Tax-summary scale tests | 4 | 3,040 | 99.9% | 99.9% |
| Driver-schedule scale test | 1 | 500 | 99.4% | 99.4% |
| Mileage-by-vehicle scale tests | 8 | 17,565 | 99.7% | 99.8% |
| Vehicle-schedule scale tests | 2 | 1,600 | 99.6% | 100.0% |

Full-context one-shot prompting is not treated as a full-corpus protocol for this release. It is useful as a lower-bound stress test, but the largest documents can hit model output limits or latency timeouts before returning a scoreable complete list.

For all released runs, claim tasks received the published JSON Schema. Generic tasks received sample-specific field names and record groups derived from ground-truth object structure. This disclosed the output schema but not target values or counts. Each temporary workspace contained only the OCR transcript, field contract, prompt, and output directory; the macOS sandbox denied the benchmark repository, and the prompt prohibited other host files. This was repository isolation rather than a host-wide filesystem allowlist. Scoring normalizes whitespace, dates, decimals, accounting negatives, string case, and documented region/fuel/line-of-business/clause-scope representations before comparing complete records and secondary field-value pairs.

## Development Setup

### Installing the Pre-Commit Hook

Optional: install a pre-commit hook to quickly sanity-check that the paper compiles:

```bash
# From the repository root
cp pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook runs a fast LaTeX compile (`make quick`) in the `paper` directory; in strict mode it can prevent the commit if compilation fails.

By default, the hook is best-effort and will skip (or warn) when dependencies are missing. To make paper compilation failures block commits, set:

```bash
export STRICT_PAPER_COMPILE=1
```

**Manually invoking the hook:**
```bash
# Test the hook without committing
.git/hooks/pre-commit
```

Alternatively, run the same check from your virtualenv:
```bash
source .venv/bin/activate
make -C paper quick
```

**Note:** You can skip the hook for a specific commit using:
```bash
git commit --no-verify
```

### Paper Build Only

LaTeX is only needed if you want to compile the paper locally.

- LaTeX distribution (TeX Live, MacTeX, or similar)
- `pdflatex` and `biber` available in your `PATH`
- See [paper/README.md](paper/README.md) for paper-specific build instructions
