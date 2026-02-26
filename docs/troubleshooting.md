# Troubleshooting

Common issues and their solutions when running INCEPT.

## Server Won't Start

### Port already in use

**Symptom**: `OSError: [Errno 98] Address already in use` or similar.

**Solution**: Either stop the process using port 8080 or change the bind port:

```bash
# Find what's using the port
lsof -i :8080

# Use a different port
INCEPT_PORT=9090 incept serve --port 9090

# Or with Docker
docker run -p 9090:9090 -e INCEPT_PORT=9090 incept
```

### Missing model file

**Symptom**: Server starts but `/v1/health/ready` returns `{"ready": false}`, or the model-based classifier fails.

**Solution**: Ensure the GGUF model is at the expected path:

```bash
# Check the configured path
echo $INCEPT_MODEL_PATH  # default: /app/models/v1/model.gguf

# In Docker, verify the volume mount
docker exec incept ls -la /app/models/v1/

# Copy the model into the volume
docker cp model.gguf incept:/app/models/v1/model.gguf
```

Note: The regex-based preclassifier works without a model. The model is only required for the model-based classifier (Sprint 4+).

### Import errors

**Symptom**: `ModuleNotFoundError` on startup.

**Solution**: Install the correct extras:

```bash
# For server mode
pip install ".[server]"

# For CLI mode
pip install ".[cli]"

# For everything
pip install ".[all]"
```

## Rate Limit Errors (429)

**Symptom**: `{"detail": "Rate limit exceeded"}` with HTTP 429.

**Causes and fixes**:

- **Too many requests**: Wait for your per-IP token bucket to refill (tokens replenish at `INCEPT_RATE_LIMIT / 60` per second). Check the `X-RateLimit-Remaining` and `Retry-After` response headers.
- **Rate limit too low**: Increase the limit:
  ```bash
  INCEPT_RATE_LIMIT=120 incept serve
  ```
- **Wrong client IP behind proxy**: If all clients share the same rate limit bucket, your reverse proxy may not be forwarding client IPs. Enable proxy trust:
  ```bash
  INCEPT_TRUST_PROXY=true incept serve
  ```
  Ensure your proxy sends the `X-Forwarded-For` header.
- **Load testing**: Health and metrics endpoints are exempt. If you need to test without rate limiting, set a very high value:
  ```bash
  INCEPT_RATE_LIMIT=10000 incept serve
  ```

## Authentication Failures (401)

**Symptom**: `{"detail": "Missing API key"}` or `{"detail": "Invalid API key"}`.

**Causes and fixes**:

- **Missing header**: Include the `Authorization` header:
  ```bash
  curl -H "Authorization: Bearer your-key" http://localhost:8080/v1/command ...
  ```
- **Wrong key**: Verify the key matches `INCEPT_API_KEY` exactly (case-sensitive).
- **Auth not intended**: If you don't want auth, unset `INCEPT_API_KEY`:
  ```bash
  unset INCEPT_API_KEY
  # or in Docker
  docker run -e INCEPT_API_KEY= incept
  ```

## No Command Match

**Symptom**: Response has `"status": "no_match"` or the REPL says "No matching command found."

**Causes and fixes**:

- **Ambiguous phrasing**: Rephrase the request to be more specific. Include the tool name if possible (e.g., "use grep to search for error in log.txt" instead of "look for errors").
- **Out-of-scope request**: INCEPT handles Linux system administration tasks only. Non-Linux requests (e.g., "write a Python script") return `OUT_OF_SCOPE`.
- **No compiler registered**: Some intents may not yet have a compiler implementation. Check `/v1/intents` for the full list of supported intents.
- **Preclassifier mismatch**: The regex-based preclassifier may not recognize unusual phrasing. The model-based classifier (when available) handles a wider range of inputs.

## Docker Build Failures

### Build runs out of memory

**Solution**: Increase Docker's memory allocation in Docker Desktop settings, or build with `--memory`:

```bash
docker build --memory=2g -t incept .
```

### Pip install fails during build

**Solution**: Check your network connectivity (dependencies are fetched during the builder stage). For air-gapped builds, pre-download wheels and use `--find-links`.

### Image too large

**Expected size**: Under 1 GB without the model file. If the image is significantly larger:

```bash
# Check image size
docker images incept

# Verify the multi-stage build is working (intermediate layers should not be in the final image)
docker history incept:latest
```

## Permission Issues

### Container can't write to model directory

**Symptom**: Permission denied when copying model files.

**Solution**: The model directory must be owned by UID 1000 (the `incept` user):

```bash
# Fix ownership on a bind mount
sudo chown -R 1000:1000 /path/to/models

# Or use a named volume (Docker manages ownership)
docker volume create model-data
```

### REPL history file not writable

**Symptom**: Warning about history file on REPL startup.

**Solution**: Ensure the history file location is writable:

```bash
touch ~/.incept_history
# Or change the path in ~/.config/incept/config.toml
```

## Request Timeouts (504)

**Symptom**: `{"detail": "Request timed out"}` with HTTP 504.

**Causes and fixes**:

- **Model inference too slow**: Increase the timeout:
  ```bash
  INCEPT_REQUEST_TIMEOUT=60 incept serve
  ```
- **System under heavy load**: Check CPU and memory usage. The Docker Compose config limits resources to 1 GB RAM and 2 CPUs by default.

## Getting Help

1. Check the API response body -- error messages include `reason` and `suggestion` fields.
2. Run the smoke test to verify basic functionality: `./scripts/smoke_test.sh`
3. Set `INCEPT_LOG_LEVEL=debug` for verbose logging.
4. Check `/v1/metrics` for request count and latency trends.
