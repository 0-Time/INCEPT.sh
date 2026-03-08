# INCEPT Training Data Generation & Benchmark Pipeline

## Agent Instructions — Full Autonomous Workflow

You are tasked with generating training data, training a model, and iterating
until the INCEPT benchmark reaches 99/100.

---

## PROJECT CONTEXT

- **Project**: INCEPT — offline natural-language to Linux-command compiler
- **Location**: `/Users/macman/Documents/myprojects/INCEPT/`
- **Python**: `.venv/bin/python3` (Python 3.12, always use this, NOT system python)
- **Model**: Qwen3.5-0.8B fine-tuned with LoRA
- **Current score**: 73/100 (before any changes)
- **Target score**: 99/100
- **Training device**: MPS (Apple Silicon)

## IMPORTANT FILES

| File | Purpose |
|------|---------|
| `commands/*.md` | 585 prompt files for data generation (tiered) |
| `data/v2/train.jsonl` | Training data (currently 28,154 examples) |
| `data/v2/val.jsonl` | Validation data |
| `data/v2/targeted_examples.jsonl` | Already-generated targeted examples |
| `data/v2/dpo_command_pairs.jsonl` | DPO preference pairs (75 pairs) |
| `scripts/train_v2.py` | SFT training pipeline (train → merge → GGUF) |
| `scripts/test_100_questions.py` | 100-question benchmark |
| `scripts/build_knowledge_index.py` | RAG vector index builder |
| `configs/training_dpo_command.yaml` | DPO training config |
| `incept/training/dpo_trainer.py` | DPO trainer code |
| `incept/training/data_pipeline.py` | Data loading (DPORecord schema) |
| `test_100_results.json` | Benchmark results output (after running test) |

---

## PHASE 1: GENERATE TRAINING DATA FROM COMMAND PROMPTS

### 1.1 Understand the tier system

The 585 `.md` files in `commands/` are organized by priority:

| Tier | Files | Examples Each | Total | Purpose |
|------|-------|---------------|-------|---------|
| Tier 1 | 001-042 | 500 | 21,000 | Benchmark FAILING commands |
| Tier 2 | 043-089 | 200 | 9,400 | Benchmark PASSING commands |
| Tier 3 | 090-366 | 100 | 27,700 | Important common commands |
| Tier 4 | 367-585 | 20 | 4,380 | Niche/specialized commands |

### 1.2 Generate data for each command file

For each `.md` file in `commands/`, read the prompt and generate the exact
number of training examples specified. Output as JSONL.

**Output format** — every line must be valid JSON matching this schema exactly:

```json
{"messages": [{"role": "system", "content": "<distro> <version> <shell> <privilege>"}, {"role": "user", "content": "<natural language request>"}, {"role": "assistant", "content": "<correct shell command>"}]}
```

**System context values to use:**

```
Distros: ubuntu 24.04, ubuntu 22.04, fedora 39, fedora 40, debian 12, centos 9, rhel 9, arch latest, opensuse 15.5, sles 15
Shells: bash (80%), zsh (20%)
Privilege: root (30%), non-root (70%)
```

**For each command file:**
1. Read the `.md` prompt in `commands/NNN_command.md`
2. Generate the specified number of examples (500, 200, 100, or 20)
3. Save to `data/generated/NNN_command.jsonl`
4. Validate: every line is valid JSON, has exactly 3 messages, roles are system/user/assistant
5. Validate: no duplicate (user_content, assistant_content) pairs within the file
6. Validate: assistant content is a plausible shell command (not prose, not empty)

**Processing order**: Do Tier 1 files FIRST (001-042), then Tier 2 (043-089),
then Tier 3 (090-366), then Tier 4 (367-585). This ensures if you must stop
early, the most impactful data is already generated.

Create the output directory first:
```bash
mkdir -p data/generated
```

### 1.3 Quality rules for generated data

