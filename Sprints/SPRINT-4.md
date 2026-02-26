# Sprint 4: Model Training (SFT)

**Duration:** Weeks 7-8
**Phase:** Phase 3 — Model Training
**Sprint Goal:** Fine-tune Qwen2.5-0.5B-Instruct with QLoRA for intent classification and slot filling, establish baseline metrics, and verify constrained decoding works with the fine-tuned model.

---

## Sprint Backlog

### Story 4.1 — Training Infrastructure Setup
**Points:** 5
**Priority:** P0 — Critical

**As a** ML engineer,
**I want** a reproducible training environment,
**So that** model training is consistent and experiments are trackable.

**Acceptance Criteria:**
- [ ] Training environment: **local GPU with ≥4GB VRAM (primary)** or CPU-only (slower, viable for 500M model)
- [ ] Dependencies: `transformers`, `peft`, `trl`, `bitsandbytes`, `datasets`
- [ ] **Experiment tracking: local-only** — use `mlflow` with local file backend (`mlflow server --backend-store-uri ./mlruns`) or TensorBoard. **No cloud accounts required.**
- [ ] Training config YAML with all hyperparameters from spec Section 16.3
- [ ] Base model **pre-downloaded once** to local `models/` directory: `Qwen/Qwen2.5-0.5B-Instruct`
- [ ] Fallback model **pre-downloaded once**: `HuggingFaceTB/SmolLM2-360M-Instruct`
- [ ] **`HF_HUB_OFFLINE=1`** environment variable set during training to prevent any HuggingFace Hub calls after initial download
- [ ] Data loading pipeline: reads formatted JSONL → HuggingFace Dataset objects (local files only, no streaming)
- [ ] Reproducibility: fixed random seeds, deterministic data loading

**Tasks:**
- [ ] Set up local training machine (document minimum GPU specs; note CPU-only fallback)
- [ ] Install dependencies and verify GPU access
- [ ] **One-time model download:** `huggingface-cli download` both base models to local cache
- [ ] Set `HF_HUB_OFFLINE=1` and verify training works without internet
- [ ] Create training config YAML
- [ ] Set up local MLflow or TensorBoard for experiment tracking
- [ ] Implement data loading pipeline (local JSONL files only)
- [ ] Verify full training loop runs (1 batch, no crash, no network calls)

---

### Story 4.2 — Intent Classification Fine-Tuning (SFT)
**Points:** 8
**Priority:** P0 — Critical

**As a** ML engineer,
**I want** a fine-tuned LoRA adapter for intent classification,
**So that** the model accurately selects the correct intent from 55 labels.

**Acceptance Criteria:**
- [ ] QLoRA config: `r=16`, `alpha=32`, `dropout=0.05`, targeting `q_proj, k_proj, v_proj, o_proj`
- [ ] Training: `lr=2e-4`, cosine scheduler, 5 epochs, `batch_size=16`, `grad_accum=2`
- [ ] `max_seq_length=512`
- [ ] Training loss converges (decreasing trend, no divergence)
- [ ] Validation loss does not diverge from training loss by >20% (no severe overfitting)
- [ ] Save LoRA adapter checkpoint per epoch + best checkpoint by val loss
- [ ] Intent accuracy on validation set: **≥90%** (pre-DPO baseline)
- [ ] Intent accuracy on golden test set: **≥88%** (pre-DPO baseline)
- [ ] Confusion matrix generated: identify worst-performing intent pairs

**Tasks:**
- [ ] Prepare intent classification training data (instruction format)
- [ ] Configure QLoRA with specified hyperparameters
- [ ] Run SFT training (5 epochs)
- [ ] Monitor training/validation loss curves
- [ ] Save checkpoints per epoch
- [ ] Evaluate on validation set
- [ ] Evaluate on golden test set
- [ ] Generate confusion matrix
- [ ] Document baseline metrics

---

### Story 4.3 — Slot Filling Fine-Tuning (SFT)
**Points:** 8
**Priority:** P0 — Critical

**As a** ML engineer,
**I want** a fine-tuned LoRA adapter for slot filling,
**So that** the model accurately extracts parameter values in key=value format.

**Acceptance Criteria:**
- [ ] Separate LoRA adapter (not shared with intent classifier)
- [ ] Same QLoRA config as Story 4.2
- [ ] Training data includes correct intent in prompt (ground truth, not predicted)
- [ ] Training loss converges
- [ ] Slot exact match on validation set: **≥80%** (pre-DPO baseline)
- [ ] Slot F1 on validation set: **≥84%** (pre-DPO baseline)
- [ ] Per-intent slot accuracy breakdown generated
- [ ] Identify worst-performing intents for targeted DPO in Sprint 5

