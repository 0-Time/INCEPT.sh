# Configuration Reference

INCEPT is configured through three mechanisms, listed by priority (highest first):

1. **CLI flags** -- override everything for a single invocation.
2. **Environment variables** -- configure the server and override TOML defaults.
3. **TOML config file** -- persistent user preferences for the CLI.

## CLI Configuration File

**Location**: `~/.config/incept/config.toml`

The file is optional. If absent, all settings use their defaults. The config is read from the `[incept]` section.

```toml
[incept]
safe_mode = true
verbosity = "normal"
auto_execute = false
color = true
prompt = "incept> "
model_path = "/path/to/model.gguf"
history_file = "~/.incept_history"
```

### CLI Config Options

| Key | Type | Default | Description |
|---|---|---|---|
| `safe_mode` | bool | `true` | Enable additional banned patterns (chmod 777, eval, sudo su, etc.) |
| `verbosity` | string | `"normal"` | Output detail level: `"minimal"`, `"normal"`, or `"detailed"` |
| `auto_execute` | bool | `false` | Automatically execute generated commands (use with caution) |
| `color` | bool | `true` | Enable colored terminal output |
| `prompt` | string | `"incept> "` | REPL prompt string |
| `model_path` | string | `null` | Path to a GGUF model file for model-based classification |
| `history_file` | string | `"~/.incept_history"` | Path to the REPL command history file |

## CLI Flags

Flags are passed when invoking `incept` from the command line.

| Flag | Description |
|---|---|
| `--exec` | Execute the generated command after displaying it |
| `--minimal` | Output only the raw command string (no explanation or formatting) |
| `--explain` | Explain a shell command instead of generating one (reverse pipeline) |
| `--version` | Print the version and exit |

### One-shot Mode

```bash
# Show the command with explanation
incept "find all Python files modified today"

# Output only the command string
incept --minimal "find all Python files modified today"

# Generate and execute immediately
incept --exec "list files in /tmp sorted by size"

# Explain a shell command (reverse pipeline)
incept --explain "grep -r TODO src/"
```

### Interactive Mode

```bash
# Start the REPL (no arguments)
incept
```

### Server Mode

```bash
# Start the API server (subcommand)
incept serve --host 0.0.0.0 --port 8080
```

### Shell Plugin

```bash
# Install the shell plugin (auto-detects bash/zsh)
incept plugin install

# Install for a specific shell
incept plugin install --shell zsh

# Uninstall
incept plugin uninstall
```

The shell plugin binds **Ctrl+I** in your terminal. Type a natural language request on the command line, press Ctrl+I, and it is replaced with the generated command.

## Server Environment Variables

These variables configure the FastAPI server. They are read at startup via `ServerConfig.from_env()`.

| Variable | Type | Default | Description |
|---|---|---|---|
| `INCEPT_HOST` | string | `0.0.0.0` | Server bind address |
| `INCEPT_PORT` | int | `8080` | Server bind port |
| `INCEPT_API_KEY` | string | *(none)* | API key for Bearer token auth; auth is disabled if unset |
| `INCEPT_RATE_LIMIT` | int | `60` | Maximum requests per minute per client IP (token bucket) |
| `INCEPT_TRUST_PROXY` | bool | `false` | Use `X-Forwarded-For` for client IP (enable only behind a trusted proxy) |
| `INCEPT_MAX_SESSIONS` | int | `1000` | Maximum concurrent sessions (0 = unlimited) |
| `INCEPT_CORS_ORIGINS` | string | `*` | Comma-separated list of allowed CORS origins |
| `INCEPT_REQUEST_TIMEOUT` | float | `30.0` | Per-request timeout in seconds |
| `INCEPT_MODEL_PATH` | string | *(none)* | Path to the GGUF model file |
| `INCEPT_SAFE_MODE` | string | `true` | Enable safe mode (`true`/`false`/`0`/`1`/`yes`/`no`) |
| `INCEPT_LOG_LEVEL` | string | `info` | Log level: `debug`, `info`, `warning`, `error` |

### CORS Configuration

Set `INCEPT_CORS_ORIGINS` to a comma-separated list:

```bash
INCEPT_CORS_ORIGINS="https://app.example.com,https://admin.example.com"
```

An empty string or unset value defaults to `*` (allow all origins).

### Safe Mode Parsing

`INCEPT_SAFE_MODE` accepts case-insensitive values. Safe mode is **disabled** only when the value is one of: `false`, `0`, `no`. All other values (including unset) enable safe mode.
