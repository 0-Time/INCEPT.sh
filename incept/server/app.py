"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from incept.server.config import ServerConfig
from incept.server.middleware.auth import AuthMiddleware
from incept.server.middleware.rate_limit import RateLimitMiddleware
from incept.server.middleware.request_id import RequestIdMiddleware
from incept.server.middleware.security_headers import SecurityHeadersMiddleware
from incept.server.middleware.timeout import TimeoutMiddleware
from incept.server.routes import command, explain, feedback, health, intents, metrics
from incept.server.state import AppState


def create_app(config: ServerConfig | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if config is None:
        config = ServerConfig()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # Startup
        state = AppState(max_sessions=config.max_sessions)
        app.state.app_state = state

        # Warm up the GGUF model singleton
        from incept.core.model_loader import get_model

        model = get_model(config.model_path)
        state.model = model
        state.model_ready = model is not None

        yield
        # Shutdown (cleanup)

    app = FastAPI(
        title="INCEPT",
        description="Offline NL-to-Linux-command compiler API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Store config on app
    app.state.config = config

    # Initialize state eagerly for test clients (lifespan may not fire)
    app.state.app_state = AppState(max_sessions=config.max_sessions)

    # Middleware — order matters (outermost first)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(TimeoutMiddleware, timeout=config.request_timeout)
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=config.rate_limit,
        trust_proxy=config.trust_proxy,
    )
    app.add_middleware(AuthMiddleware, api_key=config.api_key)

    # Routes
    app.include_router(health.router)
    app.include_router(command.router)
    app.include_router(explain.router)
    app.include_router(feedback.router)
    app.include_router(intents.router)
    app.include_router(metrics.router)

    return app
