"""Tests for incept.confidence.scoring — fully local, no ML deps."""

from __future__ import annotations

import pytest

from incept.confidence.scoring import (
    ConfidenceLevel,
    ConfidenceResult,
    _classify_level,
    _logprob_to_prob,
    compute_confidence,
    to_confidence_score,
)
from incept.schemas.ir import ConfidenceScore


class TestLogprobToProb:
    def test_zero_logprob(self) -> None:
        assert _logprob_to_prob(0.0) == 1.0

    def test_negative_logprob(self) -> None:
        result = _logprob_to_prob(-0.1)
        assert 0.9 < result < 1.0

    def test_very_negative_logprob(self) -> None:
        result = _logprob_to_prob(-10.0)
        assert result < 0.001

    def test_large_positive_clamped(self) -> None:
        # exp(1.0) > 1.0, should clamp to 1.0
        assert _logprob_to_prob(1.0) == 1.0

    def test_negative_inf(self) -> None:
        assert _logprob_to_prob(float("-inf")) == 0.0


class TestClassifyLevel:
    def test_high(self) -> None:
        assert _classify_level(0.95) == ConfidenceLevel.HIGH
        assert _classify_level(0.90) == ConfidenceLevel.HIGH

    def test_medium(self) -> None:
        assert _classify_level(0.85) == ConfidenceLevel.MEDIUM
        assert _classify_level(0.70) == ConfidenceLevel.MEDIUM

    def test_low(self) -> None:
        assert _classify_level(0.65) == ConfidenceLevel.LOW
        assert _classify_level(0.50) == ConfidenceLevel.LOW

    def test_very_low(self) -> None:
        assert _classify_level(0.49) == ConfidenceLevel.VERY_LOW
        assert _classify_level(0.0) == ConfidenceLevel.VERY_LOW


class TestComputeConfidence:
    def test_perfect_scores(self) -> None:
        """All perfect → HIGH confidence."""
        result = compute_confidence(
            intent_logprob=0.0,
            slot_logprobs=[0.0, 0.0],
            retrieval_score=1.0,
            compiler_had_fallbacks=False,
        )
        assert result.intent == 1.0
        assert result.slots == 1.0
        assert result.composite == 1.0
        assert result.level == ConfidenceLevel.HIGH

    def test_no_slots(self) -> None:
        """No slot logprobs → slot confidence defaults to 1.0."""
        result = compute_confidence(intent_logprob=0.0, slot_logprobs=None)
        assert result.slots == 1.0
        assert result.composite == 1.0

    def test_empty_slots(self) -> None:
        """Empty slot list → slot confidence defaults to 1.0."""
        result = compute_confidence(intent_logprob=0.0, slot_logprobs=[])
        assert result.slots == 1.0

    def test_fallback_penalty(self) -> None:
        """Fallback penalty reduces composite by 0.85."""
        without = compute_confidence(intent_logprob=0.0, compiler_had_fallbacks=False)
        with_fb = compute_confidence(intent_logprob=0.0, compiler_had_fallbacks=True)
        assert with_fb.composite == pytest.approx(without.composite * 0.85, abs=0.001)

    def test_low_intent_logprob(self) -> None:
        """Very low intent logprob → low composite."""
        result = compute_confidence(intent_logprob=-5.0, slot_logprobs=[0.0])
        assert result.intent < 0.01
        assert result.composite < 0.6

    def test_mixed_slot_logprobs(self) -> None:
        """Mix of good and bad slots."""
        result = compute_confidence(
            intent_logprob=-0.05,
            slot_logprobs=[-0.1, -3.0],
        )
        # slot_probs ≈ [0.905, 0.05], mean ≈ 0.477
        assert result.slots < 0.6
        assert result.slots > 0.3

    def test_weights_sum(self) -> None:
        """Verify weights: 0.5 intent + 0.3 slots + 0.2 retrieval."""
        # intent = 1.0 (logprob=0), slots = 1.0 (none), retrieval = 0.0
        result = compute_confidence(
            intent_logprob=0.0, slot_logprobs=None, retrieval_score=0.0
        )
        # 0.5 * 1.0 + 0.3 * 1.0 + 0.2 * 0.0 = 0.8
        assert result.composite == pytest.approx(0.8, abs=0.01)

    def test_retrieval_weight(self) -> None:
        """Retrieval=0.0 vs retrieval=1.0 differs by 0.2."""
        r0 = compute_confidence(intent_logprob=0.0, retrieval_score=0.0)
        r1 = compute_confidence(intent_logprob=0.0, retrieval_score=1.0)
        assert r1.composite - r0.composite == pytest.approx(0.2, abs=0.01)

    def test_retrieval_clamped(self) -> None:
        """Retrieval scores outside [0,1] are clamped."""
        result = compute_confidence(intent_logprob=0.0, retrieval_score=1.5)
        assert result.composite <= 1.0

    def test_display_format(self) -> None:
        result = compute_confidence(intent_logprob=0.0)
        assert "HIGH" in result.display
        assert "%" in result.display

    def test_composite_clamped_to_01(self) -> None:
        """Composite should never exceed 1.0."""
        result = compute_confidence(
            intent_logprob=1.0,  # clamped to 1.0
            slot_logprobs=[1.0],
            retrieval_score=1.5,
        )
        assert result.composite <= 1.0


class TestToConfidenceScore:
    def test_bridge(self) -> None:
        cr = compute_confidence(intent_logprob=-0.2, slot_logprobs=[-0.3])
        cs = to_confidence_score(cr)
        assert isinstance(cs, ConfidenceScore)
        assert cs.intent == cr.intent
        assert cs.slots == cr.slots
        assert cs.composite == cr.composite

    def test_roundtrip_values(self) -> None:
        cr = ConfidenceResult(
            intent=0.85, slots=0.72, composite=0.80,
            level=ConfidenceLevel.MEDIUM, display="MEDIUM (80%)"
        )
        cs = to_confidence_score(cr)
        assert cs.intent == 0.85
        assert cs.slots == 0.72
        assert cs.composite == 0.80


class TestConfidenceLevel:
    def test_enum_values(self) -> None:
        assert ConfidenceLevel.HIGH == "HIGH"
        assert ConfidenceLevel.MEDIUM == "MEDIUM"
        assert ConfidenceLevel.LOW == "LOW"
        assert ConfidenceLevel.VERY_LOW == "VERY_LOW"

    def test_from_string(self) -> None:
        assert ConfidenceLevel("HIGH") is ConfidenceLevel.HIGH
