# INCEPT v2 — The Definitive Blueprint

## The Vision

One model call. Type English, get the exact command for YOUR system. It remembers your corrections, knows your server's custom scripts, asks smart questions when it's unsure, and recovers from errors automatically. 500MB RAM. No internet. Runs anywhere.

---

## Architecture: Three Layers

```
                        +---------------------------+
                        |       User Interface       |
                        |   REPL / CLI / API / Ctrl+I|
                        +------------+--------------+
                                     |
                        +------------v--------------+
                        |         Engine             |
                        |   Prompt Assembly          |
                        |   + Model Inference (1x)   |
                        |   + Safety Check           |
                        |   + Confidence Score       |
                        +--+--------------------+---+
                           |                    |
              +------------v---+    +-----------v-----------+
              |  Session       |    |  Knowledge (zvec)      |
              |  Last N turns  |    |  Few-shot bank         |
              |  (in memory)   |    |  + User runbooks       |
              |                |    |  + Correction memory   |
              +----------------+    +------------------------+
```

**Runtime code: ~1,200 lines total.** (Down from 14,000.)

---

## Layer 1: The Engine (~300 lines)

The engine does ONE thing: assemble a prompt, call the model once, validate the output.

### Prompt Format (Native Qwen3.5 ChatML)

Use the model's NATIVE chat template. Stop fighting the pre-training.

```
<|im_start|>system
Linux command assistant.
System: ubuntu 22.04, bash, non-root
Packages: apt-get, snap
Tools: docker, git, python3, node

Similar examples:
- "install curl" → sudo apt-get install -y curl
- "install htop" → sudo apt-get install -y htop

Context from knowledge base:
- Web app runs on pm2, process name 'api-server'
<|im_end|>
<|im_start|>user
install nginx<|im_end|>
<|im_start|>assistant
sudo apt-get install -y nginx<|im_end|>
<|im_start|>user
now start it<|im_end|>
<|im_start|>assistant
sudo systemctl start nginx<|im_end|>
<|im_start|>user
is it running?<|im_end|>
<|im_start|>assistant
```

The model generates: `sudo systemctl is-active nginx`

Everything is in ONE prompt:
- **System context** (distro, shell, root, installed tools)
- **Few-shot examples** (retrieved from zvec, most similar to current query)
- **User knowledge** (retrieved from zvec, runbooks/scripts)
- **Conversation history** (last 3 exchanges)
- **Current query**

One model call. One generation. Done.

### Token Budget (max_seq_length = 1024)

| Section | Tokens | Notes |
|---------|--------|-------|
| System context | 40-60 | Distro, shell, tools |
| Few-shot examples (3) | 60-120 | Short: "query" → command |
| Knowledge chunks (2) | 40-100 | Only if relevant docs exist |
| History (3 turns) | 90-180 | 3 user+assistant pairs |
| Current query | 10-40 | User's input |
| **Input total** | **~240-500** | Leaves room for output |
| Model output | 30-100 | Command + optional note |
| **Total** | **~300-600** | Well within 1024 |

### Response Types (All From Same Model)

The model learns FIVE response types during training:

**1. Direct command** (most common)
```
user: install nginx
assistant: sudo apt-get install -y nginx
```

**2. Command + brief note** (when context matters)
```
user: find large files
assistant: find / -type f -size +100M -exec ls -lh {} +
Note: searches entire filesystem, may take a while. Add a path to narrow: find /home -type f -size +100M
```

**3. Clarification** (when ambiguous)
```
user: delete the logs
assistant: Which logs? For example:
- System logs: sudo journalctl --vacuum-size=500M
- Nginx logs: sudo truncate -s 0 /var/log/nginx/*.log
- All logs older than 7 days: sudo find /var/log -name '*.log' -mtime +7 -delete
```

**4. Refusal + safe alternative** (when dangerous)
```
user: wipe the disk
assistant: I won't generate a disk wipe command — that destroys all data irreversibly.
If you want to free disk space: sudo apt-get autoremove && sudo apt-get clean
If you want to securely erase a specific file: shred -vfz -n 3 <filename>
```

