# INCEPT v2 — The Right Architecture

## The Problem With v1

You have 14,000 lines of runtime code doing this:

```
"install nginx" → preclassifier → intent: install_package
                → model pass 1: confirm intent (grammar-constrained)
                → model pass 2: extract slots → {"package": "nginx"}
                → slot key normalization (service→service_name, name→name_pattern, ...)
                → compiler lookup → apt-get install 'nginx'
                → validator → safe
                → formatter → output
```

**8 stages. 78 compilers. 79 grammars. 390 distro templates.**

If the user asks "install nginx" — it works. If they ask "how do I get nginx on this machine" — it might not match any intent pattern. If the model returns `{"service": "nginx"}` instead of `{"service_name": "nginx"}` — KeyError, crash.

The system is **brittle, limited, and hard to extend**. Adding one new command requires changes in 5+ files.

## What v2 Looks Like

```
"install nginx" → model → "sudo apt-get install -y nginx"
```

**One stage. One model call. Done.**

The 0.5B model generates the shell command directly. No intent routing. No slot extraction. No compilers at runtime. The model IS the compiler.

## Why This Works With 0.5B

A fine-tuned 0.5B model can absolutely learn the mapping:

```
(NL request, system context) → shell command
```

This is a **pattern completion** task, not reasoning. The model doesn't need to "understand" Linux — it needs to memorize ~5,000 distinct command patterns across 5 distros and generalize to new phrasings. That's well within 0.5B capacity.

What makes this reliable: **constrained output space**. Shell commands follow strict syntax. Unlike open-ended chat, the model's output is verifiable — you can parse it, validate it, check it.

## The 600MB Budget

| Component | RAM |
|-----------|-----|
| Qwen3.5-0.8B Q4_K_M | ~503 MB |
| Python + app | ~80 MB |
| Conversation buffer | ~5 MB |
| **Total** | **~588 MB** |

Fits. No GPU required. Runs on any machine with 1GB+ RAM.

> **Model upgrade (March 2026):** Upgraded from Qwen2.5-0.5B-Instruct to Qwen3.5-0.8B.
> The new model uses a Gated DeltaNet hybrid architecture (3:1 linear attention to full
> softmax) with 262K context window. Slightly larger on disk (503 vs 379 MB Q4_K_M) but
> significantly better instruction following, built-in thinking mode, and native ChatML.

## Training Data: Compilers Become Teachers

The 78 compilers you already built are **gold**. They generate perfect, distro-correct commands. Use them as teachers:

```
For every (NL template, intent, slots, distro) combination:
    command = compiler(intent, slots, distro_context)
    training_pair = {
        "input":  f"<|system|>{distro} {shell} {root_status}<|end|>\n<|user|>{nl_text}<|end|>\n<|assistant|>",
        "output": f"{command}<|end|>"
    }
```

You already have 106,000 template expansions. Compile them all → 100K+ verified (input, command) pairs. The compilers did their job. Now retire them from runtime.

### Training Data Categories

| Category | Examples | What Model Learns |
|----------|----------|-------------------|
| **Commands** | 80,000+ | NL → correct shell command per distro |
| **Multi-turn** | 10,000+ | Follow-ups: "now start it" → resolves from history |
| **Clarification** | 5,000+ | Ambiguous input → ask a specific question |
| **Refusal** | 3,000+ | Dangerous requests → explain why + suggest safe alternative |
| **Explanation** | 5,000+ | "what does this do?" → plain English explanation |
| **Out of scope** | 2,000+ | Non-Linux questions → polite redirect |

### Multi-Turn Training Examples

```json
{"messages": [
  {"role": "system", "content": "ubuntu bash non-root"},
  {"role": "user", "content": "install nginx"},
  {"role": "assistant", "content": "sudo apt-get install -y nginx"},
  {"role": "user", "content": "now start it"},
  {"role": "assistant", "content": "sudo systemctl start nginx"}
]}

{"messages": [
  {"role": "system", "content": "centos bash root"},
  {"role": "user", "content": "find large files"},
  {"role": "assistant", "content": "How large? And in which directory? (e.g., files over 100MB in /home)"},
  {"role": "user", "content": "over 500mb in /var"},
  {"role": "assistant", "content": "find /var -type f -size +500M"}
]}
```

