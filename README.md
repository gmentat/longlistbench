# LongListBench

Benchmark for long-list entity extraction from semi-structured documents under complex layouts, OCR noise, and long-range cross-page evidence complexity, inspired by recurring patterns observed in real-world claims documents.

This benchmark was developed at [Kay.ai](https://kay.ai).

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

# Generate the complete benchmark dataset and organize it under data/
python benchmarks/generate_claims_benchmark.py
python benchmarks/organize_dataset.py --move

# Optional: add single-document cross-page multi-hop cases
python benchmarks/generate_multihop_benchmark.py
```

## Reproducibility

Convenience targets are provided via the repository root `Makefile`:

```bash
make help

# Create venv + install deps + install Playwright Chromium
make setup

# Generate synthetic benchmark dataset and organize artifacts under data/
make generate

# Generate single-document cross-page multi-hop cases
make generate-multihop

# Build the paper
make paper
```

See [`benchmarks/README.md`](benchmarks/README.md) for benchmark documentation.

## Versioning and Citation

- **Version**: see `VERSION`.
- **Citation metadata**: see `CITATION.cff`.

## Benchmark Overview

- **80 benchmark instances** across 4 difficulty tiers × 2 formats
- **2,700 base claims** across all instances (some instances include additional rows due to `large_doc` and `duplicates`)
- **7 implemented problem types** approximating common long-list failure modes
- **2 document formats** (detailed and table views)
- **Ground truth annotations** in JSON format
- **Canonical transcripts** derived from rendered HTML
- **OCR transcript generation** via Gemini page-image OCR (run separately after PDF generation)
- **Multi-hop extension** with single-document long-range cross-page evidence joins

## Dataset Layout

Released artifacts are organized by modality under `data/`:

```text
data/
  manifest.json
  pdfs/{sample_id}.pdf
  html/{sample_id}.html
  ground_truth/{sample_id}.json
  transcripts/canonical/{sample_id}.md
  transcripts/ocr_gemini/{sample_id}.md  # created after running OCR
  metadata/{sample_id}.json
  schemas/loss_run_incident.schema.json
```

`data/manifest.json` is the source of truth for sample IDs, complexity regimes, artifact paths, transcript availability, and per-sample metadata.

### Problem Types

| Code | Meaning |
|------|---------|
| `page_breaks` | Detailed documents can split one incident across pages; table documents insert row-boundary page breaks with repeated table headers. |
| `multi_row` | Key fields (especially descriptions) span multiple lines/rows instead of being single-line. |
| `duplicates` | Duplicate incidents are inserted (exact repeats) to test deduplication and counting. |
| `large_doc` | Document is much longer than normal (many more incidents/pages). |
| `multiple_tables` | Adds additional irrelevant tables/sections mixed in with the main claims content. |
| `multi_column` | Uses a multi-column layout in detailed-format content and distractor sections to stress reading order. |
| `merged_cells` | Uses merged table cells (e.g. `rowspan`/`colspan`) to make table structure harder. |

The strongest `page_breaks` and `multi_column` effects are format-dependent: detailed documents receive split-record page breaks and multi-column primary content, while table documents keep the main claims table single-span.

### Difficulty Tiers

| Tier | Seed Claims/PDF | Released Rows/Doc | Instances | Formats | Problems |
|------|-----------------|-------------------|-----------|---------|----------|
| Easy | 10 | 10-11 | 15×2 = 30 | Detailed + Table | 1-2 |
| Medium | 25 | 25-27 | 12×2 = 24 | Detailed + Table | 3-4 |
| Hard | 50 | 55 | 8×2 = 16 | Detailed + Table | 5-6 |
| Extreme | 100 | 500 | 5×2 = 10 | Detailed + Table | All 7 |

The released dataset includes additional rows from `duplicates` and `large_doc`. Extreme filenames retain a legacy `_100_` seed-count suffix, but every released extreme document contains 500 incidents.

### Document Formats

- **Detailed**: Incident sections with line items and financial breakdowns
- **Table**: Compact tabular format with all claims in rows

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
| `multihop_012_001_crosspage` | 76 | 12 |
| `multihop_025_001_crosspage` | 126 | 25 |
| `mixed_040_001_crosspage` | 198 | 40 |

Join/evidence metadata is recorded in `data/metadata/{sample_id}.json`; the rendered documents do not expose benchmark instructions such as "join on" labels.

The policy multi-hop suite has 3 commercial insurance policy PDFs and 345 target policy records. A policy packet is the contract document issued by an insurer; it combines declarations, covered locations or classifications, coverage limits and deductibles, rating or premium schedules, required forms, and endorsements that modify the base policy. The samples cover Businessowners Policy (BOP), Workers Compensation (WC), and Commercial General Liability (CGL) schemas inspired by real policy-review workflows. The visible document content is synthetic, but the packet structure mirrors observed commercial policy packets.

Policy prose generation is split from ground-truth generation. The item values are deterministic Python fixtures; the long policy-condition prose can be generated from Markdown prompts under `benchmarks/policy_multihop/prompts/` with Gemini:

```bash
POLICY_TEXT_GENERATOR=gemini make generate-policy-multihop
```

The default `POLICY_TEXT_GENERATOR=template` path stays offline for tests and contributors without API keys.

| Sample | Pages | Target policy records |
|--------|-------|-----------------------|
| `multihop_bop_012_001` | 90 | 48 |
| `multihop_wc_025_001` | 140 | 113 |
| `mixed_cgl_040_001` | 214 | 184 |

## Saved Evaluation Artifacts

The core-suite reports under `benchmarks/results/` are archival snapshots from earlier layouts and earlier model defaults. After regenerating layouts, rerun OCR and evaluation before citing current-layout or current-model baselines. The evaluator supports direct clean-vs-OCR comparisons by running the same extractor over `canonical` and `ocr` transcript conditions.

The current multi-hop OCR agentic run is saved under `benchmarks/results/agentic_multihop_gpt55/`.

## Development

For development and testing, see [`benchmarks/synthetic/README.md`](benchmarks/synthetic/README.md) for the synthetic data generator.

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