**5. Explanation** (when asked about a command)
```
user: what does tar -xzf archive.tar.gz do?
assistant: Extracts a gzip-compressed tar archive:
  -x = extract files
  -z = decompress gzip
  -f = read from file 'archive.tar.gz'
Files will be extracted to the current directory.
```

### Confidence Scoring (Zero-Cost)

After generation, compute mean log-probability of output tokens:

```python
logprob = mean(token_logprobs)

if logprob > -0.3:    # High confidence
    display(command)
elif logprob > -1.0:  # Medium confidence
    display(command, note="verify before running")
else:                  # Low confidence
    display(command, note="I'm not sure about this — check man page")
```

**No extra inference. No extra model. Just math on existing logprobs.**

The user sees:
```
> install nginx
  sudo apt-get install -y nginx

> configure nginx reverse proxy for port 3000 with websocket support
  sudo nano /etc/nginx/sites-available/default
  # ... (model less sure about exact config)
  ⚠ Verify: I'm less confident about this one. Check: man nginx
```

Honesty builds trust.

### Post-Generation Safety (Last Resort)

The model is trained to refuse dangerous requests. But as a safety net, fast regex scan on output:

```python
BANNED = [
    r"rm\s+-[rf]*\s+/\s",           # rm -rf /
    r"dd\s+.*of=/dev/[sh]d",         # dd to raw disk
    r"mkfs\s+.*?/dev/[sh]d",         # format disk
    r":\(\)\s*\{\s*:\|:\s*&\s*\}",   # fork bomb
    r"chmod\s+-R\s+777\s+/\s",       # chmod 777 /
    r">\s*/dev/[sh]d",               # redirect to disk
]
```

~20 patterns. 50 microseconds. Catches catastrophic commands the model might hallucinate.

---

## Layer 2: Knowledge Store (zvec + TF-IDF, ~200 lines)

### No Embedding Model. Zero Extra RAM for Embeddings.

Use **TF-IDF sparse vectors** instead of neural embeddings:
- scikit-learn's `TfidfVectorizer` — deterministic, fast, tiny
- Vocabulary for Linux commands is small (~5,000 terms)
- TF-IDF RAM: ~15MB
- zvec index RAM: ~10-20MB for 100K docs

### Three Collections in One zvec Database

```python
# ~/.incept/incept.zvec

Collection 1: "examples"     # 100K+ training examples as few-shot bank
Collection 2: "knowledge"    # User's runbooks, scripts, notes (optional)
Collection 3: "corrections"  # User corrections learned over time
```

### Collection 1: Few-Shot Bank (Always Active)

At startup, index all training examples:
```python
{"query": "install nginx", "response": "sudo apt-get install -y nginx", "distro": "debian"}
{"query": "find log files", "response": "find /var/log -name '*.log'", "distro": "debian"}
...
```

At query time:
```python
def get_examples(query: str, distro: str, top_k: int = 3) -> list[Example]:
    # TF-IDF vectorize the query
    vec = self.vectorizer.transform([query])
    # Search zvec for most similar training examples
    results = self.examples.search(vec, top_k=top_k * 2)
    # Filter to matching distro, return top_k
    return [r for r in results if r.distro == distro][:top_k]
```

**Why this is genius:** The model sees 3 examples of similar commands FOR ITS DISTRO right in the prompt. Even if the model's weights are slightly wrong, the few-shot examples correct it. It's like giving the model a cheat sheet for every question.

### Collection 2: User Knowledge (Optional)

User drops files into `~/.incept/knowledge/`:

```
~/.incept/knowledge/
├── deploy.md        → "Deploy: /opt/deploy/release.sh --env {staging|prod}"
├── services.txt     → "API runs on pm2 as 'api-server', port 3000"
└── backup-notes.md  → "Backups: /data/backups/pg_dump_*.sql.gz, daily at 2am"
```

On startup (or `incept --reindex`), these are chunked, TF-IDF vectorized, and stored in zvec.

At query time, if relevant chunks are found, they're injected into the system message:
```
Context from knowledge base:
- API runs on pm2 as 'api-server', port 3000
```

Now "restart the api" → `pm2 restart api-server`. No retraining needed.

### Collection 3: Correction Memory (The Learning Loop)

When the user corrects a command:
```
> restart the api
  sudo systemctl restart api    ← model's guess (wrong)

> actually it's: pm2 restart api-server
  Got it. I'll remember that.
```

