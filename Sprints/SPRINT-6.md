# Sprint 6: Production Readiness

**Duration:** Weeks 11-12
**Phase:** Phase 4 — Integration and Polish
**Sprint Goal:** Build the API server, error recovery loop, session tracking, telemetry, packaging (Docker + llamafile), and documentation. System is production-ready at sprint end.

---

## Sprint Backlog

### Story 6.1 — FastAPI Server
**Points:** 8
**Priority:** P0 — Critical

**As a** user/integrator,
**I want** a production-grade HTTP API to submit NL requests and receive commands,
**So that** any client can interact with the system securely over the network.

**Acceptance Criteria:**
- [ ] `POST /v1/command` — accepts request JSON, returns command response JSON (per spec Section 18.3)
- [ ] `POST /v1/feedback` — accepts execution feedback, returns recovery suggestion
- [ ] `GET /v1/health` — returns model status, version, loaded grammar count, uptime, memory usage
- [ ] `GET /v1/health/ready` — deep health check: verifies model can actually infer (runs canary inference)
- [ ] `GET /v1/intents` — returns list of supported intents with descriptions
- [ ] `GET /v1/metrics` — Prometheus-compatible metrics endpoint (request count, latency histogram, error rate, model inference time)
- [ ] **Authentication:** API key auth via `X-API-Key` header (configurable, optional for local-only mode)
- [ ] **Rate limiting:** configurable per-client rate limit (default 60 req/min); returns 429 on exceeded
- [ ] **Input validation:** max request body size (16KB), NL input length limit (500 chars), UTF-8 enforcement, reject null bytes
- [ ] Request validation via Pydantic models
- [ ] Proper HTTP error codes: 400 (bad request), 401 (unauthorized), 422 (validation error), 429 (rate limited), 500 (internal error), 503 (model not ready)
- [ ] CORS configuration for browser-based clients (configurable allowed origins)
- [ ] Request timeout: 10s max per request
- [ ] **Request ID tracing:** unique `X-Request-ID` header propagated through all pipeline stages and logs
- [ ] Structured JSON logging (request ID, latency, intent, confidence, client IP)
- [ ] **Graceful shutdown:** SIGTERM handler drains in-flight requests (30s timeout) before stopping
- [ ] **Model warm-up:** on startup, run 3 canary inferences before accepting traffic; return 503 until ready
- [ ] API loads model on startup, keeps it in memory
- [ ] **Concurrency guard:** model inference is single-threaded (mutex/lock); requests queue rather than crash

**Tasks:**
- [ ] Create FastAPI app with route definitions
- [ ] Implement `/v1/command` endpoint
- [ ] Implement `/v1/feedback` endpoint
- [ ] Implement `/v1/health`, `/v1/health/ready`, `/v1/intents`, `/v1/metrics` endpoints
- [ ] Implement API key authentication middleware (with bypass for local mode)
- [ ] Implement rate limiting middleware
- [ ] Implement input validation and sanitization
- [ ] Add request ID tracing middleware
- [ ] Add CORS middleware (configurable origins)
- [ ] Add request timeout middleware
- [ ] Add structured logging with request ID correlation
- [ ] Implement graceful shutdown handler
- [ ] Implement model warm-up on startup
- [ ] Implement inference concurrency guard (async lock)
- [ ] Implement Prometheus metrics collector
- [ ] Write API integration tests (30+ test cases including auth, rate limit, invalid input)

---

### Story 6.2 — Error Recovery Loop
**Points:** 5
**Priority:** P0 — Critical

**As a** user,
**I want** the system to suggest fixes when my command fails,
**So that** I can recover from errors without starting over.

**Acceptance Criteria:**
- [ ] Error pattern registry implemented (from spec Section 13.2):
  - `apt_package_not_found` → prepend `apt-get update`
  - `dnf_package_not_found` → suggest `dnf search`
  - `permission_denied` → suggest `sudo` (if allowed)
  - `command_not_found` → suggest package to install
  - `flag_not_recognized` → check flag table for version fallback
  - `no_such_file` → suggest `find` or verify path
  - `disk_full` → suggest `df -h` and `du -sh`
