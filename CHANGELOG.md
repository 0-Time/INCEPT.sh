# Changelog

All notable changes to INCEPT will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-02-27 (Sprint 8: macOS + Explain Mode + Hardening + Shell Plugin)

### Added
- **macOS distro family support** — 5th distro family (`macos`/`darwin`). Compiler
  variants across all intent categories:
  - Package management: `brew install/uninstall/update/upgrade/search`.
  - Service management: `brew services start/stop/restart/info`.
  - Networking: `ifconfig` (not `ip`), `lsof -iTCP` (not `ss`), `ping -t` (not `-W`).
  - Process management: `ps aux` with `sort -rnk` pipe, `vm_stat`, `sysctl`.
  - Logs: `log show` (with `--predicate`, `--start`, `--last`), `log stream`.
  - Firewall: `pfctl` rules (`echo "pass/block ..." | sudo pfctl -ef -`).
  - Disk: `diskutil list`, `diskutil verifyDisk`.
  - File operations: `du -d` (not `--max-depth`) on macOS.
  - Darwin detection via `uname -s` in context snapshot script.
  - macOS entries in all package maps, service maps, and path defaults.
  - macOS system paths (`/System`, `/Library`, `/Applications`) added to safety validator.
- **Explain mode** — reverse pipeline: paste a shell command, get a structured NL
  explanation.
  - 17 inverse parsers covering apt-get, dnf, pacman, zypper, brew, systemctl,
    find, grep, sed, tar, docker, git, ssh, ufw, curl, wget, crontab.
  - `ExplainResponse` model with command, intent, explanation, flag explanations,
    side effects, risk level, and extracted parameters.
  - `POST /v1/explain` API endpoint.
  - `--explain` CLI flag for one-shot mode.
  - `/explain` REPL slash command.
  - Reuses existing `validate_command()` for risk assessment and explanation templates.
- **Shell plugin** for bash and zsh:
  - `scripts/plugins/incept.bash` — Ctrl+I keybinding via `bind -x`, reads
    `$READLINE_LINE`, calls `incept --minimal`.
  - `scripts/plugins/incept.zsh` — Ctrl+I keybinding via `zle -N` widget, reads
    `$BUFFER`, calls `incept --minimal`.
  - `incept plugin install [--shell bash|zsh]` — appends idempotent source line to
    rc file.
  - `incept plugin uninstall [--shell bash|zsh]` — removes the source line.
  - `/plugin` REPL slash command with installation instructions.

### Security
- **Per-client-IP rate limiting**: Each client IP gets an independent token bucket.
  Stale buckets auto-cleaned after 5 minutes of inactivity. Response headers include
  `X-RateLimit-Remaining` and `Retry-After`.
- **X-Forwarded-For support**: When `INCEPT_TRUST_PROXY=true`, the first IP in the
  `X-Forwarded-For` header is used as the client IP. Disabled by default.
- **Security headers middleware**: Every response includes `X-Content-Type-Options:
  nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`,
  `Content-Security-Policy: default-src 'none'`, `Referrer-Policy`,
  `Permissions-Policy`, `Cache-Control: no-store`.
- **Max session count**: Configurable limit (default: 1000) with
  `SessionLimitError`. Expired sessions are cleaned before rejecting new ones.
  Set to 0 for unlimited.
- **Telemetry table whitelist**: Only `requests`, `feedback`, and `errors` are valid
  table names. Any other table name raises `ValueError`, preventing SQL injection
  via table name interpolation.

### Changed
- Rate limiting upgraded from global single bucket to per-client-IP buckets.
- `ServerConfig` gains `trust_proxy` and `max_sessions` fields.
- `SessionStore` gains `max_sessions` enforcement.
- Distro family count: 4 → 5 (debian, rhel, arch, suse, macos).
- Test count: 1,833 → 2,073 (240 new tests).

## [0.3.0] - 2026-02-26 (Sprint 7: Expansion & Release)

### Added
- **Arch Linux support:** `pacman` compiler variants for package management intents
  (`install_package`, `remove_package`, `update_packages`, `search_package`).
- **openSUSE/SLES support:** `zypper` compiler variants for package management intents.
- Arch and SUSE default registries, package maps, and service maps.
- Context resolver detection for `ID=arch`, `ID=opensuse-leap`,
  `ID=opensuse-tumbleweed`, `ID=sles`, and `ID_LIKE` containing "arch".
