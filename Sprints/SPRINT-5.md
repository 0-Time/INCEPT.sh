# Sprint 5: Model Hardening & Integration

**Duration:** Weeks 9-10
**Phase:** Phase 3 (completion) + Phase 4 (start)
**Sprint Goal:** Run DPO and adversarial hardening, quantize the final model, integrate the model into the pipeline replacing the hard-coded classifier, and achieve MVP accuracy targets.

---

## Sprint Backlog

### Story 5.1 — DPO Preference Tuning
**Points:** 8
**Priority:** P0 — Critical

**As a** ML engineer,
**I want** preference-tuned adapters that resolve the model's worst confusion pairs,
**So that** intent accuracy and slot filling reach MVP targets.

**Acceptance Criteria:**
- [ ] DPO training on ≥1,000 preference pairs (from Sprint 3)
- [ ] Focus areas based on Sprint 4 confusion matrix:
  - Near-miss intent pairs (`find_files` vs `search_text`, `install_package` vs `search_package`, etc.)
  - Distro-correct vs distro-wrong slot fills
  - `CLARIFY` vs guessing when info is missing
- [ ] Separate DPO runs for intent adapter and slot adapter
- [ ] DPO hyperparameters: `beta=0.1`, `lr=5e-5`, 2 epochs
- [ ] Intent accuracy improvement: **+3-5%** over SFT baseline
- [ ] Slot F1 improvement: **+2-4%** over SFT baseline
- [ ] No regression on previously correct examples (check on golden set)

**Tasks:**
- [ ] Prepare DPO preference pairs from confusion matrix analysis
- [ ] Add additional DPO pairs for worst-performing intents
- [ ] Run DPO on intent adapter
- [ ] Run DPO on slot adapter
- [ ] Evaluate both adapters on validation set
- [ ] Evaluate on golden test set
- [ ] Compare with SFT baseline — verify improvement, no regressions
- [ ] Select best checkpoint per adapter

---

### Story 5.2 — Adversarial Hardening
**Points:** 5
**Priority:** P0 — Critical

**As a** safety engineer,
**I want** the model hardened against prompt injection and adversarial inputs,
**So that** safety compliance remains at 100%.

**Acceptance Criteria:**
- [ ] Fine-tune on adversarial subset (≥3,000 examples from Sprint 3)
- [ ] Prompt injection → `UNSAFE_REQUEST` (100% required)
- [ ] Social engineering → `UNSAFE_REQUEST` (100% required)
- [ ] Out-of-scope → `OUT_OF_SCOPE` (≥90%)
- [ ] Ambiguous → `CLARIFY` (≥85%)
- [ ] No regression on normal intent classification (≤1% drop allowed)
- [ ] All 15 safety canary tests pass
- [ ] Additional adversarial test set (50 hand-crafted examples not in training) — 100% pass

**Tasks:**
- [ ] Prepare adversarial training data in instruction format
- [ ] Run adversarial fine-tuning (additional SFT on adversarial data)
- [ ] Evaluate on safety canary suite
- [ ] Evaluate on held-out adversarial test set
- [ ] Verify no regression on normal intents
- [ ] Document safety compliance results

---

### Story 5.3 — Final Quantization & Benchmarking
**Points:** 5
**Priority:** P0 — Critical

**As a** deployment engineer,
**I want** the final model quantized to INT4 GGUF with verified accuracy,
**So that** it runs within the 250MB / 2GB RAM target on commodity hardware.

**Acceptance Criteria:**
- [ ] Merge all LoRA adapters (SFT + DPO + adversarial) with base model
- [ ] Export to GGUF: FP16, Q8_0, Q4_K_M, Q4_0
- [ ] Benchmark each quantization level on golden test set:
  - Intent accuracy
  - Slot exact match
  - Slot F1
  - Safety canary pass rate
- [ ] Accuracy drop from FP16 → Q4_K_M must be **<2%**
- [ ] If >2% drop, use Q8_0 instead
- [ ] Latency benchmarks on target hardware (or representative):
  - CPU (Apple Silicon or x86)
  - GPU (if available)
- [ ] Final model file size confirmed: ~250MB for Q4_K_M
- [ ] Constrained decoding verified with quantized model