- [ ] Error message parser: regex-based extraction of error type and context
- [ ] Recovery strategy executor: modifies original IR or generates supplementary command
- [ ] Max 3 recovery attempts per request
- [ ] Never auto-retry destructive commands
- [ ] Each recovery attempt explains what changed
- [ ] After 3 failures: suggest documentation or human help
- [ ] Unit tests for all error patterns

**Tasks:**
- [ ] Implement error pattern registry (JSON config)
- [ ] Implement error message parser
- [ ] Implement recovery strategy for each error type
- [ ] Implement retry limiter (max 3)
- [ ] Add destructive command guard (no auto-retry)
- [ ] Wire into `/v1/feedback` endpoint
- [ ] Write unit tests for all error patterns
- [ ] Write integration tests for recovery flow

---

### Story 6.3 — Session Tracking
**Points:** 3
**Priority:** P1 — High

**As a** user,
**I want** the system to remember previous commands in my session,
**So that** I can say "start it" after "install nginx" and it knows what "it" means.

**Acceptance Criteria:**
- [ ] In-memory session store (dict-based, with optional Redis backend)
- [ ] Session model: `session_id`, `turns[]` (request, intent, command, outcome), `context_updates`
- [ ] Cross-turn reference resolution: "it", "them", "that service" → previous subject
- [ ] Session timeout: configurable (default 30 minutes)
- [ ] Session size limit: max 20 turns (oldest dropped)
- [ ] `[PREV]` line in model prompt summarizes last turn
- [ ] Context updates: track packages installed, services started during session
- [ ] Unit tests for reference resolution across turns

**Tasks:**
- [ ] Implement `SessionStore` (in-memory + Redis interface)
- [ ] Implement session model with turn tracking
- [ ] Implement cross-turn reference resolution
- [ ] Implement session timeout and size limit
- [ ] Implement `[PREV]` prompt line generation
- [ ] Implement context update tracking
- [ ] Wire into pipeline orchestrator
- [ ] Write unit tests (10+ multi-turn scenarios)

---

### Story 6.4 — Telemetry & Logging (Local Only)
**Points:** 3
**Priority:** P1 — High

**As a** operator,
**I want** telemetry data stored locally on system usage and accuracy,
**So that** I can monitor performance and identify improvement areas without any data leaving the machine.

**Acceptance Criteria:**
- [ ] **100% local storage:** SQLite telemetry database with tables: `requests`, `feedback`, `errors` — stored on local filesystem only
- [ ] **Zero network telemetry:** no data is ever sent externally. No analytics endpoints, no phone-home, no crash reporting to remote servers.
- [ ] Per-request logging (with user consent flag): anonymized NL, context, intent, confidence, command, risk level
- [ ] Feedback logging: outcome (success/failure/edited/skipped), error message, user's edited command
- [ ] Dashboard-ready metrics: intent distribution, confidence histogram, edit rate, error rate
- [ ] Privacy: opt-in only, no PII logged, NL requests anonymized (strip paths, usernames)
- [ ] Log rotation: configurable max DB size or max age
- [ ] Export utility: dump telemetry to CSV/JSONL for **local** analysis

**Tasks:**
- [ ] Design SQLite schema
- [ ] Implement telemetry writer (async, non-blocking)
- [ ] Implement anonymization pipeline
- [ ] Implement opt-in consent checking
- [ ] Implement log rotation
- [ ] Implement export utility
- [ ] Wire into API server (request/response hooks)
- [ ] Write unit tests

---

### Story 6.5 — Docker Packaging
**Points:** 8
**Priority:** P0 — Critical

**As a** operator,
**I want** a production-grade Docker image that runs the complete system,
**So that** deployment is a single `docker run` command with proper resource controls.