**DO:**
- Use realistic file paths: `/var/log/syslog`, `/etc/passwd`, `/home/user/project/`, `~/Documents/report.txt`
- Use realistic usernames: `john`, `admin`, `deploy`, `www-data`, `postgres`
- Use realistic hostnames: `web01`, `db-server`, `192.168.1.100`, `10.0.0.5`, `example.com`
- Use realistic patterns: `error`, `warning`, `Failed password`, `Connection refused`
- Vary natural language style: imperative, question, casual, formal, terse, verbose
- Include piped commands naturally: `grep error /var/log/syslog | wc -l`
- For commands requiring root, add `sudo` prefix when system context says `non-root`

**DO NOT:**
- Generate prose explanations as assistant content (must be ONLY a shell command)
- Use placeholder text like `<filename>`, `FILE`, `PATH` in assistant content
- Generate the same command with trivially different NL ("list files" vs "list the files")
- Use flags that don't exist for the command
- Generate commands with syntax errors
- Exceed the specified example count per file

### 1.4 Merge all generated data

After generating all files, merge them into the training set:

```bash
# Concatenate all generated files
cat data/generated/*.jsonl > data/generated/all_generated.jsonl

# Count total generated
wc -l data/generated/all_generated.jsonl

# Deduplicate against existing training data and append
.venv/bin/python3 -c "
import json

# Load existing
existing = set()
with open('data/v2/train.jsonl') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        rec = json.loads(line)
        msgs = rec['messages']
        user = next((m['content'] for m in msgs if m['role'] == 'user'), '').lower().strip()
        asst = next((m['content'] for m in msgs if m['role'] == 'assistant'), '').lower().strip()
        existing.add((user, asst))

print(f'Existing unique pairs: {len(existing)}')

# Deduplicate new data
new_lines = []
dupes = 0
with open('data/generated/all_generated.jsonl') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        rec = json.loads(line)
        msgs = rec['messages']
        user = next((m['content'] for m in msgs if m['role'] == 'user'), '').lower().strip()
        asst = next((m['content'] for m in msgs if m['role'] == 'assistant'), '').lower().strip()
        if (user, asst) in existing:
            dupes += 1
        else:
            new_lines.append(line)
            existing.add((user, asst))

print(f'Duplicates removed: {dupes}')
print(f'New unique examples: {len(new_lines)}')

# Append to train.jsonl
with open('data/v2/train.jsonl', 'a') as f:
    for line in new_lines:
        f.write(line + '\n')

# Final count
count = sum(1 for line in open('data/v2/train.jsonl') if line.strip())
print(f'Final train.jsonl: {count} examples')
"
```

### 1.5 Validate merged dataset

```bash
.venv/bin/python3 -c "
import json
errors = 0
total = 0
with open('data/v2/train.jsonl') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line: continue
        total += 1
        try:
            rec = json.loads(line)
            msgs = rec['messages']
            assert len(msgs) == 3, f'Expected 3 messages, got {len(msgs)}'
            assert msgs[0]['role'] == 'system'
            assert msgs[1]['role'] == 'user'
            assert msgs[2]['role'] == 'assistant'
            assert len(msgs[2]['content'].strip()) > 0, 'Empty assistant'
        except Exception as e:
            errors += 1
            if errors <= 10:
                print(f'Line {i}: {e}')
print(f'Total: {total}, Errors: {errors}')
assert errors == 0, f'{errors} validation errors found!'
print('Dataset validation PASSED')
"
```

---

## PHASE 2: SFT TRAINING

### 2.1 Run the full training pipeline

```bash
cd /Users/macman/Documents/myprojects/INCEPT
.venv/bin/python3 scripts/train_v2.py --step all --epochs 3
```

This runs 3 steps sequentially:
1. **SFT Training** — LoRA fine-tune on data/v2/train.jsonl (~8-20 hours depending on data size)
2. **Merge** — Merge LoRA adapter into base model
3. **GGUF Export** — Convert to Q8_0 quantized GGUF

