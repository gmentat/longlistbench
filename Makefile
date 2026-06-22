# Repository Makefile (convenience targets)

.PHONY: help setup generate generate-multihop generate-policy-multihop ocr ocr-multihop eval hf-export paper paper-quick clean

VENV_DIR ?= .venv
EVAL_OUT ?= benchmarks/results/scratch/eval_ocr
EVAL_MODELS ?= gpt55_oneshot
EVAL_WORKERS ?= 2
HF_OUT ?= dist/huggingface/longlistbench
HF_REPO_ID ?= kaydotai/LongListBench
OCR_ENGINE ?= gemini
OCR_MODEL ?= gemini-3.5-flash
POLICY_TEXT_GENERATOR ?= template
POLICY_GEMINI_MODEL ?= gemini-3.1-pro-preview
POLICY_GEMINI_THINKING_LEVEL ?= high

help:
	@echo "Targets:"
	@echo "  make setup       - Create .venv + install benchmark deps + install Playwright Chromium"
	@echo "  make generate    - Generate and organize the synthetic benchmark dataset"
	@echo "  make generate-multihop - Generate single-document cross-page multi-hop cases"
	@echo "  make generate-policy-multihop - Generate BOP/WC/CGL policy multi-hop cases"
	@echo "  make ocr         - OCR all generated PDFs (requires GEMINI_API_KEY)"
	@echo "  make ocr-multihop - OCR cross-page multi-hop PDFs"
	@echo "  make eval        - Run evaluation (requires model API keys unless --offline)"
	@echo "  make hf-export   - Build a local Hugging Face dataset package under dist/"
	@echo "  make paper       - Build the paper PDF (full build with bibliography)"
	@echo "  make paper-quick - Quick paper build (single pass, no bibliography update)"
	@echo "  make clean       - Clean paper build artifacts"

setup:
	python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && python -m pip install -r benchmarks/requirements.txt
	. $(VENV_DIR)/bin/activate && python -m playwright install chromium

generate:
	. $(VENV_DIR)/bin/activate && python benchmarks/generate_claims_benchmark.py
	. $(VENV_DIR)/bin/activate && python benchmarks/organize_dataset.py --move
	. $(VENV_DIR)/bin/activate && python benchmarks/build_instance_index.py --input data

generate-multihop:
	. $(VENV_DIR)/bin/activate && python benchmarks/generate_multihop_benchmark.py
	. $(VENV_DIR)/bin/activate && python benchmarks/build_instance_index.py --input data

generate-policy-multihop:
	. $(VENV_DIR)/bin/activate && python benchmarks/generate_policy_multihop_benchmark.py --text-generator $(POLICY_TEXT_GENERATOR) --gemini-model $(POLICY_GEMINI_MODEL) --thinking-level $(POLICY_GEMINI_THINKING_LEVEL)
	. $(VENV_DIR)/bin/activate && python benchmarks/build_instance_index.py --input data

ocr:
	. $(VENV_DIR)/bin/activate && python benchmarks/ocr_claims_pdfs.py

ocr-multihop:
	. $(VENV_DIR)/bin/activate && python benchmarks/ocr_claims_pdfs.py --tiers multihop mixed --ocr-engine $(OCR_ENGINE) --model $(OCR_MODEL)

eval:
	. $(VENV_DIR)/bin/activate && python benchmarks/evaluate_models.py --models $(EVAL_MODELS) --transcripts ocr --parallel-models --model-workers $(EVAL_WORKERS) --output-dir $(EVAL_OUT)

hf-export:
	. $(VENV_DIR)/bin/activate && python benchmarks/export_hf_dataset.py --input data --output $(HF_OUT) --repo-id $(HF_REPO_ID) --overwrite

paper:
	$(MAKE) -C paper pdf

paper-quick:
	$(MAKE) -C paper quick

clean:
	$(MAKE) -C paper clean
