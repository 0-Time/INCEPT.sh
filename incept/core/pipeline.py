"""End-to-end pipeline orchestrator.

Chains all stages: pre-classifier → decomposer → model slot-filling → compiler →
validator → formatter. The pre-classifier provides fast safety/OOS filtering and
intent detection; the Qwen3.5-0.8B GGUF model fills slots (parameters) for every
matched intent and acts as a full classifier when the regex misses.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from pydantic import BaseModel, Field

from incept.compiler.expanded_ops import EXPANDED_OPS_COMPILERS
from incept.compiler.file_ops import FILE_OPS_COMPILERS
from incept.compiler.router import CompileResult, IntentRouter
from incept.compiler.system_ops import SYSTEM_OPS_COMPILERS
from incept.compiler.text_ops import TEXT_OPS_COMPILERS
from incept.core.context import EnvironmentContext, parse_context
from incept.core.decomposer import decompose
from incept.core.model_loader import get_model
from incept.core.preclassifier import classify as preclassify
from incept.safety.validator import ValidationResult, validate_command
from incept.schemas.intents import IntentLabel
from incept.templates.formatter import (
    FormattedResponse,
    format_clarification,
    format_command_response,
)

logger = logging.getLogger(__name__)


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
    router.register_many(EXPANDED_OPS_COMPILERS)
    return router


# Module-level singleton router
_ROUTER = _build_router()


def _compile_and_validate(
    intent: IntentLabel,
    params: dict[str, Any],
    ctx: EnvironmentContext,
    requires_sudo: bool,
    verbosity: Literal["minimal", "normal", "detailed"] = "normal",
    confidence: Any | None = None,
) -> FormattedResponse:
    """Compile a single intent and validate the result."""
    from incept.schemas.ir import ConfidenceScore, SingleIR

    if confidence is None:
        confidence = ConfidenceScore(intent=0.9, slots=0.9, composite=0.9)

    ir = SingleIR(
        intent=intent,
        confidence=confidence,
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


def _extract_basic_slots(intent: IntentLabel, text: str) -> dict[str, Any]:
    """Best-effort slot extraction from NL text when the model is unavailable.

    Covers the most common intents so the pipeline can still compile useful
    commands without a model.  Returns an empty dict for unhandled intents.
    """
    import re as _re

    text = text.strip()
    slots: dict[str, Any] = {}

    if intent == IntentLabel.install_package:
        m = _re.search(r"\binstall\s+([\w.+-]+)", text, _re.IGNORECASE)
        if m:
            slots["package"] = m.group(1)
    elif intent == IntentLabel.remove_package:
        m = _re.search(r"\b(?:remove|uninstall)\s+([\w.+-]+)", text, _re.IGNORECASE)
        if m:
            slots["package"] = m.group(1)
    elif intent == IntentLabel.search_package:
        m = _re.search(
            r"\b(?:search|find|look\s+for)\s+(?:a\s+)?(?:package\s+)?(?:called\s+)?([\w.+-]+)",
            text,
            _re.IGNORECASE,
        )
        if m:
            slots["query"] = m.group(1)
    elif intent in (
        IntentLabel.start_service,
        IntentLabel.stop_service,
        IntentLabel.restart_service,
        IntentLabel.enable_service,
        IntentLabel.service_status,
    ):
        verb = {
            "start_service": "start",
            "stop_service": "stop",
            "restart_service": "restart",
            "enable_service": "enable",
            "service_status": "(?:status|check)",
        }
        v = verb.get(intent.value, "start")
        m = _re.search(rf"\b{v}\s+(?:the\s+)?([\w.+-]+)(?:\s+service)?", text, _re.IGNORECASE)
        if m:
            svc = m.group(1)
            if svc.lower() not in ("the", "a", "my", "this"):
                slots["service_name"] = svc
    elif intent == IntentLabel.find_files:
        # Extract path if present
        m = _re.search(r"\bin\s+(/[\w/.-]+)", text)
        if m:
            slots["path"] = m.group(1)
        # Extract name pattern (e.g. "log files" → "*.log", "*.py files" → "*.py")
        m = _re.search(r"(\*?\.\w+)\s+files?", text, _re.IGNORECASE)
        if m:
            slots["name_pattern"] = m.group(1) if m.group(1).startswith("*") else f"*{m.group(1)}"
        else:
            m = _re.search(r"\b(\w+)\s+files?", text, _re.IGNORECASE)
            if m and m.group(1).lower() not in (
                "all",
                "the",
                "some",
                "any",
                "find",
                "large",
                "old",
                "new",
                "empty",
            ):
                slots["name_pattern"] = f"*.{m.group(1)}"
    elif intent == IntentLabel.list_directory:
        m = _re.search(r"\bin\s+(/[\w/.-]+)", text)
        if m:
            slots["path"] = m.group(1)
    elif intent == IntentLabel.disk_usage:
        m = _re.search(r"\b(?:of|in|for)\s+(/[\w/.-]+)", text)
        if m:
            slots["path"] = m.group(1)
    elif intent == IntentLabel.view_file:
        m = _re.search(
            r"(?:view|show|display|read|cat)\s+(?:the\s+)?(?:contents?\s+of\s+)?(/?[\w/.~-]+\.\w+)",
            text,
            _re.IGNORECASE,
        )
        if m:
            slots["file"] = m.group(1)
    elif intent == IntentLabel.search_text:
        # grep "pattern" path
        m = _re.search(
            r"\b(?:search|grep|find)\s+(?:for\s+)?['\"]?(\S+)['\"]?\s+(?:in\s+)?(/?[\w/.-]+)",
            text,
            _re.IGNORECASE,
        )
        if m:
            slots["pattern"] = m.group(1)
            slots["path"] = m.group(2)
        else:
            m = _re.search(
                r"\b(?:search|grep|find)\s+(?:for\s+)?['\"]?(\S+)['\"]?", text, _re.IGNORECASE
            )
            if m:
                slots["pattern"] = m.group(1)

    return slots


# Mapping of model-produced slot keys to compiler-expected keys.
# The fine-tuned model sometimes emits shorter or variant names.
_SLOT_KEY_ALIASES: dict[str, str] = {
    "service": "service_name",
    "svc": "service_name",
    "name_pattern": "name_pattern",
    "name": "name_pattern",  # find_files: "name" → "name_pattern"
    "filename": "name_pattern",
    "file_name": "name_pattern",
    "target": "target",
    "container_name": "container",
    "container_id": "container",
    "pkg": "package",
    "job_id_or_pattern": "job_id_or_pattern",
    "pattern": "pattern",  # keep as-is for non-find intents
    "field_spec": "field_spec",
    "input_file": "input_file",
    "source": "source",
    "destination": "destination",
}

# Intent-specific key overrides (when a key means different things per intent)
_INTENT_SLOT_OVERRIDES: dict[str, dict[str, str]] = {
    "find_files": {"name": "name_pattern"},
    "remove_cron": {"pattern": "job_id_or_pattern"},
    "sort_output": {"file": "input_file"},
    "count_lines": {"file": "input_file"},
    "extract_columns": {"file": "input_file"},
    "unique_lines": {"file": "input_file"},
    "kill_process": {"pid": "target", "process": "target", "name": "target"},
}


def _normalize_slot_keys(intent: IntentLabel, slots: dict[str, Any]) -> dict[str, Any]:
    """Normalize model-produced slot keys to match compiler expectations."""
    overrides = _INTENT_SLOT_OVERRIDES.get(intent.value, {})
    normalized: dict[str, Any] = {}
    for k, v in slots.items():
        # Intent-specific override first, then global alias, then keep as-is
        new_key = overrides.get(k) or _SLOT_KEY_ALIASES.get(k, k)
        normalized[new_key] = v
    # Fix find_files: if name_pattern doesn't have a glob, wrap it
    if intent == IntentLabel.find_files and "name_pattern" in normalized:
        pat = str(normalized["name_pattern"])
        if "*" not in pat and "?" not in pat:
            normalized["name_pattern"] = f"*.{pat}"
    # Sanitize path slots: the model sometimes echoes the intent name
    # (e.g. "disk_usage") as the path.  Drop non-path-like values.
    if "path" in normalized:
        p = str(normalized["path"])
        if not (p.startswith("/") or p.startswith(".") or p.startswith("~")):
            del normalized["path"]
    return normalized


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
    use_model_classifier: bool = False,
    model: Any = None,
) -> PipelineResponse:
    """Run the full NL → command pipeline.

    Stages:
    1. Parse context
    2. Pre-classify (safety, OOS, fast-path intent)
    3. Decompose compound requests
    4. For each sub-request:
       a. Preclassifier for safety / OOS / fast intent detection
       b. Model fills slots when preclassifier matched an intent
       c. Model does full classify + slot fill when preclassifier missed
       d. Compile → validate → format
    5. Return assembled response

    The model is loaded automatically via the singleton ``get_model()``.
    Legacy parameters ``use_model_classifier`` and ``model`` are accepted
    for backwards compatibility but are no longer required — the pipeline
    always uses the model when a GGUF file is available.
    """
    ctx = parse_context(context_json)
    response = PipelineResponse(original_request=nl_request)

    # Resolve the model: prefer explicit arg, then singleton
    llm = model or get_model()

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
        # Use pre-classifier as fast safety/intent filter
        sub_result = preclassify(sub_text)

        if sub_result.matched_intent is None:
            # No match from preclassifier — use model for full classification
            if llm is not None:
                from incept.core.model_classifier import model_classify

                mc_result = model_classify(llm, sub_text, context_json)

                if mc_result.intent == IntentLabel.UNSAFE_REQUEST:
                    response.status = "blocked"
                    response.responses.append(
                        FormattedResponse(
                            status="blocked",
                            error={  # type: ignore[arg-type]
                                "error": "Unsafe request detected by model",
                                "reason": "model_safety",
                            },
                        )
                    )
                    continue

                if mc_result.intent == IntentLabel.CLARIFY:
                    response.status = "no_match"
                    response.responses.append(
                        format_clarification(
                            template_key="clarify_intent",
                            reason="model_low_confidence",
                        )
                    )
                    continue

                if mc_result.intent == IntentLabel.OUT_OF_SCOPE:
                    response.responses.append(
                        FormattedResponse(
                            status="error",
                            error={  # type: ignore[arg-type]
                                "error": "Out of scope",
                                "reason": "model_out_of_scope",
                            },
                        )
                    )
                    continue

                # Model returned a valid intent — compile with real confidence
                mc_intent = mc_result.intent
                mc_params: dict[str, Any] = _normalize_slot_keys(mc_intent, mc_result.slots)
                mc_sudo = _needs_sudo(mc_intent)

                if not _ROUTER.has_compiler(mc_intent):
                    response.responses.append(
                        format_clarification(
                            template_key="clarify_intent",
                            reason=f"no_compiler_for_{mc_intent.value}",
                        )
                    )
                    continue

                fmt_response = _compile_and_validate(
                    mc_intent,
                    mc_params,
                    ctx,
                    mc_sudo,
                    verbosity,
                    confidence=mc_result.confidence,
                )
                response.responses.append(fmt_response)
                continue

            # No model available — fall back to clarification
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

        # Preclassifier matched an actionable intent — use model for slot filling
        requires_sudo = _needs_sudo(intent)
        params: dict[str, Any] = {}

        if llm is not None:
            from incept.core.model_classifier import fill_slots

            try:
                slot_result = fill_slots(llm, intent.value, sub_text, context_json)
                params = _normalize_slot_keys(intent, slot_result.slots)
            except Exception:
                logger.warning(
                    "Model slot filling failed for %s, using basic extraction", intent.value
                )
                params = _normalize_slot_keys(intent, _extract_basic_slots(intent, sub_text))
        else:
            # No model — use regex-based slot extraction as fallback
            params = _normalize_slot_keys(intent, _extract_basic_slots(intent, sub_text))

        # Check if router has a compiler for this intent
        if not _ROUTER.has_compiler(intent):
            response.responses.append(
                format_clarification(
                    template_key="clarify_intent",
                    reason=f"no_compiler_for_{intent.value}",
                )
            )
            continue

        fmt_response = _compile_and_validate(intent, params, ctx, requires_sudo, verbosity)
        response.responses.append(fmt_response)

    if not response.responses:
        response.status = "no_match"

    # If all responses are success, overall is success
    if all(r.status == "success" for r in response.responses):
        response.status = "success"

    return response
