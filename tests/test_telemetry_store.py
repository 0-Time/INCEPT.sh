"""Tests for telemetry SQLite store."""

from __future__ import annotations

from pathlib import Path

import pytest

from incept.telemetry.store import TelemetryStore


class TestTelemetryStore:
    """SQLite telemetry storage tests."""

    def test_create_tables(self, tmp_path: Path) -> None:
        db = tmp_path / "telemetry.db"
        store = TelemetryStore(str(db), enabled=True)
        store.close()
        assert db.exists()

    def test_log_request(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True)
        store.log_request("install nginx", "install_package", 0.15)
        rows = store.get_requests(limit=10)
        assert len(rows) == 1
        assert rows[0]["intent"] == "install_package"
        store.close()

    def test_log_feedback(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True)
        store.log_feedback("apt install nginx", "success")
        rows = store.get_feedback(limit=10)
        assert len(rows) == 1
        store.close()

    def test_log_error(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True)
        store.log_error("ValueError", "bad input")
        rows = store.get_errors(limit=10)
        assert len(rows) == 1
        store.close()

    def test_opt_in_required(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=False)
        store.log_request("test", "test_intent", 0.1)
        rows = store.get_requests(limit=10)
        assert len(rows) == 0
        store.close()

    def test_rotation_by_count(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True, max_entries=5)
        for i in range(10):
            store.log_request(f"cmd {i}", "test", 0.1)
        rows = store.get_requests(limit=100)
        assert len(rows) <= 5
        store.close()


class TestTelemetryExport:
    """CSV and JSONL export tests."""

    def test_export_csv(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True)
        store.log_request("find files", "find_files", 0.2)
        csv_path = tmp_path / "export.csv"
        store.export_csv(str(csv_path))
        content = csv_path.read_text()
        assert "find_files" in content
        store.close()

    def test_export_jsonl(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True)
        store.log_request("list dir", "list_directory", 0.1)
        jsonl_path = tmp_path / "export.jsonl"
        store.export_jsonl(str(jsonl_path))
        content = jsonl_path.read_text()
        assert "list_directory" in content
        store.close()


class TestTableWhitelist:
    """Telemetry table name whitelist (Story 8.3d)."""

    def test_valid_table_requests(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True)
        # Should not raise
        store._rotate("requests")
        store.close()

    def test_valid_table_feedback(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True)
        store._rotate("feedback")
        store.close()

    def test_valid_table_errors(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True)
        store._rotate("errors")
        store.close()

    def test_invalid_table_raises(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True)
        with pytest.raises(ValueError, match="Invalid table"):
            store._rotate("users")
        store.close()

    def test_sql_injection_rejected(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True)
        with pytest.raises(ValueError, match="Invalid table"):
            store._rotate("requests; DROP TABLE requests; --")
        store.close()

    def test_empty_table_name_rejected(self, tmp_path: Path) -> None:
        store = TelemetryStore(str(tmp_path / "t.db"), enabled=True)
        with pytest.raises(ValueError, match="Invalid table"):
            store._rotate("")
        store.close()
