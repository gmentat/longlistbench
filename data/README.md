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

All visible names, identifiers, values, and document content are synthetic. Private production PDFs were used only as structural layout references and are not included in this repository.