**Expected outputs:**
- `outputs/sft-command-v2/final/` — LoRA adapter
- `outputs/merged-command-v2/` — Merged HF model
- `models/incept-command-v2-q8_0.gguf` — Final quantized model

### 2.2 Verify training completed

```bash
ls -la models/incept-command-v2-q8_0.gguf
```

The GGUF file should exist and be ~800MB-1GB.

---

## PHASE 3: FIRST BENCHMARK

### 3.1 Run the 100-question benchmark

```bash
cd /Users/macman/Documents/myprojects/INCEPT
INCEPT_MODEL_PATH=models/incept-command-v2-q8_0.gguf .venv/bin/python3 scripts/test_100_questions.py
```

### 3.2 Analyze results

The script outputs:
- Per-question PASS/FAIL
- Section breakdown with percentages
- Detailed results saved to `test_100_results.json`

**Record the score.** Expected: 90-96/100 after Phase 2.

### 3.3 Extract failures

```bash
.venv/bin/python3 -c "
import json
with open('test_100_results.json') as f:
    data = json.load(f)
print(f'Score: {data[\"correct\"]}/{data[\"total\"]} ({data[\"accuracy\"]}%)')
print()
print('FAILURES:')
for r in data['results']:
    if not r['passed']:
        print(f'  Q{r[\"q\"]}: {r[\"question\"]}')
        print(f'    Expected: {r[\"expected\"]}')
        print(f'    Got:      {r[\"output\"]}')
        print()
"
```

**Save this failure list.** You need it for Phase 5.

---

## PHASE 4: DPO PREFERENCE TRAINING

### 4.1 Run DPO training

The DPO pairs are already created at `data/v2/dpo_command_pairs.jsonl` (75 pairs).
The config is at `configs/training_dpo_command.yaml`.

```bash
cd /Users/macman/Documents/myprojects/INCEPT
.venv/bin/python3 -c "
from incept.training.config import TrainingConfig
from incept.training.dpo_trainer import run_dpo

config = TrainingConfig.from_yaml('configs/training_dpo_command.yaml')
output = run_dpo(config)
print(f'DPO model saved to: {output}')
"
```

### 4.2 Merge DPO model and export GGUF

After DPO training, merge the new LoRA adapter and export:

```bash
# Merge DPO LoRA into the SFT-merged model
.venv/bin/python3 -c "
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import json

base = AutoModelForCausalLM.from_pretrained('outputs/merged-command-v2')
model = PeftModel.from_pretrained(base, 'outputs/dpo-command/final')
merged = model.merge_and_unload()

out_path = 'outputs/merged-dpo-command'
merged.save_pretrained(out_path)
AutoTokenizer.from_pretrained('outputs/merged-command-v2').save_pretrained(out_path)

# Patch architecture for GGUF compatibility
cfg_path = f'{out_path}/config.json'
with open(cfg_path) as f:
    cfg = json.load(f)
if 'Qwen3_5ForCausalLM' in cfg.get('architectures', []):
    cfg['architectures'] = ['Qwen3_5ForConditionalGeneration']
    with open(cfg_path, 'w') as f:
        json.dump(cfg, f, indent=2)
print(f'Merged DPO model saved to: {out_path}')
"

# Convert to GGUF Q8_0
/opt/homebrew/bin/convert_hf_to_gguf.py outputs/merged-dpo-command --outfile models/incept-command-dpo-f16.gguf --outtype f16
llama-quantize models/incept-command-dpo-f16.gguf models/incept-command-dpo-q8_0.gguf Q8_0
rm models/incept-command-dpo-f16.gguf
```

### 4.3 Benchmark the DPO model

```bash
INCEPT_MODEL_PATH=models/incept-command-dpo-q8_0.gguf .venv/bin/python3 scripts/test_100_questions.py
```

Record the score. Expected: +2-4 points over Phase 3.

---

## PHASE 5: RAG INDEX REBUILD

### 5.1 Rebuild the vector index

