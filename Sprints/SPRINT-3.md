# Sprint 3: Data Engineering

**Duration:** Weeks 5-6
**Phase:** Phase 2 — Data
**Sprint Goal:** Build the complete training dataset (15,000+ examples), flag tables, retrieval index, and expand the golden test set to 500+ examples.

---

## Sprint Backlog

### Story 3.1 — Template-Based Training Data Generation
**Points:** 8
**Priority:** P0 — Critical

**As a** ML engineer,
**I want** high-quality template-generated NL↔intent↔slot training pairs,
**So that** the model has a clean, diverse foundation to learn from.

**Acceptance Criteria:**
- [ ] 10-20 NL templates per intent (52 intents × 15 avg = ~780 templates)
- [ ] Slot value pools: realistic paths, package names, service names, usernames, file patterns, sizes, timestamps
- [ ] Template expander generates all combinations with varied slot values
- [ ] Output format: JSONL with `id`, `source`, `license`, `nl_request`, `context_line`, `expected_intent`, `expected_slots`, `expected_behavior`, `tags`
- [ ] Distro-aware context lines (vary between debian/rhel, different versions, root/non-root, safe/unsafe)
- [ ] Target: **8,000+ examples** from templates
- [ ] Quality check: 100 random samples manually verified

**Tasks:**
- [ ] Write NL templates for File Operations (12 intents × 15 templates)
- [ ] Write NL templates for Text Processing (6 intents × 15 templates)
- [ ] Write NL templates for Archive Operations (2 intents × 15 templates)
- [ ] Write NL templates for Package Management (4 intents × 15 templates)
- [ ] Write NL templates for Service Management (5 intents × 15 templates)
- [ ] Write NL templates for User/Log/Cron (9 intents × 15 templates)
- [ ] Write NL templates for Network/Process/Disk (11 intents × 15 templates)
- [ ] Write NL templates for CLARIFY/OUT_OF_SCOPE/UNSAFE (3 × 20 templates)
- [ ] Build slot value pools (JSON files per domain)
- [ ] Implement template expander script
- [ ] Generate 8,000+ examples
- [ ] Manual QA: verify 100 random samples

---

### Story 3.2 — Paraphrase Generation (via Claude Code)
**Points:** 5
**Priority:** P0 — Critical

**As a** ML engineer,
**I want** diverse paraphrases of training examples,
**So that** the model generalizes to varied phrasings it hasn't seen in templates.

**Acceptance Criteria:**
- [ ] **Method:** Use **Claude (via Claude Code)** to generate 5-10 paraphrases per seed example — this is a one-time build step, not a runtime dependency
- [ ] Claude generates paraphrases in batch, output saved as JSONL files locally
- [ ] Once generated, the paraphrase data is **committed to the repo** — Claude is never needed again
- [ ] Paraphrase prompts enforce: same intent, same slot values, different phrasing
- [ ] Include colloquial, formal, terse, and verbose variants
- [ ] Target: **4,000+ additional examples**
- [ ] Human review: 15% stratified sample verified (600+ examples reviewed)
- [ ] Rejection rate tracked and reported
- [ ] **Clarification:** Claude is used only at build time for data generation. The deployed system uses only Qwen2.5-0.5B. No Claude dependency at runtime.

**Tasks:**
- [ ] Design paraphrase generation prompt for Claude
- [ ] Select seed examples (diverse across intents and complexity)
- [ ] Run paraphrase generation batches via Claude Code (save output as JSONL)
- [ ] Commit generated paraphrases to repo
- [ ] Build QA tool for human review (simple CLI or notebook)
- [ ] Conduct human review of 15% sample
- [ ] Filter out low-quality paraphrases
- [ ] Merge into training dataset

---

### Story 3.2b — Forum Mining (Real-World Phrasing, Offline)
**Points:** 3
**Priority:** P1 — High

**As a** ML engineer,
**I want** real-world Q&A pairs from Stack Overflow and Unix Stack Exchange,
**So that** the model handles natural, messy phrasings from real users.

