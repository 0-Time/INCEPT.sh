"""SQLite telemetry store for local usage tracking."""

from __future__ import annotations

import csv
import json
import sqlite3
import time
from typing import Any

_VALID_TABLES: frozenset[str] = frozenset({"requests", "feedback", "errors"})


class TelemetryStore:
    """Local SQLite store for anonymized telemetry data.

    Args:
        db_path: Path to SQLite database file.
        enabled: Whether telemetry collection is enabled (opt-in).
        max_entries: Maximum rows before rotation.
    """

    def __init__(self, db_path: str, *, enabled: bool = False, max_entries: int = 10000) -> None:
        self.enabled = enabled
        self.max_entries = max_entries
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        cur = self._conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nl TEXT,
                intent TEXT,
                latency REAL,
                timestamp REAL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT,
                outcome TEXT,
                timestamp REAL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT,
                message TEXT,
                timestamp REAL
            )
        """)
        self._conn.commit()

    def log_request(self, nl: str, intent: str, latency: float) -> None:
        """Log a command request."""
        if not self.enabled:
            return
        self._conn.execute(
            "INSERT INTO requests (nl, intent, latency, timestamp) VALUES (?, ?, ?, ?)",
            (nl, intent, latency, time.time()),
        )
        self._conn.commit()
        self._rotate("requests")

    def log_feedback(self, command: str, outcome: str) -> None:
        """Log execution feedback."""
        if not self.enabled:
            return
        self._conn.execute(
            "INSERT INTO feedback (command, outcome, timestamp) VALUES (?, ?, ?)",
            (command, outcome, time.time()),
        )
        self._conn.commit()

    def log_error(self, error_type: str, message: str) -> None:
        """Log an error event."""
        if not self.enabled:
            return
        self._conn.execute(
            "INSERT INTO errors (error_type, message, timestamp) VALUES (?, ?, ?)",
            (error_type, message, time.time()),
        )
        self._conn.commit()

    def get_requests(self, limit: int = 100) -> list[dict[str, Any]]:
        """Fetch recent request logs."""
        rows = self._conn.execute(
            "SELECT * FROM requests ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_feedback(self, limit: int = 100) -> list[dict[str, Any]]:
        """Fetch recent feedback logs."""
        rows = self._conn.execute(
            "SELECT * FROM feedback ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_errors(self, limit: int = 100) -> list[dict[str, Any]]:
        """Fetch recent error logs."""
        rows = self._conn.execute(
            "SELECT * FROM errors ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def _rotate(self, table: str) -> None:
        """Remove oldest entries if over max_entries."""
        if table not in _VALID_TABLES:
            raise ValueError(f"Invalid table name: {table!r}")
        count = self._conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        if count > self.max_entries:
            excess = count - self.max_entries
            self._conn.execute(
                f"DELETE FROM {table} WHERE id IN (SELECT id FROM {table} ORDER BY id ASC LIMIT ?)",
                (excess,),
            )
            self._conn.commit()

    def export_csv(self, path: str) -> None:
        """Export request logs to CSV."""
        rows = self.get_requests(limit=100000)
        if not rows:
            return
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def export_jsonl(self, path: str) -> None:
        """Export request logs to JSONL."""
        rows = self.get_requests(limit=100000)
        with open(path, "w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
