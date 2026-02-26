"""PII anonymizer for telemetry data."""

from __future__ import annotations

import re

# Patterns to strip PII
_IP_PATTERN = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_HOME_PATH_PATTERN = re.compile(r"/home/[a-zA-Z0-9._-]+")
_USER_PATH_PATTERN = re.compile(r"/Users/[a-zA-Z0-9._-]+")
_USERNAME_PATTERN = re.compile(r"\b(?:user|username|login)\s+([a-zA-Z0-9._-]+)")


def anonymize_nl(text: str) -> str:
    """Strip PII from natural language input while preserving intent keywords.

    Removes: IP addresses, email addresses, home directory paths, usernames.
    Preserves: command keywords, package names, service names.
    """
    if not text:
        return text

    result = text
    result = _IP_PATTERN.sub("<IP>", result)
    result = _EMAIL_PATTERN.sub("<EMAIL>", result)
    result = _HOME_PATH_PATTERN.sub("<HOME>", result)
    result = _USER_PATH_PATTERN.sub("<HOME>", result)
    result = _USERNAME_PATTERN.sub(lambda m: "user <USER>", result)

    return result
