# Generation Support Modules

This directory contains shared helpers rather than a standalone benchmark generator.

The legacy v1 claim-layout generator was removed because the released v2 dataset
ships generated artifacts under `data/`. Current public generators live under
`benchmarks/core_operations/`, `benchmarks/generate_multihop_benchmark.py`, and
`benchmarks/policy_multihop/`.

The remaining modules are shared helpers used by current cross-page generation
code:

- `generate_claim_data.py` creates synthetic claim fixture rows for the claim
  multi-hop generator.
- `html_to_pdf.py` renders HTML artifacts to PDF for multi-hop generators.

Do not use this directory to regenerate the released benchmark corpus.
