"""Training data generator for direct NL → command model.

Uses existing compiler functions as "teachers" to generate (prompt, completion)
pairs from assembled records.  Each assembled record contains an NL request,
context line, expected intent, and expected slots.  The compiler converts these
into the actual shell command, producing training pairs of the form:

    prompt:     <s>[INST] [CONTEXT] debian bash non-root safe\n[REQUEST] install nginx [/INST]
    completion: sudo apt-get install -y nginx</s>

Special intents map to refusal tokens instead of commands:
    UNSAFE_REQUEST → [UNSAFE]
    OUT_OF_SCOPE   → [OOS]
    CLARIFY        → [CLARIFY]
"""

from __future__ import annotations

import logging
from typing import Any

from incept.compiler.expanded_ops import EXPANDED_OPS_COMPILERS
from incept.compiler.file_ops import FILE_OPS_COMPILERS
from incept.compiler.router import IntentRouter
from incept.compiler.system_ops import SYSTEM_OPS_COMPILERS
from incept.compiler.text_ops import TEXT_OPS_COMPILERS
from incept.core.context import EnvironmentContext
from incept.schemas.intents import IntentLabel

logger = logging.getLogger(__name__)

# Special intent → refusal token mapping
_REFUSAL_MAP: dict[str, str] = {
    "UNSAFE_REQUEST": "[UNSAFE]",
    "OUT_OF_SCOPE": "[OOS]",
    "CLARIFY": "[CLARIFY]",
}

# Intents that typically require sudo
_SUDO_INTENTS: frozenset[str] = frozenset({
    "install_package",
    "remove_package",
    "update_packages",
    "start_service",
    "stop_service",
    "restart_service",
    "enable_service",
    "create_user",
    "delete_user",
    "modify_user",
    "mount_device",
    "unmount_device",
})


def _build_router() -> IntentRouter:
    """Create and populate the intent router with all compiler functions."""
    router = IntentRouter()
    router.register_many(FILE_OPS_COMPILERS)
    router.register_many(TEXT_OPS_COMPILERS)
    router.register_many(SYSTEM_OPS_COMPILERS)
    router.register_many(EXPANDED_OPS_COMPILERS)
    return router


_ROUTER = _build_router()


def _context_line_to_env(context_line: str) -> EnvironmentContext:
    """Parse a compact context line into an EnvironmentContext.

    Context lines look like: "debian bash non-root safe"
    """
    parts = context_line.strip().split()
    distro = parts[0] if len(parts) > 0 else "debian"
    shell = parts[1] if len(parts) > 1 else "bash"
    is_root = parts[2] == "root" if len(parts) > 2 else False
    safe_mode = parts[3] != "unsafe" if len(parts) > 3 else True

    # Map distro_id to distro_family
    family_map: dict[str, str] = {
        "debian": "debian",
        "ubuntu": "debian",
        "rhel": "rhel",
        "centos": "rhel",
        "fedora": "rhel",
        "rocky": "rhel",
        "alma": "rhel",
        "arch": "arch",
        "manjaro": "arch",
        "suse": "suse",
        "opensuse-leap": "suse",
        "opensuse-tumbleweed": "suse",
        "macos": "macos",
    }
    distro_family = family_map.get(distro, "debian")

    return EnvironmentContext(
        distro_id=distro,
        distro_family=distro_family,  # type: ignore[arg-type]
        shell=shell,
        is_root=is_root,
        safe_mode=safe_mode,
        allow_sudo=True,
    )


def compile_record(record: dict[str, Any]) -> dict[str, str] | None:
    """Compile a single assembled record into a training pair.

    Args:
        record: An assembled record with keys: nl_request, context_line,
                expected_intent, expected_slots.

    Returns:
        A dict with 'prompt' and 'completion' keys, or None on failure.
    """
    intent_str = record.get("expected_intent", "")
    nl_request = record.get("nl_request", "")
    context_line = record.get("context_line", "debian bash non-root safe")
    slots = record.get("expected_slots", {})

    if not nl_request or not intent_str:
        return None

    # Handle special/refusal intents
    if intent_str in _REFUSAL_MAP:
        prompt = f"<s>[INST] [CONTEXT] {context_line}\n[REQUEST] {nl_request} [/INST]"
        completion = f"{_REFUSAL_MAP[intent_str]}</s>"
        return {"prompt": prompt, "completion": completion}

    # Try to compile via the router
    try:
        intent = IntentLabel(intent_str)
    except ValueError:
        logger.debug("Unknown intent: %s", intent_str)
        return None

    if not _ROUTER.has_compiler(intent):
        logger.debug("No compiler for intent: %s", intent_str)
        return None

    ctx = _context_line_to_env(context_line)

    try:
        from incept.schemas.ir import ConfidenceScore, SingleIR

        requires_sudo = intent_str in _SUDO_INTENTS
        ir = SingleIR(
            intent=intent,
            confidence=ConfidenceScore(intent=0.9, slots=0.9, composite=0.9),
            params=slots,
            requires_sudo=requires_sudo,
        )
        result = _ROUTER.compile_single(ir, ctx)
        command = result.full_command
    except Exception as e:
        logger.debug("Compilation failed for %s: %s", intent_str, e)
        return None

    if not command.strip():
        return None

    prompt = f"<s>[INST] [CONTEXT] {context_line}\n[REQUEST] {nl_request} [/INST]"
    completion = f"{command}</s>"
    return {"prompt": prompt, "completion": completion}


def generate_command_pairs(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], int]:
    """Generate training pairs from a list of assembled records.

    Args:
        records: List of assembled records.

    Returns:
        Tuple of (successful pairs, failure count).
    """
    pairs: list[dict[str, str]] = []
    failures = 0

    for record in records:
        pair = compile_record(record)
        if pair is not None:
            pairs.append(pair)
        else:
            failures += 1

    return pairs, failures