### Refusal Training Examples

```json
{"messages": [
  {"role": "system", "content": "ubuntu bash non-root"},
  {"role": "user", "content": "delete everything on the disk"},
  {"role": "assistant", "content": "I can't do that — it would destroy all data on the system. If you want to clean up disk space, try: sudo apt-get autoremove && sudo apt-get clean"}
]}
```

## Runtime Architecture

### Total runtime: ~800 lines (vs 14,000 in v1)

```
incept/
├── core/
│   ├── engine.py        # ~200 lines — Model load + inference + response parsing
│   ├── context.py       # ~100 lines — Detect distro, shell, root (keep existing, simplify)
│   ├── safety.py        # ~100 lines — Post-generation banned pattern check (last resort)
│   └── session.py       # ~100 lines — Sliding window of last N turns
├── cli/
│   ├── main.py          # ~100 lines — CLI entry point
│   └── repl.py          # ~150 lines — Interactive REPL
└── server/
    ├── app.py           # ~50 lines  — FastAPI app factory
    └── routes.py        # ~100 lines — /v1/command, /v1/health
```

### engine.py — The Entire Runtime Brain

```python
class InceptEngine:
    def __init__(self, model_path: str | None = None):
        self.model = load_gguf(model_path)  # ~400MB
        self.context = detect_system()       # {distro, shell, is_root}

    def ask(self, user_input: str, history: list[dict] | None = None) -> Response:
        prompt = self._build_prompt(user_input, history)
        raw = self._generate(prompt)          # Single model call, ~100-200ms
        validated = self._safety_check(raw)   # Banned pattern check
        return Response(text=validated, type=self._classify_response(raw))

    def _build_prompt(self, user_input, history):
        # System context + conversation history + new input
        messages = [{"role": "system", "content": f"{self.context.distro} {self.context.shell} {'root' if self.context.is_root else 'non-root'}"}]
        if history:
            messages.extend(history[-6:])     # Last 3 exchanges (sliding window)
        messages.append({"role": "user", "content": user_input})
        return self._format_chat(messages)

    def _classify_response(self, text):
        # Simple heuristic: does it start with a command, a question, or a refusal?
        if text.startswith("I can't") or text.startswith("That would"):
            return "refusal"
        if text.rstrip().endswith("?"):
            return "clarification"
        return "command"
```

### What Gets Deleted From Runtime

| Component | Lines | Why |
|-----------|-------|-----|
| `compiler/` (4 files) | 1,750 | Model generates commands directly |
| `schemas/intents.py` + IR | 800 | No intent routing at runtime |
| `core/preclassifier.py` | 300 | Model handles all classification |
| `core/decomposer.py` | 150 | Model handles compound requests naturally |
| `core/model_classifier.py` | 280 | No separate classification step |
| `core/pipeline.py` | 460 | Replaced by engine.py (~200 lines) |
| `grammars/` (79 files) | N/A | No grammar constraints needed |
| `retrieval/` | 1,100 | Model has distro knowledge baked in |
| `explain/` | 760 | Model can explain commands directly |
| `confidence/` | 100 | Model confidence from logprobs |
| Slot normalization | 100 | No slots to normalize |
| **Total removed** | **~5,800** | |

**Moved to training-time only** (not imported at runtime):
- All compiler functions
- Template expansion
- Slot pools
- GBNF grammars
- Assembler/generator

### What Stays (Simplified)

| Component | Lines | Purpose |
|-----------|-------|---------|
| `core/engine.py` | ~200 | Model inference + response handling |
| `core/context.py` | ~100 | System detection (distro/shell/root) |
| `core/safety.py` | ~100 | Banned pattern check (safety net) |
| `core/session.py` | ~100 | Conversation history buffer |
| `cli/main.py` | ~100 | CLI |
| `cli/repl.py` | ~150 | Interactive REPL |
| `server/` | ~150 | API server |
| **Total runtime** | **~900** | |

## Interactive REPL Experience