The correction is stored in zvec:
```python
{"query": "restart the api", "correction": "pm2 restart api-server", "timestamp": ...}
```

Next time someone asks "restart the api", the correction is retrieved and shown as a few-shot example in the prompt. The model sees:

```
Similar examples:
- "restart the api" → pm2 restart api-server  [from corrections]
```

**The tool gets smarter over time WITHOUT retraining.** Every correction teaches it. This is the single most powerful feature for real-world use.

### RAM Budget

| Component | RAM |
|-----------|-----|
| Qwen3.5-0.8B Q4_K_M model | ~503 MB |
| Python runtime + app | ~50 MB |
| TF-IDF vectorizer (~5K vocab) | ~15 MB |
| zvec index (examples + knowledge) | ~20 MB |
| Session buffer | ~5 MB |
| **Total** | **~593 MB** |

Fits in 1GB. No GPU. No internet.

---

## Layer 3: Context Detection (~100 lines)

### Rich System Profile

Don't just detect "ubuntu." Detect everything useful:

```python
@dataclass
class SystemProfile:
    # Core
    distro: str          # "ubuntu"
    distro_version: str  # "22.04"
    distro_family: str   # "debian"
    kernel: str          # "5.15.0"
    arch: str            # "x86_64" or "aarch64"

    # Shell
    shell: str           # "bash"
    is_root: bool        # False

    # Available tools (detected via `which`)
    has_docker: bool
    has_git: bool
    has_systemctl: bool
    has_snap: bool
    has_flatpak: bool
    has_python3: bool
    has_node: bool
    has_brew: bool       # macOS

    # Package manager
    pkg_manager: str     # "apt-get", "dnf", "pacman", "brew"
```

**Detection runs ONCE at startup** (~200ms). Cached for the session.

The model sees: `ubuntu 22.04, bash, non-root, apt-get, docker, git, systemctl`

This is FAR richer than v1's `"debian bash non-root safe"`. The model knows what tools are available and can generate commands that actually work on THIS machine.

---

## Training Data Strategy

### Sources (Use Existing Assets)

| Source | Count | What |
|--------|-------|------|
| **Compiler-generated pairs** | ~80,000 | 78 intents × 5 distros × ~200 variations |
| **Multi-turn chains** | ~15,000 | Sequences of 2-4 related commands |
| **Explanation pairs** | ~5,000 | Command → plain English |
| **Error → recovery pairs** | ~5,000 | Common errors → fix commands |
| **Safety refusals** | ~3,000 | Dangerous request → refusal + alternative |
| **Clarification** | ~3,000 | Ambiguous → smart question |
| **Out-of-scope** | ~2,000 | Non-Linux → polite redirect |
| **Augmented (templates × slots)** | ~20,000 | Diverse phrasings |
| **Total** | **~133,000** | |

### Training Data Format (ChatML)

**Single-turn command:**
```json
{
  "messages": [
    {"role": "system", "content": "ubuntu 22.04 bash non-root apt-get docker git systemctl"},
    {"role": "user", "content": "install nginx"},
    {"role": "assistant", "content": "sudo apt-get install -y nginx"}
  ]
}
```

**Multi-turn chain:**
```json
{
  "messages": [
    {"role": "system", "content": "ubuntu 22.04 bash non-root apt-get docker git systemctl"},
    {"role": "user", "content": "install nginx"},
    {"role": "assistant", "content": "sudo apt-get install -y nginx"},
    {"role": "user", "content": "start it"},
    {"role": "assistant", "content": "sudo systemctl start nginx"},
    {"role": "user", "content": "make it start on boot"},
    {"role": "assistant", "content": "sudo systemctl enable nginx"}
  ]
}
```

**With few-shot examples in system (teaching the model to USE retrieved context):**
```json
{
  "messages": [
    {"role": "system", "content": "centos 7 bash non-root yum systemctl\n\nSimilar:\n- install httpd → sudo yum install -y httpd\n- install wget → sudo yum install -y wget"},
    {"role": "user", "content": "install redis"},
    {"role": "assistant", "content": "sudo yum install -y redis"}
  ]
}
```

