"""Explain endpoint: POST /v1/explain."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from incept.explain.pipeline import run_explain_pipeline

router = APIRouter()


class ExplainRequest(BaseModel):
    """Request body for the explain endpoint."""

    command: str = Field(..., min_length=1)
    context: str | None = None


@router.post("/v1/explain")
async def explain(request: ExplainRequest) -> dict[str, Any]:
    """Explain a shell command."""
    resp = run_explain_pipeline(request.command, context_json=request.context)
    return resp.model_dump()