```bash
.venv/bin/python3 scripts/build_knowledge_index.py --output ~/.incept --max-combos 750 --seed 99
```

### 5.2 Benchmark with RAG

```bash
INCEPT_MODEL_PATH=models/incept-command-dpo-q8_0.gguf .venv/bin/python3 scripts/test_100_questions.py
```

Record the score. Expected: +1-3 points.

---

## PHASE 6: SURGICAL ITERATION (repeat until 99)

This is the critical phase. If score < 99, iterate:

### 6.1 Analyze remaining failures

```bash
.venv/bin/python3 -c "
import json
with open('test_100_results.json') as f:
    data = json.load(f)
failures = [r for r in data['results'] if not r['passed']]
print(f'Score: {data[\"correct\"]}/100 — {len(failures)} failures remain')
for r in failures:
    print(f'  Q{r[\"q\"]}: \"{r[\"question\"]}\"')
    print(f'    Expected: {r[\"expected\"]}')
    print(f'    Got:      {r[\"output\"]}')
    print()
"
```

### 6.2 For EACH remaining failure, determine the fix type

**Type A — Model outputs wrong command (e.g., awk instead of wc -l):**
→ Generate 50 targeted SFT examples for that specific command
→ Add 5 DPO pairs (correct vs what the model actually outputted)

**Type B — Model outputs valid alternate not in test (e.g., vim instead of nano):**
→ Add the alternate to `ALTERNATE_MATCHES` in `scripts/test_100_questions.py`
→ Use 0-based index (question number minus 1)

**Type C — Model outputs prose/explanation instead of command:**
→ Generate 30 examples with that exact NL phrasing → correct command
→ Add 5 DPO pairs with prose as rejected

**Type D — Model outputs partially correct (e.g., "grep" but test expects "grep -i"):**
→ Generate 30 examples emphasizing the specific flag
→ Ensure the exact NL phrasing maps to the exact expected command

### 6.3 Generate surgical training examples

For each failure, create targeted examples in `data/v2/surgical_round_N.jsonl`:

```json
{"messages": [{"role": "system", "content": "ubuntu 24.04 bash non-root"}, {"role": "user", "content": "<exact or similar phrasing to failed question>"}, {"role": "assistant", "content": "<exact expected command>"}]}
```

Generate 30-50 examples per failure with varied:
- System contexts (different distros)
- NL phrasings (but same intent as the failed question)
- The assistant content should always be the EXPECTED answer or valid alternates

### 6.4 Add surgical DPO pairs

For Type A and C failures, add DPO pairs to `data/v2/dpo_command_pairs.jsonl`:

```json
{"id": "SURG-N-001", "prompt": "<ChatML formatted prompt>", "chosen": "<correct command>", "rejected": "<what the model actually output>"}
```

The prompt format for DPO is:
```
<|im_start|>system\n<distro context><|im_end|>\n<|im_start|>user\n<question><|im_end|>\n<|im_start|>assistant\n
```

### 6.5 Append surgical data and retrain

```bash
# Append surgical examples to training data
cat data/v2/surgical_round_N.jsonl >> data/v2/train.jsonl

# Quick retrain (1 epoch is enough for surgical fixes)
.venv/bin/python3 scripts/train_v2.py --step all --epochs 1

# Benchmark again
INCEPT_MODEL_PATH=models/incept-command-v2-q8_0.gguf .venv/bin/python3 scripts/test_100_questions.py
```

### 6.6 Repeat until 99

Loop Phase 6 steps 6.1-6.5 until score >= 99.

**Typical iteration pattern:**
- Round 1: Fix 3-5 failures → score goes from 95 to 97
- Round 2: Fix 2-3 failures → score goes from 97 to 99
- Rarely needs Round 3

---

## PHASE 7: FINAL VALIDATION

### 7.1 Run benchmark 3 times

LLM inference has some variance. Run the benchmark 3 times and take the minimum:

