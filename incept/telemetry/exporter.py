"""Telemetry data export utilities."""

from __future__ import annotations

from incept.telemetry.store import TelemetryStore


def export_csv(store: TelemetryStore, path: str) -> None:
    """Export telemetry to CSV format."""
    store.export_csv(path)


def export_jsonl(store: TelemetryStore, path: str) -> None:
    """Export telemetry to JSONL format."""
    store.export_jsonl(path)
