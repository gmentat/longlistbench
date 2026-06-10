# Repository Makefile (convenience targets)

.PHONY: help setup generate generate-multihop ocr ocr-multihop eval paper paper-quick clean

VENV_DIR ?= .venv
EVAL_OUT ?= benchmarks/results/scratch/eval_ocr100
EVAL_MODELS ?= gemini gpt52
EVAL_WORKERS ?= 2
OCR_ENGINE ?= gemini
OCR_MODEL ?= gemini-2.5-flash

help:
	@echo "Targets:"
	@echo "  make setup       - Create .venv + install benchmark deps + install Playwright Chromium"
	@echo "  make generate    - Generate the synthetic benchmark dataset (PDF/HTML/JSON)"
	@echo "  make generate-multihop - Generate cross-document multi-hop cases"
	@echo "  make ocr         - OCR all generated PDFs (requires GEMINI_API_KEY)"
	@echo "  make ocr-multihop - OCR multi-hop PDFs recursively"
	@echo "  make eval        - Run evaluation (requires model API keys unless --offline)"
	@echo "  make paper       - Build the paper PDF (full build with bibliography)"
	@echo "  make paper-quick - Quick paper build (single pass, no bibliography update)"
	@echo "  make clean       - Clean paper build artifacts"

setup:
	python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && python -m pip install -r benchmarks/requirements.txt
	. $(VENV_DIR)/bin/activate && python -m playwright install chromium

generate:
	. $(VENV_DIR)/bin/activate && python benchmarks/generate_claims_benchmark.py

generate-multihop:
	. $(VENV_DIR)/bin/activate && python benchmarks/generate_multihop_benchmark.py

ocr:
	. $(VENV_DIR)/bin/activate && python benchmarks/ocr_claims_pdfs.py

ocr-multihop:
	. $(VENV_DIR)/bin/activate && python benchmarks/ocr_claims_pdfs.py --claims-dir benchmarks/multihop_claims --recursive --ocr-engine $(OCR_ENGINE) --model $(OCR_MODEL)

eval:
	. $(VENV_DIR)/bin/activate && python benchmarks/evaluate_models.py --models $(EVAL_MODELS) --parallel-models --model-workers $(EVAL_WORKERS) --output-dir $(EVAL_OUT)

paper:
	$(MAKE) -C paper pdf

paper-quick:
	$(MAKE) -C paper quick

clean:
	$(MAKE) -C paper clean
