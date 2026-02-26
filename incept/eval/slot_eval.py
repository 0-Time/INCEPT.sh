"""Slot filling evaluation orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from incept.eval.loader import GoldenTestCase, load_golden_tests
from incept.eval.metrics import SlotMetrics, compute_slot_metrics


def evaluate_slot_predictions(
    predictions: list[dict[str, Any]],
    ground_truth: list[dict[str, Any]],
    intents: list[str] | None = None,
) -> SlotMetrics:
    """Evaluate slot predictions against ground truth.

    Thin wrapper around compute_slot_metrics for consistent API.
    """
    return compute_slot_metrics(predictions, ground_truth, intents=intents)


def evaluate_golden_slots(
    predictions_dict: dict[str, dict[str, Any]],
    golden_path: str | Path,
) -> SlotMetrics:
    """Evaluate slot predictions against golden test cases.

    Args:
        predictions_dict: Mapping of golden test ID → predicted slot dict.
        golden_path: Path to the golden test JSONL file.

    Returns:
        SlotMetrics computed over matched test cases.
    """
    golden_tests = load_golden_tests(golden_path)
    golden_map: dict[str, GoldenTestCase] = {t.id: t for t in golden_tests}

    preds: list[dict[str, Any]] = []
    gt: list[dict[str, Any]] = []
    intents: list[str] = []

    for test_id, pred_slots in predictions_dict.items():
        if test_id not in golden_map:
            continue
        test = golden_map[test_id]
        preds.append(pred_slots)
        gt.append(test.expected_slots)
        intents.append(test.expected_intent.value)

    return compute_slot_metrics(preds, gt, intents=intents)
