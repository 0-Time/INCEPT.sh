"""Core IR models: SingleIR, PipelineIR, ClarificationIR, ConfidenceScore."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from incept.schemas.intents import IntentLabel


class ConfidenceScore(BaseModel):
    """Confidence scores for intent classification and slot filling."""

    intent: float = Field(ge=0.0, le=1.0)
    slots: float = Field(ge=0.0, le=1.0)
    composite: float = Field(ge=0.0, le=1.0)


class SingleIR(BaseModel):
    """IR for a single-intent command."""

    type: Literal["single"] = "single"
    intent: IntentLabel
    confidence: ConfidenceScore
    params: dict[str, object]
    defaults_applied: list[str] = Field(default_factory=list)
    requires_sudo: bool = False
    clarifications_needed: list[str] = Field(default_factory=list)


class PipelineIR(BaseModel):
    """IR for a multi-step pipeline command."""

    type: Literal["pipeline"] = "pipeline"
    composition: Literal["sequential", "pipe", "independent", "subshell", "xargs"]
    steps: list[SingleIR]
    variable_bindings: dict[str, str] = Field(default_factory=dict)


class ClarificationIR(BaseModel):
    """IR for a clarification request."""

    type: Literal["clarification"] = "clarification"
    intent: Literal[IntentLabel.CLARIFY] = IntentLabel.CLARIFY
    reason: str
    missing_params: list[str] = Field(default_factory=list)
    question_template: str
    options: list[str] = Field(default_factory=list)


# Union type for any IR
AnyIR = SingleIR | PipelineIR | ClarificationIR
