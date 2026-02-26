# Sprint 8: macOS + Explain Mode + Hardening + Shell Plugin

**Duration:** 2 weeks (post-MVP)
**Total Story Points:** 34
**Approach:** TDD — tests written first, then implementation
**Final Test Count:** 2,073 (240 new tests added)

---

## Sprint Goal

Extend INCEPT beyond the Linux MVP with macOS as the 5th distro family, add a reverse
pipeline (explain mode) for command-to-explanation, harden the server with per-IP rate
limiting and security headers, and ship the deferred shell plugin.

---

## Stories

| ID | Story | SP | Priority | Status |
|----|-------|-----|----------|--------|
| **8.1** | macOS distro family support | 8 | P1 | DONE |
| **8.2** | Explain mode — reverse pipeline | 8 | P1 | DONE |
| **8.3** | Security hardening (4 sub-stories) | 8 | P1 | DONE |
| **8.4** | Shell plugin for bash/zsh | 5 | P2 | DONE |

---

## Story 8.1: macOS Distro Family (8 SP)

**Acceptance Criteria:**
- `EnvironmentContext(distro_family="macos")` accepted by type system
- `compile_install_package({"package": "nginx"}, macos_ctx)` returns `"brew install 'nginx'"`
- All 13 compiler function families have macOS branches
- Darwin detected via `uname -s` in context snapshot script
- macOS entries in all package/service/path maps
- `/System`, `/Library`, `/Applications` flagged as system-critical paths
- 119 new tests passing

**Files Modified:** `context.py`, `system_ops.py`, `expanded_ops.py`, `file_ops.py`,
`distro_maps.py`, `slot_pools.py`, `validator.py`

**New Files:** `tests/test_compilers_macos.py`

---

## Story 8.2: Explain Mode (8 SP)

**Acceptance Criteria:**
- `run_explain_pipeline("apt-get install nginx")` returns structured ExplainResponse
- 17 inverse parsers cover major command families
- `POST /v1/explain` returns 200 with explanation
- `--explain` CLI flag works in one-shot mode
- `/explain` REPL slash command works
- Unknown commands return `intent=None, explanation="Unrecognized command"`
- Dangerous commands get appropriate `risk_level`
- 104 new tests passing

**New Files:** `incept/explain/__init__.py`, `parsers.py`, `registry.py`, `pipeline.py`,
`incept/server/routes/explain.py`, `tests/test_explain_parsers.py`,
`tests/test_explain_pipeline.py`, `tests/test_cli_explain.py`, `tests/test_server_explain.py`

---

## Story 8.3: Security Hardening (8 SP)

### 8.3a — Per-Client-IP Rate Limiting (3 SP)

- Each client IP gets an independent token bucket
- `X-Forwarded-For` used when `trust_proxy=true`
- Stale buckets cleaned after 5 min inactivity
- `X-RateLimit-Remaining` and `Retry-After` response headers
- 15 new tests

### 8.3b — Security Headers Middleware (2 SP)

- 7 security headers on every response
- Does not overwrite custom headers
- 11 new tests

### 8.3c — Max Session Count (2 SP)

- `max_sessions=1000` default, `SessionLimitError` on overflow
- Expired sessions cleaned before rejecting
- `max_sessions=0` means unlimited
- 10 new tests (extending existing test file)

### 8.3d — Telemetry Table Whitelist (1 SP)

- Only `requests`, `feedback`, `errors` permitted
- SQL injection via table name blocked
- 6 new tests (extending existing test file)

---

## Story 8.4: Shell Plugin (5 SP)

**Acceptance Criteria:**
- `scripts/plugins/incept.bash` passes `bash -n` syntax check
- `scripts/plugins/incept.zsh` passes `zsh -n` syntax check
- Both scripts bind Ctrl+I and call `incept --minimal`
- `incept plugin install` appends source line idempotently
- `incept plugin uninstall` removes source line
- Shell type auto-detected from `$SHELL`
- Empty input handled gracefully
- 28 new tests passing

**New Files:** `scripts/plugins/incept.bash`, `scripts/plugins/incept.zsh`,
`incept/cli/shell_plugin.py`, `tests/test_shell_plugin.py`

---

## Verification Results

| Check | Result |
|-------|--------|
| `pytest tests/` | 2,073 passed, 0 failed |
| `ruff check incept/ tests/` | All checks passed |
| `mypy incept/` | Success: no issues in 110 files |
