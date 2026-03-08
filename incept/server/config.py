"""Server configuration from environment variables."""

from __future__ import annotations

import os

from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """FastAPI server configuration."""

    host: str = "127.0.0.1"
    port: int = 8080
    api_key: str | None = None
    rate_limit: int = 60  # requests per minute
    cors_origins: list[str] = Field(default_factory=list)
    request_timeout: float = 30.0
    model_path: str | None = None
    warm_up_count: int = 0
    safe_mode: bool = True
    log_level: str = "info"
    trust_proxy: bool = False
    max_sessions: int = 1000

    @classmethod
    def from_env(cls) -> ServerConfig:
        """Create config from environment variables."""
        cors_raw = os.environ.get("INCEPT_CORS_ORIGINS", "")
        cors = [o.strip() for o in cors_raw.split(",") if o.strip()] if cors_raw else []

        safe_raw = os.environ.get("INCEPT_SAFE_MODE", "true")
        safe_mode = safe_raw.lower() not in ("false", "0", "no")

        return cls(
            host=os.environ.get("INCEPT_HOST", "127.0.0.1"),
            port=int(os.environ.get("INCEPT_PORT", "8080")),
            api_key=os.environ.get("INCEPT_API_KEY"),
            rate_limit=int(os.environ.get("INCEPT_RATE_LIMIT", "60")),
            cors_origins=cors,
            request_timeout=float(os.environ.get("INCEPT_REQUEST_TIMEOUT", "30.0")),
            model_path=os.environ.get("INCEPT_MODEL_PATH"),
            safe_mode=safe_mode,
            log_level=os.environ.get("INCEPT_LOG_LEVEL", "info"),
            trust_proxy=os.environ.get("INCEPT_TRUST_PROXY", "false").lower()
            in ("true", "1", "yes"),
            max_sessions=int(os.environ.get("INCEPT_MAX_SESSIONS", "1000")),
        )
