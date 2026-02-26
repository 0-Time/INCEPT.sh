"""Parameter schemas for Process Management (3 intents)."""

from typing import Literal

from pydantic import BaseModel


class ProcessListParams(BaseModel):
    filter: str | None = None
    sort_by: Literal["cpu", "memory", "pid", "name"] | None = None
    user: str | None = None


class KillProcessParams(BaseModel):
    target: str
    signal: str | None = None
    force: bool = False


class SystemInfoParams(BaseModel):
    info_type: Literal["memory", "cpu", "uptime", "all"] = "all"