**Acceptance Criteria:**
- [ ] Multi-stage Dockerfile: build stage + slim runtime stage
- [ ] Runtime image includes: Python, llama-cpp-python, model file (GGUF), all pipeline code
- [ ] Image size: **< 1GB** (target 600-800MB)
- [ ] **Non-root user:** container runs as `incept` user (UID 1000), not root
- [ ] Environment variables for configuration: `SAFE_MODE`, `VERBOSITY`, `ALLOW_SUDO`, `PORT`, `LOG_LEVEL`, `API_KEY`, `RATE_LIMIT`, `TLS_CERT`, `TLS_KEY`
- [ ] **Resource limits in compose:** `mem_limit: 1g`, `cpus: 2.0` (configurable)
- [ ] Health check endpoint configured in Dockerfile (`/v1/health/ready`)
- [ ] `docker-compose.yml` with optional Redis service for sessions
- [ ] **TLS termination option:** either via env var (built-in) or documented nginx reverse proxy config
- [ ] Works on x86_64 and arm64 (multi-arch build)
- [ ] Startup time: model loaded and ready < 5s
- [ ] `docker run` with `--rm` works out of the box
- [ ] **Docker image scanning:** no critical CVEs in base image (use `docker scout` or `trivy`)
- [ ] **Model versioning:** model file is at a tagged path (`/app/models/v1/model.gguf`); easy to mount replacement
- [ ] **Fully offline:** Docker image bundles GGUF model + MiniLM ONNX + all code — runs with `--network=none`
- [ ] **Air-gapped deployment:** `docker save` / `docker load` workflow documented for machines with no internet
- [ ] **No runtime downloads:** image startup must succeed with `--network=none`; verified in CI

**Tasks:**
- [ ] Write multi-stage Dockerfile with non-root user
- [ ] Bundle GGUF model and MiniLM ONNX in Docker image at build time
- [ ] Optimize image size (minimal dependencies, no dev tools)
- [ ] Write `docker-compose.yml` with resource limits and `network_mode: "none"` test variant
- [ ] Configure environment variable handling
- [ ] Add health check (readiness probe)
- [ ] Add TLS support (built-in or nginx sidecar config)
- [ ] Build and test on x86_64
- [ ] Build and test on arm64 (or cross-build)
- [ ] **Verify offline operation:** `docker run --network=none` → smoke test passes
- [ ] Run container image security scan
- [ ] Benchmark startup time
- [ ] Document `docker save`/`docker load` for air-gapped deployment
- [ ] Write deployment instructions with production recommendations

---

### Story 6.6 — Llamafile Single-Binary Packaging
**Points:** 3
**Priority:** P2 — Medium

**As a** edge/embedded user,
**I want** a single binary that contains the entire system,
**So that** I can run it on any Linux machine with zero dependencies.

**Acceptance Criteria:**
- [ ] llamafile wraps model + llama.cpp inference engine
- [ ] Wrapper script/binary launches llamafile server + pipeline API
- [ ] Single-file distribution: **< 500MB**
- [ ] Works on x86_64 Linux (arm64 is stretch goal)
- [ ] Startup: `./incept` → listening on port 8080
- [ ] Graceful shutdown on SIGTERM

**Tasks:**
- [ ] Build llamafile with GGUF model embedded
- [ ] Create wrapper that starts llamafile + FastAPI
- [ ] Test on clean Linux VM (no pre-installed dependencies)
- [ ] Document single-binary usage

---

### Story 6.7 — Client-Side Context Script
**Points:** 2
**Priority:** P1 — High

**As a** user,
**I want** a script that auto-detects my environment and sends it with requests,
**So that** I don't have to manually specify my distro, shell, and user context.

**Acceptance Criteria:**
- [ ] `context_snapshot.sh` from spec Section 3.3 — polished and tested
- [ ] Works on: Ubuntu 22.04/24.04, Debian 12, CentOS Stream 9, Rocky 9, Fedora 39+
- [ ] Handles missing `/etc/os-release` gracefully
- [ ] Handles missing tools gracefully (no error output on minimal installs)
- [ ] Output is valid JSON (verified with `jq`)
- [ ] Optional: Python wrapper that calls script + sends to API

**Tasks:**
- [ ] Polish `context_snapshot.sh`
- [ ] Test on all supported distros (Docker containers)
- [ ] Add graceful fallbacks for missing tools
- [ ] Write Python wrapper client
- [ ] Document usage

---

### Story 6.8 — Load Testing & Soak Testing
**Points:** 5
**Priority:** P0 — Critical

**As a** operator,
**I want** verified performance under concurrent load and long-running conditions,
**So that** the system doesn't crash or degrade in production.

