"""POST /v1/command route."""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Request

from incept.core.engine import InceptEngine
from incept.server.models import CommandRequest

router = APIRouter()

# Module-level engine singleton (loaded once on first request)
_engine: InceptEngine | None = None


def _get_engine() -> InceptEngine:
    global _engine
    if _engine is None:
        _engine = InceptEngine()
    return _engine


@router.post("/v1/command")
async def command(req: CommandRequest, request: Request) -> dict[str, Any]:
    """Translate natural language to Linux command."""
    state = request.app.state.app_state

    engine = _get_engine()

    start = time.time()
    resp = engine.ask(req.nl)
    latency = time.time() - start
    state.record_request(latency)

    return resp.model_dump()
