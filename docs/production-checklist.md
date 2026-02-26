# Production Checklist

Complete this checklist before deploying INCEPT to a production environment.

## Build and Test

- [ ] All tests pass (`pytest` exits with code 0)
- [ ] Docker image builds successfully
- [ ] Docker image size is under 1 GB (excluding model file)
- [ ] Smoke test passes against the built image (`./scripts/smoke_test.sh`)

## Security

- [ ] `INCEPT_API_KEY` is set to a strong, random value
- [ ] API key is stored securely (not in source control)
- [ ] TLS is terminated at the reverse proxy (nginx, Caddy, Traefik, or load balancer)
- [ ] `INCEPT_SAFE_MODE` is `true` (the default)
- [ ] `INCEPT_CORS_ORIGINS` is restricted to known origins (not `*` in production)

## Rate Limiting, Sessions, and Timeouts

- [ ] `INCEPT_RATE_LIMIT` is set appropriately for expected traffic (per-IP bucket)
- [ ] `INCEPT_TRUST_PROXY` is `true` if behind a reverse proxy (for accurate per-IP rate limiting)
- [ ] `INCEPT_MAX_SESSIONS` is set based on expected concurrent users (default: 1000)
- [ ] `INCEPT_REQUEST_TIMEOUT` is set (default 30s is suitable for most deployments)

## Health and Monitoring

- [ ] Health check is configured in the orchestrator (Kubernetes, ECS, Docker Swarm)
  - Liveness: `GET /v1/health`
  - Readiness: `GET /v1/health/ready`
- [ ] Prometheus (or equivalent) is scraping `/v1/metrics`
- [ ] Monitoring alerts are configured:
  - Container unhealthy
  - High error rate (>5% over 5 minutes)
  - High latency (>5s average over 5 minutes)
  - Service unreachable

## Logging

- [ ] `INCEPT_LOG_LEVEL` is set to `info` or `warning` (not `debug` in production)
- [ ] Logs are forwarded to a centralized logging system
- [ ] Log rotation is configured if writing to disk

## Resources

- [ ] Memory limit is set (recommended: 1 GB)
- [ ] CPU limit is set (recommended: 2 CPUs)
- [ ] Disk space is sufficient for model file and SQLite telemetry (if enabled)

## Model

- [ ] Model file is present at `INCEPT_MODEL_PATH` (default: `/app/models/v1/model.gguf`)
- [ ] Model file version matches the deployment version
- [ ] `/v1/health/ready` returns `{"ready": true}`

## Rollback

- [ ] Previous Docker image version is tagged and available
- [ ] Rollback procedure is tested (`PREVIOUS_TAG=vX.Y.Z ./scripts/rollback.sh`)
- [ ] Rollback completes within acceptable downtime window

## Networking

- [ ] Only port 8080 (or the configured port) is exposed
- [ ] Network access is restricted to trusted clients
- [ ] No sensitive host directories are mounted into the container

## Final Verification

- [ ] Run `./scripts/smoke_test.sh` against the production URL
- [ ] Verify a sample request produces the expected command
- [ ] Verify a known-dangerous request is blocked
- [ ] Confirm `X-Request-ID` headers are present in responses
- [ ] Confirm security headers are present (`X-Content-Type-Options`, `X-Frame-Options`, etc.)
- [ ] Verify `POST /v1/explain` returns structured explanation for a known command
- [ ] Verify per-IP rate limiting works (two IPs get independent buckets)
