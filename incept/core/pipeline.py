"""End-to-end pipeline orchestrator.

Chains all stages: pre-classifier → decomposer → (classifier) → compiler →
validator → formatter. Uses the pre-classifier as a hard-coded regex
classifier for Sprint 2 (model-based classifier comes in Sprint 4).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from incept.compiler.file_ops import FILE_OPS_COMPILERS
from incept.compiler.router import CompileResult, IntentRouter
from incept.compiler.system_ops import SYSTEM_OPS_COMPILERS
from incept.compiler.text_ops import TEXT_OPS_COMPILERS
from incept.core.context import EnvironmentContext, parse_context
from incept.core.decomposer import decompose
from incept.core.preclassifier import classify as preclassify
from incept.safety.validator import ValidationResult, validate_command
from incept.schemas.intents import IntentLabel
from incept.templates.formatter import (
    FormattedResponse,
    format_clarification,
    format_command_response,
)


class PipelineResponse(BaseModel):
    """Top-level pipeline output."""

    status: Literal["success", "clarification", "error", "blocked", "no_match"] = "success"
    responses: list[FormattedResponse] = Field(default_factory=list)
    is_compound: bool = False
    original_request: str = ""


def _build_router() -> IntentRouter:
    """Create and populate the intent router with all compiler functions."""
    router = IntentRouter()
    router.register_many(FILE_OPS_COMPILERS)
    router.register_many(TEXT_OPS_COMPILERS)
    router.register_many(SYSTEM_OPS_COMPILERS)
    return router


# Module-level singleton router
_ROUTER = _build_router()


def _compile_and_validate(
    intent: IntentLabel,
    params: dict[str, Any],
    ctx: EnvironmentContext,
    requires_sudo: bool,
    verbosity: Literal["minimal", "normal", "detailed"] = "normal",
) -> FormattedResponse:
    """Compile a single intent and validate the result."""
    from incept.schemas.ir import ConfidenceScore, SingleIR

    ir = SingleIR(
        intent=intent,
        confidence=ConfidenceScore(intent=0.9, slots=0.9, composite=0.9),
        params=params,
        requires_sudo=requires_sudo,
    )

    try:
        result: CompileResult = _ROUTER.compile_single(ir, ctx)
    except (KeyError, ValueError) as e:
        return FormattedResponse(
            status="error",
            error={"error": str(e), "reason": "compilation_failed"},  # type: ignore[arg-type]
        )

    command = result.full_command
    validation: ValidationResult = validate_command(command, ctx)
    return format_command_response(command, intent, params, validation, verbosity)


def _needs_sudo(intent: IntentLabel) -> bool:
    """Determine if an intent typically requires sudo."""
    sudo_intents = {
        IntentLabel.install_package,
        IntentLabel.remove_package,
        IntentLabel.update_packages,
        IntentLabel.start_service,
        IntentLabel.stop_service,
        IntentLabel.restart_service,
        IntentLabel.enable_service,
        IntentLabel.create_user,
        IntentLabel.delete_user,
        IntentLabel.modify_user,
        IntentLabel.mount_device,
        IntentLabel.unmount_device,
    }
    return intent in sudo_intents


def run_pipeline(
    nl_request: str,
    context_json: str = "{}",
    verbosity: Literal["minimal", "normal", "detailed"] = "normal",
) -> PipelineResponse:
    """Run the full NL → command pipeline.

    Stages:
    1. Parse context
    2. Pre-classify (safety, OOS, fast-path intent)
    3. Decompose compound requests
    4. For each sub-request: classify → compile → validate → format
    5. Return assembled response
    """
    ctx = parse_context(context_json)
    response = PipelineResponse(original_request=nl_request)

    # Stage 1: Pre-classify for safety and OOS
    pre_result = preclassify(nl_request)

    if pre_result.is_safety_violation:
        response.status = "blocked"
        response.responses.append(
            FormattedResponse(
                status="blocked",
                error={  # type: ignore[arg-type]
                    "error": "Request blocked by safety rules",
                    "reason": pre_result.matched_pattern or "safety_violation",
                    "suggestion": "This type of request is not allowed.",
                },
            )
        )
        return response

    if pre_result.is_out_of_scope:
        response.status = "error"
        response.responses.append(
            FormattedResponse(
                status="error",
                error={  # type: ignore[arg-type]
                    "error": "Request is out of scope",
                    "reason": pre_result.matched_pattern or "out_of_scope",
                    "suggestion": "I can only help with Linux system administration tasks.",
                },
            )
        )
        return response

    # Stage 2: Decompose compound requests
    decomp = decompose(nl_request)
    response.is_compound = decomp.is_compound

    # Stage 3: Classify and compile each sub-request
    sub_texts = [sr.text for sr in decomp.sub_requests]

    for sub_text in sub_texts:
        # Use pre-classifier as the hard-coded classifier
        sub_result = preclassify(sub_text)

        if sub_result.matched_intent is None:
            # No match — would go to model in Sprint 4
            response.status = "no_match"
            response.responses.append(
                format_clarification(
                    template_key="clarify_intent",
                    reason="no_intent_match",
                )
            )
            continue

        intent = sub_result.matched_intent

        # Special intents
        if intent == IntentLabel.UNSAFE_REQUEST:
            response.status = "blocked"
            response.responses.append(
                FormattedResponse(
                    status="blocked",
                    error={  # type: ignore[arg-type]
                        "error": "Unsafe request detected",
                        "reason": sub_result.matched_pattern or "unsafe",
                    },
                )
            )
            continue

        if intent == IntentLabel.OUT_OF_SCOPE:
            response.responses.append(
                FormattedResponse(
                    status="error",
                    error={  # type: ignore[arg-type]
                        "error": "Out of scope",
                        "reason": "out_of_scope",
                    },
                )
            )
            continue

        # For the hard-coded classifier, we don't have slot-filling
        # Use empty params — the compiler will use defaults
        params: dict[str, Any] = {}
        requires_sudo = _needs_sudo(intent)

        # Check if router has a compiler for this intent
        if not _ROUTER.has_compiler(intent):
            response.responses.append(
                format_clarification(
                    template_key="clarify_intent",
                    reason=f"no_compiler_for_{intent.value}",
                )
            )
            continue

        fmt_response = _compile_and_validate(
            intent, params, ctx, requires_sudo, verbosity
        )
        response.responses.append(fmt_response)

    if not response.responses:
        response.status = "no_match"

    # If all responses are success, overall is success
    if all(r.status == "success" for r in response.responses):
        response.status = "success"

    return response
