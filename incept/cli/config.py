"""CLI configuration loading from TOML files."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class InceptConfig(BaseModel):
    """User-facing CLI configuration."""

    safe_mode: bool = True
    verbosity: Literal["minimal", "normal", "detailed"] = "normal"
    auto_execute: bool = False
    color: bool = True
    prompt: str = "incept> "
    model_path: str | None = None
    history_file: str = "~/.incept_history"
    think: bool = False


def load_config(path: str | None = None) -> InceptConfig:
    """Load config from a TOML file. Returns defaults if file not found."""
    if path is None:
        path = str(Path.home() / ".config" / "incept" / "config.toml")

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except (FileNotFoundError, OSError):
        return InceptConfig()

    section = data.get("incept", {})
    valid = {k: v for k, v in section.items() if k in InceptConfig.model_fields}
    return InceptConfig(**valid)
