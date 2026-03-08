"""Application state: shared across request handlers."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from incept.session.store import SessionStore


class AppState:
    """Shared application state for the FastAPI server."""

    def __init__(self, max_sessions: int = 1000) -> None:
        self.model: Any = None
        self.model_ready: bool = False
        self.lock: asyncio.Lock = asyncio.Lock()
        self.start_time: float = time.time()
        self.request_count: int = 0
        self.total_latency: float = 0.0
        self.session_store: SessionStore = SessionStore(max_sessions=max_sessions)

    def record_request(self, latency: float) -> None:
        """Record a completed request's latency."""
        self.request_count += 1
        self.total_latency += latency

    @property
    def uptime(self) -> float:
        """Seconds since server start."""
        return time.time() - self.start_time

    @property
    def avg_latency(self) -> float:
        """Average request latency in seconds."""
        if self.request_count == 0:
            return 0.0
        return self.total_latency / self.request_count
