# Benchmarks

This directory contains benchmark generation and processing tools for the LongListBench project.

Each benchmark instance always exposes a clean transcript and can expose an OCR transcript after running OCR:

- `canonical` - a clean transcript derived from the rendered HTML/document structure
- `ocr` - a noisy transcript derived from Gemini OCR over rendered page images, created by `ocr_claims_pdfs.py`

## Setup

Run these commands from the repository root.

1. Install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r benchmarks/requirements.txt
   python -m playwright install chromium
   ```

2. Install poppler (required for PDF processing):
   ```bash
   # macOS
   brew install poppler
   
   # Linux
   apt-get install poppler-utils
   ```

3. Set up API keys (only needed for OCR/evaluation runs):
   ```bash
   cp .env.example .env
   ```
   Then edit the repo-root `.env` and set:
   ```
   VERTEX_AI_API_KEY=your-gemini-or-vertex-api-key
   GEMINI_API_KEY=your-gemini-api-key  # also supported
   OPENROUTER_API_KEY=your-openrouter-api-key  # optional, for --ocr-engine openrouter
   OPENAI_API_KEY=your-openai-api-key

   # Optional override (only affects benchmarks/evaluate_models.py; default is gemini-3.1-pro-preview)
   GEMINI_MODEL_ID=gemini-3.1-pro-preview

   # Optional evaluation controls
   LLB_MODEL_WORKERS=2
   LLB_GEMINI_CHUNK_MAX_INPUT_TOKENS=12000
   ```

## Generate Claims Benchmark

Generate synthetic benchmark artifacts:

```bash
python benchmarks/generate_claims_benchmark.py
python benchmarks/organize_dataset.py --move
```

The generator first writes the legacy flat working directory, then the organizer moves artifacts into the public `data/` layout:

- `data/pdfs/<instance_id>.pdf`
- `data/html/<instance_id>.html`
- `data/ground_truth/<instance_id>.json`
- `data/transcripts/canonical/<instance_id>.md`
- `data/metadata/<instance_id>.json`

`data/manifest.json` is the source of truth for artifact paths and transcript availability.

If you need to regenerate the flat generator metadata before organizing, run:

```bash
python benchmarks/generate_claims_benchmark.py --rebuild-metadata
```

## Generate Multi-Hop Benchmark

Generate single-document cross-page cases where the full incident records require joins across distant sections of one long PDF:

```bash
python benchmarks/generate_multihop_benchmark.py
```

This writes 3 additional samples into the same `data/` layout:

- `data/pdfs/<sample_id>.pdf`
- `data/html/<sample_id>.html`
- `data/ground_truth/<sample_id>.json`
- `data/transcripts/canonical/<sample_id>.md`
- `data/metadata/<sample_id>.json`

The cross-page samples are `multihop_012_001_crosspage`, `multihop_025_001_crosspage`, and `mixed_040_001_crosspage`. They have one PDF each, but the evidence needed for one incident is separated by dozens to hundreds of pages. Current join requirements include `policy_number -> policy register`, `unit_number -> driver roster`, `cause_code -> cause classification appendix`, and `incident_number -> claimant index/financial ledger`. The mixed sample also includes archived distractor sections with overlapping reference values.

To generate the LOB-specific policy multi-hop suite:

```bash
python benchmarks/generate_policy_multihop_benchmark.py
```

This writes `multihop_bop_012_001`, `multihop_wc_025_001`, and `mixed_cgl_040_001`. Each sample is one PDF, and each target record is a LOB-specific policy item assembled from distant sections such as declarations, described premises or classifications, coverage/limit schedules, payroll or exposure rating schedules, forms and endorsements, exclusion or endorsement detail pages, and premium summaries.

## Problem Matrix (Which files have which problems)

The authoritative mapping of `instance_id -> problems` lives in `data/manifest.json` under `instances[]`.

Each instance is generated in **two formats** (`detailed` and `table`) and each format produces:

- **PDF**: `data/pdfs/<instance_id>.pdf`
- **HTML**: `data/html/<instance_id>.html`
- **Ground truth**: `data/ground_truth/<instance_id>.json`

Below is the expected problem mapping based on `BENCHMARK_CONFIG` (the instance number cycles through the tier’s problem combinations).

Notes:

- Extreme file IDs retain a legacy `_100_` seed-count suffix; `large_doc` expands each released extreme document to 500 incidents.
- `page_breaks` and `multi_column` are strongest in detailed format. In table format, page breaks split table sections between rows and the main claims table remains single-span.

### Easy (`easy_10_XXX_{detailed,table}`)

| Instance numbers | Enabled problems |
|---|---|
| `001, 006, 011` | `multi_row` |
| `002, 007, 012` | `page_breaks` |
| `003, 008, 013` | `multi_row`, `page_breaks` |
| `004, 009, 014` | `duplicates` |
| `005, 010, 015` | `multi_row`, `duplicates` |

### Medium (`medium_25_XXX_{detailed,table}`)

| Instance numbers | Enabled problems |
|---|---|
| `001, 005, 009` | `page_breaks`, `multi_row`, `duplicates` |
| `002, 006, 010` | `page_breaks`, `multi_row`, `multiple_tables` |
| `003, 007, 011` | `multi_row`, `duplicates`, `multiple_tables` |
| `004, 008, 012` | `page_breaks`, `duplicates`, `multiple_tables` |

### Hard (`hard_50_XXX_{detailed,table}`)

| Instance numbers | Enabled problems |
|---|---|
| `001, 004, 007` | `page_breaks`, `multi_row`, `duplicates`, `multiple_tables`, `multi_column` |
| `002, 005, 008` | `page_breaks`, `multi_row`, `duplicates`, `multiple_tables`, `merged_cells` |
| `003, 006` | `page_breaks`, `multi_row`, `duplicates`, `multi_column`, `merged_cells` |

### Extreme (`extreme_100_XXX_{detailed,table}`)

| Instance numbers | Enabled problems |
|---|---|
| `001-005` | `page_breaks`, `multi_row`, `duplicates`, `large_doc`, `multiple_tables`, `multi_column`, `merged_cells` |

## OCR Claims PDFs

## Policy Multi-Hop Generation

Policy multi-hop fixtures are generated by `benchmarks/generate_policy_multihop_benchmark.py`, which delegates to the smaller `benchmarks/policy_multihop/` package. Deterministic Python code generates the ground-truth policy items; Markdown prompts in `benchmarks/policy_multihop/prompts/` describe how Gemini should write original synthetic BOP, WC, and CGL policy prose.

Offline/template generation:

```bash
python benchmarks/generate_policy_multihop_benchmark.py
```

Gemini-authored synthetic policy prose:

```bash
python benchmarks/generate_policy_multihop_benchmark.py \
  --text-generator gemini \
  --gemini-model gemini-3.1-pro-preview \
  --thinking-level high
