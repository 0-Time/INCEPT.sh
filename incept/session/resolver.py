"""Cross-turn reference resolution."""

from __future__ import annotations

import re

from incept.session.models import Session

# Patterns that indicate a pronoun/reference needing resolution
_PRONOUN_PATTERNS = [
    (re.compile(r"\bit\b", re.IGNORECASE), "it"),
    (re.compile(r"\bthem\b", re.IGNORECASE), "them"),
    (re.compile(r"\bthat service\b", re.IGNORECASE), "that service"),
    (re.compile(r"\bthe file\b", re.IGNORECASE), "the file"),
    (re.compile(r"\bthat file\b", re.IGNORECASE), "that file"),
    (re.compile(r"\bthose\b", re.IGNORECASE), "those"),
]


def resolve_references(text: str, session: Session) -> str:
    """Replace pronouns/references with the subject from the most recent turn.

    If no previous subject exists, returns the text unchanged.
    """
    if not text:
        return text

    subject = session.prev_line()
    if not subject:
        return text

    result = text
    for pattern, _label in _PRONOUN_PATTERNS:
        if pattern.search(result):
            result = pattern.sub(subject, result)
            break  # Only resolve the first matching pronoun

    return result
