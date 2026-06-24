# Internal Generation Helpers

This directory is not a public benchmark generator.

The legacy v1 claim-layout generator was removed because the released v2 dataset
ships generated artifacts under `data/`, and the production-like template
generators used to create those artifacts are intentionally kept outside the
repository.

The remaining modules are shared helpers used by current cross-page generation
code:

- `generate_claim_data.py` creates synthetic claim fixture rows for the claim
  multi-hop generator.
- `html_to_pdf.py` renders HTML artifacts to PDF for multi-hop generators.

Do not use this directory to regenerate the released benchmark corpus.
