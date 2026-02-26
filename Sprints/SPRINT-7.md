# Sprint 7: Expansion & Release

**Duration:** Weeks 13-14
**Phase:** Phase 5 — Expand
**Sprint Goal:** Add Arch/SUSE distro support, build CLI client and shell plugin, expand intent coverage, prepare for open-source release.

---

## Sprint Backlog

### Story 7.1 — Arch Linux Distro Family Support
**Points:** 5
**Priority:** P1 — High

**As a** Arch/Manjaro user,
**I want** the system to generate correct `pacman` commands,
**So that** the tool works on my distro.

**Acceptance Criteria:**
- [ ] `pacman` compiler variants for: `install_package`, `remove_package`, `update_packages`, `search_package`
- [ ] Arch-specific defaults in default registry (`package_manager: pacman`, `default_editor: vim`)
- [ ] `package_map.json` for Arch (generic → pacman package names)
- [ ] `service_map.json` for Arch (same as systemd-based)
- [ ] Context resolver handles `ID=arch` and `ID_LIKE` containing "arch"
- [ ] Flag tables updated for Arch-specific tool versions (if different)
- [ ] Golden test cases: ≥20 Arch-specific examples
- [ ] Training data: ≥500 Arch-context examples added
- [ ] Model retrained with new data (incremental LoRA update)
- [ ] E2E accuracy on Arch golden tests: ≥80%

**Tasks:**
- [ ] Add `pacman` compiler variants for package intents
- [ ] Create Arch default registry entries
- [ ] Create Arch package/service maps
- [ ] Update context resolver for Arch detection
- [ ] Write Arch golden test cases
- [ ] Generate Arch training data
- [ ] Retrain model with Arch data
- [ ] Evaluate on Arch golden tests
- [ ] Add Arch Docker container for execution testing

---

### Story 7.2 — SUSE Distro Family Support
**Points:** 5
**Priority:** P1 — High

**As a** openSUSE/SLES user,
**I want** the system to generate correct `zypper` commands,
**So that** the tool works on my distro.

**Acceptance Criteria:**
- [ ] `zypper` compiler variants for: `install_package`, `remove_package`, `update_packages`, `search_package`
- [ ] SUSE-specific defaults in default registry
- [ ] `package_map.json` for SUSE
- [ ] Context resolver handles `ID=opensuse-leap`, `ID=opensuse-tumbleweed`, `ID=sles`
- [ ] Golden test cases: ≥20 SUSE-specific examples
- [ ] Training data: ≥500 SUSE-context examples added
- [ ] Model retrained with new data
- [ ] E2E accuracy on SUSE golden tests: ≥80%

**Tasks:**
- [ ] Add `zypper` compiler variants
- [ ] Create SUSE default registry entries
- [ ] Create SUSE package/service maps
- [ ] Update context resolver for SUSE detection
- [ ] Write SUSE golden test cases
- [ ] Generate SUSE training data
- [ ] Retrain model with SUSE data
- [ ] Evaluate on SUSE golden tests
- [ ] Add SUSE Docker container for execution testing

---

### Story 7.3 — Shell Plugin (bash/zsh)
**Points:** 5
**Priority:** P2 — Medium

> **NOTE:** The interactive terminal (primary CLI) has been moved to **Sprint 6, Story 6.11** as a P0. This story covers only the shell plugin integration.

---

### Story 7.4 — Intent Expansion (50 → 80+)
**Points:** 8
**Priority:** P2 — Medium

**As a** user,
**I want** more commands supported,
**So that** the system covers more of my daily Linux operations.

**Acceptance Criteria:**
- [ ] 30+ new intents added. Candidates:
  - **Docker:** `docker_run`, `docker_ps`, `docker_stop`, `docker_logs`, `docker_build`, `docker_exec`
  - **Git:** `git_status`, `git_commit`, `git_push`, `git_pull`, `git_log`, `git_diff`, `git_branch`
  - **SSH keys:** `generate_ssh_key`, `copy_ssh_key`
  - **Disk info:** `list_partitions`, `check_filesystem`
  - **Firewall:** `firewall_allow`, `firewall_deny`, `firewall_list`
  - **DNS:** `dns_lookup`, `dns_resolve`
  - **Environment:** `set_env_var`, `list_env_vars`
  - **Systemd timers:** `create_timer`, `list_timers`
- [ ] IR schemas, GBNF grammars, compiler functions for each new intent
- [ ] ≥5 golden test cases per new intent
- [ ] ≥50 training examples per new intent
- [ ] Model retrained with expanded data
- [ ] Overall accuracy does not regress (≥93% intent, ≥85% slot EM)

**Tasks:**
- [ ] Define new intent schemas and param models
- [ ] Write GBNF grammars for new intents
- [ ] Implement compiler functions
- [ ] Write golden tests
- [ ] Generate training data
- [ ] Retrain model
- [ ] Run full evaluation suite
- [ ] Verify no regression

