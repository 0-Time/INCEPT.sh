# INCEPT — Full Product Backlog

## Backlog Legend

| Priority | Meaning |
|----------|---------|
| **P0** | Must have — blocks sprint goal |
| **P1** | Should have — important for completeness |
| **P2** | Nice to have — can defer to next sprint |
| **P3** | Future — post-MVP |

| Status | Meaning |
|--------|---------|
| `TODO` | Not started |
| `IN_PROGRESS` | Currently being worked |
| `DONE` | Completed |
| `DEFERRED` | Moved to future sprint |

---

## Epic 1: Core Pipeline (Sprints 1-2)

| ID | Story | Points | Priority | Sprint | Status |
|----|-------|--------|----------|--------|--------|
| 1.1 | Project scaffold and dependency setup | 3 | P0 | 1 | TODO |
| 1.2 | Pydantic IR schema definition (52 intents) | 5 | P0 | 1 | TODO |
| 1.3 | GBNF grammar files (intent + 52 slot grammars) | 8 | P0 | 1 | TODO |
| 1.4 | Context resolver (environment detection) | 3 | P1 | 1 | TODO |
| 1.5 | Pre-classifier (rule-based regex/keyword) | 5 | P1 | 1 | TODO |
| 1.6 | Initial golden test cases (100+) | 5 | P1 | 1 | TODO |
| 2.1 | Compiler core (routing, quoting, composition) | 3 | P0 | 2 | TODO |
| 2.2 | File Operations compilers (12 intents) | 8 | P0 | 2 | TODO |
| 2.3 | Text Processing + Archive compilers (8 intents) | 5 | P0 | 2 | TODO |
| 2.4 | Pkg/Service/User/Log/Cron/Net/Proc compilers (27 intents) | 13 | P0 | 2 | TODO |
| 2.5 | Version-aware flag tables (20+ commands) | 5 | P0 | 2 | TODO |
| 2.6 | Validator & safety layer | 8 | P0 | 2 | TODO |
| 2.7 | Multi-step decomposer | 5 | P1 | 2 | TODO |
| 2.8 | Response formatter & templates | 5 | P1 | 2 | TODO |
| 2.9 | End-to-end pipeline (hard-coded classifier) | 5 | P0 | 2 | TODO |

---

## Epic 2: Data Platform (Sprint 3)

| ID | Story | Points | Priority | Sprint | Status |
|----|-------|--------|----------|--------|--------|
| 3.1 | Template-based training data (8,000+) | 8 | P0 | 3 | TODO |
| 3.2 | Paraphrase generation via Claude Code — one-time build step (4,000+) | 5 | P0 | 3 | TODO |
| 3.2b | Forum mining — offline data dump, real-world phrasing (1,000+) | 3 | P1 | 3 | TODO |
| 3.3 | Adversarial & negative data (3,000+) | 5 | P0 | 3 | TODO |
| 3.4 | Dataset assembly, dedup, stratified split | 3 | P0 | 3 | TODO |
| 3.5 | Flag tables & retrieval index (BM25 + MiniLM) | 5 | P0 | 3 | TODO |
| 3.6 | Expand golden test set (500+) | 5 | P1 | 3 | TODO |
| 3.7 | Training data format conversion (instruction + DPO) | 3 | P1 | 3 | TODO |

---

## Epic 3: Model Training (Sprints 4-5)

| ID | Story | Points | Priority | Sprint | Status |
|----|-------|--------|----------|--------|--------|
| 4.1 | Training infrastructure setup | 5 | P0 | 4 | TODO |
| 4.2 | Intent classification SFT (LoRA adapter) | 8 | P0 | 4 | TODO |
| 4.3 | Slot filling SFT (LoRA adapter) | 8 | P0 | 4 | TODO |
| 4.4 | Constrained decoding verification (GGUF + GBNF) | 5 | P0 | 4 | TODO |
| 4.5 | Confidence scoring implementation | 3 | P1 | 4 | TODO |
| 4.6 | Baseline evaluation report | 3 | P1 | 4 | TODO |
| 5.1 | DPO preference tuning (intent + slot) | 8 | P0 | 5 | TODO |
| 5.2 | Adversarial hardening | 5 | P0 | 5 | TODO |
| 5.3 | Final quantization & benchmarking (GGUF Q4_K_M) | 5 | P0 | 5 | TODO |
| 5.4 | Model integration into pipeline | 8 | P0 | 5 | TODO |
| 5.5 | Component-level evaluation automation (CI) | 3 | P1 | 5 | TODO |

---

## Epic 4: System Integration & Production Hardening (Sprint 6)