**Tasks:**
- [ ] Prepare slot filling training data (instruction format with intent label)
- [ ] Configure QLoRA (separate adapter)
- [ ] Run SFT training (5 epochs)
- [ ] Monitor training/validation loss curves
- [ ] Save checkpoints
- [ ] Evaluate slot exact match and F1 on validation set
- [ ] Evaluate on golden test set
- [ ] Generate per-intent accuracy breakdown
- [ ] Document baseline metrics and worst-performers

---

### Story 4.4 — Constrained Decoding Verification
**Points:** 5
**Priority:** P0 — Critical

**As a** ML engineer,
**I want** to verify that GBNF constrained decoding works with the fine-tuned model,
**So that** all model outputs are guaranteed to be structurally valid.

**Acceptance Criteria:**
- [ ] Export fine-tuned model (base + LoRA merged) to GGUF format
- [ ] Load in `llama-cpp-python` with `intent_grammar.gbnf`
- [ ] Run 100 intent classification inferences with grammar — all outputs are valid intent labels
- [ ] Load per-intent slot grammars — run 200 slot-filling inferences — all outputs are valid key=value
- [ ] Measure accuracy WITH constrained decoding vs WITHOUT — report difference
- [ ] Measure latency WITH constrained decoding vs WITHOUT — report overhead
- [ ] No grammar causes the model to enter an infinite loop or produce empty output
- [ ] Logprobs are extractable for confidence scoring

**Tasks:**
- [ ] Merge LoRA adapters with base model
- [ ] Convert to GGUF format (FP16 first, then Q4_K_M)
- [ ] Test intent grammar with 100 examples
- [ ] Test slot grammars across 10+ intents with 20 examples each
- [ ] Benchmark accuracy with/without constrained decoding
- [ ] Benchmark latency with/without constrained decoding
- [ ] Verify logprob extraction
- [ ] Document findings and any grammar adjustments needed

---

### Story 4.5 — Confidence Scoring Implementation
**Points:** 3
**Priority:** P1 — High

**As a** pipeline developer,
**I want** confidence scores derived from model logprobs,
**So that** the system can adjust its behavior based on prediction certainty.

**Acceptance Criteria:**
- [ ] `compute_confidence()` function implemented per spec Section 14.3
- [ ] Inputs: intent logprob, slot logprobs (per-slot), retrieval score, compiler fallback flag
- [ ] Output: `{intent, slots, composite, display}` with display thresholds: high/medium/low/very_low
- [ ] Calibration check: high-confidence predictions are actually correct ≥90% of the time
- [ ] Low-confidence predictions trigger verification messages
- [ ] Very-low-confidence predictions trigger clarification or refusal
- [ ] Unit tests with mocked logprobs

**Tasks:**
- [ ] Implement `compute_confidence()` function
- [ ] Implement confidence-to-behavior mapping
- [ ] Run calibration analysis on golden test set
- [ ] Adjust thresholds if calibration is off
- [ ] Write unit tests

---

### Story 4.6 — Baseline Evaluation Report
**Points:** 3
**Priority:** P1 — High

**As a** project stakeholder,
**I want** a comprehensive baseline evaluation report,
**So that** I know where the model stands before optimization and can track progress.

**Acceptance Criteria:**
- [ ] Report includes all metrics from spec Section 17.2
- [ ] Separate scores for: intent eval, slot eval, compiler eval, end-to-end eval
- [ ] Breakdown by: intent category, distro, risk tier
- [ ] Confusion matrix for intents (top 10 confused pairs highlighted)
- [ ] Per-intent slot F1 scores (worst 10 highlighted)
- [ ] Safety canary results: must be 100%
- [ ] Comparison: hard-coded classifier (Sprint 2) vs model classifier (this sprint)
- [ ] Recommendations for DPO focus areas in Sprint 5

**Tasks:**
- [ ] Run all evaluation suites
- [ ] Generate visualizations (confusion matrix, per-intent bar charts)
- [ ] Write narrative report with findings
- [ ] Identify DPO priority areas
- [ ] Archive report in project docs

---

## Sprint Metrics

| Metric | Target (Baseline, pre-DPO) |
|--------|---------------------------|
| Total Story Points | 32 |
| Intent accuracy (val) | ≥90% |
| Intent accuracy (golden) | ≥88% |
| Slot exact match (val) | ≥80% |
| Slot F1 (val) | ≥84% |
| Safety canary pass rate | 100% |
| Constrained decoding validity | 100% (all outputs structurally valid) |
| Model export successful | GGUF Q4_K_M generated |

## Dependencies
- Sprint 3 training dataset (≥15,000 examples)
- Sprint 1 GBNF grammars
- GPU access for training

## Risks
- Slot filling accuracy may be below target at 500M — if <75%, consider encoder+decoder split (Risk R1)
- GGUF conversion may require model architecture adjustments
- Constrained decoding may slow inference beyond latency targets — monitor closely