---

### Story 7.5 — Security Audit & Hardening
**Points:** 5
**Priority:** P0 — Critical

**As a** security engineer,
**I want** a thorough security audit of the entire system,
**So that** the production system and open-source release have no exploitable vulnerabilities.

**Acceptance Criteria:**
- [ ] **OWASP API Top 10 audit:**
  - Broken Object Level Authorization — verify session isolation
  - Broken Authentication — verify API key validation, timing-safe comparison
  - Unrestricted Resource Consumption — verify rate limiting, input size limits, inference timeout
  - Server Side Request Forgery — verify no user-controlled URLs in pipeline
  - Security Misconfiguration — verify default config is secure (safe-mode=on, auth required)
- [ ] **Command injection audit:** verify model output never flows unsanitized into shell execution
  - All compiler outputs go through `shlex.quote()`
  - No `os.system()` or `subprocess.call(shell=True)` anywhere
  - Validator catches any bypass attempts
- [ ] **Input validation audit:** NL input, environment context, settings — all validated
- [ ] **Dependency audit:** `pip audit` / `safety check` — no known CVEs in dependencies
- [ ] **Secrets scan:** no API keys, passwords, tokens in codebase (`trufflehog` or `gitleaks`)
- [ ] **Container audit:** non-root user, no unnecessary capabilities, read-only filesystem where possible
- [ ] Findings documented with severity and resolution status
- [ ] All critical/high findings resolved before release

**Tasks:**
- [ ] Run OWASP API Top 10 checklist
- [ ] Audit compiler and pipeline for command injection paths
- [ ] Audit input validation across all endpoints
- [ ] Run `pip audit` and resolve findings
- [ ] Run secrets scanner on full repo history
- [ ] Audit Docker container security posture
- [ ] Document findings and resolutions
- [ ] Fix all critical and high severity issues

---

### Story 7.6 — Open-Source Release Preparation
**Points:** 5
**Priority:** P1 — High

**As a** project maintainer,
**I want** the project ready for public release,
**So that** the community can use, contribute to, and extend the system.

**Acceptance Criteria:**
- [ ] License selected and applied (Apache 2.0 recommended for code; CC-BY-SA for training data if includes SA sources)
- [ ] `LICENSE` file in repo root
- [ ] `CONTRIBUTING.md` with: development setup, coding standards, PR process, testing requirements
- [ ] `README.md` with: project overview, quick start, architecture diagram, benchmarks, examples
- [ ] All third-party licenses documented (model license, data source licenses)
- [ ] Training data provenance file: source, license, count per source
- [ ] No hardcoded secrets, API keys, or internal paths in codebase (verified by Story 7.6)
- [ ] CI/CD pipeline runs all tests and evaluations locally (`make eval`)
- [ ] **CI/CD builds Docker image** on tag/release (push to registry is optional, not required)
- [ ] **Offline distribution bundle:** tarball containing Docker image (`docker save`), GGUF model, llamafile, context script, docs — deployable on air-gapped machines
- [ ] GitHub release with: Docker image, GGUF model file, llamafile (if ready), offline bundle
- [ ] PyPI package (optional): `pip install incept` — but offline install via wheel also documented
- [ ] **CHANGELOG.md** with version history
- [ ] **SECURITY.md** with vulnerability reporting instructions

**Tasks:**
- [ ] Select and apply license
- [ ] Write `CONTRIBUTING.md`
- [ ] Write comprehensive `README.md` — emphasize offline-first design prominently
- [ ] Write `CHANGELOG.md` and `SECURITY.md`
- [ ] Document all third-party licenses
- [ ] Create training data provenance file
- [ ] **Build offline distribution bundle script** (`scripts/build_offline_bundle.sh`)
- [ ] Set up CI/CD for Docker image building (push optional)
- [ ] Create GitHub release artifacts including offline bundle
- [ ] Write release notes
- [ ] Optional: set up PyPI publishing + document offline wheel install

---

## Sprint Metrics

| Metric | Target |
|--------|--------|
| Total Story Points | 33 |
| New distros supported | +2 (Arch, SUSE) |
| New intents added | ≥30 |
| Total intents | ≥80 |
| Shell plugin functional | bash + zsh (extends Sprint 6 interactive terminal) |
| Security audit passed | All critical/high resolved |
| Dependency CVEs (critical) | 0 |
| Open-source ready | Yes |
| Overall intent accuracy (no regression) | ≥93% |
| Overall slot F1 (no regression) | ≥88% |

## Dependencies
- Sprint 6 API server and Docker packaging
- Sprint 5 model and evaluation infrastructure

## Risks
- Adding new distros + intents + retraining in one sprint is ambitious — prioritize Arch over SUSE if time is tight
- Shell plugin keybinding may conflict with existing terminal shortcuts — make configurable
- Intent expansion may cause confusion with existing intents — monitor confusion matrix closely
- Open-source prep is time-consuming — start license/README work early in the sprint
