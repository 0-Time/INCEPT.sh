# INCEPT — NL Linux Command Compiler: Sprint Overview

## Agile Framework

- **Methodology:** Scrum
- **Sprint Duration:** 2 weeks
- **Total Sprints:** 7 (14 weeks)
- **Team Assumption:** 1-2 developers (adjust velocity accordingly)
- **Story Points:** Fibonacci scale (1, 2, 3, 5, 8, 13)
- **Definition of Done:** Code written, tests pass, reviewed, documented, security reviewed
- **Production Gate:** Sprint 6 must pass production readiness checklist before release
- **Offline Constraint:** System runs 100% offline at inference time. Zero internet required after deployment. Build-time downloads (models, deps) are one-time setup only.

---

## Phase-to-Sprint Mapping

| Sprint | Weeks | Phase | Theme | Key Deliverable |
|--------|-------|-------|-------|-----------------|
| **Sprint 1** | 1-2 | Phase 1 | Foundation & IR Schema | Pydantic IR models, GBNF grammars, project scaffold |
| **Sprint 2** | 3-4 | Phase 1 | Compiler & Validator | All 52 intent compilers, safety layer, hard-coded classifier |
| **Sprint 3** | 5-6 | Phase 2 | Data Engineering | 15,000+ training examples, flag tables, retrieval index |
| **Sprint 4** | 7-8 | Phase 3 | Model Training (SFT) | Fine-tuned Qwen2.5-0.5B, LoRA adapters, baseline metrics |
| **Sprint 5** | 9-10 | Phase 3+4 | Model Hardening & Integration | DPO, adversarial training, quantization, model-in-pipeline |
| **Sprint 6** | 11-12 | Phase 4 | Interactive Terminal + Production | **Interactive REPL (primary UI)**, API server, load testing, Docker, smoke test |
| **Sprint 7** | 13-14 | Phase 5 | Security, Expansion & Release | Security audit, Arch/SUSE support, CLI client, shell plugin, open-source prep |

---

## Velocity Tracking Template

| Sprint | Planned SP | Completed SP | Carryover | Notes |
|--------|-----------|-------------|-----------|-------|
| 1 | — | — | — | |
| 2 | — | — | — | |
| 3 | — | — | — | |
| 4 | — | — | — | |
| 5 | — | — | — | |
| 6 | — | — | — | |
| 7 | — | — | — | |

---

## Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Sprint |
|----|------|-----------|--------|------------|--------|
| R1 | Qwen2.5-0.5B slot-filling accuracy below 85% | Medium | High | Fallback to encoder+decoder split architecture | 4 |
| R2 | Constrained decoding grammars too restrictive for edge cases | Medium | Medium | Add `CLARIFY` escape hatch; expand grammars iteratively | 1-2 |
| R3 | Insufficient training data diversity | Medium | High | Supplement with LLM paraphrasing + forum mining | 3 |
| R4 | Quantization drops accuracy >2% | Low | High | Benchmark Q4_K_M vs Q8_0; use higher quant if needed | 5 |
| R5 | Multi-step decomposer fails on complex compound sentences | High | Medium | Limit to 4 sub-steps; ask for clarification on complex requests | 2 |
| R6 | Flag table coverage gaps for edge-case tool versions | Medium | Low | Telemetry will identify gaps; patch incrementally post-MVP | 2-3 |
| R7 | bashlex cannot parse all generated commands | Low | Medium | Fallback to shlex tokenization; custom parser for edge cases | 2 |
| R8 | Sprint 2 overloaded (57 SP) causes carryover cascade | High | High | Spillover buffer: allow Stories 2.7, 2.8 to carry into Sprint 3 | 2-3 |
| R9 | API exposed without auth in production deployment | High | Critical | Add API key auth + rate limiting in Sprint 6; TLS via reverse proxy | 6 |
| R10 | No rollback mechanism for failed model/deploy updates | Medium | High | Model versioning + Docker tag pinning + rollback script | 6 |
| R11 | Concurrent requests cause model inference contention | Medium | Medium | Load test in Sprint 6; add request queuing if needed | 6 |
| R12 | Memory leak in long-running inference server | Medium | High | Soak test 24h+; monitor RSS in Sprint 6 | 6 |

---

## Epic Breakdown

| Epic | Description | Sprints |
|------|-------------|---------|
| **E1: Core Pipeline** | IR schema, GBNF grammars, compiler, validator, formatter | 1-2 |
| **E2: Data Platform** | Training data generation, flag tables, retrieval index, golden test set | 2-3 |
| **E3: Model Training** | SFT, DPO, adversarial hardening, quantization, evaluation | 4-5 |
| **E4: System Integration** | Model integration, error recovery, sessions, API server | 5-6 |
| **E5: Deployment** | Docker, llamafile, telemetry, documentation | 6 |
| **E6: Expansion** | New distros, new intents, CLI client, shell plugin | 7 |

---

## Sprint Cadence

| Day | Activity |
|-----|----------|
| Day 1 (Mon) | Sprint Planning — select backlog items, estimate, commit |
| Days 2-9 | Development — daily standup (async check-in if solo) |
| Day 10 (Fri) | Sprint Review — demo deliverables, update metrics |
| Day 10 (Fri) | Sprint Retrospective — what worked, what to improve |
| Weekend | Backlog grooming for next sprint |

---

## File Index

| File | Contents |
|------|----------|
| `SPRINT-OVERVIEW.md` | This file — master plan |
| `SPRINT-1.md` | Foundation & IR Schema |
| `SPRINT-2.md` | Compiler & Validator |
| `SPRINT-3.md` | Data Engineering |
| `SPRINT-4.md` | Model Training (SFT) |
| `SPRINT-5.md` | Model Hardening & Integration |
| `SPRINT-6.md` | Production Readiness |
| `SPRINT-7.md` | Expansion & Release |
| `BACKLOG.md` | Full product backlog |
