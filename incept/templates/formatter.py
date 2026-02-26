"""Response formatter: produces structured output with explanations."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from incept.safety.validator import RiskLevel, ValidationResult
from incept.schemas.intents import IntentLabel
from incept.templates.explanations import (
    CLARIFICATION_TEMPLATES,
    EXPLANATION_TEMPLATES,
)


class CommandResponse(BaseModel):
    """Structured response for a compiled command."""

    command: str
    intent: IntentLabel
    explanation: str = ""
    flag_explanations: dict[str, str] = Field(default_factory=dict)
    side_effects: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.SAFE
    warnings: list[str] = Field(default_factory=list)
    requires_sudo: bool = False


class ClarificationResponse(BaseModel):
    """Structured response for a clarification request."""

    question: str
    reason: str
    options: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Structured response for an error/blocked command."""

    error: str
    reason: str
    suggestion: str = ""


class FormattedResponse(BaseModel):
    """Top-level response structure matching spec Section 14.2."""

    status: Literal["success", "clarification", "error", "blocked"] = "success"
    command: CommandResponse | None = None
    clarification: ClarificationResponse | None = None
    error: ErrorResponse | None = None


def format_command_response(
    command: str,
    intent: IntentLabel,
    params: dict[str, Any],
    validation: ValidationResult,
    verbosity: Literal["minimal", "normal", "detailed"] = "normal",
) -> FormattedResponse:
    """Format a compiled command into a structured response."""
    # Check if blocked
    if not validation.is_valid and validation.is_banned:
        return FormattedResponse(
            status="blocked",
            error=ErrorResponse(
                error="Command blocked by safety rules",
                reason=validation.banned_reason or "Unknown safety violation",
                suggestion="Please rephrase your request or check safety guidelines.",
            ),
        )

    # Check for validation errors
    if not validation.is_valid:
        return FormattedResponse(
            status="error",
            error=ErrorResponse(
                error="Command validation failed",
                reason="; ".join(validation.errors),
            ),
        )

    # Build explanation from templates
    template = EXPLANATION_TEMPLATES.get(intent)
    explanation = ""
    flag_expl: dict[str, str] = {}
    side_effects: list[str] = []

    if template:
        # Build template kwargs from params
        kwargs = {k: str(v) for k, v in params.items() if v is not None}
        explanation = template.render(**kwargs)
        flag_expl = template.flag_explanations
        side_effects = template.side_effects

    cmd_response = CommandResponse(
        command=command,
        intent=intent,
        explanation=explanation,
        risk_level=validation.risk_level,
        warnings=validation.warnings,
        requires_sudo=validation.requires_sudo,
    )

    # Apply verbosity levels
    if verbosity == "minimal":
        cmd_response.explanation = ""
        cmd_response.flag_explanations = {}
        cmd_response.side_effects = []
    elif verbosity == "normal":
        cmd_response.flag_explanations = {}
        cmd_response.side_effects = side_effects
    elif verbosity == "detailed":
        cmd_response.flag_explanations = flag_expl
        cmd_response.side_effects = side_effects

    return FormattedResponse(status="success", command=cmd_response)


def format_clarification(
    template_key: str,
    reason: str,
    options: list[str] | None = None,
    **kwargs: str,
) -> FormattedResponse:
    """Format a clarification request."""
    template = CLARIFICATION_TEMPLATES.get(template_key, "Could you provide more details?")
    try:
        question = template.format(**kwargs)
    except KeyError:
        question = template

    return FormattedResponse(
        status="clarification",
        clarification=ClarificationResponse(
            question=question,
            reason=reason,
            options=options or [],
        ),
    )
