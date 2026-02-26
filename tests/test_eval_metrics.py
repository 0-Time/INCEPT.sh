"""Tests for incept.eval.metrics — fully local, no ML deps."""

from __future__ import annotations

import pytest

from incept.eval.metrics import (
    _slot_f1_single,
    compute_intent_accuracy,
    compute_slot_metrics,
)


class TestComputeIntentAccuracy:
    def test_perfect_accuracy(self) -> None:
        preds = ["find_files", "copy_files", "delete_files"]
        gt = ["find_files", "copy_files", "delete_files"]
        m = compute_intent_accuracy(preds, gt)
        assert m.accuracy == 1.0
        assert m.total == 3
        assert m.correct == 3
        assert m.confusion_pairs == []

    def test_zero_accuracy(self) -> None:
        preds = ["copy_files", "delete_files", "find_files"]
        gt = ["find_files", "copy_files", "delete_files"]
        m = compute_intent_accuracy(preds, gt)
        assert m.accuracy == 0.0
        assert m.correct == 0

    def test_partial_accuracy(self) -> None:
        preds = ["find_files", "copy_files", "move_files", "delete_files"]
        gt = ["find_files", "copy_files", "search_text", "delete_files"]
        m = compute_intent_accuracy(preds, gt)
        assert m.accuracy == 0.75
        assert m.correct == 3
        assert m.total == 4

    def test_per_intent_accuracy(self) -> None:
        preds = ["find_files", "find_files", "copy_files", "copy_files"]
        gt = ["find_files", "find_files", "copy_files", "find_files"]
        m = compute_intent_accuracy(preds, gt)
        assert m.per_intent_accuracy["find_files"] == pytest.approx(2 / 3)
        assert m.per_intent_accuracy["copy_files"] == 1.0

    def test_confusion_pairs(self) -> None:
        preds = ["copy_files", "copy_files", "find_files"]
        gt = ["find_files", "find_files", "find_files"]
        m = compute_intent_accuracy(preds, gt)
        assert len(m.confusion_pairs) == 1
        assert m.confusion_pairs[0] == ("find_files", "copy_files", 2)

    def test_empty_inputs(self) -> None:
        m = compute_intent_accuracy([], [])
        assert m.accuracy == 0.0
        assert m.total == 0

    def test_length_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="Length mismatch"):
            compute_intent_accuracy(["a"], ["a", "b"])

    def test_single_element(self) -> None:
        m = compute_intent_accuracy(["find_files"], ["find_files"])
        assert m.accuracy == 1.0
        assert m.total == 1

    def test_confusion_pairs_sorted_by_count(self) -> None:
        preds = ["a", "a", "b", "c", "c", "c"]
        gt = ["b", "b", "a", "a", "a", "a"]
        m = compute_intent_accuracy(preds, gt)
        # (a, c) appears 3 times, (b, a) appears 2 times
        assert m.confusion_pairs[0][2] >= m.confusion_pairs[1][2]


class TestSlotF1Single:
    def test_perfect_match(self) -> None:
        p, r, f1 = _slot_f1_single({"file": "/etc/hosts"}, {"file": "/etc/hosts"})
        assert f1 == 1.0

    def test_no_overlap(self) -> None:
        p, r, f1 = _slot_f1_single({"file": "/tmp"}, {"path": "/etc"})
        assert f1 == 0.0

    def test_partial_overlap(self) -> None:
        pred = {"file": "/tmp", "mode": "755"}
        gt = {"file": "/tmp", "owner": "root"}
        p, r, f1 = _slot_f1_single(pred, gt)
        # tp=1, pred=2, gt=2 → p=0.5, r=0.5, f1=0.5
        assert f1 == pytest.approx(0.5)

    def test_both_empty(self) -> None:
        p, r, f1 = _slot_f1_single({}, {})
        assert f1 == 1.0

    def test_pred_empty(self) -> None:
        p, r, f1 = _slot_f1_single({}, {"file": "/tmp"})
        assert f1 == 0.0

    def test_gt_empty(self) -> None:
        p, r, f1 = _slot_f1_single({"file": "/tmp"}, {})
        assert f1 == 0.0


class TestComputeSlotMetrics:
    def test_perfect_slots(self) -> None:
        preds = [{"file": "/tmp"}, {"path": "/var"}]
        gt = [{"file": "/tmp"}, {"path": "/var"}]
        m = compute_slot_metrics(preds, gt)
        assert m.exact_match == 1.0
        assert m.slot_f1 == 1.0
        assert m.total == 2

    def test_zero_exact_match(self) -> None:
        preds = [{"file": "/tmp"}, {"path": "/var"}]
        gt = [{"file": "/etc"}, {"path": "/home"}]
        m = compute_slot_metrics(preds, gt)
        assert m.exact_match == 0.0
        assert m.slot_f1 == 0.0

    def test_partial_match(self) -> None:
        preds = [{"file": "/tmp", "mode": "755"}, {"path": "/var"}]
        gt = [{"file": "/tmp", "owner": "root"}, {"path": "/var"}]
        m = compute_slot_metrics(preds, gt)
        assert m.exact_match == 0.5
        assert 0.5 < m.slot_f1 < 1.0

    def test_with_intents(self) -> None:
        preds = [{"file": "/tmp"}, {"path": "/var"}, {"file": "/etc"}]
        gt = [{"file": "/tmp"}, {"path": "/var"}, {"file": "/etc"}]
        intents = ["find_files", "find_files", "copy_files"]
        m = compute_slot_metrics(preds, gt, intents=intents)
        assert m.per_intent_exact_match["find_files"] == 1.0
        assert m.per_intent_exact_match["copy_files"] == 1.0
        assert m.per_intent_f1["find_files"] == 1.0

    def test_empty_inputs(self) -> None:
        m = compute_slot_metrics([], [])
        assert m.exact_match == 0.0
        assert m.total == 0

    def test_length_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="Length mismatch"):
            compute_slot_metrics([{}], [{}, {}])

    def test_worst_intents(self) -> None:
        preds = [{"a": "1"}, {"b": "2"}, {"c": "3"}]
        gt = [{"a": "X"}, {"b": "2"}, {"c": "3"}]
        intents = ["bad_intent", "good1", "good2"]
        m = compute_slot_metrics(preds, gt, intents=intents)
        assert m.worst_intents[0][0] == "bad_intent"
        assert m.worst_intents[0][1] == 0.0

    def test_slot_values_stringified(self) -> None:
        """Values are compared as strings."""
        preds = [{"count": 5}]
        gt = [{"count": 5}]
        m = compute_slot_metrics(preds, gt)
        assert m.exact_match == 1.0

    def test_mixed_types_in_values(self) -> None:
        """String '5' vs int 5 should match after stringification."""
        preds = [{"count": "5"}]
        gt = [{"count": 5}]
        m = compute_slot_metrics(preds, gt)
        assert m.exact_match == 1.0
