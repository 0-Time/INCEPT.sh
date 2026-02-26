"""Confidence scoring for INCEPT predictions. Zero ML deps."""

from __future__ import annotations

import math
from enum import StrEnum

from pydantic import BaseModel, Field

from incept.schemas.ir import ConfidenceScore


class ConfidenceLevel(StrEnum):
    """Human-readable confidence levels."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"


class ConfidenceResult(BaseModel):
    """Computed confidence result with per-component and composite scores."""

    intent: float = Field(ge=0.0, le=1.0)
    slots: float = Field(ge=0.0, le=1.0)
    composite: float = Field(ge=0.0, le=1.0)
    level: ConfidenceLevel
    display: str


def _logprob_to_prob(logprob: float) -> float:
    """Convert a log-probability to a probability in [0, 1]."""
    return min(1.0, max(0.0, math.exp(logprob)))


def _classify_level(score: float) -> ConfidenceLevel:
    """Map a composite score to a ConfidenceLevel."""
    if score >= 0.9:
        return ConfidenceLevel.HIGH
    elif score >= 0.7:
        return ConfidenceLevel.MEDIUM
    elif score >= 0.5:
        return ConfidenceLevel.LOW
    else:
        return ConfidenceLevel.VERY_LOW


def compute_confidence(
    intent_logprob: float,
    slot_logprobs: list[float] | None = None,
    retrieval_score: float = 1.0,
    compiler_had_fallbacks: bool = False,
) -> ConfidenceResult:
    """Compute a composite confidence score from component log-probabilities.

    Weights:
        - intent: 0.5
        - slots: 0.3  (mean of per-slot probabilities)
        - retrieval: 0.2
    Fallback penalty: 0.85 multiplier when compiler used fallbacks.

    Args:
        intent_logprob: Log-probability of the predicted intent.
        slot_logprobs: Log-probabilities for each extracted slot.
            If None or empty, slot confidence defaults to 1.0.
        retrieval_score: BM25 retrieval score, already in [0, 1].
        compiler_had_fallbacks: Whether the compiler applied fallback defaults.

    Returns:
        ConfidenceResult with component scores and level.
    """
    intent_prob = _logprob_to_prob(intent_logprob)

    if slot_logprobs:
        slot_probs = [_logprob_to_prob(lp) for lp in slot_logprobs]
        slots_prob = sum(slot_probs) / len(slot_probs)
    else:
        slots_prob = 1.0

    retrieval_clamped = min(1.0, max(0.0, retrieval_score))

    composite = 0.5 * intent_prob + 0.3 * slots_prob + 0.2 * retrieval_clamped

    if compiler_had_fallbacks:
        composite *= 0.85

    composite = min(1.0, max(0.0, composite))

    level = _classify_level(composite)
    display = f"{level.value} ({composite:.0%})"

    return ConfidenceResult(
        intent=round(intent_prob, 4),
        slots=round(slots_prob, 4),
        composite=round(composite, 4),
        level=level,
        display=display,
    )


def to_confidence_score(result: ConfidenceResult) -> ConfidenceScore:
    """Bridge ConfidenceResult to the IR schema ConfidenceScore model."""
    return ConfidenceScore(
        intent=result.intent,
        slots=result.slots,
        composite=result.composite,
    )
