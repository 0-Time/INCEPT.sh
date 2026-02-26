"""Pre-classifier: fast regex/keyword-based intent detection, safety, and OOS filtering."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from incept.schemas.intents import IntentLabel

_I = re.IGNORECASE


class PreClassifierResult(BaseModel):
    """Result from the pre-classifier stage."""

    matched_intent: IntentLabel | None = None
    is_safety_violation: bool = False
    is_out_of_scope: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    matched_pattern: str | None = None


# --- Safety violation patterns ---
# These are checked FIRST and unconditionally block execution.

_SAFETY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Fork bomb
    (re.compile(r":\(\)\s*\{.*:\|:.*\}", _I), "fork_bomb"),
    (re.compile(r"fork\s*bomb", _I), "fork_bomb_mention"),
    # rm -rf / variants
    (re.compile(r"\brm\s+(-\w*r\w*f|-\w*f\w*r)\s+/(\s|$)", _I), "rm_rf_root"),
    (
        re.compile(
            r"delete\s+(everything|all(\s+files)?)\s+(on|from)"
            r"\s+(this\s+)?(machine|system|computer|server|disk)",
            _I,
        ),
        "delete_everything",
    ),
    (
        re.compile(r"wipe\s+(the\s+)?(entire\s+)?(disk|drive|system|machine)", _I),
        "wipe_system",
    ),
    (re.compile(r"format\s+(my\s+)?(hard\s*drive|disk|ssd|sda)", _I), "format_disk"),
    # Pipe-to-shell
    (re.compile(r"curl\s+.*\|\s*(ba)?sh", _I), "pipe_to_shell"),
    (re.compile(r"wget\s+.*\|\s*(ba)?sh", _I), "pipe_to_shell"),
    (re.compile(r"curl\s+.*\|\s*sudo\s+(ba)?sh", _I), "pipe_to_shell_sudo"),
    # Write to raw disk
    (re.compile(r"dd\s+.*of=/dev/sd[a-z]", _I), "dd_to_disk"),
    (re.compile(r"dd\s+.*of=/dev/nvme", _I), "dd_to_disk"),
    (re.compile(r">\s*/dev/sd[a-z]", _I), "write_to_raw_disk"),
    (re.compile(r"echo\s+.*>\s*/dev/sd[a-z]", _I), "write_to_raw_disk"),
    # Dangerous chmod targets
    (re.compile(r"chmod\s+777\s+/etc/(passwd|shadow|sudoers)", _I), "dangerous_chmod"),
    (
        re.compile(r"(readable|writable)\s+.*(/etc/shadow|/etc/passwd)", _I),
        "expose_sensitive_file",
    ),
    # Prompt injection
    (
        re.compile(
            r"(ignore|disregard|forget)\s+(all\s+)?"
            r"(safety|security|previous)\s+(rules|instructions|constraints)",
            _I,
        ),
        "prompt_injection",
    ),
    (
        re.compile(
            r"(you\s+are\s+now|switch\s+to|enter)"
            r"\s+(unrestricted|unsafe|admin|root)\s+mode",
            _I,
        ),
        "role_injection",
    ),
    # mkfs on mounted devices
    (re.compile(r"mkfs\s+.*\s+/dev/sd[a-z]", _I), "mkfs_raw"),
]

# --- Out-of-scope patterns ---

_OOS_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(weather|temperature|forecast)\b.*\?", _I), "weather"),
    (re.compile(r"what('?s| is)\s+the\s+weather", _I), "weather"),
    (re.compile(r"\b(recipe|cook|bake|ingredient)\b", _I), "cooking"),
    (
        re.compile(
            r"\b(calculate|solve|compute)\b.*\b(equation|integral|derivative|matrix)\b",
            _I,
        ),
        "math",
    ),
    (
        re.compile(r"(write|compose)\s+(a\s+)?(poem|story|essay|song|email|letter)", _I),
        "creative_writing",
    ),
    (
        re.compile(r"\b(aws|azure|gcp|s3|lambda|ec2|cloud\s*formation)\b", _I),
        "cloud_services",
    ),
    (re.compile(r"(translate|translation)\s+.*(to|into|from)\s+\w+", _I), "translation"),
    (
        re.compile(r"\b(stock|bitcoin|crypto|invest)\s*(price|market|trading)\b", _I),
        "finance",
    ),
    (
        re.compile(r"(who|what|when|where|why)\s+(is|was|are|were)\s+\w+.*\?$", _I),
        "trivia",
    ),
]

# --- Fast-path intent patterns (top 20 most common) ---
# fmt: off
_P = IntentLabel
_INTENT_PATTERNS: list[tuple[re.Pattern[str], IntentLabel, float, str]] = [
    # find_files
    (re.compile(r"\bfind\b.*\bfiles?\b", _I), _P.find_files, 0.85, "find_files"),
    (re.compile(r"\bsearch\s+for\s+files?\b", _I), _P.find_files, 0.85, "search_for_files"),
    (re.compile(r"\blocate\b.*\bfiles?\b", _I), _P.find_files, 0.80, "locate_files"),
    # copy_files
    (re.compile(r"\bcopy\b.*\b(file|director|folder)", _I), _P.copy_files, 0.85, "copy_files"),
    # move_files
    (re.compile(r"\b(move|rename)\b.*\b(file|director|folder)", _I), _P.move_files, 0.85, "move_files"),
    # delete_files
    (re.compile(r"\b(delete|remove)\b.*\bfiles?\b", _I), _P.delete_files, 0.80, "delete_files"),
    # change_permissions
    (re.compile(r"\bchmod\b", _I), _P.change_permissions, 0.90, "chmod"),
    (re.compile(r"\b(change|set|modify)\s+(the\s+)?permissions?\b", _I), _P.change_permissions, 0.85, "change_permissions"),
    # change_ownership
    (re.compile(r"\bchown\b", _I), _P.change_ownership, 0.90, "chown"),
    (re.compile(r"\bchange\s+(the\s+)?own(er|ership)\b", _I), _P.change_ownership, 0.85, "change_ownership"),
    # create_directory
    (re.compile(r"\b(create|make)\s+(a\s+)?(new\s+)?(director|folder)", _I), _P.create_directory, 0.90, "create_directory"),
    (re.compile(r"\bmkdir\b", _I), _P.create_directory, 0.90, "mkdir"),
    # list_directory
    (re.compile(r"\blist\b.*\b(director|folder|files)\b", _I), _P.list_directory, 0.80, "list_directory"),
    (re.compile(r"\bls\b", _I), _P.list_directory, 0.85, "ls"),
    # disk_usage
    (re.compile(r"\bdisk\s+(usage|space)\b", _I), _P.disk_usage, 0.90, "disk_usage"),
    (re.compile(r"\bdu\b\s+", _I), _P.disk_usage, 0.85, "du"),
    (re.compile(r"\b(how\s+much|check)\s+(disk\s+)?space\b", _I), _P.disk_usage, 0.85, "check_space"),
    # search_text
    (re.compile(r"\bgrep\b", _I), _P.search_text, 0.90, "grep"),
    (re.compile(r"\bsearch\b.*\b(text|string|pattern|content)\b", _I), _P.search_text, 0.80, "search_text"),
    # install_package
    (re.compile(r"\binstall\b.*\bpackage\b", _I), _P.install_package, 0.85, "install_package"),
    (re.compile(r"\b(apt|dnf|yum|pacman)\s+(install|add)\b", _I), _P.install_package, 0.90, "pkg_install"),
    (re.compile(r"\binstall\s+\w+", _I), _P.install_package, 0.75, "install_generic"),
    # remove_package
    (re.compile(r"\b(remove|uninstall)\b.*\bpackage\b", _I), _P.remove_package, 0.85, "remove_package"),
    # start_service
    (re.compile(r"\bstart\s+(the\s+)?(\w+\s+)?service\b", _I), _P.start_service, 0.85, "start_service"),
    (re.compile(r"\bsystemctl\s+start\b", _I), _P.start_service, 0.90, "systemctl_start"),
    # stop_service
    (re.compile(r"\bstop\s+(the\s+)?(\w+\s+)?service\b", _I), _P.stop_service, 0.85, "stop_service"),
    (re.compile(r"\bsystemctl\s+stop\b", _I), _P.stop_service, 0.90, "systemctl_stop"),
    # restart_service
    (re.compile(r"\brestart\s+(the\s+)?(\w+\s+)?service\b", _I), _P.restart_service, 0.85, "restart_service"),
    # view_logs
    (re.compile(r"\b(view|show|check)\s+(the\s+)?(system\s+)?logs?\b", _I), _P.view_logs, 0.85, "view_logs"),
    (re.compile(r"\bjournalctl\b", _I), _P.view_logs, 0.85, "journalctl"),
    # process_list
    (re.compile(r"\b(list|show)\s+(running\s+)?processes\b", _I), _P.process_list, 0.85, "list_processes"),
    (re.compile(r"\bps\s+aux\b", _I), _P.process_list, 0.90, "ps_aux"),
    # kill_process
    (re.compile(r"\bkill\s+(the\s+)?(\w+\s+)?process\b", _I), _P.kill_process, 0.85, "kill_process"),
    # download_file
    (re.compile(r"\bdownload\b.*\b(file|url)\b", _I), _P.download_file, 0.85, "download_file"),
    (re.compile(r"\b(curl|wget)\s+http", _I), _P.download_file, 0.85, "curl_wget"),
    # view_file
    (re.compile(r"\b(view|show|display|cat|read)\s+(the\s+)?(contents?\s+of\s+)?\w+\.\w+", _I), _P.view_file, 0.75, "view_file"),
    # compress_archive
    (re.compile(r"\b(compress|archive|tar|zip)\b.*\b(file|director|folder)", _I), _P.compress_archive, 0.80, "compress"),
    (re.compile(r"\bcreate\s+(a\s+)?(tar|zip|archive)\b", _I), _P.compress_archive, 0.85, "create_archive"),
    # extract_archive
    (re.compile(r"\b(extract|unzip|untar|decompress)\b", _I), _P.extract_archive, 0.85, "extract"),
    # system_info
    (re.compile(r"\b(system\s+info|uptime|memory\s+usage|cpu\s+usage)\b", _I), _P.system_info, 0.85, "system_info"),
]
# fmt: on


def classify(text: str) -> PreClassifierResult:
    """Run the pre-classifier on a natural language request.

    Checks in order: safety violations, out-of-scope, then fast-path intent matching.
    """
    text = text.strip()

    # 1. Safety violations (checked first, unconditionally)
    for pattern, name in _SAFETY_PATTERNS:
        if pattern.search(text):
            return PreClassifierResult(
                matched_intent=IntentLabel.UNSAFE_REQUEST,
                is_safety_violation=True,
                confidence=0.99,
                matched_pattern=name,
            )

    # 2. Out-of-scope detection
    for pattern, name in _OOS_PATTERNS:
        if pattern.search(text):
            return PreClassifierResult(
                matched_intent=IntentLabel.OUT_OF_SCOPE,
                is_out_of_scope=True,
                confidence=0.90,
                matched_pattern=name,
            )

    # 3. Fast-path intent matching
    best_match: tuple[IntentLabel, float, str] | None = None
    for pattern, intent, confidence, name in _INTENT_PATTERNS:
        if pattern.search(text) and (best_match is None or confidence > best_match[1]):
            best_match = (intent, confidence, name)

    if best_match is not None:
        return PreClassifierResult(
            matched_intent=best_match[0],
            confidence=best_match[1],
            matched_pattern=best_match[2],
        )

    # 4. No match — defer to model
    return PreClassifierResult()