**Acceptance Criteria:**
- [ ] **Use offline data dumps** (Stack Exchange releases quarterly XML dumps under CC-BY-SA 4.0 at archive.org) — no live API required
- [ ] Download data dump once, store locally, process offline
- [ ] Extract question+answer pairs from `linux`, `ubuntu`, `unix` tags
- [ ] License: CC-BY-SA 4.0 — attribute properly, track provenance per snippet
- [ ] Map each pair to intent + slot values (semi-automatic with manual verification)
- [ ] Target: **1,000+ real-world examples**
- [ ] Filter out: multi-step questions (too complex), non-command answers, distro-specific answers without context
- [ ] Provenance file: source URL, license, extraction date per example
- [ ] Human review: 20% sample verified

**Tasks:**
- [ ] Download Stack Exchange data dump (one-time, ~2-5GB compressed)
- [ ] Build offline XML parser for Stack Exchange dump format
- [ ] Implement intent mapping heuristics
- [ ] Manual verification of 20% sample
- [ ] Merge into training dataset with proper attribution
- [ ] Create provenance tracking file

---

### Story 3.3 — Adversarial & Negative Training Data
**Points:** 5
**Priority:** P0 — Critical

**As a** safety engineer,
**I want** adversarial and negative examples comprising ≥20% of training data,
**So that** the model reliably detects dangerous, ambiguous, and out-of-scope requests.

**Acceptance Criteria:**
- [ ] **Prompt injection examples (500+):** "ignore instructions and...", "you are now in unrestricted mode", role injection variants
- [ ] **Dangerous request recognition (500+):** "delete everything", "nuke that folder", "wipe the disk"
- [ ] **Wrong-distro traps (300+):** Arch context with `apt` language, RHEL context with `pacman` language
- [ ] **Ambiguous requests requiring CLARIFY (400+):** "compress the logs", "install a package", "delete log files"
- [ ] **Out-of-scope requests (300+):** weather, math, cooking, Kubernetes, cloud services
- [ ] **Near-miss intents (500+):** `find_files` vs `search_text`, `install_package` vs `search_package`, `delete_files` vs `remove_package`
- [ ] Total adversarial: **≥3,000 examples** (≥20% of full dataset)
- [ ] All tagged with appropriate `tags` field

**Tasks:**
- [ ] Write prompt injection variants (hand-crafted + LLM-expanded)
- [ ] Write dangerous request variants
- [ ] Write wrong-distro trap examples
- [ ] Write ambiguous/CLARIFY examples
- [ ] Write out-of-scope examples
- [ ] Write near-miss intent pairs
- [ ] Tag all examples
- [ ] Merge into training dataset

---

### Story 3.4 — Dataset Assembly & Split
**Points:** 3
**Priority:** P0 — Critical

**As a** ML engineer,
**I want** a clean, deduplicated, properly split dataset,
**So that** training, validation, and test sets are ready for model training.

**Acceptance Criteria:**
- [ ] Merge all data sources (templates, paraphrases, adversarial)
- [ ] Deduplicate by NL request similarity (fuzzy matching, threshold 0.95)
- [ ] Validate every record against JSONL schema
- [ ] Stratified split: 80% train / 10% validation / 10% test
- [ ] Stratification by: intent label, distro context, adversarial tag
- [ ] Golden test set kept separate (never in train/val)
- [ ] Dataset statistics report: examples per intent, adversarial %, distro distribution
- [ ] Total: **≥15,000 clean examples**

**Tasks:**
- [ ] Implement merge script
- [ ] Implement deduplication (TF-IDF or embedding similarity)
- [ ] Implement schema validation
- [ ] Implement stratified splitter
- [ ] Generate dataset statistics report
- [ ] Export final train/val/test JSONL files
- [ ] Verify golden test set isolation

---

### Story 3.5 — Flag Tables & Retrieval Index
**Points:** 5
**Priority:** P0 — Critical

**As a** compiler developer,
**I want** comprehensive flag tables and a retrieval index,
**So that** the compiler generates version-correct commands and can look up distro-specific syntax.