| ID | Story | Points | Priority | Sprint | Status |
|----|-------|--------|----------|--------|--------|
| 6.1 | FastAPI server (auth, rate limiting, metrics, graceful shutdown) | 8 | P0 | 6 | TODO |
| 6.2 | Error recovery loop (7 error patterns) | 5 | P0 | 6 | TODO |
| 6.3 | Session tracking (multi-turn context) | 3 | P1 | 6 | TODO |
| 6.4 | Telemetry & logging (SQLite, local only, zero phone-home) | 3 | P1 | 6 | TODO |
| 6.5 | Docker packaging (non-root, resource limits, TLS, image scan) | 8 | P0 | 6 | TODO |
| 6.6 | Llamafile single-binary packaging | 3 | P2 | 6 | TODO |
| 6.7 | Client-side context script (polished) | 2 | P1 | 6 | TODO |
| 6.8 | Load testing & soak testing (concurrency, memory) | 5 | P0 | 6 | TODO |
| 6.9 | Smoke test & rollback procedure | 3 | P0 | 6 | TODO |
| **6.10** | **Interactive terminal — primary interface (Claude Code-style REPL)** | **13** | **P0** | **6** | **TODO** |
| 6.11 | Documentation (API, deployment, security, operations runbook) | 5 | P0 | 6 | TODO |

---

## Epic 5: Deployment (Sprint 6, overlap)

Covered by Stories 6.5, 6.6, 6.8 above.

---

## Epic 6: Expansion & Release (Sprint 7)

| ID | Story | Points | Priority | Sprint | Status |
|----|-------|--------|----------|--------|--------|
| 7.1 | Arch Linux distro family support | 5 | P1 | 7 | TODO |
| 7.2 | SUSE distro family support | 5 | P1 | 7 | TODO |
| 7.3 | Shell plugin (bash/zsh keybinding) | 5 | P2 | 7 | TODO |
| 7.4 | Intent expansion (50 → 80+ intents) | 8 | P2 | 7 | TODO |
| 7.5 | Security audit & hardening (OWASP, deps, container) | 5 | P0 | 7 | TODO |
| 7.6 | Open-source release preparation | 5 | P1 | 7 | TODO |

---

## Future Backlog (Post-Sprint 7)

| ID | Story | Points | Priority | Notes |
|----|-------|--------|----------|-------|
| F1 | V1 model accuracy targets (97% intent, 92% slot EM) | 13 | P3 | More data + larger model experiments |
| F2 | Expand to 200+ intents | 13 | P3 | Docker, git, systemd timers, firewall, etc. |
| F3 | BSD/macOS support | 8 | P3 | Different coreutils, no systemd |
| F4 | Offline mode (no server, embedded inference) | 8 | P3 | CLI directly loads model |
| F5 | Web UI | 13 | P3 | Browser-based NL → command interface |
| F6 | VS Code / terminal extension | 8 | P3 | IDE integration |
| F7 | Command history learning | 8 | P3 | Personalize based on user's shell history |
| F8 | Multilingual NL input (Spanish, Portuguese, etc.) | 13 | P3 | Requires multilingual training data |
| F9 | Explain mode (paste command → NL explanation) | 5 | P3 | Reverse direction: command → explanation |
| F10 | Audit log for enterprise (who ran what, when) | 5 | P3 | Compliance feature |
| F11 | Rust/Go pipeline rewrite for minimal runtime | 13 | P3 | Eliminate Python dependency |
| F12 | ARM-optimized GGUF for Raspberry Pi | 3 | P3 | NEON-tuned quantization |
| F13 | Model distillation (500M → 150M) | 13 | P3 | Research: can we go even smaller? |
| F14 | Plugin architecture for custom intents | 8 | P3 | Users register their own commands/scripts |
| F15 | Auto-update flag tables from man pages | 5 | P3 | Scrape man pages on target system |

---

## Cumulative Story Points by Sprint

| Sprint | Sprint Points | Cumulative | % Complete | Notes |
|--------|-------------|-----------|-----------|-------|
| 1 | 29 | 29 | 10% | Foundation |
| 2 | 57 | 86 | 28% | **Heavy — spillover plan in place** |
| 3 | 37 | 123 | 40% | +forum mining; absorbs Sprint 2 spillover |
| 4 | 32 | 155 | 51% | Model baseline |
| 5 | 29 | 184 | 60% | Model hardened + integrated |
| 6 | 58 | 242 | 79% | **Interactive terminal + production hardening (heaviest)** |
| 7 | 33 | 275 | 100% | Security audit + expansion + release |

