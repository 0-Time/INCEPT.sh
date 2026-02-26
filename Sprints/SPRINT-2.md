# Sprint 2: Compiler & Validator

**Duration:** Weeks 3-4
**Phase:** Phase 1 — Schema and Compiler (completion)
**Sprint Goal:** Implement all 52 intent compiler functions, the safety/validation layer, multi-step decomposer, response formatter, and achieve a working end-to-end pipeline with a hard-coded classifier.

---

## Sprint Backlog

### Story 2.1 — Compiler Core & Shell Quoting
**Points:** 3
**Priority:** P0 — Critical

**As a** compiler developer,
**I want** a compiler framework with shell quoting and intent routing,
**So that** individual intent compilers plug into a consistent, safe architecture.

**Acceptance Criteria:**
- [ ] `IntentRouter` dispatches IR to the correct compiler function by intent label
- [ ] `quote_value(value, shell)` handles POSIX sh, bash, zsh quoting
- [ ] `ansi_c_quote()` for bash `$'...'` quoting of control characters
- [ ] `shlex.quote()` used as default for all user-supplied values
- [ ] Composition handler joins sub-commands: `&&`, `|`, `;`, `$()`, `| xargs`
- [ ] Variable binding resolution (`$PREV_OUTPUT` → shell constructs)
- [ ] Unit tests for quoting edge cases: spaces, quotes, newlines, glob chars, empty strings

**Tasks:**
- [ ] Implement `IntentRouter` class
- [ ] Implement `quote_value()` with shell-specific logic
- [ ] Implement `CompositionHandler` for pipeline IR
- [ ] Implement variable binding resolution
- [ ] Write quoting unit tests (30+ edge cases)

---

### Story 2.2 — File Operations Compilers (12 intents)
**Points:** 8
**Priority:** P0 — Critical

**As a** user,
**I want** accurate commands for file operations,
**So that** I can find, copy, move, delete, and manage files safely.

**Acceptance Criteria:**
- [ ] `compile_find_files()` — handles all optional params, correct `find` syntax
- [ ] `compile_copy_files()` — `cp` with recursive, preserve attrs
- [ ] `compile_move_files()` — `mv` with proper quoting
- [ ] `compile_delete_files()` — `rm` with recursive, force; never generates `rm -rf /`
- [ ] `compile_change_permissions()` — `chmod` with recursive, octal or symbolic
- [ ] `compile_change_ownership()` — `chown` with group, recursive
- [ ] `compile_create_directory()` — `mkdir` with `-p` for parents
- [ ] `compile_list_directory()` — `ls` with long format, all files, sort
- [ ] `compile_disk_usage()` — `du`/`df` with human readable, max depth
- [ ] `compile_view_file()` — `cat`/`head`/`tail` based on params
- [ ] `compile_create_symlink()` — `ln -s` with correct argument order
- [ ] `compile_compare_files()` — `diff` with context lines
- [ ] Each compiler tested with ≥5 param combinations
- [ ] All generated commands pass `bashlex` syntax validation

**Tasks:**
- [ ] Implement all 12 compiler functions
- [ ] Write unit tests for each (≥60 test cases total)
- [ ] Test with Debian and RHEL context variants
- [ ] Verify generated commands against golden tests

---

### Story 2.3 — Text Processing & Archive Compilers (8 intents)
**Points:** 5
**Priority:** P0 — Critical

**As a** user,
**I want** accurate commands for text search, replacement, and archiving,
**So that** I can process text and manage archives correctly.

**Acceptance Criteria:**
- [ ] `compile_search_text()` — `grep` with recursive, ignore case, PCRE vs ERE based on version
- [ ] `compile_replace_text()` — `sed` with in-place, backup, global
- [ ] `compile_sort_output()` — `sort` with reverse, numeric, unique, field
- [ ] `compile_count_lines()` — `wc` with mode selection (lines/words/chars)
- [ ] `compile_extract_columns()` — `awk`/`cut` based on delimiter and field spec
- [ ] `compile_unique_lines()` — `sort | uniq` with count, duplicates-only
- [ ] `compile_compress_archive()` — `tar`/`zip` with format selection, exclude patterns
- [ ] `compile_extract_archive()` — `tar`/`unzip` with format auto-detection
- [ ] Version-aware flag selection (e.g., `grep -P` fallback to `grep -E`)
- [ ] Each compiler tested with ≥4 param combinations

**Tasks:**
- [ ] Implement all 8 compiler functions
- [ ] Build version-checking logic for grep, sed, tar
- [ ] Write unit tests (≥32 test cases)
- [ ] Test archive format variations (tar.gz, tar.bz2, tar.xz, zip)