- 26 new intents (78 total), including Docker operations (`docker_run`, `docker_ps`,
  `docker_stop`, `docker_logs`, `docker_build`, `docker_exec`), Git operations
  (`git_status`, `git_commit`, `git_push`, `git_pull`, `git_log`, `git_diff`,
  `git_branch`), SSH key management, disk/partition info, firewall rules,
  DNS lookups, environment variable management, and systemd timers.
- IR schemas, GBNF grammars, and compiler functions for all new intents.
- Golden test cases for Arch, SUSE, and all new intents.
- Expanded training data with 1000+ new distro-specific examples.
- `SECURITY.md` with vulnerability reporting instructions and responsible disclosure policy.
- `CONTRIBUTING.md` with development setup, coding standards, and PR process.
- `CHANGELOG.md` (this file).
- `LICENSE` file (Apache 2.0).
- `scripts/build_offline_bundle.sh` for building air-gapped distribution tarballs.
- GitHub Actions CI pipeline with lint, typecheck, test, and docker-build jobs.

### Changed
- Model retrained with expanded intent coverage and distro-specific data.
- CI pipeline upgraded with separate jobs for lint, typecheck, test, and Docker build.

### Security
- Full OWASP API Top 10 audit completed.
- Command injection audit: verified all compiler outputs pass through `shlex.quote()`,
  no `os.system()` or `subprocess.call(shell=True)` in codebase.
- Input validation audit across all API endpoints.
- Dependency audit (`pip audit`): zero known CVEs in production dependencies.
- Secrets scan (`gitleaks`): no API keys, passwords, or tokens in repository history.
- Container audit: non-root user, no unnecessary capabilities, resource limits enforced.

## [0.2.0] - 2026-02-12 (Sprint 6: Production Readiness)

### Added
- **FastAPI server** with production-grade endpoints:
  - `POST /v1/command` -- NL-to-command translation.
  - `POST /v1/feedback` -- execution feedback and error recovery.
  - `GET /v1/health` and `GET /v1/health/ready` -- health and readiness checks.
  - `GET /v1/intents` -- list supported intents.
  - `GET /v1/metrics` -- Prometheus-compatible metrics.
- **Interactive REPL terminal** (`incept` command) as the primary user interface:
  - Persistent session with command history.
  - Execute, edit, copy, or skip generated commands.
  - Dangerous command confirmation flow with risk warnings.
  - Inline error recovery with up to 3 retry attempts.
  - Clarification prompts for ambiguous requests.
  - Multi-step command plans with step-by-step execution.
  - Slash commands (`/help`, `/context`, `/safe`, `/verbose`, `/history`, `/clear`, `/exit`).
  - One-shot mode (`incept "query"`) and pipe-friendly output (`--minimal`).
  - Colored output via `rich` (respects `NO_COLOR`).
  - Tab completion for slash commands.
- **Error recovery loop** with 7 error pattern handlers:
  `apt_package_not_found`, `dnf_package_not_found`, `permission_denied`,
  `command_not_found`, `flag_not_recognized`, `no_such_file`, `disk_full`.
- **Session tracking** with in-memory session store, cross-turn reference resolution
  ("install nginx" then "start it"), session timeout (30 min), and context updates.
- **Local-only telemetry** with opt-in SQLite storage, anonymization pipeline,
  and CSV/JSONL export. Zero network telemetry -- no data leaves the machine.
- **Docker packaging:**
  - Multi-stage Dockerfile with non-root `incept` user.
  - `docker-compose.yml` with resource limits (1 GB memory, 2 CPUs).
  - Health check via `/v1/health/ready`.
  - Fully offline: runs with `--network=none`.
  - Air-gapped deployment via `docker save`/`docker load`.
