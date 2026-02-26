"""Explain pipeline: command → structured NL explanation."""

from __future__ import annotations

from pydantic import BaseModel, Field

from incept.core.context import EnvironmentContext
from incept.explain.registry import parse_command
from incept.safety.validator import validate_command
from incept.schemas.intents import IntentLabel, get_intent_descriptions
from incept.templates.explanations import EXPLANATION_TEMPLATES


class ExplainResponse(BaseModel):
    """Structured explanation of a shell command."""

    command: str
    intent: str | None = None
    explanation: str = ""
    flag_explanations: dict[str, str] = Field(default_factory=dict)
    side_effects: list[str] = Field(default_factory=list)
    risk_level: str = "safe"
    params: dict[str, str | bool | None] = Field(default_factory=dict)


def run_explain_pipeline(
    command: str,
    context_json: str | None = None,
) -> ExplainResponse:
    """Run the explain pipeline on a shell command.

    1. Parse command to extract intent + params
    2. Look up explanation template
    3. Validate command for risk assessment
    4. Return structured ExplainResponse
    """
    if not command or not command.strip():
        return ExplainResponse(
            command=command or "",
            explanation="Empty command provided.",
        )

    # 1. Parse command
    parse_result = parse_command(command)

    if parse_result is None:
        # Unknown command — still do risk check
        ctx = EnvironmentContext()
        validation = validate_command(command, ctx)
        return ExplainResponse(
            command=command,
            intent=None,
            explanation="Unrecognized command.",
            risk_level=validation.risk_level.value,
        )

    intent = parse_result.intent
    params = parse_result.params

    # 2. Look up explanation template
    explanation = _build_explanation(intent, params)
    flag_explanations: dict[str, str] = {}
    side_effects: list[str] = []

    try:
        intent_label = IntentLabel(intent)
        tmpl = EXPLANATION_TEMPLATES.get(intent_label)
        if tmpl:
            explanation = tmpl.render(**{k: str(v) for k, v in params.items()})
            flag_explanations = tmpl.flag_explanations
            side_effects = tmpl.side_effects
    except ValueError:
        pass  # intent not in IntentLabel enum

    # 3. Validate command for risk
    ctx = EnvironmentContext()
    validation = validate_command(command, ctx)

    return ExplainResponse(
        command=command,
        intent=intent,
        explanation=explanation,
        flag_explanations=flag_explanations,
        side_effects=side_effects,
        risk_level=validation.risk_level.value,
        params=params,
    )


def _build_explanation(intent: str, params: dict[str, str | bool | None]) -> str:
    """Build a basic explanation from intent + params."""
    descriptions = get_intent_descriptions()
    desc = descriptions.get(intent, "")
    if desc:
        return desc
    # Fallback: humanize the intent name
    return intent.replace("_", " ").capitalize()