---

### Story 2.4 — Package, Service, User, Log, Cron, Network, Process Compilers (27 intents)
**Points:** 13
**Priority:** P0 — Critical

**As a** user,
**I want** accurate distro-aware commands for system administration,
**So that** package, service, user, and network operations work on my specific distro.

**Acceptance Criteria:**
- [ ] **Package (4):** `apt-get`/`dnf` switching based on distro family; `sudo` prepended; version pinning
- [ ] **Service (5):** `systemctl` commands for start/stop/restart/enable/status
- [ ] **User (3):** `useradd`/`userdel`/`usermod` with groups, shell, home dir
- [ ] **Log (3):** `journalctl` with unit, since/until, priority, follow mode
- [ ] **Cron (3):** `crontab` manipulation — list, add (via temp file + `crontab`), remove
- [ ] **Network (6):** `ip`/`ping`/`curl`/`wget`/`scp`/`rsync`/`ssh`/`ss` with correct flags
- [ ] **Process (3):** `ps`/`kill`/`top`/`free`/`uptime` based on info type
- [ ] **Disk/Mount (2):** `mount`/`umount` with filesystem type, options
- [ ] Every compiler handles Debian and RHEL contexts correctly
- [ ] `sudo` prepended when `requires_sudo=true` and `allow_sudo=true`
- [ ] Each compiler tested with ≥3 param combinations per distro

**Tasks:**
- [ ] Implement Package Management compilers (4 functions, 2 distro variants each)
- [ ] Implement Service Management compilers (5 functions)
- [ ] Implement User Management compilers (3 functions)
- [ ] Implement Log Operations compilers (3 functions)
- [ ] Implement Scheduling compilers (3 functions)
- [ ] Implement Networking compilers (6 functions)
- [ ] Implement Process Management compilers (3 functions)
- [ ] Implement Disk/Mount compilers (2 functions)
- [ ] Write unit tests for all (≥160 test cases)
- [ ] Test Debian vs RHEL output for all distro-sensitive intents

---

### Story 2.5 — Version-Aware Flag Tables
**Points:** 5
**Priority:** P0 — Critical

**As a** compiler developer,
**I want** JSON flag tables for all supported commands,
**So that** the compiler generates version-correct flags with proper fallbacks.

**Acceptance Criteria:**
- [ ] Flag table JSON for: `find`, `grep`, `sed`, `awk`, `tar`, `cp`, `mv`, `rm`, `chmod`, `chown`, `ls`, `du`, `df`, `curl`, `wget`, `ssh`, `scp`, `rsync`, `ip`, `ss`, `ps`
- [ ] Each flag entry has: description, min_version (gnu/bsd), fallback
- [ ] `FlagLookup` utility: `get_flag(command, flag, distro, version) → flag | fallback | None`
- [ ] Compiler functions use `FlagLookup` instead of hard-coded flags
- [ ] Unit tests for version fallback scenarios

**Tasks:**
- [ ] Create JSON flag tables for all commands (~20 files)
- [ ] Implement `FlagLookup` class
- [ ] Integrate into compiler functions
- [ ] Write fallback scenario tests

---

### Story 2.6 — Validator & Safety Layer
**Points:** 8
**Priority:** P0 — Critical

**As a** safety engineer,
**I want** a deterministic validator that blocks dangerous commands,
**So that** no harmful command ever reaches the user regardless of model behavior.

**Acceptance Criteria:**
- [ ] `bashlex` syntax validation — reject unparseable commands
- [ ] Banned pattern registry (from spec Section 8.3) — regex-based
- [ ] Risk classification: Safe / Caution / Dangerous / Blocked
- [ ] Sudo audit: reject if `sudo` present but `allow_sudo=false`
- [ ] Path safety check: flag writes to `/etc`, `/boot`, `/usr`, `/bin`, `/sbin`, `/dev`
- [ ] Safe-mode enforcement: additional blocks for pipe-to-shell, `chmod 777` on system dirs
- [ ] All 15 safety canary tests from Appendix D pass (100%)
- [ ] No false positives on normal commands (`install nginx`, `find files`, `list directory`)

**Tasks:**
- [ ] Implement syntax validator using `bashlex`
- [ ] Implement banned pattern registry with safe-mode toggle
- [ ] Implement risk classifier
- [ ] Implement sudo auditor
- [ ] Implement path safety checker
- [ ] Write safety canary tests (all 15 from Appendix D)
- [ ] Write false-positive tests (≥20 normal commands that must NOT be blocked)
- [ ] Integration test: validator receives compiler output → correct classification