- API key authentication via `X-API-Key` header (optional for local mode).
- Rate limiting (configurable, default 60 req/min).
- Input validation: 16 KB max body, 500 char NL limit, UTF-8 enforcement.
- Request ID tracing (`X-Request-ID`) through all pipeline stages.
- Structured JSON logging with request correlation.
- Graceful shutdown with in-flight request draining.
- Model warm-up on startup (3 canary inferences before accepting traffic).
- Inference concurrency guard (async lock for single-threaded model).
- `scripts/smoke_test.sh` -- 5-check post-deployment verification (<30s).
- `scripts/rollback.sh` -- automated rollback to previous Docker image tag.
- `scripts/load_test.py` -- Locust-based load testing script.
- Client-side `context_snapshot.sh` for environment auto-detection.
- Comprehensive documentation: API reference, deployment guide, operations runbook,
  configuration reference, intent catalog, safety guide, security guide,
  troubleshooting guide, and production readiness checklist.

### Changed
- Pipeline orchestrator now supports session-aware context injection.
- Confidence scoring integrated into API response format.

## [0.1.0] - 2026-01-15 (Sprints 1-5: Core Pipeline)

### Added
- **Core NL-to-command pipeline:**
  - Preclassifier: intent detection with confidence scoring.
  - Decomposer: multi-step request splitting (up to 4 sub-steps).
  - Slot filler: parameter extraction via constrained small-model decoding.
  - Compiler: IR-to-shell-command generation with distro-aware variants.
  - Validator: syntax validation via `bashlex`, safety checks, `shlex.quote()` sanitization.
  - Formatter: human-readable output with explanations and risk assessments.
- **52 intents** covering core Linux operations:
  - File management: `list_dir`, `find_files`, `copy_file`, `move_file`, `delete_file`,
    `create_dir`, `change_permissions`, `change_owner`, `disk_usage`, `archive_create`,
    `archive_extract`.
  - Package management: `install_package`, `remove_package`, `update_packages`,
    `search_package` (apt, dnf, yum variants).
  - Service management: `start_service`, `stop_service`, `restart_service`,
    `enable_service`, `service_status`.
  - Process management: `list_processes`, `kill_process`, `top_processes`.
  - Network: `check_port`, `network_info`, `download_file`, `ping_host`,
    `dns_lookup`, `curl_request`.
  - User/group management: `add_user`, `delete_user`, `add_group`, `modify_user`.
  - Text processing: `search_text`, `count_lines`, `sort_file`, `unique_lines`,
    `replace_text`, `head_file`, `tail_file`.
  - System: `system_info`, `check_memory`, `check_disk`, `uptime`, `hostname`,
    `set_timezone`, `schedule_cron`.
  - And more.
- **Pydantic IR schemas** for all 52 intents with typed parameter models.
- **GBNF grammars** for constrained decoding of each intent's slot structure.
- **Safety and validation layer:**
  - Three risk tiers: safe, caution, dangerous.
  - Blocked command patterns (e.g., `rm -rf /`, `mkfs` on mounted partitions).
  - `shlex.quote()` on all user-supplied parameters.
  - No `os.system()` or `shell=True` anywhere in the codebase.
- **Distro-aware compilation** for Ubuntu/Debian (apt), Fedora/RHEL/CentOS (dnf/yum),
  with package maps, service maps, and flag tables.
- **Training data pipeline:**
  - 15,000+ synthetic training examples across all intents.
  - Template-based generation with LLM paraphrasing.
  - Adversarial examples for safety hardening.
  - Flag tables for 50+ common Linux tools with version-specific flags.
- **Model training infrastructure:**
  - SFT (Supervised Fine-Tuning) with LoRA adapters on Qwen2.5-0.5B.
  - DPO (Direct Preference Optimization) for output quality improvement.
  - Adversarial training for safety robustness.
  - GGUF quantization (Q4_K_M) for efficient CPU inference.
  - `llama-cpp-python` integration for local inference.
- **Evaluation framework:**
  - Golden test suite with known-good input/output pairs.
  - Intent accuracy, slot exact-match, and slot F1 metrics.
  - Benchmark runner with structured reporting.
  - Baseline evaluation reports.
- **Retrieval-augmented context** for flag tables and package maps.
- **Confidence scoring** with calibrated thresholds for intent classification.
- **Project scaffold:** `pyproject.toml` with hatchling build, optional dependency
  groups (`dev`, `server`, `cli`, `ml`, `eval`), Makefile with standard targets.

[0.4.0]: https://github.com/incept-project/INCEPT/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/incept-project/INCEPT/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/incept-project/INCEPT/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/incept-project/INCEPT/releases/tag/v0.1.0