```

Gemini outputs are cached under `data/generated_text/policy_multihop/` by default so regenerated HTML/PDF artifacts can reuse the same synthetic prose. This is separate from OCR; run OCR only after the PDFs are accepted.

Process PDF files in `data/pdfs/` using Gemini OCR:

```bash
python benchmarks/ocr_claims_pdfs.py --model gemini-3.5-flash
```

For only the cross-page multi-hop cases:

```bash
python benchmarks/ocr_claims_pdfs.py --tiers multihop mixed --force
```

If you use OpenRouter for Gemini OCR instead of a direct Gemini key:

```bash
python benchmarks/ocr_claims_pdfs.py \
  --tiers multihop mixed \
  --ocr-engine openrouter \
  --model google/gemini-3.5-flash
```

This will:
- Process all PDF files in parallel
- Extract text using the Google Gemini vision model
- Save results under `data/transcripts/ocr_gemini/{sample_id}.md`
- Skip files that have already been processed
- Handle multi-page PDFs efficiently

After regenerating PDFs, rerun OCR with `--force`; OCR transcripts from older PDFs are intentionally not reusable.

The default OCR path is `gemini`, not text-layer extraction. Text-layer mode remains available only as an explicit local/debug option.

The script will show progress for each file and provide a summary at the end.

Recommended staged workflow (validate each tier before moving on):

```bash
python benchmarks/ocr_claims_pdfs.py --force --tiers easy
python benchmarks/validate_ocr_vs_golden.py --claims-dir data --tiers easy