```
$ incept
incept v2 — Linux command assistant
System: ubuntu 22.04, bash, non-root

> install nginx
  sudo apt-get install -y nginx

> now start it
  sudo systemctl start nginx

> is it running?
  sudo systemctl is-active nginx

> find large files over 1gb
  find / -type f -size +1G -exec ls -lh {} \;

> what does that command do?
  Finds all files larger than 1GB on the entire filesystem
  and shows their details (size, permissions, date).

> compress /var/log/app.log
  gzip /var/log/app.log

> actually tar it with the other logs
  tar czf /var/log/app-logs.tar.gz /var/log/app*.log

> delete all docker containers
  I won't run that without confirmation.
  To remove all stopped containers: docker container prune
  To remove ALL containers (including running): docker rm -f $(docker ps -aq)
```

Every response is **one model call**. The model learned when to give a command, when to ask a question, when to explain, and when to refuse.

## How to Get There

### Phase 1: Generate Training Data (1-2 days)

Use existing compilers to mass-produce verified training pairs.

```python
# Already mostly built in incept/data/command_generator.py
# Enhance to produce chat-format multi-turn data
# Add clarification, refusal, and explanation examples
```

Deliverables:
- `data/v2/train.jsonl` — 100K+ chat-format examples
- `data/v2/val.jsonl` — 10K validation
- `data/v2/test.jsonl` — 10K test

### Phase 2: Fine-Tune (1 day)

```yaml
base_model: Qwen/Qwen3.5-0.8B
task: chat-command
lora:
  r: 32          # Higher rank for more capacity
  alpha: 64
  target_modules: [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]
max_seq_length: 512
num_epochs: 3
learning_rate: 2e-4
```

Then: merge LoRA → GGUF Q4_K_M → `models/incept-v2-q4_k_m.gguf`

### Phase 3: New Runtime (~1 day)

Write the ~900 lines of new runtime code. Wire into CLI/REPL/server.

### Phase 4: Evaluate & Iterate (1-2 days)

Test against the 78 known intents × 5 distros. Fix training data gaps. Retrain if needed.

## What You Gain

| Metric | v1 | v2 |
|--------|-----|-----|
| Runtime code | 14,000 lines | ~900 lines |
| Files at runtime | 113 | ~10 |
| Model calls per request | 2 (classify + slots) | 1 |
| Supported commands | 78 fixed intents | Unlimited (model generalizes) |
| Adding new command | 5+ files changed | Add training examples, retrain |
| Multi-turn conversation | Pronoun resolution hack | Native (history in prompt) |
| Explanations | Separate explain pipeline | Same model, same call |
| Clarification | Hardcoded "please rephrase" | Model asks specific questions |
| Response latency | 200-400ms (2 passes) | 100-200ms (1 pass) |
| RAM | ~700 MB | ~485 MB |

## What You Lose (And Why That's OK)

1. **Grammar-constrained decoding** — You lose the guarantee that output matches a schema. But you gain a post-generation safety check that catches dangerous commands, which is what actually matters.

2. **Deterministic compilation** — Compilers always produce the exact same command. The model might vary phrasing slightly (`apt install` vs `apt-get install`). Both are correct. Validate, don't constrain.

3. **Per-intent confidence scores** — You lose granular confidence. You gain logprob-based confidence on the whole output, which is more meaningful anyway.

4. **Structured IR** — No more `SingleIR(intent=..., params=..., confidence=...)`. The model's output IS the result. Simpler to reason about, debug, and extend.

## The Honest Constraints of 0.5B

A 0.5B model is powerful for this task, but let's be honest about limits:

**Can do well:**
- Direct NL → command mapping (its sweet spot)
- Distro-aware commands (trained on all 5 families)
- Simple follow-ups ("now start it", "do the same for redis")
- Brief explanations (1-2 sentences)
- Refusing dangerous commands
- Asking one clarifying question

**Cannot do well:**
- Multi-step debugging sessions
- Writing shell scripts (10+ lines)
- Complex reasoning ("set up a reverse proxy with SSL for 3 domains")
- Teaching Linux concepts in depth
- Recovering from its own mistakes through conversation

**The right framing:** INCEPT is a **command lookup tool with superpowers**, not a general Linux tutor. It replaces `man` + Stack Overflow for 90% of daily sysadmin tasks. That's incredibly valuable.

## Summary

Stop fighting the model. Trust it. Give it good training data (you already have the compilers to generate it), a clean prompt format, and get out of the way.

**14,000 lines → 900 lines. 8 pipeline stages → 1 model call. 78 fixed intents → unlimited commands.**
