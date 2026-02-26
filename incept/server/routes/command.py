"""POST /v1/command route."""

from __future__ import annotations

import json
import time
from typing import Any

from fastapi import APIRouter, Request

from incept.core.pipeline import run_pipeline
from incept.server.models import CommandRequest

router = APIRouter()


@router.post("/v1/command")
async def command(req: CommandRequest, request: Request) -> dict[str, Any]:
    """Translate natural language to Linux command."""
    state = request.app.state.app_state

    context_json = json.dumps(req.context) if req.context else "{}"

    start = time.time()
    result = run_pipeline(
        nl_request=req.nl,
        context_json=context_json,
        verbosity=req.verbosity,
    )
    latency = time.time() - start
    state.record_request(latency)

    return result.model_dump()
