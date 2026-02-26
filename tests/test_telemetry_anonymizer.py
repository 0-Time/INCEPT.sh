"""Tests for telemetry PII anonymizer."""

from __future__ import annotations

from incept.telemetry.anonymizer import anonymize_nl


class TestAnonymizer:
    """PII stripping from natural language input."""

    def test_strips_absolute_paths(self) -> None:
        result = anonymize_nl("find files in /home/john/documents")
        assert "/home/john" not in result
        assert "find files" in result

    def test_strips_usernames(self) -> None:
        result = anonymize_nl("create user johndoe with password secret123")
        assert "johndoe" not in result or "USER" in result

    def test_strips_ip_addresses(self) -> None:
        result = anonymize_nl("connect to 192.168.1.100 via ssh")
        assert "192.168.1.100" not in result
        assert "connect" in result

    def test_preserves_intent_keywords(self) -> None:
        result = anonymize_nl("install nginx on the server")
        assert "install" in result
        assert "nginx" in result

    def test_strips_email(self) -> None:
        result = anonymize_nl("send log to admin@example.com")
        assert "admin@example.com" not in result

    def test_empty_string(self) -> None:
        assert anonymize_nl("") == ""

    def test_no_pii_unchanged(self) -> None:
        text = "list all running processes"
        assert anonymize_nl(text) == text
