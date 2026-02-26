# API Reference

INCEPT exposes a RESTful JSON API via FastAPI on `/v1/` endpoints. The default bind address is `0.0.0.0:8080`.

## Authentication

Authentication is optional. When `INCEPT_API_KEY` is set, all endpoints except the health checks require a Bearer token:

```
Authorization: Bearer <your-api-key>
```

Health endpoints (`/v1/health`, `/v1/health/ready`) are always public.

Requests without a valid token receive a `401` response:

```json
{"detail": "Missing API key"}
```

or

```json
{"detail": "Invalid API key"}
```

## Rate Limiting

A per-client-IP token-bucket rate limiter enforces a configurable per-minute request limit (default: 60 requests/minute, set via `INCEPT_RATE_LIMIT`). Each client IP address gets its own independent bucket. Health and metrics endpoints are exempt. Exceeding the limit returns `429`:

```json
{"detail": "Rate limit exceeded"}
```

Rate-limited responses include these headers:

| Header | Description |
|---|---|
| `X-RateLimit-Remaining` | Tokens remaining in the client's bucket |
| `Retry-After` | Seconds until the next token is available (on 429 responses) |

When `INCEPT_TRUST_PROXY=true`, the first IP in the `X-Forwarded-For` header is used as the client IP. This should only be enabled when running behind a trusted reverse proxy.

Stale per-IP buckets are automatically cleaned up after 5 minutes of inactivity to prevent memory leaks.

## Security Headers

Every API response includes the following security headers:

| Header | Value |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains` |
| `Content-Security-Policy` | `default-src 'none'` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `geolocation=(), camera=(), microphone=()` |
| `Cache-Control` | `no-store` |

## Request Timeout

All requests are subject to a configurable timeout (default: 30 seconds, set via `INCEPT_REQUEST_TIMEOUT`). Timeouts return `504`:

```json
{"detail": "Request timed out"}
```

## Request ID Tracing

Every response includes an `X-Request-ID` header. If the client sends an `X-Request-ID` header, that value is propagated; otherwise a UUID is generated.

---

## Endpoints

### POST /v1/command

Translate a natural language request into a Linux command.

**Request Body**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `nl` | string | yes | -- | Natural language request (1--2000 chars, no null bytes) |
| `context` | object | no | `null` | Environment context (distro, shell, cwd, etc.) |
| `verbosity` | string | no | `"normal"` | One of `"minimal"`, `"normal"`, `"detailed"` |
| `session_id` | string | no | `null` | Session ID for multi-turn context |

**Example Request**

```bash
curl -X POST http://localhost:8080/v1/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my-secret-key" \
  -d '{"nl": "find all log files larger than 100MB", "verbosity": "normal"}'
```

**Response**

Returns a `PipelineResponse` object:

| Field | Type | Description |
|---|---|---|
| `status` | string | `"success"`, `"clarification"`, `"error"`, `"blocked"`, or `"no_match"` |
| `responses` | array | List of response objects (one per sub-command for compound requests) |
| `is_compound` | bool | Whether the request was decomposed into multiple sub-commands |
| `original_request` | string | The original NL input |

Each item in `responses` contains one of:

- **command**: `{command, explanation, risk_level, warnings}`
- **clarification**: `{question, options}`
- **error**: `{error, reason, suggestion}`

**Example Response**

```json
{
  "status": "success",
  "responses": [
    {
      "status": "success",
      "command": {
        "command": "find / -name '*.log' -size +100M",
        "explanation": "Search the filesystem for files ending in .log that are larger than 100MB",
        "risk_level": "safe",
        "warnings": []
      },
      "clarification": null,
      "error": null
    }
  ],
  "is_compound": false,
  "original_request": "find all log files larger than 100MB"
}
```

---

### POST /v1/feedback

Report the outcome of executing a generated command. On failure, the server suggests a recovery action.

**Request Body**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `session_id` | string | no | `""` | Session ID |
| `command` | string | yes | -- | The command that was executed |
| `outcome` | string | yes | -- | `"success"` or `"failure"` |
| `stderr` | string | no | `""` | stderr output from the failed command |
| `attempt` | int | no | `1` | Current retry attempt number (1-based) |

**Example Request**

```bash
curl -X POST http://localhost:8080/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "command": "apt install htop",
    "outcome": "failure",
    "stderr": "E: Could not open lock file - Permission denied",
    "attempt": 1
  }'
```

**Success Outcome Response**

```json
{"status": "acknowledged"}
```

**Failure Outcome Response**

```json
{
  "status": "recovery",
  "recovery": {
    "recovery_command": "sudo apt install htop",
    "explanation": "Permission denied. Retrying with sudo.",
    "can_auto_retry": true,
    "attempt_number": 1,
    "gave_up": false
  }
}
```

After 3 failed recovery attempts, `gave_up` is set to `true` and `recovery_command` is empty.

---

### GET /v1/health

Basic health check. Always public (no auth required).

**Response**

```json
{
  "status": "ok",
  "version": "0.1.0",
  "uptime": 3621.5
}
```

---

### GET /v1/health/ready

Readiness probe. Returns whether the model is loaded and ready to serve. Always public.

**Response**

```json
{"ready": true}
```

---

### POST /v1/explain

Explain a shell command — returns a structured NL explanation with risk assessment.

**Request Body**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `command` | string | yes | -- | Shell command to explain (min 1 char) |
| `context` | string | no | `null` | Optional JSON string with environment context |

**Example Request**

```bash
curl -X POST http://localhost:8080/v1/explain \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my-secret-key" \
  -d '{"command": "grep -r TODO src/"}'
```

**Response**

Returns an `ExplainResponse` object:

| Field | Type | Description |
|---|---|---|
| `command` | string | The original command |
| `intent` | string \| null | Detected intent label (e.g., `search_text`) or null if unrecognized |
| `explanation` | string | Human-readable explanation of what the command does |
| `flag_explanations` | object | Map of flags to their explanations (e.g., `{"-r": "recursive"}`) |
| `side_effects` | array | List of side effects (e.g., `["modifies files in-place"]`) |
| `risk_level` | string | One of `safe`, `caution`, `dangerous`, `blocked` |
| `params` | object | Extracted parameters (e.g., `{"pattern": "TODO", "recursive": true}`) |

**Example Response**

```json
{
  "command": "grep -r TODO src/",
  "intent": "search_text",
  "explanation": "Search for text patterns in files",
  "flag_explanations": {},
  "side_effects": [],
  "risk_level": "safe",
  "params": {"pattern": "TODO", "recursive": true}
}
```

---

### GET /v1/intents

List all 78 supported intent labels with human-readable descriptions.

**Response**

```json
{
  "intents": {
    "find_files": "Search for files by name, type, size, or modification time",
    "copy_files": "Copy files or directories to a new location",
    "...": "..."
  }
}
```

---

### GET /v1/metrics

Prometheus-compatible plain-text metrics.

**Response** (`text/plain`)

```
# HELP request_count Total number of /v1/command requests
# TYPE request_count counter
request_count 42

# HELP latency_seconds Average request latency
# TYPE latency_seconds gauge
latency_seconds 0.0312

# HELP uptime_seconds Server uptime
# TYPE uptime_seconds gauge
uptime_seconds 3621.5
```

---

## Error Codes

| HTTP Status | Meaning |
|---|---|
| 200 | Success |
| 401 | Missing or invalid API key |
| 422 | Validation error (bad request body) |
| 429 | Rate limit exceeded |
| 504 | Request timed out |