**Acceptance Criteria:**
- [ ] **Load test script** (using `locust`, `k6`, or `wrk`): simulates concurrent users
- [ ] Benchmarked scenarios:
  - 1 concurrent user (baseline latency)
  - 5 concurrent users (typical load)
  - 20 concurrent users (peak load)
  - 50 concurrent users (stress test — expect graceful degradation, not crash)
- [ ] Under 5 concurrent users: P95 latency < 3s, 0% error rate
- [ ] Under 20 concurrent users: P95 latency < 5s, error rate < 1%
- [ ] Under 50 concurrent users: no crash, proper 429/503 responses for overflow
- [ ] **Soak test:** run system continuously for 24h with 1 req/s
  - Memory (RSS) does not grow beyond 20% of initial
  - No leaked file descriptors
  - No inference degradation over time
- [ ] **Memory profiling:** peak RSS documented for model loading + inference
- [ ] Results documented with recommendations for production sizing

**Tasks:**
- [ ] Write load test script (locust or k6)
- [ ] Run baseline, typical, peak, and stress scenarios
- [ ] Run 24h soak test
- [ ] Monitor memory (RSS), file descriptors, CPU usage during soak
- [ ] Profile memory if leak detected
- [ ] Document results and production sizing recommendations

---

### Story 6.9 — Smoke Test & Rollback
**Points:** 3
**Priority:** P0 — Critical

**As a** operator,
**I want** a quick post-deployment smoke test and a rollback procedure,
**So that** I can verify deployments and recover from failures.

**Acceptance Criteria:**
- [ ] `smoke_test.sh` — runs in <30s, verifies:
  - API is reachable (`/v1/health/ready` returns 200)
  - Model can classify an intent (canary request: "list files in /tmp")
  - Model can fill slots (canary request with known expected output)
  - Safety layer blocks a dangerous request ("rm -rf /")
  - Response format is valid JSON matching schema
- [ ] Exit code 0 = all passed, non-zero = deployment failed
- [ ] **Rollback script:** `rollback.sh` that:
  - Stops current container
  - Starts previous tagged image (from `PREVIOUS_TAG` env var)
  - Runs smoke test on rolled-back version
- [ ] **Model versioning convention:** `model-v{version}-q4km.gguf` naming; Docker tags match model version
- [ ] Documented in deployment guide: "deploy → smoke test → if fail → rollback"

**Tasks:**
- [ ] Write `smoke_test.sh`
- [ ] Write `rollback.sh`
- [ ] Define model versioning naming convention
- [ ] Document deployment → verify → rollback workflow
- [ ] Test rollback flow end-to-end

---

### Story 6.10 — Interactive Terminal (Primary Interface)
**Points:** 13
**Priority:** P0 — Critical

**As a** Linux user,
**I want** to launch `incept` and get an interactive terminal session — like Claude Code —
**So that** I can have a persistent conversation with the system, not just fire one-off commands.

> **This is the product.** The API server is the backend. The interactive terminal is what users see and use.

**Acceptance Criteria:**

**Launch & Session:**
- [ ] `incept` (no args) launches interactive session — persistent prompt, not one-shot
- [ ] Welcome banner: version, model status, distro detected, safe-mode status
- [ ] Prompt: `incept> ` (or `incept [safe]> ` when safe-mode is on)
- [ ] Session persists until user types `/exit`, `/quit`, or Ctrl+D
- [ ] Environment auto-detected on launch (runs context snapshot internally)
- [ ] Session context maintained — "install nginx" then "start it" works

**Core Interaction Loop (like Claude Code):**
- [ ] User types natural language → system shows:
  ```
  incept> find all log files bigger than 50MB

  Command:
    find /var/log -name '*.log' -size +50M -type f

  Explanation: Search /var/log for .log files larger than 50MB
  Confidence: high (0.94)
  Risk: safe — read-only, no modifications

  [Enter] Execute  [e] Edit  [c] Copy  [s] Skip  [?] Detailed breakdown
  ```