**With knowledge context (teaching the model to USE retrieved knowledge):**
```json
{
  "messages": [
    {"role": "system", "content": "ubuntu 22.04 bash non-root apt-get\n\nKnowledge:\n- Web app: pm2 process 'api-server' on port 3000"},
    {"role": "user", "content": "restart the web app"},
    {"role": "assistant", "content": "pm2 restart api-server"}
  ]
}
```

**Clarification:**
```json
{
  "messages": [
    {"role": "system", "content": "ubuntu 22.04 bash non-root apt-get"},
    {"role": "user", "content": "delete the logs"},
    {"role": "assistant", "content": "Which logs do you mean?\n- System journal: sudo journalctl --vacuum-size=500M\n- Application logs in /var/log: sudo find /var/log -name '*.log' -mtime +7 -delete\n- Specific service: sudo truncate -s 0 /var/log/<service>/*.log"}
  ]
}
```

**Refusal:**
```json
{
  "messages": [
    {"role": "system", "content": "ubuntu 22.04 bash non-root apt-get"},
    {"role": "user", "content": "remove all files from the root directory"},
    {"role": "assistant", "content": "I won't do that — rm -rf / would destroy your entire system.\nTo free disk space safely: sudo apt-get autoremove && sudo apt-get clean\nTo find large files: du -sh /* | sort -rh | head -10"}
  ]
}
```

**Explanation:**
```json
{
  "messages": [
    {"role": "system", "content": "ubuntu 22.04 bash non-root apt-get"},
    {"role": "user", "content": "what does tar -xzf backup.tar.gz do?"},
    {"role": "assistant", "content": "Extracts a gzip-compressed tar archive:\n  -x = extract\n  -z = decompress gzip\n  -f = from file 'backup.tar.gz'\nFiles extracted to current directory."}
  ]
}
```

**Error recovery:**
```json
{
  "messages": [
    {"role": "system", "content": "ubuntu 22.04 bash non-root apt-get"},
    {"role": "user", "content": "install nginx"},
    {"role": "assistant", "content": "sudo apt-get install -y nginx"},
    {"role": "user", "content": "I got: E: Unable to locate package nginx"},
    {"role": "assistant", "content": "Package index is outdated. Update and retry:\nsudo apt-get update && sudo apt-get install -y nginx"}
  ]
}
```

### Data Generation Pipeline

```python
# scripts/generate_v2_data.py

Step 1: Compile all 13,704 assembled records using existing compilers
        → ~11,000 (NL, context, command) pairs

Step 2: Augment with template expansion (50K target)
        → ~50,000 additional pairs (diverse phrasings)

Step 3: Generate multi-turn chains
        - install → start → enable → status
        - create_user → modify_user (add to group)
        - find_files → view_file → delete_files
        - docker_build → docker_run → docker_logs
        → ~15,000 chain examples

Step 4: Generate explanation examples
        - For each command, generate "what does X do?" + explanation
        → ~5,000 examples

Step 5: Generate error recovery examples
        - Common error patterns → fix commands
        → ~5,000 examples

Step 6: Generate safety/refusal examples
        - Dangerous requests → refusal + safe alternative
        → ~3,000 examples

Step 7: Generate clarification examples
        - Ambiguous requests → specific question
        → ~3,000 examples

Step 8: Generate out-of-scope examples
        → ~2,000 examples

Step 9: Add few-shot-in-system-message examples (30% of all data)
        - Randomly sample 2-3 related training examples
        - Put them in the system message
        - Teaches the model to USE retrieved context
        → Augments ~40,000 existing examples with in-context shots

Step 10: Shuffle, deduplicate, split (80/10/10)
         → train.jsonl, val.jsonl, test.jsonl
```

### Training Config

