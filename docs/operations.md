# Operations Guide

## Health Checks

INCEPT exposes two health endpoints:

- **`GET /v1/health`** -- returns server status, version, and uptime. Use for basic liveness probes.
- **`GET /v1/health/ready`** -- returns `{"ready": true}` when the model is loaded and the server can accept requests. Use for readiness probes in orchestrators (Kubernetes, ECS, etc.).

Both endpoints bypass authentication and rate limiting.

### Docker Built-in Health Check

The Dockerfile includes a health check that probes `/v1/health/ready` every 30 seconds with a 5-second timeout, 10-second start period, and 3 retries before marking the container as unhealthy.

### Orchestrator Integration

For Kubernetes:

```yaml
livenessProbe:
  httpGet:
    path: /v1/health
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 30
readinessProbe:
  httpGet:
    path: /v1/health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
```

## Metrics

**`GET /v1/metrics`** returns Prometheus-compatible plain-text metrics:

| Metric | Type | Description |
|---|---|---|
| `request_count` | counter | Total `/v1/command` requests served |
| `latency_seconds` | gauge | Average request latency in seconds |
| `uptime_seconds` | gauge | Server uptime in seconds |

Scrape this endpoint with Prometheus by adding a target to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: incept
    static_configs:
      - targets: ["incept:8080"]
    metrics_path: /v1/metrics
```

The metrics endpoint is exempt from rate limiting.

## Logging

Set the log level via the `INCEPT_LOG_LEVEL` environment variable. Accepted values:

| Level | Use Case |
|---|---|
| `debug` | Development and troubleshooting |
| `info` | Standard production logging (default) |
| `warning` | Quieter production logging |
| `error` | Errors only |

Logs are written to stdout/stderr, compatible with container log drivers (Docker, CloudWatch, Stackdriver).

## Session Management

Sessions are stored in-memory with the following defaults:

- **Timeout**: 1800 seconds (30 minutes) of inactivity.
- **Max turns per session**: 20 (oldest turns are dropped when the limit is exceeded).
- **Max concurrent sessions**: 1000 (configurable via `INCEPT_MAX_SESSIONS`). When the limit is reached, expired sessions are cleaned before rejecting. Set to 0 for unlimited.

Call `SessionStore.cleanup_expired()` to purge stale sessions. In the current implementation, sessions are not persisted across restarts. A server restart clears all sessions.

If the session limit is reached, new session creation returns a `SessionLimitError`. Monitor active session count via the metrics endpoint.

## Telemetry

Local telemetry is stored in a SQLite database (opt-in, disabled by default). The telemetry store tracks:

- Request logs (NL input, detected intent, latency)
- Feedback logs (command, outcome)
- Error logs (error type, message)

PII is stripped before storage using the anonymizer module (IPs, emails, home paths, usernames are replaced with placeholders).

The store auto-rotates at 10,000 entries per table. Export to CSV or JSONL for analysis.

## Smoke Testing

Run the smoke test suite after deployment to verify the server is functioning:

```bash
# Against localhost (default)
./scripts/smoke_test.sh

# Against a specific URL
INCEPT_URL=http://your-server:8080 ./scripts/smoke_test.sh
```

The smoke test performs 5 checks:

1. Health endpoint returns 200
2. Readiness returns `ready: true`
3. Canary classification produces a command for a safe request
4. Safety system blocks a dangerous request
5. JSON schema validation of the response structure

Exit code 0 means all checks passed; non-zero means at least one failed.

## Rollback

Use the rollback script to revert to a previous Docker image version:

```bash
PREVIOUS_TAG=v0.1.0 ./scripts/rollback.sh
```

The script:

1. Stops and removes the current container.
2. Starts the previous version.
3. Waits 5 seconds for startup.
4. Runs the smoke test suite against the rolled-back instance.
5. Exits 0 on success, non-zero if smoke tests fail.

You can customize the container name with `CONTAINER_NAME` and the current tag with `CURRENT_TAG`.

## Recommended Alerts

| Alert | Condition | Severity |
|---|---|---|
| High error rate | >5% of requests return non-200 over 5 min | Warning |
| High latency | `latency_seconds` > 5s average over 5 min | Warning |
| Container unhealthy | Docker health check fails 3 times | Critical |
| Memory pressure | Container memory usage > 90% of limit | Warning |
| Service down | `/v1/health` unreachable for > 1 min | Critical |
