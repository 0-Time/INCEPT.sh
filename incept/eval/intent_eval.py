"""Intent classification evaluation orchestration."""

from __future__ import annotations

from pathlib import Path

from incept.eval.loader import GoldenTestCase, load_golden_tests
from incept.eval.metrics import IntentMetrics, compute_intent_accuracy


def evaluate_intent_predictions(
    predictions: list[str],
    ground_truth: list[str],
) -> IntentMetrics:
    """Evaluate intent predictions against ground truth.

    Thin wrapper around compute_intent_accuracy for consistent API.
    """
    return compute_intent_accuracy(predictions, ground_truth)


def evaluate_golden_intents(
    predictions_dict: dict[str, str],
    golden_path: str | Path,
) -> IntentMetrics:
    """Evaluate intent predictions against golden test cases.

    Args:
        predictions_dict: Mapping of golden test ID → predicted intent label.
        golden_path: Path to the golden test JSONL file.

    Returns:
        IntentMetrics computed over matched test cases.
    """
    golden_tests = load_golden_tests(golden_path)
    golden_map: dict[str, GoldenTestCase] = {t.id: t for t in golden_tests}

    preds: list[str] = []
    gt: list[str] = []

    for test_id, pred_intent in predictions_dict.items():
        if test_id not in golden_map:
            continue
        preds.append(pred_intent)
        gt.append(golden_map[test_id].expected_intent.value)

    return compute_intent_accuracy(preds, gt)