python benchmarks/ocr_claims_pdfs.py --force --tiers medium
python benchmarks/validate_ocr_vs_golden.py --claims-dir data --tiers medium
```

## Multi-Model Evaluation

Run extraction evaluation across the registered model/regime keys. Common keys are `gemini`, `gemini_oneshot`, `gpt52`, `gpt55_oneshot`, `gpt55_chunked`, and `gpt55_agent`.

Note: running evaluation with `--offline` regenerates reports from saved `*_predicted.json` files without making API calls.

```bash
# Default evaluation uses canonical transcripts available after generation
python benchmarks/evaluate_models.py --models gemini gpt52 --parallel-models --model-workers 2

# Full OCR-condition evaluation (all tiers, both formats)
python benchmarks/evaluate_models.py --models gemini gpt52 --parallel-models --model-workers 2 --transcripts ocr

# GPT-5.5 regime ablation on the OCR condition
python benchmarks/evaluate_models.py --models gpt55_oneshot gpt55_chunked gpt55_agent --transcripts ocr

# GPT-5.5 agentic extraction on the multi-hop OCR cases
LLB_AGENT_REASONING_EFFORT=xhigh LLB_AGENT_VERBOSITY=high \
python benchmarks/evaluate_models.py \
  --models gpt55_agent \
  --tiers multihop mixed \
  --transcripts ocr \
  --output-dir benchmarks/results/agentic_multihop_gpt55

# Quick test (one sample per tier)
python benchmarks/evaluate_models.py --quick

# Compare clean vs OCR conditions on a slice
python benchmarks/evaluate_models.py --tiers easy --formats detailed --transcripts canonical ocr

# Regenerate a report offline from an existing results directory
python benchmarks/evaluate_models.py --offline --output-dir benchmarks/results/released/medium --transcripts ocr
```

Results are written to the `--output-dir` (default: `benchmarks/results/scratch/`):
- `evaluation_report.json` - Full metrics data
- `evaluation_report.md` - Human-readable summary

When multiple transcript conditions are evaluated in the same run, reports include transcript-aware breakdowns in addition to tier/format summaries.

This repository includes released evaluation artifacts under:
- `benchmarks/results/agentic_multihop_gpt55/`
- `benchmarks/results/local_two_regimes/`
- `benchmarks/results/oneshot_gpt55/`
- `benchmarks/results/chunked_gpt55/`
- `benchmarks/results/agentic_gpt55/`
- `benchmarks/results/released/easy/`
- `benchmarks/results/released/medium/`
- `benchmarks/results/released/hard/`
- `benchmarks/results/released/extreme/`

## Directory Structure

- `../data/` - Public dataset artifacts organized by modality
- `../data/manifest.json` - Dataset manifest and sample index
- `../data/pdfs/` - Rendered PDFs
- `../data/html/` - Rendered HTML sources
- `../data/ground_truth/` - Ground-truth incident JSON files
- `../data/transcripts/canonical/` - Clean transcripts derived from HTML
- `../data/transcripts/ocr_gemini/` - Gemini OCR transcripts
- `../data/metadata/` - Per-sample metadata and evidence maps
- `results/scratch/` - Scratch evaluation output directory (default)
- `results/released/` - Released evaluation artifacts per tier
- `synthetic/` - Synthetic data generation tools
- `generate_claims_benchmark.py` - Main benchmark generation script
- `organize_dataset.py` - Converts flat generator output into the public `data/` layout
- `generate_multihop_benchmark.py` - Single-document cross-page multi-hop generator
- `ocr_claims_pdfs.py` - OCR processing script for PDFs
- `evaluate_models.py` - Multi-model evaluation script