**Total MVP: 275 story points across 7 sprints (14 weeks)**
**Production-critical points (P0 only): ~200 SP**

> **Note:** Sprint 6 can be split into 6a + 6b (15 weeks total) if 58 SP is too heavy.

---

## Key Milestones

| Milestone | Sprint | Gate Criteria |
|-----------|--------|---------------|
| **M1: Architecture Validated** | End of Sprint 2 | Pipeline works e2e with hard-coded classifier; compiler ≥95% golden tests |
| **M2: Data Ready** | End of Sprint 3 | ≥16,000 training examples; ≥500 golden tests; retrieval index operational |
| **M3: Model Baseline** | End of Sprint 4 | SFT model meets pre-DPO accuracy targets; constrained decoding verified |
| **M4: Model MVP** | End of Sprint 5 | All MVP accuracy targets met; model integrated in pipeline; CI evaluation |
| **M5: Production Ready** | End of Sprint 6 | **GATE:** API auth + rate limiting + TLS + load test passed + smoke test passes + rollback tested + operations runbook written + production checklist complete |
| **M6: Secure Release** | End of Sprint 7 | Security audit passed (0 critical/high); multi-distro; CLI client; CHANGELOG + SECURITY.md + open-source prep complete |

---

## Definition of Done (Global)

A story is DONE when:
1. Code is written and passes linting (`ruff`) and type checking (`mypy`)
2. Unit tests written and passing (≥85% coverage on new code)
3. Integration tests passing (where applicable)
4. Golden test suite does not regress
5. Safety canary suite passes 100%
6. Code reviewed (or self-reviewed with checklist if solo)
7. No new security vulnerabilities introduced (no `os.system`, no unsanitized input, no hardcoded secrets)
8. **No runtime internet dependency introduced** — no network calls at inference time, no model downloads, no external API calls, no telemetry phone-home
9. Documentation updated (if user-facing changes)
10. Changes committed to main branch

---

## Production Readiness Checklist (Sprint 6 Gate)

Before declaring production-ready, ALL of these must be true:

**Security:**
- [ ] API authentication enabled (API key required)
- [ ] Rate limiting configured and tested
- [ ] TLS configured (built-in or reverse proxy)
- [ ] Input validation on all endpoints (size limits, encoding, null bytes)
- [ ] No hardcoded secrets in codebase or Docker image
- [ ] Container runs as non-root user
- [ ] `pip audit` shows 0 critical CVEs

**Reliability:**
- [ ] Graceful shutdown handles SIGTERM (drains in-flight requests)
- [ ] Model warm-up runs before accepting traffic
- [ ] Health check endpoint verifies model can infer (not just "server is up")
- [ ] Inference concurrency guard prevents race conditions
- [ ] Error recovery loop handles top 7 error patterns
- [ ] Max 3 retries enforced; destructive commands never auto-retried

**Observability:**
- [ ] Structured JSON logging with request ID correlation
- [ ] Prometheus metrics endpoint operational
- [ ] Telemetry database records requests, feedback, errors
- [ ] Log rotation configured

**Performance:**
- [ ] P95 latency < 2s (single user, CPU)
- [ ] P95 latency < 3s (5 concurrent users)
- [ ] 24h soak test: no memory leak > 20% RSS growth
- [ ] Model file size ~250MB (Q4_K_M)

**Operations:**
- [ ] Smoke test script passes in <30s
- [ ] Rollback procedure tested end-to-end
- [ ] Docker image < 1GB, 0 critical CVEs
- [ ] Operations runbook covers: startup, shutdown, monitoring, log interpretation, recovery
- [ ] Production deployment guide with recommended resource limits

**Quality:**
- [ ] E2E command match ≥82% on golden test set
- [ ] Execution success ≥88% in container tests
- [ ] Safety canary 100% (15/15)
- [ ] Intent accuracy ≥93%, Slot F1 ≥88%

**Offline Compliance (HARD GATE):**
- [ ] `docker run --network=none incept` → smoke test passes (zero internet required)
- [ ] No `requests.get`, `urllib.urlopen`, `httpx.get` or any outbound HTTP in inference code path
- [ ] All models (GGUF, MiniLM ONNX) bundled in Docker image at build time
- [ ] `HF_TRANSFORMERS_OFFLINE=1` and `HF_HUB_OFFLINE=1` set in Dockerfile
- [ ] Telemetry is SQLite-only, zero external transmission
- [ ] `grep -r "requests\.\|urllib\.\|httpx\." incept/` returns only test files or client code, never core pipeline
- [ ] Air-gapped deployment documented and tested (`docker save` / `docker load` workflow)