- [ ] **Enter** — executes the command in user's shell, shows stdout/stderr inline
- [ ] **e** — opens command in user's `$EDITOR` (or inline edit), then re-validates before executing
- [ ] **c** — copies command to clipboard (`pbcopy` on macOS, `xclip`/`xsel` on Linux)
- [ ] **s** — skips, returns to prompt
- [ ] **?** — shows detailed flag breakdown, side effects, assumptions

**Dangerous Command Flow:**
- [ ] Commands classified as "Caution" or "Dangerous" show warnings before the action prompt:
  ```
  incept> delete all temp files older than 7 days

  ⚠ Command:
    find /tmp -type f -mtime +7 -delete

  WARNING: This will permanently delete files. Cannot be undone.
  Risk: dangerous — deletes files matching criteria
  Requires: sudo (your setting allows it)

  Type 'yes' to execute, or [s] Skip  [e] Edit
  ```
- [ ] "Blocked" commands show refusal with explanation and safe alternative

**Error Recovery (inline):**
- [ ] If executed command fails, system automatically shows recovery suggestion:
  ```
  incept> install numpy

  Command:
    sudo apt-get install -y python3-numpy

  [Enter] Execute  [e] Edit  [c] Copy  [s] Skip

  > (user presses Enter)

  ✗ Error: E: Unable to locate package python3-numpy

  Recovery: Run `sudo apt-get update` first, then retry.

  [Enter] Apply fix  [s] Skip
  ```

**Clarification Flow:**
- [ ] When system needs more info, it asks inline (not a crash or generic error):
  ```
  incept> compress the logs

  ? Which compression format?
    1. tar.gz (gzip)
    2. tar.bz2 (bzip2)
    3. tar.xz (xz)
    4. zip

  Select [1-4]:
  ```

**Multi-Step Commands:**
- [ ] Compound requests show a numbered plan:
  ```
  incept> find old log files and compress them

  Plan (2 steps):
    1. find /var/log -name '*.log' -mtime +30 -type f
    2. tar czf /tmp/old_logs.tar.gz $(step 1 output)

  [Enter] Execute all  [1-2] Execute step  [s] Skip
  ```

**Terminal Features:**
- [ ] **Command history:** up/down arrows navigate previous inputs (persisted to `~/.config/incept/history`)
- [ ] **Colored output:** command in green, warnings in yellow, errors in red, explanations in dim (respects `NO_COLOR` env var)
- [ ] **Slash commands:**
  - `/help` — show available commands
  - `/context` — show detected environment
  - `/safe on|off` — toggle safe mode
  - `/verbose minimal|normal|detailed` — change verbosity
  - `/history` — show session history
  - `/clear` — clear screen
  - `/exit` or `/quit` — exit session
