# INCEPT

**Offline natural-language to Linux/macOS command compiler using constrained small-model decoding.**

INCEPT translates plain English requests like *"find all log files larger than 100MB"* into the correct shell command for your distro — entirely offline, with no cloud API calls.

[![CI](https://github.com/ProMohanad/INCEPT.sh/actions/workflows/ci.yml/badge.svg)](https://github.com/ProMohanad/INCEPT.sh/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

---

## Features

- **78 intents** — file ops, text processing, packages, services, networking, Docker, Git, firewall, cron, disk, SSH, and more
- **5 distro families** — Debian/Ubuntu, RHEL/Fedora, Arch, openSUSE, macOS (brew/launchctl)
- **Fully offline** — runs on a quantized 0.5B-parameter model (Qwen2.5-0.5B Q4_K_M, ~250MB), no internet required
- **Explain mode** — paste a command, get a structured plain-English explanation with risk assessment
- **Safety layer** — 22 banned patterns, 4 risk levels (safe/caution/dangerous/blocked), safe-mode toggle
- **Shell plugin** — Ctrl+I keybinding for bash and zsh; type in English, get the command inline
- **REST API** — FastAPI server with auth, per-IP rate limiting, security headers, session tracking
- **Interactive REPL** — slash commands, multi-turn context, command history, clipboard support

## Quick Start

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[cli,server]"
```

> **Note:** Requires Python 3.11+ and pip 21.3+. The editable install uses `pyproject.toml` with hatchling, which older pip versions don't support. The virtual environment ensures a compatible pip.

### Interactive REPL

```bash
incept
```

```
incept> install nginx
  apt-get install 'nginx'       # Debian/Ubuntu
  dnf install 'nginx'           # RHEL/Fedora
  pacman -S 'nginx'             # Arch
  brew install 'nginx'          # macOS

incept> /explain tar -czf backup.tar.gz /var/log
  Command: tar -czf backup.tar.gz /var/log
  Intent:  compress_archive
  Risk:    safe
  Explanation: Create a compressed archive...
```

### One-Shot Mode

```bash
# Translate to command
incept "find all python files modified in the last 7 days"

# Output only the raw command (for scripts)
incept --minimal "find all python files modified in the last 7 days"

# Explain a command
incept --explain "grep -rn 'TODO' --include='*.py' ."
```

### Shell Plugin (Ctrl+I)

```bash
# Install for your current shell
incept plugin install

# Or specify the shell
incept plugin install --shell zsh
incept plugin install --shell bash
```

Then type a request in your terminal and press **Ctrl+I** — it gets replaced with the generated command.

### API Server

```bash
# Start the server
incept serve --host 0.0.0.0 --port 8080

# Or with environment variables
INCEPT_API_KEY=my-secret-key incept serve
```

```bash
# Translate
curl -X POST http://localhost:8080/v1/command \
  -H "Content-Type: application/json" \
  -d '{"nl": "install nginx"}'

# Explain
curl -X POST http://localhost:8080/v1/explain \
  -H "Content-Type: application/json" \
  -d '{"command": "grep -rn error /var/log"}'
```

## Architecture

```
User Input ("install nginx")
      │
      ▼
┌─────────────┐
│ Preclassifier│──→ intent: install_package, confidence: 0.95
└──────┬──────┘
       ▼
┌─────────────┐
│  Decomposer │──→ single step (or multi-step split)
└──────┬──────┘
       ▼
┌─────────────┐
│   Compiler  │──→ routes to distro-specific compiler
│  (78 intents│    uses flag tables + distro maps
│   5 distros)│
└──────┬──────┘
       ▼
┌─────────────┐
│  Validator  │──→ risk: safe / caution / dangerous / blocked
└──────┬──────┘
       ▼
┌─────────────┐
│  Formatter  │──→ "apt-get install 'nginx'"
└─────────────┘
```

See [docs/architecture.md](docs/architecture.md) for full component diagrams with module-level dependency maps.

## Project Structure

```
incept/
├── cli/            # Click CLI, REPL, shell plugin, slash commands
├── core/           # Pipeline orchestrator, preclassifier, decomposer, context
├── compiler/       # Intent → shell command (file, text, system, expanded ops)
├── explain/        # Reverse pipeline: command → NL explanation (17 parsers)
├── schemas/        # Pydantic IR models, 78 intents, 13 param model groups
├── safety/         # Validator: 22 banned patterns, 4 risk levels
├── server/         # FastAPI app, 5 middleware layers, 6 route groups
├── session/        # Multi-turn sessions with pronoun resolution
├── recovery/       # Error classification + recovery suggestions (7 patterns)
├── retrieval/      # BM25 index, distro maps (packages, services, paths)
├── telemetry/      # SQLite logging, PII anonymization, export
├── templates/      # Response formatting, explanation templates
├── confidence/     # Confidence scoring
├── grammars/       # GBNF grammar files for constrained decoding
├── training/       # SFT, DPO trainers, benchmarking, export
├── data/           # Training data generation, assembly, conversion
└── eval/           # Intent/slot evaluation metrics + reporting
```

## Supported Intents (78)

| Category | Intents | Examples |
|----------|---------|----------|
| File Operations | 12 | find, copy, move, delete, chmod, chown, mkdir, ls, du, cat, ln, diff |
| Text Processing | 6 | grep, sed, sort, wc, awk/cut, uniq |
| Archive | 2 | tar/zip create, tar/zip extract |
| Package Management | 4 | install, remove, update, search |
| Service Management | 5 | start, stop, restart, enable, status |
| User Management | 3 | useradd, userdel, usermod |
| Log Operations | 3 | view, follow, filter |
| Scheduling | 3 | crontab add/list/remove |
| Networking | 6 | ifconfig/ip, ping, wget/curl, scp/rsync, ssh, ss/lsof |
| Process Management | 3 | ps, kill, uname/uptime |
| Docker | 6 | run, ps, stop, logs, build, exec |
| Git | 7 | status, commit, push, pull, log, diff, branch |
| SSH Keys | 2 | ssh-keygen, ssh-copy-id |
| Disk | 4 | mount, umount, lsblk/diskutil, fsck |
| Firewall | 3 | allow, deny, list |
| DNS | 2 | dig, host/nslookup |
| Environment | 2 | export, env/printenv |
| Systemd Timers | 2 | create, list |
| Special | 3 | CLARIFY, OUT_OF_SCOPE, UNSAFE_REQUEST |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `INCEPT_HOST` | `0.0.0.0` | Server bind address |
| `INCEPT_PORT` | `8080` | Server port |
| `INCEPT_API_KEY` | *(none)* | Bearer token for API auth |
| `INCEPT_RATE_LIMIT` | `60` | Requests per minute per IP |
| `INCEPT_REQUEST_TIMEOUT` | `30.0` | Request timeout in seconds |
| `INCEPT_CORS_ORIGINS` | *(none)* | Allowed CORS origins (comma-separated) |
| `INCEPT_MODEL_PATH` | *(none)* | Path to GGUF model file |
| `INCEPT_SAFE_MODE` | `true` | Block destructive commands |
| `INCEPT_LOG_LEVEL` | `info` | Logging level |
| `INCEPT_TRUST_PROXY` | `false` | Trust X-Forwarded-For for rate limiting |
| `INCEPT_MAX_SESSIONS` | `1000` | Maximum concurrent sessions |

## Development

```bash
# Create venv and install all dev dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[cli,server,dev]"

# Run tests (2,073 tests)
make test

# Lint
make lint

# Type check
make typecheck

# Format
make format

# All checks
make lint && make typecheck && make test
```

### Docker

```bash
# Build
make docker-build

# Run (fully offline — no network needed)
docker run --network=none -p 8080:8080 incept

# Smoke test
make smoke
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/command` | Translate NL → shell command |
| `POST` | `/v1/explain` | Explain a shell command |
| `POST` | `/v1/feedback` | Submit feedback / trigger recovery |
| `GET`  | `/v1/health` | Health check (model readiness) |
| `GET`  | `/v1/intents` | List supported intents |
| `GET`  | `/v1/metrics` | Prometheus metrics |

## Security

- **Offline-only** — zero outbound network calls at runtime
- **22 banned patterns** — `rm -rf /`, `:(){ :|:& };:`, `mkfs`, `dd if=/dev/zero`, etc.
- **4 risk levels** — safe, caution, dangerous, blocked
- **Per-IP rate limiting** with token bucket algorithm
- **7 security headers** — HSTS, CSP, X-Frame-Options, X-Content-Type-Options, etc.
- **Non-root Docker** container with resource limits
- **Table whitelist** on telemetry SQL to prevent injection
- **Session limits** to prevent resource exhaustion

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

## Documentation

- [Architecture & Diagrams](docs/architecture.md)
- [API Reference](docs/api.md)
- [Intent Catalog](docs/intent-catalog.md)
- [Safety & Risk Model](docs/safety.md)
- [Security](docs/security.md)
- [Configuration Reference](docs/config-reference.md)
- [Deployment Guide](docs/deployment.md)
- [Operations Runbook](docs/operations.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Production Checklist](docs/production-checklist.md)

## License

[Apache License 2.0](LICENSE)