**Tasks:**
- [ ] Merge all LoRA adapters
- [ ] Convert to GGUF (4 quantization levels)
- [ ] Run full golden test evaluation per quantization level
- [ ] Run safety canary suite per quantization level
- [ ] Run latency benchmarks
- [ ] Select final quantization level
- [ ] Run constrained decoding verification on final model
- [ ] Document benchmark results

---

### Story 5.4 — Model Integration into Pipeline
**Points:** 8
**Priority:** P0 — Critical

**As a** developer,
**I want** the trained model replacing the hard-coded classifier in the pipeline,
**So that** the system handles any natural language input, not just regex-matched patterns.

**Acceptance Criteria:**
- [ ] `ModelClassifier` class wraps `llama-cpp-python` with GBNF grammar loading
- [ ] Two-pass inference: intent classification → slot filling (separate adapters or single model)
- [ ] Grammar auto-selection: after intent classification, load the correct slot grammar
- [ ] Logprob extraction for confidence scoring
- [ ] Fallback behavior: if model confidence < 0.5, fall back to pre-classifier or ask CLARIFY
- [ ] Pipeline seamlessly switches between hard-coded and model classifier (config flag)
- [ ] End-to-end accuracy on golden test set: **≥82%** command match
- [ ] Execution success rate: **≥88%** (in container tests)
- [ ] P95 latency < 2s on CPU

**Tasks:**
- [ ] Implement `ModelClassifier` class
- [ ] Implement grammar auto-selection based on classified intent
- [ ] Implement logprob extraction and confidence scoring integration
- [ ] Implement fallback to pre-classifier
- [ ] Wire into pipeline orchestrator (replace hard-coded classifier)
- [ ] Add config flag for classifier switching
- [ ] Run full end-to-end evaluation
- [ ] Run container execution tests
- [ ] Run latency benchmarks
- [ ] Compare: hard-coded vs model-based pipeline results

---

### Story 5.5 — Component-Level Evaluation Automation
**Points:** 3
**Priority:** P1 — High

**As a** ML engineer,
**I want** automated evaluation scripts for each pipeline component,
**So that** regressions are caught immediately on any change.

**Acceptance Criteria:**
- [ ] `eval/run_intent_eval.py` — intent accuracy with configurable threshold
- [ ] `eval/run_slot_eval.py` — slot exact match and F1 with threshold
- [ ] `eval/run_compiler_eval.py` — compiler correctness with threshold
- [ ] `eval/run_safety_eval.py` — safety canary with 100% hard gate
- [ ] `eval/run_e2e_eval.py` — end-to-end command match with distro flag
- [ ] All scripts exit with non-zero code if threshold not met
- [ ] **Local CI:** `make eval` runs all evaluations locally without internet
- [ ] **Optional remote CI:** GitHub Actions workflow wraps `make eval` (for teams using GitHub)
- [ ] Results logged to local MLflow/TensorBoard (no cloud tracking)

**Tasks:**
- [ ] Implement 5 evaluation scripts
- [ ] Add threshold arguments and exit codes
- [ ] Create `Makefile` targets: `make eval-intent`, `make eval-slot`, `make eval-compiler`, `make eval-safety`, `make eval-e2e`, `make eval` (all)
- [ ] Optional: Create CI workflow (`.github/workflows/eval.yml`) wrapping `make eval`
- [ ] Integrate with local experiment tracking (MLflow file backend)

---

## Sprint Metrics

| Metric | Target (Post-DPO, Post-Quantization) |
|--------|---------------------------------------|
| Total Story Points | 29 |
| Intent accuracy (golden) | **≥93%** |
| Slot exact match (golden) | **≥85%** |
| Slot F1 (golden) | **≥88%** |
| E2E command match (golden) | **≥82%** |
| Execution success rate | **≥88%** |
| Safety canary pass rate | **100%** |
| Out-of-scope detection | **≥82%** |
| P95 latency (CPU) | **< 2s** |
| Quantized model size | **~250MB** |

## Dependencies
- Sprint 4 SFT adapters and baseline metrics
- Sprint 3 DPO pairs and adversarial data
- Sprint 2 pipeline orchestrator

## Risks
- DPO may cause regression on previously correct examples — monitor golden set per DPO batch
- Adversarial hardening may make model too conservative (over-triggering CLARIFY) — tune threshold
- Quantization + constrained decoding interaction may cause unexpected behavior — test thoroughly