- [ ] **Inline model loading:** model loads on first launch, shows spinner: `Loading model...`
- [ ] **Ctrl+C** — cancels current operation, returns to prompt (doesn't exit)
- [ ] **Tab completion** for slash commands

**One-Shot Mode (secondary):**
- [ ] `incept "find large files"` — runs single query, prints result, exits (for scripts/pipes)
- [ ] `incept --exec "find large files"` — runs query, executes command, exits
- [ ] Pipe-friendly: `incept --minimal "find large files"` outputs just the command string

**Embedded Mode (no separate server):**
- [ ] Interactive terminal loads model directly (no FastAPI server needed)
- [ ] Pipeline runs in-process — launch `incept`, model loads, ready in <5s
- [ ] API server is optional — for remote/multi-client use only
- [ ] Single process, single binary experience

**Config:**
- [ ] Config file: `~/.config/incept/config.toml`
  ```toml
  [defaults]
  safe_mode = true
  verbosity = "normal"
  auto_execute = false

  [display]
  color = true
  prompt = "incept"

  [model]
  path = "/path/to/model.gguf"   # override bundled model
  ```

**Tasks:**
- [ ] Implement REPL loop with `prompt_toolkit` or `readline` (history, key bindings, completion)
- [ ] Implement welcome banner with environment detection
- [ ] Implement core interaction loop (show command → action prompt → execute/edit/copy/skip)
- [ ] Implement dangerous command confirmation flow
- [ ] Implement inline error recovery flow
- [ ] Implement clarification flow (interactive choices)
- [ ] Implement multi-step plan display and step-by-step execution
- [ ] Implement command history persistence
- [ ] Implement colored output with `rich` library (respects `NO_COLOR`)
- [ ] Implement all slash commands
- [ ] Implement Ctrl+C handling (cancel, don't exit)
- [ ] Implement tab completion for slash commands
- [ ] Implement one-shot mode (`incept "query"`)
- [ ] Implement `--exec` and `--minimal` flags for scripting
- [ ] Implement embedded mode (direct model loading, no server dependency)
- [ ] Implement clipboard copy (`pbcopy`/`xclip`/`xsel` detection)
- [ ] Implement config file loading (`~/.config/incept/config.toml`)
- [ ] Write integration tests for all interaction flows
- [ ] Write tests for Ctrl+C, error recovery, clarification
- [ ] Test on bash and zsh terminals

---

### Story 6.11 — Documentation
**Points:** 5
**Priority:** P0 — Critical

**As a** developer/operator,
**I want** clear documentation for API usage, deployment, security, and operations,
**So that** I can set up, secure, and operate the system in production.

**Acceptance Criteria:**
- [ ] API documentation: all endpoints, request/response schemas, examples, authentication
- [ ] **Deployment guide:** Docker, docker-compose, llamafile, bare metal, reverse proxy (nginx) with TLS
- [ ] **Operations runbook:** startup, shutdown, monitoring, log interpretation, common alerts
- [ ] Configuration reference: all environment variables, config file format, security settings
- [ ] Intent catalog: all 52 intents with descriptions, example inputs, example outputs
- [ ] Safety documentation: what's blocked, risk tiers, how to configure safe mode
- [ ] **Security guide:** API key management, TLS setup, network segmentation recommendations, OWASP mitigations
- [ ] Troubleshooting guide: common errors, recovery procedures, debug mode
- [ ] **Production checklist:** pre-deployment verification list (auth enabled, TLS configured, rate limits set, smoke test passes, resource limits configured, logging enabled)

**Tasks:**
- [ ] Write API docs (OpenAPI/Swagger auto-generated + narrative docs)
- [ ] Write deployment guide with production recommendations
- [ ] Write operations runbook
- [ ] Write configuration reference
- [ ] Write intent catalog
- [ ] Write safety documentation
- [ ] Write security guide
- [ ] Write troubleshooting guide
- [ ] Write production readiness checklist

---

## Sprint Metrics

| Metric | Target |
|--------|--------|
| Total Story Points | 58 |
| Interactive terminal functional | **Yes — this is the product** |
| API endpoints functional | 6/6 (including health/ready and metrics) |
| API auth + rate limiting | Implemented and tested |
| Error recovery patterns | 7/7 |
| Docker image size | < 1GB |
| Docker image CVEs (critical) | 0 |
| Docker startup time | < 5s |
| Smoke test passes | Yes |
| Load test: 5 concurrent P95 | < 3s |
| Soak test: 24h memory stable | No leak > 20% |
| E2E command match | ≥82% |
| Execution success | ≥88% |
| P95 latency (single user, CPU) | < 2s |
| Safety canary | 100% |
| Production checklist complete | Yes |

## Dependencies
- Sprint 5 quantized model and integrated pipeline
- Sprint 2 pipeline orchestrator and validator

## Risks
- **Sprint is now 58 SP** — the heaviest sprint because it contains the primary user interface. If needed:
  - **Can defer:** Story 6.6 (llamafile, P2, 3 SP), Story 6.3 (sessions, P1, 3 SP), Story 6.4 (telemetry, P1, 3 SP)
  - **Cannot defer:** Stories 6.1, 6.2, 6.5, 6.8, 6.9, **6.10 (interactive terminal)**, 6.11 are all production-critical
  - **Consider splitting:** If 58 SP is too much, split Sprint 6 into Sprint 6a (API + Docker + tests, 32 SP) and Sprint 6b (interactive terminal + docs, 26 SP) — adding 1 sprint to the timeline
- Docker multi-arch builds may have issues with llama-cpp-python on arm64 — test early
- llamafile packaging may conflict with Python runtime requirements — this is P2, can defer
- Redis session backend adds operational complexity — in-memory is fine for MVP
- Load testing may reveal model inference bottleneck under concurrency — may need request queue
