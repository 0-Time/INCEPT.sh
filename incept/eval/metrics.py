"""Evaluation metrics for intent classification and slot filling."""

from __future__ import annotations

from collections import Counter
from typing import Any

from pydantic import BaseModel, Field


class IntentMetrics(BaseModel):
    """Metrics for intent classification evaluation."""

    accuracy: float = Field(ge=0.0, le=1.0)
    total: int = Field(ge=0)
    correct: int = Field(ge=0)
    per_intent_accuracy: dict[str, float] = Field(default_factory=dict)
    confusion_pairs: list[tuple[str, str, int]] = Field(default_factory=list)


class SlotMetrics(BaseModel):
    """Metrics for slot filling evaluation."""

    exact_match: float = Field(ge=0.0, le=1.0)
    slot_f1: float = Field(ge=0.0, le=1.0)
    total: int = Field(ge=0)
    per_intent_exact_match: dict[str, float] = Field(default_factory=dict)
    per_intent_f1: dict[str, float] = Field(default_factory=dict)
    worst_intents: list[tuple[str, float]] = Field(default_factory=list)


def compute_intent_accuracy(
    predictions: list[str],
    ground_truth: list[str],
) -> IntentMetrics:
    """Compute intent classification accuracy and per-intent breakdown.

    Args:
        predictions: List of predicted intent labels.
        ground_truth: List of ground-truth intent labels.

    Returns:
        IntentMetrics with accuracy, per-intent accuracy, and confusion pairs.
    """
    if len(predictions) != len(ground_truth):
        msg = (
            f"Length mismatch: {len(predictions)} predictions "
            f"vs {len(ground_truth)} ground truth"
        )
        raise ValueError(msg)

    total = len(predictions)
    if total == 0:
        return IntentMetrics(accuracy=0.0, total=0, correct=0)

    correct = sum(p == g for p, g in zip(predictions, ground_truth, strict=True))
    accuracy = correct / total

    # Per-intent accuracy
    intent_correct: Counter[str] = Counter()
    intent_total: Counter[str] = Counter()
    confusion: Counter[tuple[str, str]] = Counter()

    for pred, gt in zip(predictions, ground_truth, strict=True):
        intent_total[gt] += 1
        if pred == gt:
            intent_correct[gt] += 1
        else:
            confusion[(gt, pred)] += 1

    per_intent = {
        intent: intent_correct[intent] / intent_total[intent]
        for intent in sorted(intent_total)
    }

    # Top confusion pairs, sorted by count descending
    confusion_pairs = sorted(
        [(gt, pred, count) for (gt, pred), count in confusion.items()],
        key=lambda x: x[2],
        reverse=True,
    )[:20]

    return IntentMetrics(
        accuracy=round(accuracy, 4),
        total=total,
        correct=correct,
        per_intent_accuracy=per_intent,
        confusion_pairs=confusion_pairs,
    )


def _slot_f1_single(
    pred_slots: dict[str, Any], gt_slots: dict[str, Any]
) -> tuple[float, float, float]:
    """Compute precision, recall, F1 for a single example's slots.

    Compares slot key-value pairs as sets.
    """
    pred_set = {(k, str(v)) for k, v in pred_slots.items()}
    gt_set = {(k, str(v)) for k, v in gt_slots.items()}

    if not gt_set and not pred_set:
        return 1.0, 1.0, 1.0
    if not gt_set:
        return 0.0, 1.0, 0.0
    if not pred_set:
        return 1.0, 0.0, 0.0

    tp = len(pred_set & gt_set)
    precision = tp / len(pred_set) if pred_set else 0.0
    recall = tp / len(gt_set) if gt_set else 0.0

    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)

    return precision, recall, f1


def compute_slot_metrics(
    predictions: list[dict[str, Any]],
    ground_truth: list[dict[str, Any]],
    intents: list[str] | None = None,
) -> SlotMetrics:
    """Compute slot filling metrics: exact match and F1.

    Args:
        predictions: List of predicted slot dicts.
        ground_truth: List of ground-truth slot dicts.
        intents: Optional list of intent labels per example (for per-intent breakdown).

    Returns:
        SlotMetrics with exact_match, slot_f1, and per-intent breakdowns.
    """
    if len(predictions) != len(ground_truth):
        msg = (
            f"Length mismatch: {len(predictions)} predictions "
            f"vs {len(ground_truth)} ground truth"
        )
        raise ValueError(msg)

    total = len(predictions)
    if total == 0:
        return SlotMetrics(exact_match=0.0, slot_f1=0.0, total=0)

    exact_matches = 0
    f1_scores: list[float] = []

    intent_exact: dict[str, list[bool]] = {}
    intent_f1: dict[str, list[float]] = {}

    for i, (pred, gt) in enumerate(zip(predictions, ground_truth, strict=True)):
        # Normalize to string values for comparison
        pred_norm = {k: str(v) for k, v in pred.items()}
        gt_norm = {k: str(v) for k, v in gt.items()}

        is_exact = pred_norm == gt_norm
        if is_exact:
            exact_matches += 1

        _, _, f1 = _slot_f1_single(pred, gt)
        f1_scores.append(f1)

        if intents and i < len(intents):
            intent = intents[i]
            intent_exact.setdefault(intent, []).append(is_exact)
            intent_f1.setdefault(intent, []).append(f1)

    exact_match_rate = exact_matches / total
    avg_f1 = sum(f1_scores) / len(f1_scores)

    per_intent_em = {
        intent: sum(matches) / len(matches)
        for intent, matches in sorted(intent_exact.items())
    }
    per_intent_f1_avg = {
        intent: sum(scores) / len(scores)
        for intent, scores in sorted(intent_f1.items())
    }

    # Worst intents by F1 (bottom 10)
    worst = sorted(per_intent_f1_avg.items(), key=lambda x: x[1])[:10]

    return SlotMetrics(
        exact_match=round(exact_match_rate, 4),
        slot_f1=round(avg_f1, 4),
        total=total,
        per_intent_exact_match=per_intent_em,
        per_intent_f1=per_intent_f1_avg,
        worst_intents=worst,
    )
