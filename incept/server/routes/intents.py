"""GET /v1/intents route."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from incept.schemas.intents import get_intent_descriptions

router = APIRouter()


@router.get("/v1/intents")
async def intents() -> dict[str, Any]:
    """Return all supported intents with descriptions."""
    return {"intents": get_intent_descriptions()}
