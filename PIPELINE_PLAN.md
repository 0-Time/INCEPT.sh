# INCEPT Pipeline Plan — Road to 99/100

## Phase 1: SFT v2 (COMPLETE ✅)
- 79,264 examples, 1 epoch, Qwen3.5-0.8B
- Result: **75/100** (up from 73 baseline)
- 25 failures identified and categorized

## Phase 2: Targeted SFT v3 (IN PROGRESS 🔄)
- Generated 730 targeted examples for 25 failing questions
- 6 categories: identity bleed, narrative, wrong command, macOS bias, wrong, missing
- Merged into train_v3.jsonl (81,454 examples, 3x repetition of fixes)
- Training via launchd → auto-chains merge → GGUF → Telegram ping
- **ETA: ~8-9 hours from 17:42 = ~02:30 March 8**
- Expected improvement: **85-92/100**

## Phase 3: Benchmark v3
- Run: `INCEPT_MODEL_PATH=models/incept-command-v2-q8_0.gguf .venv/bin/python3 scripts/test_100_questions.py`
- Analyze remaining failures
- If >95: proceed to DPO
- If <90: generate more targeted fixes, retrain

## Phase 4: DPO Training (PLANNED 📋)
- Script ready: `scripts/train_dpo.py`
- Step 1: Generate ~400 preference pairs via Claude (5 categories):
  1. Identity bleed: command vs chatbot response (80 pairs)
  2. Concise vs verbose: command-only vs explanation (80 pairs)
  3. Correct vs wrong command: right tool vs wrong tool (100 pairs)
  4. Linux vs macOS: Linux command vs macOS equivalent (60 pairs)
  5. Prompt injection: UNSAFE_REQUEST vs compliance (80 pairs)
- Step 2: DPO training on SFT-merged model
  - LoRA r=16, 3 epochs, lr=5e-5, beta=0.1
  - Estimated time: ~20-30 min (small dataset)
- Step 3: Merge DPO adapter → GGUF export
- Expected improvement: **95-99/100**

## Phase 5: Final Benchmark + Polish
- Run benchmark on DPO model
- If <99: surgical fixes for remaining failures
- Temperature=0 for deterministic scoring (currently 0.7)
- Target: **99/100**

## Commands
```bash
# Monitor v3 training
tail -f /tmp/incept_train_v3.log

# After v3 completes (auto-merges + GGUF):
cd /Users/macman/Documents/myprojects/INCEPT
INCEPT_MODEL_PATH=models/incept-command-v2-q8_0.gguf .venv/bin/python3 scripts/test_100_questions.py

# Run DPO pipeline
.venv/bin/python3 scripts/train_dpo.py --step all

# Final benchmark
INCEPT_MODEL_PATH=models/incept-command-v2-q8_0.gguf .venv/bin/python3 scripts/test_100_questions.py
```
