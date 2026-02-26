"""Multi-step decomposer: splits compound NL requests into sub-requests."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field


class SubRequest(BaseModel):
    """A single sub-request extracted from a compound request."""

    text: str
    index: int
    has_reference: bool = False
    reference_type: str | None = None


class DecompositionResult(BaseModel):
    """Result of decomposing a compound request."""

    is_compound: bool = False
    sub_requests: list[SubRequest] = Field(default_factory=list)
    composition: Literal["sequential", "pipe", "independent"] = "sequential"
    was_truncated: bool = False
    original_text: str = ""


# Maximum sub-steps allowed
MAX_SUBSTEPS = 4

# fmt: off
# ── Split patterns ────────────────────────────────────────────────────────────

# Patterns that indicate command boundaries
_SPLIT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Explicit sequencing
    (re.compile(r",\s*then\s+", re.IGNORECASE), "then"),
    (re.compile(r"\s+and\s+then\s+", re.IGNORECASE), "and_then"),
    (re.compile(r"\s+then\s+", re.IGNORECASE), "then"),
    (re.compile(r"\s+after\s+that[,]?\s+", re.IGNORECASE), "after_that"),
    (re.compile(r"\s+afterwards[,]?\s+", re.IGNORECASE), "afterwards"),
    # "and" followed by a verb (indicates separate action)
    (re.compile(r",\s*and\s+(?=\w+\s)", re.IGNORECASE), "and_verb"),
    # Pipe indicator
    (re.compile(r"\s+pipe\s+(?:it\s+)?to\s+", re.IGNORECASE), "pipe"),
    (re.compile(r"\s*\|\s*", re.IGNORECASE), "pipe_char"),
    # Sentence boundaries with new action verbs
    (re.compile(r"\.\s+(?=[A-Z])", 0), "sentence"),
    (re.compile(r";\s+", 0), "semicolon"),
]

# Verbs that start a new action
_ACTION_VERBS = frozenset({
    "find", "search", "copy", "move", "delete", "remove", "create", "make",
    "list", "show", "install", "uninstall", "start", "stop", "restart",
    "enable", "disable", "kill", "check", "test", "ping", "download",
    "upload", "compress", "extract", "archive", "mount", "unmount",
    "change", "modify", "set", "add", "schedule", "view", "tail",
    "grep", "sort", "count", "replace", "filter", "connect",
})

# ── Pronoun/reference patterns ────────────────────────────────────────────────

_REFERENCE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bthem\b", re.IGNORECASE), "pronoun_them"),
    (re.compile(r"\bit\b", re.IGNORECASE), "pronoun_it"),
    (re.compile(r"\bthe\s+result(s)?\b", re.IGNORECASE), "the_result"),
    (re.compile(r"\bthe\s+output\b", re.IGNORECASE), "the_output"),
    (re.compile(r"\bthe\s+file(s)?\b", re.IGNORECASE), "the_files"),
    (re.compile(r"\bthose\b", re.IGNORECASE), "pronoun_those"),
    (re.compile(r"\bthese\b", re.IGNORECASE), "pronoun_these"),
]

# ── Before/after reordering patterns ─────────────────────────────────────────

_BEFORE_PATTERN = re.compile(r"\bbefore\s+", re.IGNORECASE)
_AFTER_PATTERN = re.compile(r"\bafter\s+", re.IGNORECASE)
# fmt: on


def _detect_references(text: str) -> tuple[bool, str | None]:
    """Detect pronoun/reference in a sub-request text."""
    for pattern, ref_type in _REFERENCE_PATTERNS:
        if pattern.search(text):
            return True, ref_type
    return False, None


def _infer_composition(
    parts: list[str], split_types: list[str]
) -> Literal["sequential", "pipe", "independent"]:
    """Infer composition type from split patterns used."""
    if any(t in ("pipe", "pipe_char") for t in split_types):
        return "pipe"
    if any(t in ("semicolon",) for t in split_types):
        return "independent"
    return "sequential"


def _has_action_verb(text: str) -> bool:
    """Check if text starts with or contains an action verb."""
    words = text.strip().lower().split()
    if not words:
        return False
    return words[0] in _ACTION_VERBS


def _split_on_and_verb(text: str) -> list[str]:
    """Split on ', and' only if followed by an action verb."""
    parts: list[str] = []
    remaining = text
    pattern = re.compile(r",\s*and\s+", re.IGNORECASE)

    while True:
        match = pattern.search(remaining)
        if not match:
            parts.append(remaining.strip())
            break

        before = remaining[: match.start()].strip()
        after = remaining[match.end() :].strip()

        if _has_action_verb(after):
            parts.append(before)
            remaining = after
        else:
            # Not a split point, keep searching after this match
            parts.append(remaining.strip())
            break

    return [p for p in parts if p]


def decompose(text: str) -> DecompositionResult:
    """Decompose a compound NL request into sub-requests.

    Detects split points, resolves pronouns, infers composition type,
    and enforces complexity limits.
    """
    result = DecompositionResult(original_text=text)

    # Try each split pattern
    parts: list[str] = [text]
    split_types: list[str] = []

    for pattern, split_type in _SPLIT_PATTERNS:
        new_parts: list[str] = []
        found = False
        for part in parts:
            splits = pattern.split(part)
            if len(splits) > 1:
                found = True
                # Filter out empty strings
                valid_splits = [s.strip() for s in splits if s.strip()]
                new_parts.extend(valid_splits)
                split_types.extend([split_type] * (len(valid_splits) - 1))
            else:
                new_parts.append(part)
        if found:
            parts = new_parts
            break  # Use first matching pattern

    # If no pattern matched, try "and + verb" splitting
    if len(parts) == 1:
        and_parts = _split_on_and_verb(text)
        if len(and_parts) > 1:
            parts = and_parts
            split_types = ["and_verb"] * (len(and_parts) - 1)

    # Handle before/after reordering for exactly 2 parts
    if len(parts) == 2:
        if _BEFORE_PATTERN.search(parts[0]) and not _BEFORE_PATTERN.search(parts[1]):
            # "Do X before Y" → Y should come first? No — "before" means X first
            # Actually "X before Y" means "do X, then do Y"
            # But "before you Y, X" means "X first, then Y"
            pass
        if _AFTER_PATTERN.search(parts[0]):
            # "After X, do Y" → X first, then Y → reverse
            parts = list(reversed(parts))
            # Clean up the "after" from the first part
            parts[0] = _AFTER_PATTERN.sub("", parts[0]).strip()

    # Not compound if only 1 part
    if len(parts) <= 1:
        result.is_compound = False
        result.sub_requests = [
            SubRequest(text=text.strip(), index=0)
        ]
        return result

    # Enforce complexity limit
    if len(parts) > MAX_SUBSTEPS:
        parts = parts[:MAX_SUBSTEPS]
        result.was_truncated = True

    # Build sub-requests with reference detection
    sub_requests: list[SubRequest] = []
    for i, part in enumerate(parts):
        has_ref, ref_type = _detect_references(part)
        sub_requests.append(
            SubRequest(
                text=part.strip(),
                index=i,
                has_reference=has_ref,
                reference_type=ref_type,
            )
        )

    result.is_compound = True
    result.sub_requests = sub_requests
    result.composition = _infer_composition(parts, split_types)

    return result