---

### Story 2.7 — Multi-Step Decomposer
**Points:** 5
**Priority:** P1 — High

**As a** user,
**I want** to give compound requests like "find files and compress them",
**So that** the system handles multi-step operations correctly.

**Acceptance Criteria:**
- [ ] Detects split indicators: ", then", "and then", ", and" (with verb), "after", "before", "pipe to", `|`, sentence boundaries
- [ ] Splits into sub-requests with correct ordering
- [ ] Pronoun resolution: "them", "it", "the result", "the output", "the file(s)" → `$PREV_OUTPUT`
- [ ] Determines composition type: `sequential`, `pipe`, `independent`
- [ ] Enforces complexity limit: max 4 sub-steps, warns and truncates beyond
- [ ] "before" / "after" reordering works correctly
- [ ] Unit tests with ≥20 compound request examples

**Tasks:**
- [ ] Implement split pattern detection
- [ ] Implement pronoun/reference resolution
- [ ] Implement composition type inference
- [ ] Implement complexity limiter
- [ ] Implement reordering for "before"/"after"
- [ ] Write unit tests

---

### Story 2.8 — Response Formatter & Templates
**Points:** 5
**Priority:** P1 — High

**As a** user,
**I want** clear explanations of what each command does,
**So that** I understand the command before running it.

**Acceptance Criteria:**
- [ ] Explanation templates registered for all 52 intents
- [ ] Each template has: `summary`, `flag_explanations` (per-flag meanings), `side_effects`
- [ ] Clarification templates: all entries from spec Section 12.2
- [ ] Default registry: per-distro defaults for optional params (Debian + RHEL)
- [ ] Verbosity levels: `minimal` (command only), `normal` (command + summary + warnings), `detailed` (full breakdown)
- [ ] Response JSON structure matches spec Section 14.2
- [ ] Template variable interpolation works for all templates

**Tasks:**
- [ ] Create explanation templates for all 52 intents
- [ ] Create clarification templates (8+ templates from spec)
- [ ] Create per-distro default registry
- [ ] Implement response formatter with verbosity levels
- [ ] Write unit tests for template rendering

---

### Story 2.9 — End-to-End Pipeline (Hard-Coded Classifier)
**Points:** 5
**Priority:** P0 — Critical

**As a** developer,
**I want** the full pipeline working end-to-end with a hard-coded regex classifier,
**So that** I can validate the architecture before introducing model uncertainty.

**Acceptance Criteria:**
- [ ] Pipeline orchestrator chains all 8 stages
- [ ] Hard-coded regex classifier covers top 30 intents
- [ ] Full request → response flow works for single-step requests
- [ ] Full request → response flow works for multi-step requests
- [ ] Golden test pass rate: ≥95% on compiler-only tests
- [ ] Golden test pass rate: ≥80% end-to-end with hard-coded classifier
- [ ] Container-based execution tests set up (Ubuntu 24.04 + Rocky 9 Dockerfiles)

**Tasks:**
- [ ] Implement pipeline orchestrator
- [ ] Wire all stages together
- [ ] Implement hard-coded regex classifier for top 30 intents
- [ ] Run full golden test suite
- [ ] Create test Dockerfiles for execution testing
- [ ] Run execution tests in containers
- [ ] Document pass rates and failures

---

## Sprint Metrics

| Metric | Target |
|--------|--------|
| Total Story Points | 57 |
| Compiler functions implemented | 52/52 |
| Safety canary pass rate | 100% |
| Golden test (compiler-only) | ≥95% |
| Golden test (e2e, hard-coded) | ≥80% |
| Test coverage | ≥85% |

## Dependencies
- Sprint 1 IR schemas and GBNF grammars

## Risks

**OVERLOAD WARNING:** At 57 SP, this is nearly 2x Sprint 1. For a 1-2 person team this is aggressive.

**Spillover Plan (if velocity is insufficient):**
- **Must complete (P0):** Stories 2.1, 2.2, 2.5, 2.6, 2.9 (32 SP core)
- **Can carry to Sprint 3:** Stories 2.3, 2.4 (18 SP — remaining compilers)
- **Can carry to Sprint 3:** Stories 2.7, 2.8 (10 SP — decomposer + formatter)
- Sprint 3 has 34 SP planned, so 10-18 SP carryover is absorbable by deferring Story 3.2 (paraphrasing) by 3-5 days

**Other Risks:**
- `bashlex` may not handle all shell constructs — have a fallback plan (custom tokenizer or `shlex.split`)
- 27 compilers in Story 2.4 is the highest-risk item — consider splitting into 2 sub-stories if needed
