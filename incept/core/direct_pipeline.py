"""Direct NL → shell command pipeline.

Single model pass: NL + system context → shell command.  No intent routing,
no slot extraction, no compilers at runtime.  Replaces the multi-stage
pipeline (preclassifier → intent classifier → slot extractor → compiler).

When the loaded model is not yet trained for the command task (i.e. it's
the older intent/slot model), the pipeline automatically falls back to
the legacy ``run_pipeline`` so the system keeps working during the
transition.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Literal

from pydantic import BaseModel, Field

from incept.core.context import EnvironmentContext, parse_context
from incept.core.model_loader import get_model, is_command_model
from incept.safety.validator import RiskLevel, ValidationResult, validate_command

logger = logging.getLogger(__name__)

# Refusal tokens the model was trained to emit
_REFUSAL_TOKENS = {
    "[UNSAFE]": "blocked",
    "[OOS]": "out_of_scope",
    "[CLARIFY]": "clarification",
}

# Quick check: a valid shell command starts with a known command/path token.
# Intent labels (e.g. "install_package") and JSON blobs ("{...}") do not.
_COMMAND_START_RE = re.compile(
    r"^(?:sudo\s+)?"
    r"(?:[a-z][\w.-]*/)*"  # optional path prefix  e.g. /usr/bin/
    r"[a-z][\w.+-]*"  # command name           e.g. apt-get, find, ls
    r"(?:\s|$)",  # followed by space or end
    re.ASCII,
)


class DirectResponse(BaseModel):
    """Response from the direct NL → command pipeline."""

    status: Literal["success", "error", "blocked", "out_of_scope", "clarification"] = "success"
    command: str | None = None
    risk_level: RiskLevel = RiskLevel.SAFE
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None
    original_request: str = ""


def _build_context_line(ctx: EnvironmentContext) -> str:
    """Format an EnvironmentContext into the compact training-data format."""
    root_str = "root" if ctx.is_root else "non-root"
    safe_str = "safe" if ctx.safe_mode else "unsafe"
    distro = ctx.distro_family if ctx.distro_family != "debian" else ctx.distro_id
    return f"{distro} {ctx.shell} {root_str} {safe_str}"


def _build_prompt(nl_request: str, context_line: str) -> str:
    """Build the model prompt from NL request and context line."""
    return f"<s>[INST] [CONTEXT] {context_line}\n[REQUEST] {nl_request} [/INST]"


def _looks_like_command(text: str) -> bool:
    """Return True if *text* looks like a plausible shell command.

    Returns False for intent labels (``install_package``), JSON blobs,
    or other non-command model output — signalling that the loaded model
    is the old intent/slot model and we should fall back.
    """
    if not text:
        return False
    # Refusal tokens are valid direct-pipeline output
    if text in _REFUSAL_TOKENS:
        return True
    # Intent labels: single word with underscores, no spaces
    if re.fullmatch(r"[A-Za-z_]+", text):
        return False
    # JSON blobs from slot-filling model
    if text.startswith("{") or text.startswith("[INTENT]") or text.startswith("[SLOTS]"):
        return False
    # Should start with something that looks like a command
    return bool(_COMMAND_START_RE.match(text))


def _fallback_to_legacy(
    nl_request: str,
    context_json: str,
) -> DirectResponse:
    """Run the legacy multi-stage pipeline and convert to DirectResponse."""
    from incept.core.pipeline import run_pipeline

    legacy = run_pipeline(nl_request=nl_request, context_json=context_json)

    response = DirectResponse(original_request=nl_request)

    if legacy.status == "blocked":
        response.status = "blocked"
        if legacy.responses and legacy.responses[0].error:
            err = legacy.responses[0].error
            response.error = err.get("error", "Blocked") if isinstance(err, dict) else err.error
        else:
            response.error = "Request blocked by safety rules."
        return response

    if legacy.status in ("error", "no_match"):
        response.status = "error"
        if legacy.responses and legacy.responses[0].error:
            err = legacy.responses[0].error
            response.error = (
                err.get("error", "Unknown error") if isinstance(err, dict) else err.error
            )
        elif legacy.responses and legacy.responses[0].clarification:
            response.status = "clarification"
            response.error = legacy.responses[0].clarification.question
        else:
            response.error = "No matching command found."
        return response

    # Success path — extract command from first successful response
    for resp in legacy.responses:
        if resp.command:
            response.status = "success"
            response.command = resp.command.command
            response.risk_level = RiskLevel(resp.command.risk_level)
            response.warnings = resp.command.warnings
            return response
        if resp.clarification:
            response.status = "clarification"
            response.error = resp.clarification.question
            return response
        if resp.error:
            err = resp.error
            response.status = "error"
            response.error = err.get("error", "Unknown") if isinstance(err, dict) else err.error
            return response

    response.status = "error"
    response.error = "No matching command found."
    return response


def run_direct_pipeline(
    nl_request: str,
    context_json: str = "{}",
    model: Any = None,
) -> DirectResponse:
    """Run the direct NL → command pipeline.

    If the loaded model produces output that doesn't look like a shell
    command (e.g. the old intent/slot model emitting intent labels), the
    pipeline automatically falls back to the legacy multi-stage pipeline.

    Args:
        nl_request: Natural language request from the user.
        context_json: JSON string with environment context.
        model: Optional pre-loaded model instance (uses singleton if None).

    Returns:
        DirectResponse with the generated command or error information.
    """
    ctx = parse_context(context_json)
    response = DirectResponse(original_request=nl_request)

    # Resolve model
    llm = model or get_model()
    if llm is None:
        # No model at all — fall back to legacy (preclassifier + compilers)
        return _fallback_to_legacy(nl_request, context_json)

    # If the loaded model is NOT a command-trained model (e.g. the old
    # intent/slot "unified" model), skip inference entirely — it will
    # produce garbage for command-format prompts.  Go straight to legacy.
    if not is_command_model():
        logger.info("Loaded model is not command-trained, using legacy pipeline")
        return _fallback_to_legacy(nl_request, context_json)

    # Build prompt
    context_line = _build_context_line(ctx)
    prompt = _build_prompt(nl_request, context_line)

    # Run inference
    from incept.training.export import run_constrained_inference

    try:
        result = run_constrained_inference(
            llm,
            prompt,
            grammar=None,
            max_tokens=192,
            temperature=0.0,
        )
    except Exception as e:
        logger.warning("Direct inference failed (%s), falling back to legacy pipeline", e)
        return _fallback_to_legacy(nl_request, context_json)

    raw = result["text"].strip().rstrip("</s>").strip()

    # If the output doesn't look like a shell command, the model is probably
    # the old intent/slot model — fall back to the legacy pipeline.
    if not _looks_like_command(raw):
        logger.info("Model output %r doesn't look like a command, using legacy pipeline", raw[:60])
        return _fallback_to_legacy(nl_request, context_json)

    # Check for refusal tokens
    if raw in _REFUSAL_TOKENS:
        status = _REFUSAL_TOKENS[raw]
        response.status = status  # type: ignore[assignment]
        if status == "blocked":
            response.error = "Request blocked by safety rules."
        elif status == "out_of_scope":
            response.error = "Request is out of scope for Linux/macOS system administration."
        elif status == "clarification":
            response.error = "Could not understand the request. Please rephrase."
        return response

    # Empty output
    if not raw:
        response.status = "error"
        response.error = "Model returned empty output. Please rephrase your request."
        return response

    # Validate the generated command
    validation: ValidationResult = validate_command(raw, ctx)

    if validation.is_banned:
        response.status = "blocked"
        response.error = f"Generated command blocked: {validation.banned_reason}"
        response.risk_level = RiskLevel.BLOCKED
        return response

    response.status = "success"
    response.command = raw
    response.risk_level = validation.risk_level
    response.warnings = validation.warnings

    return response