```yaml
# configs/training_v2.yaml
base_model: Qwen/Qwen3.5-0.8B
task: chat-command

data:
  train_file: data/v2/train.jsonl
  val_file: data/v2/val.jsonl
  format: chatml                     # Native Qwen3.5 format

lora:
  r: 32                              # Higher rank for more capacity
  alpha: 64
  dropout: 0.05
  target_modules:
    - q_proj
    - k_proj
    - v_proj
    - o_proj
    - gate_proj                      # Include MLP layers
    - up_proj
    - down_proj

training:
  max_seq_length: 1024               # Room for context + history
  num_epochs: 3
  learning_rate: 2.0e-4
  lr_scheduler: cosine
  warmup_ratio: 0.05
  per_device_batch_size: 8
  gradient_accumulation_steps: 4     # Effective batch = 32
  weight_decay: 0.01
  bf16: true                         # If available, else fp16

quantization:
  load_in_4bit: true
  bnb_4bit_compute_dtype: bfloat16
  bnb_4bit_quant_type: nf4

export:
  merge_lora: true
  quantize: Q4_K_M
  output: models/incept-v2-q4_k_m.gguf
```

Key differences from v1:
- **LoRA r=32** (was 16): More capacity for command generation
- **All MLP layers included**: gate_proj, up_proj, down_proj
- **max_seq_length=1024** (was 512): Room for context + history + output
- **ChatML format**: Native to Qwen2.5, better alignment

---

## File Structure

```
incept/
├── core/
│   ├── engine.py          # ~300 lines — THE brain
│   │                      #   InceptEngine class
│   │                      #   build_prompt() → model inference → parse response
│   │                      #   confidence scoring from logprobs
│   │                      #   response type classification
│   │
│   ├── context.py         # ~100 lines — System detection
│   │                      #   detect_system() → SystemProfile
│   │                      #   distro, shell, root, installed tools
│   │
│   ├── safety.py          # ~80 lines — Post-generation safety net
│   │                      #   ~20 banned patterns (catastrophic commands)
│   │                      #   risk classification: safe/caution/dangerous
│   │
│   └── knowledge.py       # ~200 lines — zvec RAG layer
│                          #   TF-IDF vectorization (no embedding model)
│                          #   3 collections: examples, knowledge, corrections
│                          #   retrieve_examples(), retrieve_knowledge()
│                          #   store_correction()
│
├── cli/
│   ├── main.py            # ~120 lines — CLI entry point (click)
│   │                      #   incept "query" (one-shot)
│   │                      #   incept (interactive REPL)
│   │                      #   incept serve (API server)
│   │                      #   incept --reindex (rebuild knowledge index)
│   │                      #   incept --setup (first-time setup)
│   │
│   └── repl.py            # ~150 lines — Interactive REPL
│                          #   Conversation loop with session history
│                          #   /correct <command> — store correction
│                          #   /explain <command> — explain a command
│                          #   /knowledge add <file> — add to knowledge base
│                          #   Rich output (colors, risk indicators)
│
├── server/
│   ├── app.py             # ~50 lines — FastAPI factory
│   └── routes.py          # ~100 lines — POST /v1/ask, GET /v1/health
│
├── training/              # Training-time only (not loaded at runtime)
│   ├── data_gen.py        # ~400 lines — Generate v2 training data
│   │                      #   compile_to_pairs() — use compilers as teachers
│   │                      #   generate_chains() — multi-turn sequences
│   │                      #   generate_explanations() — command → explanation
│   │                      #   generate_refusals() — dangerous → refusal
│   │                      #   generate_clarifications() — ambiguous → question
│   │                      #   inject_few_shots() — add examples to system msg
│   │
│   ├── trainer.py         # Existing SFT trainer (modified for ChatML)
│   └── export.py          # Existing LoRA merge + GGUF export
│
├── compiler/              # Training-time only — NOT imported at runtime
│   ├── file_ops.py        # Existing (generates training data)
│   ├── text_ops.py        # Existing
│   ├── system_ops.py      # Existing
│   └── expanded_ops.py    # Existing
│
└── data/                  # Training-time only
    ├── templates.py       # Existing NL templates
    ├── slot_pools.py      # Existing slot values
    └── generator.py       # Existing example generator
```

### What Gets Deleted From the Project

These become dead code — remove from the package, keep in git history:

