"""Golden test case loader and validator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from incept.schemas.intents import IntentLabel


class GoldenTestCase(BaseModel):
    """A single golden test case."""

    id: str
    nl_request: str
    context_line: str = ""
    expected_intent: IntentLabel
    expected_slots: dict[str, Any] = Field(default_factory=dict)
    expected_command: str | None = None
    tags: list[str] = Field(default_factory=list)


def load_golden_tests(path: str | Path) -> list[GoldenTestCase]:
    """Load golden test cases from a JSONL file.

    Each line must be a valid JSON object conforming to GoldenTestCase schema.
    """
    path = Path(path)
    tests: list[GoldenTestCase] = []
    with open(path) as f:
        for _line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            data = json.loads(line)
            tests.append(GoldenTestCase(**data))
    return tests
