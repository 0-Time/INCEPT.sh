"""Parameter schemas for Archive Operations (2 intents)."""

from typing import Literal

from pydantic import BaseModel


class CompressArchiveParams(BaseModel):
    source: str
    destination: str | None = None
    format: Literal["tar.gz", "tar.bz2", "tar.xz", "zip"] = "tar.gz"
    exclude_pattern: str | None = None


class ExtractArchiveParams(BaseModel):
    source: str
    destination: str | None = None
