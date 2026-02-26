# Deployment Guide

INCEPT ships as a single Docker image with a multi-stage build. The image runs a FastAPI server via Uvicorn behind a non-root user.

## Building the Image

```bash
docker build -t incept .
```

The Dockerfile uses a two-stage build:

1. **Builder stage** (`python:3.11-slim`): installs Python dependencies from `pyproject.toml` with the `[server]` extra.
2. **Runtime stage** (`python:3.11-slim`): copies installed packages and application code, creates a non-root `incept` user (UID/GID 1000), and sets up the model directory.

## Running with Docker

### Standalone

```bash
docker run -d \
  --name incept \
  -p 8080:8080 \
  -e INCEPT_API_KEY=my-secret-key \
  -v model-data:/app/models \
  incept
```

### Docker Compose

```bash
docker-compose up -d
```

The provided `docker-compose.yml` includes:

- Port mapping: `8080:8080`
- Named volume `model-data` mounted at `/app/models`
- Resource limits: 1 GB memory, 2 CPUs
- Restart policy: `unless-stopped`
- Environment variable passthrough from the host

## Model Bundling

The GGUF model file must be available at `/app/models/v1/model.gguf` inside the container. Options:

1. **Volume mount** (recommended): bind a host directory or named volume to `/app/models`.
2. **Bake into image**: add a `COPY` instruction to the Dockerfile to include the model at build time.

```bash
# Example: copy model into a running container's volume
docker cp ./model.gguf incept:/app/models/v1/model.gguf
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `INCEPT_HOST` | `0.0.0.0` | Bind address |
| `INCEPT_PORT` | `8080` | Bind port |
| `INCEPT_API_KEY` | *(none)* | API key for Bearer auth (disabled if unset) |
| `INCEPT_RATE_LIMIT` | `60` | Max requests per minute per client IP |
| `INCEPT_TRUST_PROXY` | `false` | Use X-Forwarded-For for client IP (enable behind reverse proxy) |
| `INCEPT_MAX_SESSIONS` | `1000` | Maximum concurrent sessions (0 = unlimited) |
| `INCEPT_CORS_ORIGINS` | `*` | Comma-separated allowed CORS origins |
| `INCEPT_REQUEST_TIMEOUT` | `30.0` | Per-request timeout in seconds |
| `INCEPT_MODEL_PATH` | `/app/models/v1/model.gguf` | Path to GGUF model file |
| `INCEPT_SAFE_MODE` | `true` | Enable additional safety restrictions |
| `INCEPT_LOG_LEVEL` | `info` | Log level (`debug`, `info`, `warning`, `error`) |

## Resource Requirements

| Resource | Minimum | Recommended |
|---|---|---|
| RAM | 512 MB | 1 GB |
| CPU | 1 core | 2 cores |
| Disk | 200 MB (image) + model size | Same |

The Docker Compose file enforces `memory: 1g` and `cpus: 2.0` as hard limits.

## Health Check

The Dockerfile includes a built-in health check:

```
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/v1/health/ready')" || exit 1
```

This probes the `/v1/health/ready` endpoint every 30 seconds, allowing 10 seconds for initial startup.

## Container Security

- Runs as non-root user `incept` (UID 1000).
- No privileged mode or special capabilities required.
- Model directory is owned by the application user.
- Only port 8080 is exposed.

## Tagging and Versioning

Tag images with the application version for rollback support:

```bash
docker build -t incept:v0.1.0 .
docker tag incept:v0.1.0 incept:latest
```
