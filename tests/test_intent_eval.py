"""Tests for incept.eval.intent_eval — evaluation orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from incept.eval.intent_eval import evaluate_golden_intents, evaluate_intent_predictions


def _write_golden(records: list[dict[str, Any]], path: Path) -> None:
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


class TestEvaluateIntentPredictions:
    def test_perfect(self) -> None:
        m = evaluate_intent_predictions(
            ["find_files", "copy_files"],
            ["find_files", "copy_files"],
        )
        assert m.accuracy == 1.0
        assert m.total == 2

    def test_partial(self) -> None:
        m = evaluate_intent_predictions(
            ["find_files", "move_files"],
            ["find_files", "copy_files"],
        )
        assert m.accuracy == 0.5

    def test_empty(self) -> None:
        m = evaluate_intent_predictions([], [])
        assert m.accuracy == 0.0
        assert m.total == 0


class TestEvaluateGoldenIntents:
    def test_all_correct(self, tmp_path: Path) -> None:
        golden = [
            {
                "id": "GT001",
                "nl_request": "find big files",
                "expected_intent": "find_files",
                "expected_slots": {},
            },
            {
                "id": "GT002",
                "nl_request": "copy data",
                "expected_intent": "copy_files",
                "expected_slots": {},
            },
        ]
        gp = tmp_path / "golden.jsonl"
        _write_golden(golden, gp)

        preds = {"GT001": "find_files", "GT002": "copy_files"}
        m = evaluate_golden_intents(preds, gp)
        assert m.accuracy == 1.0
        assert m.total == 2

    def test_partial_correct(self, tmp_path: Path) -> None:
        golden = [
            {
                "id": "GT001",
                "nl_request": "find big files",
                "expected_intent": "find_files",
                "expected_slots": {},
            },
            {
                "id": "GT002",
                "nl_request": "copy data",
                "expected_intent": "copy_files",
                "expected_slots": {},
            },
        ]
        gp = tmp_path / "golden.jsonl"
        _write_golden(golden, gp)

        preds = {"GT001": "find_files", "GT002": "move_files"}
        m = evaluate_golden_intents(preds, gp)
        assert m.accuracy == 0.5

    def test_unknown_ids_skipped(self, tmp_path: Path) -> None:
        golden = [
            {
                "id": "GT001",
                "nl_request": "find big files",
                "expected_intent": "find_files",
                "expected_slots": {},
            },
        ]
        gp = tmp_path / "golden.jsonl"
        _write_golden(golden, gp)

        preds = {"GT001": "find_files", "GT999": "copy_files"}
        m = evaluate_golden_intents(preds, gp)
        assert m.total == 1
        assert m.accuracy == 1.0

    def test_empty_predictions(self, tmp_path: Path) -> None:
        golden = [
            {
                "id": "GT001",
                "nl_request": "find big files",
                "expected_intent": "find_files",
                "expected_slots": {},
            },
        ]
        gp = tmp_path / "golden.jsonl"
        _write_golden(golden, gp)

        m = evaluate_golden_intents({}, gp)
        assert m.total == 0
