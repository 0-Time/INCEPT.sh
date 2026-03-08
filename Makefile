PYTHON := $(shell if [ -f .venv/bin/python ]; then echo .venv/bin/python; else echo python; fi)

.PHONY: test lint format typecheck eval all train-intent train-slot train-dpo export eval-report benchmark serve repl smoke load-test

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

train-dpo:
	$(PYTHON) -c "from incept.training.config import load_config; from incept.training.dpo_trainer import run_dpo; run_dpo(load_config('configs/training_dpo.yaml'))"

benchmark:
	@echo "Run full benchmark evaluation suite"
	$(PYTHON) -c "from incept.training.benchmark import run_benchmark; r = run_benchmark('outputs/model.gguf', 'data/eval'); print(r.model_dump_json(indent=2))"

eval-report:
	@echo "Run evaluation and generate baseline report"
	$(PYTHON) -c "from incept.eval.report import BaselineReport, save_report; save_report(BaselineReport(), 'outputs/reports')"

serve:
	$(PYTHON) -m incept serve

repl:
	$(PYTHON) -m incept

smoke:
	bash scripts/smoke_test.sh

	docker run -p 8080:8080 incept

load-test:
	$(PYTHON) -m locust -f scripts/load_test.py --headless -u 5 -r 1 -t 60s
