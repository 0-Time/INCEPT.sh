# ── Stage 1: Build ──────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build
COPY pyproject.toml .
COPY incept/ incept/

RUN pip install --no-cache-dir ".[server]" \
    && pip install --no-cache-dir --target=/deps ".[server]"

# ── Stage 2: Runtime ────────────────────────────────────────────────
FROM python:3.11-slim

# Create non-root user
RUN groupadd -g 1000 incept && useradd -u 1000 -g incept -m incept

WORKDIR /app

# Copy installed packages and application
COPY --from=builder /deps /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY incept/ /app/incept/
COPY pyproject.toml /app/

# Create model directory
RUN mkdir -p /app/models/v1 && chown -R incept:incept /app

USER incept

# Environment defaults
ENV INCEPT_HOST=0.0.0.0 \
    INCEPT_PORT=8080 \
    INCEPT_SAFE_MODE=true \
    INCEPT_LOG_LEVEL=info \
    INCEPT_MODEL_PATH=/app/models/v1/model.gguf

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/v1/health/ready')" || exit 1

ENTRYPOINT ["python", "-m", "incept", "serve"]
