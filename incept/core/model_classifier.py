"""Two-pass model-based classifier: intent classification → slot filling."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from incept.confidence.scoring import compute_confidence, to_confidence_score
from incept.schemas.intents import IntentLabel
from incept.schemas.ir import ConfidenceScore
from incept.training.export import run_constrained_inference

GRAMMAR_DIR = Path(__file__).resolve().parent.parent / "grammars"


# ========================== Grammar resolution ==========================


def resolve_intent_grammar() -> Path:
    """Return the path to the intent classification grammar."""
    return GRAMMAR_DIR / "intent_grammar.gbnf"


def resolve_slot_grammar(intent: str) -> Path | None:
    """Return the path to the slot grammar for the given intent, or None if not found."""
    # Intent values may be uppercase for special intents (CLARIFY, OUT_OF_SCOPE, UNSAFE_REQUEST)
    grammar_name = f"slots_{intent.lower()}.gbnf"
    path = GRAMMAR_DIR / grammar_name
    if path.exists():
        return path
    return None


# ========================== Slot parsing ==========================


def parse_slot_output(raw: str) -> dict[str, str]:
    """Parse slot output from the model.

    Supports two formats:
    - JSON: ``{"key": "value", ...}``  (training data format)
    - key=value: one pair per line      (legacy grammar format)
    """
    text = raw.strip().rstrip("</s>").strip()

    # Try JSON first (matches training data format)
    if text.startswith("{"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return {k: str(v) for k, v in parsed.items()}
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback to key=value format
    slots: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, _, value = line.partition("=")
        slots[key.strip()] = value.strip()
    return slots


# ========================== Result models ==========================


class ClassifierResult(BaseModel):
    """Result from the intent classification pass."""

    intent: IntentLabel
    intent_logprob: float
    raw_output: str


class SlotResult(BaseModel):
    """Result from the slot filling pass."""

    slots: dict[str, str] = Field(default_factory=dict)
    slot_logprobs: list[float] = Field(default_factory=list)
    raw_output: str


class ModelClassifierResult(BaseModel):
    """Combined result from the two-pass model classifier."""

    intent: IntentLabel
    slots: dict[str, str] = Field(default_factory=dict)
    confidence: ConfidenceScore
    used_model: bool = True


# ========================== Context formatting ==========================


def _format_context_for_model(context: str) -> str:
    """Convert JSON context to the compact training-data format.

    Training data uses: ``{distro_family} {shell} {root|non-root} {safe}``
    e.g. ``debian bash non-root safe``

    If *context* is already in that format (no ``{``), return as-is.
    """
    context = context.strip()
    if not context.startswith("{"):
        return context

    try:
        data = json.loads(context)
    except (json.JSONDecodeError, ValueError):
        return context

    distro = data.get("distro_family") or data.get("distro_id") or "debian"
    shell = data.get("shell", "bash")
    is_root = data.get("is_root", False)
    safe = data.get("safe_mode", True)

    root_str = "root" if is_root else "non-root"
    safe_str = "safe" if safe else "unsafe"

    return f"{distro} {shell} {root_str} {safe_str}"


# ========================== Prompt building ==========================


def _build_intent_prompt(nl_request: str, context: str) -> str:
    """Format the intent classification prompt (matches SFT training data)."""
    ctx = _format_context_for_model(context)
    return (
        "<s>[INST] Given the context and request, classify the intent.\n"
        f"[CONTEXT] {ctx}\n"
        f"[REQUEST] {nl_request}\n"
        "[INTENT] [/INST]"
    )


def _build_slot_prompt(intent: str, nl_request: str, context: str) -> str:
    """Format the slot filling prompt (matches SFT training data)."""
    ctx = _format_context_for_model(context)
    return (
        "<s>[INST] Given the context, request, and intent, extract parameter slots.\n"
        f"[CONTEXT] {ctx}\n"
        f"[REQUEST] {nl_request}\n"
        f"[INTENT] {intent}\n"
        "[SLOTS] [/INST]"
    )


# ========================== Classification functions ==========================


def classify_intent(
    model: Any,
    nl_request: str,
    context: str,
) -> ClassifierResult:
    """Run the first pass: intent classification with grammar constraint.

    Args:
        model: A llama-cpp-python Llama model instance.
        nl_request: The natural language request.
        context: Environment context string.

    Returns:
        ClassifierResult with predicted intent and logprob.
    """
    intent_grammar_path = resolve_intent_grammar()
    with open(intent_grammar_path) as f:
        grammar_text = f.read()

    # Load grammar (import here to avoid hard dep in tests)
    from llama_cpp import LlamaGrammar

    grammar = LlamaGrammar.from_string(grammar_text)

    prompt = _build_intent_prompt(nl_request, context)
    result = run_constrained_inference(model, prompt, grammar=grammar)

    text = result["text"].strip()
    logprobs = result["logprobs"]
    mean_logprob = sum(logprobs) / len(logprobs) if logprobs else -10.0

    intent = IntentLabel(text)
    return ClassifierResult(
        intent=intent,
        intent_logprob=mean_logprob,
        raw_output=text,
    )


def fill_slots(
    model: Any,
    intent: str,
    nl_request: str,
    context: str,
) -> SlotResult:
    """Run the second pass: slot filling with grammar constraint.

    Args:
        model: A llama-cpp-python Llama model instance.
        intent: The predicted intent label.
        nl_request: The natural language request.
        context: Environment context string.

    Returns:
        SlotResult with parsed slots and logprobs.
    """
    # Slot filling runs without GBNF grammar constraints — the fine-tuned
    # model learns to output JSON from training data, while the legacy GBNF
    # grammars enforce key=value format.  Grammar-free decoding avoids the
    # format mismatch and lets the model produce the JSON it was trained on.
    prompt = _build_slot_prompt(intent, nl_request, context)
    result = run_constrained_inference(model, prompt, grammar=None, max_tokens=256)

    text = result["text"].strip()
    logprobs = result["logprobs"]
    slots = parse_slot_output(text)

    return SlotResult(
        slots=slots,
        slot_logprobs=logprobs,
        raw_output=text,
    )


def model_classify(
    model: Any,
    nl_request: str,
    context: str,
    confidence_threshold: float = 0.5,
) -> ModelClassifierResult:
    """Run the full two-pass model classification.

    Pass 1: Intent classification with grammar constraint.
    Pass 2: Slot filling with intent-specific grammar (skipped for CLARIFY/low confidence).

    Args:
        model: A llama-cpp-python Llama model instance.
        nl_request: The natural language request.
        context: Environment context string.
        confidence_threshold: Minimum confidence for non-clarification result.

    Returns:
        ModelClassifierResult with intent, slots, and confidence.
    """
    intent_result = classify_intent(model, nl_request, context)

    # Compute intent probability from logprob
    intent_prob = min(1.0, max(0.0, math.exp(intent_result.intent_logprob)))

    # If model says CLARIFY or confidence is too low, return clarification
    if intent_result.intent == IntentLabel.CLARIFY or intent_prob < confidence_threshold:
        confidence = ConfidenceScore(
            intent=round(intent_prob, 4),
            slots=0.0,
            composite=round(intent_prob * 0.5, 4),
        )
        return ModelClassifierResult(
            intent=IntentLabel.CLARIFY,
            slots={},
            confidence=confidence,
        )

    # Pass 2: Fill slots
    slot_result = fill_slots(model, intent_result.intent.value, nl_request, context)

    # Compute confidence from logprobs
    confidence_result = compute_confidence(
        intent_logprob=intent_result.intent_logprob,
        slot_logprobs=slot_result.slot_logprobs if slot_result.slot_logprobs else None,
    )
    confidence = to_confidence_score(confidence_result)

    return ModelClassifierResult(
        intent=intent_result.intent,
        slots=slot_result.slots,
        confidence=confidence,
    )
