"""Parameter schemas for Log Operations (3 intents)."""


from pydantic import BaseModel


class ViewLogsParams(BaseModel):
    unit: str | None = None
    since: str | None = None
    until: str | None = None
    lines: int | None = None
    priority: str | None = None


class FollowLogsParams(BaseModel):
    unit: str | None = None


class FilterLogsParams(BaseModel):
    pattern: str
    unit: str | None = None
    since: str | None = None
    until: str | None = None
