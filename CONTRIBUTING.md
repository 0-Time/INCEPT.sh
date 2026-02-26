# Contributing to INCEPT

Thank you for your interest in contributing to INCEPT. This document provides guidelines
and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Commit Message Format](#commit-message-format)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive
environment. Be considerate of differing viewpoints and experiences. Harassment or
abusive behavior will not be tolerated.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/INCEPT.git
   cd INCEPT
   ```
3. **Add the upstream remote:**
   ```bash
   git remote add upstream https://github.com/incept-project/INCEPT.git
   ```
4. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.11 or later
- `make` (for running project tasks)
- Docker (optional, for container builds and testing)

### Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install the package in editable mode with all development dependencies:
   ```bash
   pip install -e ".[dev,server,cli]"
   ```

3. Verify the installation:
   ```bash
   make all    # runs lint, typecheck, and test
   ```

### Optional Extras

- **ML training dependencies** (for model fine-tuning):
  ```bash
  pip install -e ".[ml]"
  ```
- **Evaluation dependencies** (for benchmark reports):
  ```bash
  pip install -e ".[eval]"
  ```
- **Everything:**
  ```bash
  pip install -e ".[all]"
  ```

## Coding Standards

### Linting

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
make lint       # check for lint errors
make format     # auto-fix formatting and lint issues
```

Ruff is configured in `pyproject.toml` with the following rules:
- **Line length:** 100 characters maximum
- **Target version:** Python 3.11
- **Selected rules:** E (pycodestyle errors), F (pyflakes), W (pycodestyle warnings),
  I (isort), UP (pyupgrade), B (flake8-bugbear), SIM (flake8-simplify)

### Type Checking

We use [mypy](https://mypy-lang.org/) in strict mode for static type analysis.

```bash
make typecheck
```

All new code must include type annotations. The mypy configuration enforces:
- `strict = true`
- `disallow_untyped_defs = true`
- `warn_return_any = true`
- `warn_unused_configs = true`

### Code Style Guidelines

- Use descriptive variable and function names.
- Prefer explicit over implicit. Avoid magic numbers; use named constants.
- Keep functions focused and short. If a function exceeds ~50 lines, consider splitting it.
- All public functions and classes must have docstrings.
- Prefer `pathlib.Path` over `os.path` for file system operations.
- Use Pydantic models for data validation and serialization.
- Never use `os.system()` or `subprocess.call(shell=True)`.
  All shell arguments must go through `shlex.quote()`.

## Testing

We follow a **test-driven development (TDD)** approach. Tests are written with
[pytest](https://docs.pytest.org/) and live in the `tests/` directory.

### Running Tests

```bash
make test       # run full test suite with coverage
make eval       # run golden test evaluation
make smoke      # run API smoke tests (requires running server)
```

### Test Requirements

- **All PRs must include tests** for new functionality or bug fixes.
- **Coverage:** new code should have meaningful test coverage. We do not enforce
  a hard coverage percentage, but untested code will be flagged during review.
- **Golden tests:** if you add or modify intents, add corresponding golden test
  cases in `golden_tests/`.
- **Test naming:** use descriptive test names that explain the scenario:
  ```python
  def test_install_package_generates_apt_command_on_ubuntu():
      ...

  def test_validator_rejects_rm_rf_root():
      ...
  ```
- **Async tests:** use `pytest-asyncio` for async test functions. The project
  is configured with `asyncio_mode = "auto"`.

### Test Structure

```
tests/
  test_compiler_*.py      # compiler unit tests (per intent group)
  test_validator.py        # safety validator tests
  test_preclassifier.py    # intent classification tests
  test_decomposer.py       # multi-step decomposition tests
  test_pipeline.py         # end-to-end pipeline tests
  test_server.py           # API server integration tests
  test_recovery.py         # error recovery tests
  test_session.py          # session tracking tests
  test_golden.py           # golden test evaluation
  ...
```

## Pull Request Process

1. **Sync with upstream** before starting work:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Make your changes** on a feature branch. Keep commits focused and atomic.

3. **Run the full check suite** before pushing:
   ```bash
   make all    # lint + typecheck + test
   ```

4. **Push your branch** and open a Pull Request against `main`:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **PR requirements:**
   - All CI checks must pass (lint, typecheck, test, docker-build).
   - At least one approving review from a maintainer.
   - PR description must explain *what* changed and *why*.
   - If the PR adds a new intent, include: IR schema, GBNF grammar, compiler
     function, golden tests, and training data.
   - If the PR changes the API, update `docs/api.md`.
   - If the PR changes configuration, update `docs/config-reference.md`.

6. **Address review feedback** by pushing additional commits (do not force-push
   during review).

7. **Merge:** maintainers will squash-merge approved PRs.

## Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type       | Description                                          |
|------------|------------------------------------------------------|
| `feat`     | A new feature                                        |
| `fix`      | A bug fix                                            |
| `docs`     | Documentation changes only                           |
| `style`    | Code style changes (formatting, no logic change)     |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test`     | Adding or updating tests                             |
| `chore`    | Build process, CI, dependency updates                |
| `perf`     | Performance improvement                              |
| `security` | Security fix or hardening                            |

### Scope

The scope should identify the subsystem affected. Common scopes:

`compiler`, `validator`, `preclassifier`, `decomposer`, `server`, `cli`,
`grammar`, `schema`, `recovery`, `session`, `telemetry`, `docker`, `training`,
`eval`, `safety`, `docs`

### Examples

```
feat(compiler): add zypper variants for SUSE package management

fix(validator): prevent false positive on find with -delete flag

test(recovery): add tests for apt-package-not-found recovery pattern

docs(api): update /v1/command endpoint examples for new response fields

chore(ci): add docker-build job to GitHub Actions pipeline
```

### Rules

- **Subject line:** imperative mood, lowercase, no period at the end, max 72 characters.
- **Body:** explain *what* and *why*, not *how*. Wrap at 100 characters.
- **Footer:** reference GitHub issues with `Fixes #123` or `Closes #123`.

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests.
- For **security vulnerabilities**, see [SECURITY.md](SECURITY.md) -- do NOT
  open a public issue.
- When reporting bugs, include:
  - INCEPT version (`incept --version` or `python -c "import incept; print(incept.__version__)"`)
  - Operating system and distribution
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - Relevant log output

## License

By contributing to INCEPT, you agree that your contributions will be licensed under the
[Apache License 2.0](LICENSE).