```
DELETED (runtime):
├── core/pipeline.py           # 460 lines → replaced by engine.py
├── core/direct_pipeline.py    # 230 lines → replaced by engine.py
├── core/preclassifier.py      # 300 lines → model handles this
├── core/decomposer.py         # 150 lines → model handles this
├── core/model_classifier.py   # 280 lines → model handles this
├── schemas/intents.py         # Still used in training, deleted from runtime imports
├── schemas/ir.py              # 200 lines → no IR at runtime
├── schemas/params/            # 800 lines → no param schemas at runtime
├── grammars/ (79 files)       # Not needed — no constrained decoding
├── retrieval/bm25.py          # 400 lines → replaced by zvec
├── retrieval/distro_maps.py   # 735 lines → baked into model
├── explain/parsers.py         # 425 lines → model explains directly
├── explain/templates.py       # 333 lines → model explains directly
├── confidence/scoring.py      # 100 lines → logprob-based
├── session/resolver.py        # 150 lines → model resolves naturally
├── templates/formatter.py     # 200 lines → simple output
├── recovery/patterns.py       # Model handles recovery
└── recovery/engine.py         # Model handles recovery
```

**~5,500 lines of runtime code deleted.**

---

## The User Experience

### First Time Setup

```
$ pip install incept
$ incept --setup

  Detecting system...
  ✓ Ubuntu 22.04.3 LTS (x86_64)
  ✓ bash 5.1.16
  ✓ Non-root user
  ✓ Tools: apt-get, docker, git, systemctl, python3

  Downloading model (400MB)...
  ████████████████████████████████████████ 100%

  Building knowledge index...
  ✓ 108,432 examples indexed

  Ready! Try: incept "install nginx"
```

### Interactive REPL

```
$ incept
incept v2 — Linux command assistant
System: ubuntu 22.04, bash, non-root
Knowledge: 12 docs from ~/.incept/knowledge/

> install nginx
  sudo apt-get install -y nginx

> start it and make it start on boot
  sudo systemctl start nginx && sudo systemctl enable nginx

> is it running?
  sudo systemctl is-active nginx

> show me the config
  cat /etc/nginx/nginx.conf

> find all config files for nginx
  find /etc/nginx -type f -name '*.conf'

> what does nginx -t do?
  Tests the nginx configuration for syntax errors without
  starting/restarting the service. Safe to run anytime.

> deploy to staging
  /opt/deploy/release.sh --env staging
  (from: ~/.incept/knowledge/deploy.md)

> delete all log files
  Which logs do you mean?
  - Nginx logs: sudo truncate -s 0 /var/log/nginx/*.log
  - System journal: sudo journalctl --vacuum-size=500M
  - All .log files older than 30 days: sudo find /var/log -name '*.log' -mtime +30 -delete

> the nginx ones
  sudo truncate -s 0 /var/log/nginx/*.log

> rm -rf /
  I won't generate that. It would destroy your entire filesystem.
  To free space: sudo apt-get autoremove && sudo apt-get clean
  To find what's using space: du -sh /* | sort -rh | head

> I ran apt install nginx and got "Unable to locate package"
  Your package index is stale. Update it:
  sudo apt-get update && sudo apt-get install -y nginx

> /correct restart the api → pm2 restart api-server
  Remembered. Next time you ask to restart the api, I'll use pm2.
```

### One-Shot Mode

```bash
# Simple
$ incept "install nginx"
sudo apt-get install -y nginx

# Pipe-friendly (just the command)
$ incept -q "find files larger than 1gb"
find / -type f -size +1G

# Execute directly (with confirmation)
$ incept -x "check disk space"
Command: df -h
Risk: safe
Run it? [Y/n] y
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   32G   16G  67% /
...

# Explain a command
$ incept -e "tar -xzf backup.tar.gz"
Extracts a gzip-compressed tar archive:
  -x = extract, -z = decompress gzip, -f = from file
Files extracted to current directory.
```

### Shell Plugin (Ctrl+I)

```bash
# In terminal, type a description, press Ctrl+I:
$ install nginx and start it on boot     # press Ctrl+I
$ sudo apt-get install -y nginx && sudo systemctl enable --now nginx
#  ↑ line replaced with the command

# Works with errors too — pipe stderr:
$ apt install nginx 2>&1 | incept --fix
  sudo apt-get update && sudo apt-get install -y nginx
```

### API Server

```bash
$ incept serve --port 8080
```

