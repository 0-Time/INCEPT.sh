"""Health check routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from incept import __version__

router = APIRouter()


@router.get("/v1/health")
async def health(request: Request) -> dict[str, Any]:
    """Basic health check."""
    state = request.app.state.app_state
    return {
        "status": "ok",
        "version": __version__,
        "uptime": state.uptime,
    }


@router.get("/v1/health/ready")
async def ready(request: Request) -> dict[str, Any]:
    """Readiness check — model loaded and warm."""
    state = request.app.state.app_state
    return {"ready": state.model_ready}
