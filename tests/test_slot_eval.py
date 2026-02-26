"""Tests for incept.eval.slot_eval — slot evaluation orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from incept.eval.slot_eval import evaluate_golden_slots, evaluate_slot_predictions


def _write_golden(records: list[dict[str, Any]], path: Path) -> None:
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


class TestEvaluateSlotPredictions:
    def test_perfect(self) -> None:
        m = evaluate_slot_predictions(
            [{"file": "/tmp"}, {"path": "/var"}],
            [{"file": "/tmp"}, {"path": "/var"}],
        )
        assert m.exact_match == 1.0
        assert m.slot_f1 == 1.0
        assert m.total == 2

    def test_zero_match(self) -> None:
        m = evaluate_slot_predictions(
            [{"file": "/tmp"}],
            [{"file": "/etc"}],
        )
        assert m.exact_match == 0.0

    def test_with_intents(self) -> None:
        m = evaluate_slot_predictions(
            [{"file": "/tmp"}, {"path": "/var"}],
            [{"file": "/tmp"}, {"path": "/var"}],
            intents=["find_files", "copy_files"],
        )
        assert m.per_intent_exact_match["find_files"] == 1.0
        assert m.per_intent_exact_match["copy_files"] == 1.0

    def test_empty(self) -> None:
        m = evaluate_slot_predictions([], [])
        assert m.total == 0


class TestEvaluateGoldenSlots:
    def test_all_correct(self, tmp_path: Path) -> None:
        golden = [
            {
                "id": "GT001",
                "nl_request": "find big files",
                "expected_intent": "find_files",
                "expected_slots": {"path": "/var/log", "size_gt": "50M"},
            },
            {
                "id": "GT002",
                "nl_request": "copy data",
                "expected_intent": "copy_files",
                "expected_slots": {"source": "/tmp/a", "dest": "/tmp/b"},
            },
        ]
        gp = tmp_path / "golden.jsonl"
        _write_golden(golden, gp)

        preds = {
            "GT001": {"path": "/var/log", "size_gt": "50M"},
            "GT002": {"source": "/tmp/a", "dest": "/tmp/b"},
        }
        m = evaluate_golden_slots(preds, gp)
        assert m.exact_match == 1.0
        assert m.total == 2

    def test_partial(self, tmp_path: Path) -> None:
        golden = [
            {
                "id": "GT001",
                "nl_request": "find big files",
                "expected_intent": "find_files",
                "expected_slots": {"path": "/var/log", "size_gt": "50M"},
            },
        ]
        gp = tmp_path / "golden.jsonl"
        _write_golden(golden, gp)

        preds = {"GT001": {"path": "/var/log", "size_gt": "100M"}}
        m = evaluate_golden_slots(preds, gp)
        assert m.exact_match == 0.0
        assert m.slot_f1 > 0.0  # partial credit for path match

    def test_unknown_ids_skipped(self, tmp_path: Path) -> None:
        golden = [
            {
                "id": "GT001",
                "nl_request": "find big files",
                "expected_intent": "find_files",
                "expected_slots": {"path": "/var"},
            },
        ]
        gp = tmp_path / "golden.jsonl"
        _write_golden(golden, gp)

        preds = {"GT001": {"path": "/var"}, "GT999": {"x": "y"}}
        m = evaluate_golden_slots(preds, gp)
        assert m.total == 1

    def test_per_intent_breakdown(self, tmp_path: Path) -> None:
        golden = [
            {
                "id": "GT001",
                "nl_request": "find",
                "expected_intent": "find_files",
                "expected_slots": {"path": "/var"},
            },
            {
                "id": "GT002",
                "nl_request": "copy",
                "expected_intent": "copy_files",
                "expected_slots": {"source": "/a"},
            },
        ]
        gp = tmp_path / "golden.jsonl"
        _write_golden(golden, gp)

        preds = {
            "GT001": {"path": "/var"},
            "GT002": {"source": "/b"},  # wrong value
        }
        m = evaluate_golden_slots(preds, gp)
        assert m.per_intent_exact_match["find_files"] == 1.0
        assert m.per_intent_exact_match["copy_files"] == 0.0

    def test_empty_predictions(self, tmp_path: Path) -> None:
        golden = [
            {
                "id": "GT001",
                "nl_request": "find",
                "expected_intent": "find_files",
                "expected_slots": {"path": "/var"},
            },
        ]
        gp = tmp_path / "golden.jsonl"
        _write_golden(golden, gp)

        m = evaluate_golden_slots({}, gp)
        assert m.total == 0