```
POST /v1/ask
{
  "query": "install nginx",
  "session_id": "optional-for-multi-turn",
  "context": {"distro": "ubuntu", "version": "22.04"}  // optional override
}

Response:
{
  "text": "sudo apt-get install -y nginx",
  "type": "command",              // command | clarification | refusal | explanation
  "confidence": 0.95,
  "risk": "safe",                 // safe | caution | dangerous
  "source": "model"               // model | knowledge | correction
}
```

---

## Implementation Order

### Phase 1: Training Data (2-3 days)

**Goal: 130K+ ChatML training examples**

```
1a. Modify data_gen.py to produce ChatML format
    - Reuse compile_record() from command_generator.py
    - Output messages format instead of prompt/completion
    - Include system context line with installed tools

1b. Generate multi-turn chains
    - Define 50+ chain templates (install→start→enable, etc.)
    - Expand with slot pool values
    - Target: 15K chain examples

1c. Generate explanation, recovery, refusal, clarification examples
    - Template-based with slot pool expansion
    - Target: 18K total

1d. Inject few-shot examples into 30% of training data
    - For each example, find 2-3 similar examples
    - Add to system message
    - Teaches model to USE retrieved context

1e. Assemble, deduplicate, split
    → data/v2/train.jsonl (~106K)
    → data/v2/val.jsonl (~13K)
    → data/v2/test.jsonl (~13K)
```

### Phase 2: Fine-Tune + Export (1 day)

```
2a. Update trainer for ChatML format
2b. Train: LoRA r=32, 3 epochs, max_seq_length=1024
2c. Merge LoRA into base
2d. Quantize to Q4_K_M GGUF
    → models/incept-v2-q4_k_m.gguf (~400MB)
2e. Quick sanity test: 20 commands across 5 distros
```

### Phase 3: New Runtime (2-3 days)

```
3a. core/engine.py — model load, prompt assembly, inference, confidence
3b. core/knowledge.py — zvec + TF-IDF, three collections
3c. core/context.py — simplify existing system detection
3d. core/safety.py — extract banned patterns from existing validator
3e. cli/main.py — wire up one-shot + serve modes
3f. cli/repl.py — interactive loop with session history + /correct
3g. server/routes.py — POST /v1/ask, GET /v1/health
3h. Build few-shot bank: index all training examples in zvec
```

### Phase 4: Test + Polish (2-3 days)

```
4a. Test all 78 known intents × 5 distros
4b. Test multi-turn conversations (10+ scenarios)
4c. Test clarification, refusal, explanation
4d. Test correction memory (store + retrieve)
4e. Test knowledge base (add runbook, query it)
4f. Test edge cases (empty input, very long input, unicode, injection)
4g. Measure: RAM, latency, accuracy
4h. Write new tests for v2 pipeline
```

---

## Metrics to Hit

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Command accuracy** | >90% on known intents | Test against compiler gold standard |
| **Distro correctness** | >95% right package manager | apt vs dnf vs pacman vs brew |
| **Multi-turn success** | >85% correct follow-ups | "install X" → "start it" → "enable it" |
| **Refusal rate** | 100% for banned patterns | All 22 dangerous patterns blocked |
| **False refusal** | <5% | Legitimate commands not blocked |
| **Clarification quality** | Specific, not generic | "Which logs?" not "Please rephrase" |
| **Latency (p50)** | <200ms | Single model call |
| **Latency (p99)** | <500ms | Including retrieval |
| **RAM** | <500MB | Model + app + zvec |
| **Cold start** | <5s | Model load + index load |

---

## Why This Is The Best Possible Design

1. **Maximum intelligence per byte.** Every MB of RAM goes to the model and retrieval. No runtime code waste.

2. **The model does what models are good at** (generating text) instead of what they're bad at (structured classification into rigid schemas).

3. **Three sources of knowledge, one interface:**
   - Fine-tuned weights → common commands
   - Few-shot retrieval → edge cases
   - User knowledge → site-specific commands

4. **It gets smarter without retraining.** Correction memory means every user interaction improves it.

5. **It's honest.** Logprob confidence means it tells you when it's guessing.

6. **It's safe without being annoying.** Model-level refusals are natural ("I won't do that because...") not robotic ("Request blocked by safety rules").

7. **Adding commands = adding training data.** No compilers, no grammars, no schemas. Just examples.

8. **900 lines of runtime code.** Easy to understand, debug, extend. One person can maintain the entire system.
