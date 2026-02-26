# Security Policy

## Reporting a Vulnerability

The INCEPT team takes security seriously. If you discover a security vulnerability in
INCEPT, please report it responsibly. **Do NOT open a public GitHub issue for
security vulnerabilities.**

### How to Report

Send an email to: **security@incept-project.org**

Include the following in your report:

1. **Description** of the vulnerability.
2. **Steps to reproduce** the issue, including any relevant configuration.
3. **Impact assessment** -- what an attacker could achieve by exploiting this vulnerability.
4. **Affected versions** -- which version(s) of INCEPT are affected.
5. **Suggested fix** (optional) -- if you have a proposed patch or mitigation.

### What to Expect

- **Acknowledgment:** We will acknowledge receipt of your report within **48 hours**.
- **Initial assessment:** We will provide an initial severity assessment within **5 business days**.
- **Resolution timeline:** We aim to release a fix within **30 days** for critical
  vulnerabilities and **90 days** for lower-severity issues.
- **Communication:** We will keep you informed of our progress throughout the process.
- **Credit:** With your permission, we will credit you in the security advisory and
  release notes.

### Responsible Disclosure

We follow a coordinated disclosure process:

1. The reporter submits the vulnerability privately.
2. We confirm the vulnerability and develop a fix.
3. We prepare a security advisory and patched release.
4. We release the fix and publish the advisory simultaneously.
5. We publicly credit the reporter (if they consent).

We ask that you:
- **Do not** disclose the vulnerability publicly until we have released a fix.
- **Do not** exploit the vulnerability beyond what is necessary to demonstrate it.
- **Do not** access, modify, or delete data belonging to other users.
- **Do** make a good-faith effort to avoid disrupting the service.

We commit to:
- **Not** pursuing legal action against researchers who follow this policy.
- Treating your report with confidentiality.
- Working with you to understand and resolve the issue promptly.

## Security Scope

The following components are in scope for security reports:

### In Scope

| Component | Description |
|-----------|-------------|
| **Command compiler pipeline** | Preclassifier, decomposer, slot filler, compiler, validator, formatter |
| **Safety and validation layer** | Risk classification, blocked command detection, input sanitization |
| **FastAPI server** | All `/v1/*` endpoints, authentication, rate limiting, input validation |
| **REPL / CLI** | Interactive terminal, command execution, slash commands |
| **Docker image** | Base image, runtime configuration, exposed services |
| **Session management** | Session store, cross-turn reference resolution |
| **Telemetry** | Local SQLite storage, anonymization, data export |
| **Build and CI** | GitHub Actions workflows, build scripts, dependency management |

### Out of Scope

| Component | Reason |
|-----------|--------|
| Third-party dependencies | Report to the upstream project directly (but do let us know) |
| Model accuracy issues | Incorrect command generation is a quality issue, not a security issue (unless it bypasses the safety layer) |
| Denial of service via resource exhaustion on unprotected instances | The server is designed for local/trusted-network use; DoS on public-facing deployments is a deployment concern |
| Social engineering attacks | Outside the scope of the software |

## Security Design Principles

INCEPT is designed with the following security principles:

### Offline-First Architecture

- The system operates **100% offline** at inference time.
- No network calls are made during command generation or execution.
- No telemetry data is sent externally. All telemetry is local-only (SQLite).
- The Docker image runs with `--network=none` capability.

### Defense in Depth (Command Safety)

1. **Intent classification** -- the model classifies intent, not arbitrary shell generation.
2. **Constrained decoding** -- GBNF grammars restrict model output to valid IR structures.
3. **Compiler** -- IR is compiled to shell commands through deterministic, audited code paths.
4. **Validator** -- `bashlex` parses the generated command; safety rules reject dangerous patterns.
5. **Sanitization** -- all user-supplied parameters pass through `shlex.quote()`.
6. **Risk classification** -- commands are classified as safe, caution, or dangerous.
7. **Blocked patterns** -- known destructive commands (e.g., `rm -rf /`, `mkfs` on mounted
   devices) are unconditionally blocked.

No model output ever flows directly into shell execution without passing through the full
compiler-validator-sanitizer chain.

### No Shell Injection Surface

- The codebase contains **zero** uses of `os.system()` or `subprocess.call(shell=True)`.
- All subprocess invocations use argument lists (not shell strings).
- All user-supplied values are quoted with `shlex.quote()` before inclusion in commands.

### API Security

- API key authentication (optional, enabled via `INCEPT_API_KEY` environment variable).
- Rate limiting (configurable, default 60 requests/minute).
- Input validation: maximum body size (16 KB), NL input length limit (500 characters),
  UTF-8 enforcement, null byte rejection.
- Request timeout (10 seconds maximum per request).
- CORS configuration for browser-based clients.
- Request ID tracing for audit logging.

### Container Security

- Runs as non-root user (`incept`, UID 1000).
- No unnecessary Linux capabilities.
- Resource limits enforced via `docker-compose.yml` (1 GB memory, 2 CPUs).
- Health check configured for orchestrator integration.
- Base image scanned for known CVEs.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.3.x   | Yes      |
| 0.2.x   | Security fixes only |
| 0.1.x   | No       |

## Security Advisories

Published security advisories will be listed in this section and on the GitHub
Security Advisories page for this repository.

*No advisories have been published yet.*