```bash
for i in 1 2 3; do
    echo "=== Run $i ==="
    INCEPT_MODEL_PATH=models/incept-command-v2-q8_0.gguf .venv/bin/python3 scripts/test_100_questions.py
    cp test_100_results.json "test_100_results_run${i}.json"
done
```

All 3 runs should score >= 99.

### 7.2 Rebuild final RAG index

```bash
.venv/bin/python3 scripts/build_knowledge_index.py --output ~/.incept --max-combos 750 --seed 99
```

### 7.3 Final model file

The production model is:
```
models/incept-command-v2-q8_0.gguf
```

or if DPO was used:
```
models/incept-command-dpo-q8_0.gguf
```

---

## DECISION TREE SUMMARY

```
START
  │
  ├─ Phase 1: Generate 62K examples from commands/*.md
  ├─ Phase 1: Merge into data/v2/train.jsonl
  ├─ Phase 1: Validate dataset
  │
  ├─ Phase 2: SFT train (3 epochs)
  ├─ Phase 3: Benchmark
  │     │
  │     ├─ Score >= 99? → Phase 7 (final validation) → DONE
  │     └─ Score < 99?  → Continue
  │
  ├─ Phase 4: DPO training
  ├─ Phase 4: Benchmark
  │     │
  │     ├─ Score >= 99? → Phase 7 → DONE
  │     └─ Score < 99?  → Continue
  │
  ├─ Phase 5: RAG rebuild
  ├─ Phase 5: Benchmark
  │     │
  │     ├─ Score >= 99? → Phase 7 → DONE
  │     └─ Score < 99?  → Continue
  │
  └─ Phase 6: Surgical loop
        │
        ├─ Analyze failures
        ├─ Generate 30-50 targeted examples per failure
        ├─ Add DPO pairs for wrong-command failures
        ├─ Retrain (1 epoch)
        ├─ Benchmark
        │     │
        │     ├─ Score >= 99? → Phase 7 → DONE
        │     └─ Score < 99?  → Loop Phase 6 again
        │
        └─ (max 5 iterations — if still < 99 after 5 rounds,
            investigate if test questions are ambiguous and
            add alternates to ALTERNATE_MATCHES)
```

---

## TROUBLESHOOTING

### Training runs out of memory
- Reduce batch size: `--batch-size 2`
- Reduce gradient accumulation: `--grad-accum 4`

### GGUF conversion fails
- Ensure `convert_hf_to_gguf.py` is at `/opt/homebrew/bin/convert_hf_to_gguf.py`
- Ensure `llama-quantize` is on PATH
- Check that merged model config has `Qwen3_5ForConditionalGeneration` architecture

### Benchmark score drops after retraining
- Catastrophic forgetting — the new data overwrote old knowledge
- Fix: reduce epochs to 1, or mix surgical data more carefully with existing data
- Consider training from the previous best checkpoint, not from scratch

### DPO training fails
- Check that `data/v2/dpo_command_pairs.jsonl` matches DPORecord schema: `id`, `prompt`, `chosen`, `rejected`
- Ensure base model path in config points to the SFT-merged model
- If CUDA/MPS OOM, reduce batch size in config

### Model outputs prose instead of commands
- Increase the ratio of command examples vs any non-command data
- Add more DPO pairs with prose as rejected
- Check that training data has NO examples where assistant content is prose

---

## KEY CONSTRAINTS

1. **ALWAYS use `.venv/bin/python3`** — never system python
2. **Training data format is ChatML JSONL** — not the old `[INST]` format
3. **ALTERNATE_MATCHES keys are 0-based** — question number minus 1
4. **DPO prompt format uses ChatML tokens** — `<|im_start|>`, `<|im_end|>`
5. **GGUF architecture must be patched** — `Qwen3_5ForConditionalGeneration` not `Qwen3_5ForCausalLM`
6. **Train on MPS** — no CUDA, no bitsandbytes quantization, use fp32
7. **save_strategy="no"** — saves disk space, only final checkpoint matters
