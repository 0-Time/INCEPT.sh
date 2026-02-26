"""POST /v1/feedback route."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from incept.recovery.engine import RecoveryEngine
from incept.server.models import FeedbackRequest

router = APIRouter()

_engine = RecoveryEngine(max_retries=3)


@router.post("/v1/feedback")
async def feedback(req: FeedbackRequest, request: Request) -> dict[str, Any]:
    """Process execution feedback, optionally suggest recovery."""
    if req.outcome == "success":
        return {"status": "acknowledged"}

    # Failure — try recovery
    result = _engine.suggest_recovery(
        original_command=req.command,
        stderr=req.stderr,
        attempt=req.attempt,
    )

    return {
        "status": "recovery",
        "recovery": result.model_dump(),
    }