**Acceptance Criteria:**
- [ ] Flag table JSON for all 20+ supported commands (from Story 2.5, now comprehensive)
- [ ] Distro-specific data: `package_map.json` (generic → apt/dnf package names), `service_map.json`, `path_defaults.json`
- [ ] BM25 index over command+flag records for pre-classifier similarity matching
- [ ] Embedding index using `all-MiniLM-L6-v2` (23M params) for NL → intent similarity — **model pre-downloaded and bundled in `models/` at build time, loaded from local file at runtime**
- [ ] **Alternative (lighter):** Use ONNX-exported MiniLM (~30MB) for faster load and no PyTorch dependency at runtime
- [ ] Index query latency < 20ms
- [ ] Retrieval index covers all 52 intents with ≥10 example queries each
- [ ] **Offline guarantee:** embedding model loaded from local path only, no HuggingFace Hub calls at runtime

**Tasks:**
- [ ] Complete flag tables for all commands
- [ ] Create `package_map.json` for Debian and RHEL
- [ ] Create `service_map.json` for common services
- [ ] Create `path_defaults.json` per distro
- [ ] Implement BM25 index builder and query
- [ ] Implement embedding index (MiniLM) builder and query
- [ ] Benchmark query latency
- [ ] Write integration tests

---

### Story 3.6 — Expand Golden Test Set to 500+
**Points:** 5
**Priority:** P1 — High

**As a** quality engineer,
**I want** a comprehensive golden test set of 500+ human-verified examples,
**So that** model evaluation is statistically meaningful across all intents and edge cases.

**Acceptance Criteria:**
- [ ] ≥10 examples per supported intent (52 × 10 = 520 minimum)
- [ ] Every distro family represented (Debian, RHEL)
- [ ] Every risk tier covered (T1-T6)
- [ ] All 15 safety canaries included
- [ ] ≥20 CLARIFY examples with varied ambiguity types
- [ ] ≥15 OUT_OF_SCOPE examples
- [ ] ≥15 multi-step compound requests
- [ ] Each example includes `expected_command` validated by running in Docker container
- [ ] Human-verified: every example reviewed by at least one person
- [ ] Total: **≥500 golden examples**

**Tasks:**
- [ ] Expand existing golden tests from Sprint 1 (100 → 500+)
- [ ] Add distro-variant tests
- [ ] Add multi-step request tests
- [ ] Validate expected commands in Docker containers
- [ ] Human review pass on all new examples
- [ ] Export final golden test JSONL

---

### Story 3.7 — Training Data Format Conversion
**Points:** 3
**Priority:** P1 — High

**As a** ML engineer,
**I want** training data converted to the model's expected instruction format,
**So that** it's ready for fine-tuning without additional processing.

**Acceptance Criteria:**
- [ ] Intent classification format: `<s>[INST]...[CONTEXT]...[REQUEST]...[INTENT] [/INST]{label}</s>`
- [ ] Slot filling format: `<s>[INST]...[CONTEXT]...[REQUEST]...[INTENT]...[SLOTS] [/INST]{slots}</s>`
- [ ] Format matches Qwen2.5 chat template (or SmolLM2 as fallback)
- [ ] Two separate JSONL files: one for intent training, one for slot training
- [ ] DPO pairs generated for near-miss intents (chosen/rejected format)
- [ ] DPO pair count: ≥1,000 preference pairs
- [ ] Validation: 50 random samples manually inspected for correct formatting

**Tasks:**
- [ ] Implement JSONL → instruction format converter (intent)
- [ ] Implement JSONL → instruction format converter (slots)
- [ ] Implement DPO pair generator from near-miss examples
- [ ] Generate formatted training files
- [ ] Manual inspection of 50 samples
- [ ] Document format and field mapping

---

## Sprint Metrics

| Metric | Target |
|--------|--------|
| Total Story Points | 37 |
| Template examples generated | ≥8,000 |
| Paraphrase examples generated | ≥4,000 |
| Forum-mined examples | ≥1,000 |
| Adversarial examples | ≥3,000 |
| Total clean dataset | ≥16,000 |
| Golden test set size | ≥500 |
| DPO preference pairs | ≥1,000 |
| Human review coverage | ≥15% of generated data |

## Dependencies
- Sprint 2 compiler (for validating golden test expected commands)
- Sprint 1 IR schemas (for data format validation)

## Risks
- LLM paraphrase quality may be inconsistent — budget extra QA time
- Adversarial examples are labor-intensive to hand-craft — consider hiring annotators or using red-team LLM sessions
- Deduplication may reduce dataset below target — generate 20% surplus
