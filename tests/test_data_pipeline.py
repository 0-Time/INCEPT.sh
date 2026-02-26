"""Tests for incept.training.data_pipeline — JSONL loading + formatting."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from incept.training.data_pipeline import (
    format_for_sft,
    load_jsonl,
    load_validation_dataset,
)


def _write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


class TestLoadJsonl:
    def test_load_basic(self, tmp_path: Path) -> None:
        records = [
            {"prompt": "hello", "completion": "world"},
            {"prompt": "foo", "completion": "bar"},
        ]
        p = tmp_path / "test.jsonl"
        _write_jsonl(records, p)
        loaded = load_jsonl(p)
        assert len(loaded) == 2
        assert loaded[0]["prompt"] == "hello"
        assert loaded[1]["completion"] == "bar"

    def test_skip_empty_lines(self, tmp_path: Path) -> None:
        p = tmp_path / "test.jsonl"
        p.write_text('{"a": 1}\n\n{"b": 2}\n   \n')
        loaded = load_jsonl(p)
        assert len(loaded) == 2

    def test_skip_comments(self, tmp_path: Path) -> None:
        p = tmp_path / "test.jsonl"
        p.write_text('# comment\n{"a": 1}\n')
        loaded = load_jsonl(p)
        assert len(loaded) == 1

    def test_empty_file(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.jsonl"
        p.write_text("")
        assert load_jsonl(p) == []

    def test_nonexistent_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_jsonl("/nonexistent/path.jsonl")

    def test_load_real_intent_sample(self) -> None:
        """Load first few records from actual intent training data."""
        path = Path("data/training/intent_train.jsonl")
        if not path.exists():
            pytest.skip("Training data not available")
        records = load_jsonl(path)
        assert len(records) > 0
        assert "prompt" in records[0]
        assert "completion" in records[0]

    def test_load_real_slot_sample(self) -> None:
        """Load first few records from actual slot training data."""
        path = Path("data/training/slot_train.jsonl")
        if not path.exists():
            pytest.skip("Training data not available")
        records = load_jsonl(path)
        assert len(records) > 0
        assert "prompt" in records[0]
        assert "completion" in records[0]


class TestFormatForSft:
    def test_basic_merge(self) -> None:
        record = {"prompt": "<s>[INST] classify [/INST]", "completion": "find_files</s>"}
        result = format_for_sft(record)
        assert result == {"text": "<s>[INST] classify [/INST]find_files</s>"}

    def test_missing_prompt(self) -> None:
        result = format_for_sft({"completion": "done"})
        assert result["text"] == "done"

    def test_missing_completion(self) -> None:
        result = format_for_sft({"prompt": "hello"})
        assert result["text"] == "hello"

    def test_empty_record(self) -> None:
        result = format_for_sft({})
        assert result["text"] == ""

    def test_extra_fields_ignored(self) -> None:
        record = {"prompt": "a", "completion": "b", "id": "X", "intent": "y"}
        result = format_for_sft(record)
        assert result == {"text": "ab"}


class TestLoadValidationDataset:
    def test_loads_intent_records(self, tmp_path: Path) -> None:
        records = [
            {
                "nl_request": "find big files",
                "context_line": "debian bash non-root safe",
                "expected_intent": "find_files",
                "expected_slots": {"path": "/var"},
            },
            {
                "nl_request": "list packages",
                "context_line": "ubuntu bash root safe",
                "expected_intent": "search_package",
                "expected_slots": {"query": "nginx"},
            },
        ]
        p = tmp_path / "val.jsonl"
        _write_jsonl(records, p)
        loaded = load_validation_dataset(p, task="intent")
        assert len(loaded) == 2
        assert loaded[0]["expected_intent"] == "find_files"

    def test_loads_slot_records(self, tmp_path: Path) -> None:
        records = [
            {
                "nl_request": "find big files",
                "context_line": "debian bash non-root safe",
                "expected_intent": "find_files",
                "expected_slots": {"path": "/var"},
            },
            {
                "nl_request": "what?",
                "context_line": "debian bash non-root safe",
                "expected_intent": "CLARIFY",
                # no expected_slots
            },
        ]
        p = tmp_path / "val.jsonl"
        _write_jsonl(records, p)
        loaded = load_validation_dataset(p, task="slot")
        assert len(loaded) == 1
        assert loaded[0]["expected_slots"] == {"path": "/var"}

    def test_skips_records_without_intent(self, tmp_path: Path) -> None:
        records = [
            {"nl_request": "something", "context_line": "debian"},
        ]
        p = tmp_path / "val.jsonl"
        _write_jsonl(records, p)
        loaded = load_validation_dataset(p, task="intent")
        assert len(loaded) == 0

    def test_empty_file(self, tmp_path: Path) -> None:
        p = tmp_path / "val.jsonl"
        p.write_text("")
        assert load_validation_dataset(p, task="intent") == []
