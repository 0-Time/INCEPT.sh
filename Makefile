PYTHON := .venv/bin/python

.PHONY: test lint format typecheck eval all train-intent train-slot export eval-report

all: lint typecheck test

test:
	$(PYTHON) -m pytest tests/ -v --cov=incept --cov-report=term-missing

lint:
	$(PYTHON) -m ruff check incept/ tests/

format:
	$(PYTHON) -m ruff format incept/ tests/
	$(PYTHON) -m ruff check --fix incept/ tests/

typecheck:
	$(PYTHON) -m mypy incept/

eval:
	$(PYTHON) -m pytest tests/test_golden.py -v

train-intent:
	$(PYTHON) -c "from incept.training.config import load_config; from incept.training.sft_trainer import run_sft; run_sft(load_config('configs/training_intent.yaml'))"

train-slot:
	$(PYTHON) -c "from incept.training.config import load_config; from incept.training.sft_trainer import run_sft; run_sft(load_config('configs/training_slot.yaml'))"

export:
	@echo "Usage: make export BASE=path/to/base ADAPTER=path/to/adapter OUTPUT=path/to/output"
	$(PYTHON) -c "from incept.training.export import merge_lora_adapter; merge_lora_adapter('$(BASE)', '$(ADAPTER)', '$(OUTPUT)')"

eval-report:
	@echo "Run evaluation and generate baseline report"
	$(PYTHON) -c "from incept.eval.report import BaselineReport, save_report; save_report(BaselineReport(), 'outputs/reports')"
