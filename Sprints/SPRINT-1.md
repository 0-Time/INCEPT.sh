# Sprint 1: Foundation & IR Schema

**Duration:** Weeks 1-2
**Phase:** Phase 1 — Schema and Compiler
**Sprint Goal:** Establish project scaffold, define all IR schemas, implement GBNF grammars, build context resolver and pre-classifier.

---

## Sprint Backlog

### Story 1.1 — Project Scaffold
**Points:** 3
**Priority:** P0 — Critical

**As a** developer,
**I want** a properly structured Python project with dependency management,
**So that** all subsequent development has a stable foundation.

**Acceptance Criteria:**
- [ ] Python project initialized with `pyproject.toml` (Python 3.11+)
- [ ] Directory structure established:
  ```
  incept/
    core/           # Pipeline stages
    compiler/       # Intent-specific compiler functions
    grammars/       # GBNF grammar files
    schemas/        # Pydantic IR models
    retrieval/      # Flag tables and index
    templates/      # Explanation and clarification templates
    safety/         # Validator and banned patterns
    tests/          # Test suite
    eval/           # Evaluation framework
  ```
- [ ] Dependencies declared: `pydantic`, `bashlex`, `fastapi`, `uvicorn`, `llama-cpp-python`
- [ ] Dev dependencies: `pytest`, `pytest-cov`, `ruff`, `mypy`, `httpx` (for API testing)
- [ ] Note: `shlex` is stdlib — no pip install needed
- [ ] **Offline constraint:** all models (GGUF, MiniLM) are pre-downloaded at build time and bundled in `models/` directory — no runtime downloads
- [ ] Makefile or justfile with: `test`, `lint`, `format`, `typecheck` targets
- [ ] `.gitignore` configured for Python + model artifacts
- [ ] CI stub: `Makefile` targets work locally (`make test`, `make lint`); GitHub Actions optional wrapper for remote CI

**Tasks:**
- [ ] Create project structure and `pyproject.toml`
- [ ] Configure linting (ruff) and type checking (mypy)
- [ ] Write initial CI workflow
- [ ] Create README with project overview

---

### Story 1.2 — Pydantic IR Schema Definition
**Points:** 5
**Priority:** P0 — Critical

**As a** compiler developer,
**I want** formally defined IR schemas for all 52 intents,
**So that** every pipeline stage has a validated contract to work against.

**Acceptance Criteria:**
- [ ] `IntentLabel` enum with all 52 intent values + 3 special intents
- [ ] `ConfidenceScore` model with `intent`, `slots`, `composite` fields
- [ ] `SingleIR` model with validated params dict per intent
- [ ] `PipelineIR` model with composition types: `sequential`, `pipe`, `independent`, `subshell`, `xargs`
- [ ] `ClarificationIR` model with reason types and template keys
- [ ] Per-intent param schemas (required/optional, types, defaults) for all 52 intents
- [ ] Validation tests: valid IR passes, invalid IR raises `ValidationError`
- [ ] 100% of IR schemas covered by unit tests

**Tasks:**
- [ ] Define `IntentLabel` enum (52 + 3 special)
- [ ] Define `ConfidenceScore`, `SingleIR`, `PipelineIR`, `ClarificationIR` models
- [ ] Define param schemas for File Operations (12 intents)
- [ ] Define param schemas for Text Processing (6 intents)
- [ ] Define param schemas for Archive Operations (2 intents)
- [ ] Define param schemas for Package Management (4 intents)
- [ ] Define param schemas for Service Management (5 intents)
- [ ] Define param schemas for User Management (3 intents)
- [ ] Define param schemas for Log Operations (3 intents)
- [ ] Define param schemas for Scheduling (3 intents)
- [ ] Define param schemas for Networking (6 intents)
- [ ] Define param schemas for Process Management (3 intents)
- [ ] Define param schemas for Disk/Mount (2 intents)
- [ ] Write validation tests for all schemas

---

### Story 1.3 — GBNF Grammar Files
**Points:** 8
**Priority:** P0 — Critical

**As a** model integration developer,
**I want** constrained decoding grammars for intent classification and every intent's slot filling,
**So that** the model can only produce structurally valid output.

**Acceptance Criteria:**
- [ ] `intent_grammar.gbnf` — forces output to exactly one of 55 intent labels
- [ ] Per-intent slot grammars for all 52 intents (52 `.gbnf` files)
- [ ] `slots_clarify.gbnf` — constrains CLARIFY output to valid reason + template pairs
- [ ] Each grammar enforces correct value types (paths start with `/`, sizes have units, etc.)
- [ ] Grammar test harness: feed valid/invalid strings, verify accept/reject
- [ ] All grammars are loadable by `llama-cpp-python`

