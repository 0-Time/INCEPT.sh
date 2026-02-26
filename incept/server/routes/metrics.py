"""GET /v1/metrics route — Prometheus-style text metrics."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("/v1/metrics")
async def metrics(request: Request) -> PlainTextResponse:
    """Return server metrics in text format."""
    state = request.app.state.app_state
    lines = [
        "# HELP request_count Total number of /v1/command requests",
        "# TYPE request_count counter",
        f"request_count {state.request_count}",
        "",
        "# HELP latency_seconds Average request latency",
        "# TYPE latency_seconds gauge",
        f"latency_seconds {state.avg_latency:.4f}",
        "",
        "# HELP uptime_seconds Server uptime",
        "# TYPE uptime_seconds gauge",
        f"uptime_seconds {state.uptime:.1f}",
    ]
    return PlainTextResponse("\n".join(lines) + "\n")