**Tasks:**
- [ ] Write `intent_grammar.gbnf`
- [ ] Write slot grammars for File Operations (12 files)
- [ ] Write slot grammars for Text Processing (6 files)
- [ ] Write slot grammars for Archive Operations (2 files)
- [ ] Write slot grammars for Package Management (4 files)
- [ ] Write slot grammars for Service Management (5 files)
- [ ] Write slot grammars for User Management (3 files)
- [ ] Write slot grammars for Log Operations (3 files)
- [ ] Write slot grammars for Scheduling (3 files)
- [ ] Write slot grammars for Networking (6 files)
- [ ] Write slot grammars for Process Management (3 files)
- [ ] Write slot grammars for Disk/Mount (2 files)
- [ ] Write `slots_clarify.gbnf` and `slots_out_of_scope.gbnf`
- [ ] Build grammar validation test harness
- [ ] Test all grammars with llama-cpp-python loading

---

### Story 1.4 — Context Resolver
**Points:** 3
**Priority:** P1 — High

**As a** system user,
**I want** the system to automatically detect my Linux environment,
**So that** commands are generated for my specific distro, shell, and permissions.

**Acceptance Criteria:**
- [ ] `EnvironmentContext` Pydantic model with all fields from spec
- [ ] `context_snapshot.sh` script that outputs JSON
- [ ] Python parser that reads JSON into `EnvironmentContext`
- [ ] Safe defaults when fields are missing (assume Debian, bash, non-root, safe-mode)
- [ ] Unit tests with mocked environment data for Debian and RHEL

**Tasks:**
- [ ] Define `EnvironmentContext` model
- [ ] Implement `context_snapshot.sh`
- [ ] Implement Python context parser with defaults
- [ ] Write unit tests for various distro/shell combos
- [ ] Write tests for missing/partial context

---

### Story 1.5 — Pre-Classifier (Rule-Based)
**Points:** 5
**Priority:** P1 — High

**As a** pipeline developer,
**I want** a fast regex/keyword-based pre-classifier,
**So that** obvious intents, safety violations, and out-of-scope requests are caught before the model runs.

**Acceptance Criteria:**
- [ ] Regex patterns for top 20 most common intents (fast-path)
- [ ] Safety violation detection (fork bombs, `rm -rf /`, pipe-to-shell, etc.)
- [ ] Out-of-scope detection (weather, math, non-Linux questions)
- [ ] Returns `PreClassifierResult` with: `matched_intent | None`, `is_safety_violation`, `is_out_of_scope`, `confidence`
- [ ] Latency < 10ms per request
- [ ] Unit tests with 50+ examples (20 fast-path, 15 safety, 15 out-of-scope)

**Tasks:**
- [ ] Define `PreClassifierResult` model
- [ ] Implement regex patterns for common intents
- [ ] Implement safety violation patterns
- [ ] Implement out-of-scope detection
- [ ] Write unit tests
- [ ] Benchmark latency

---

### Story 1.6 — Initial Golden Test Cases
**Points:** 5
**Priority:** P1 — High

**As a** quality engineer,
**I want** an initial set of golden test cases,
**So that** every pipeline component can be validated from day one.

**Acceptance Criteria:**
- [ ] 100+ golden test cases in JSONL format
- [ ] At least 2 examples per intent for the top 30 intents
- [ ] At least 10 safety canary tests (from Appendix D)
- [ ] At least 5 out-of-scope examples
- [ ] At least 5 CLARIFY examples
- [ ] Each example includes: `nl_request`, `context_line`, `expected_intent`, `expected_slots`, `expected_command`
- [ ] Test loader utility that reads JSONL and validates against IR schema

**Tasks:**
- [ ] Create JSONL schema for golden tests
- [ ] Write golden tests for File Operations (24+ examples)
- [ ] Write golden tests for Text Processing (12+ examples)
- [ ] Write golden tests for Package Management (8+ examples)
- [ ] Write golden tests for Service Management (10+ examples)
- [ ] Write golden tests for safety canaries (15 from Appendix D)
- [ ] Write golden tests for OUT_OF_SCOPE and CLARIFY (10+ examples)
- [ ] Implement test loader utility
- [ ] Write remaining golden tests to reach 100+

---

## Sprint Metrics

| Metric | Target |
|--------|--------|
| Total Story Points | 29 |
| Test Coverage | ≥90% on new code |
| All schemas validated | Yes |
| All grammars loadable | Yes |
| Golden test count | ≥100 |

## Dependencies
- None (Sprint 1 is the foundation)

## Risks
- GBNF grammar complexity for intents with many optional params (mitigation: start simple, iterate)
- Pydantic schema design may need revision as compiler work begins in Sprint 2
