"""INCEPT v2 runtime engine.

Single-class runtime that handles the full NL -> command lifecycle:
detect system context, build ChatML prompt, run inference, classify
response, score confidence, and enforce safety checks.

Replaces the multi-stage pipeline and direct_pipeline with one clean
path through a fine-tuned Qwen3 GGUF model.
"""

from __future__ import annotations

import logging
import os
import platform
import re
from statistics import mean
from typing import Any, Literal

from pydantic import BaseModel

from incept.core.model_loader import get_model
from incept.knowledge.store import KnowledgeStore
from incept.training.export import run_constrained_inference

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Response model
# ---------------------------------------------------------------------------


class EngineResponse(BaseModel):
    """Structured response from the INCEPT engine."""

    text: str  # The command or response text
    type: Literal["command", "refusal", "clarification", "info", "blocked"] = "command"
    confidence: Literal["high", "medium", "low"] = "high"
    risk: Literal["safe", "caution", "dangerous", "blocked"] = "safe"
    original_query: str = ""


# ---------------------------------------------------------------------------
# Safety patterns -- catastrophic commands that must never execute
# ---------------------------------------------------------------------------

_CATASTROPHIC_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\brm\s+(-\w*r\w*f|-\w*f\w*r)\s+/(\s|$)"), "rm -rf /"),
    (re.compile(r"\brm\s+(-\w*r\w*f|-\w*f\w*r)\s+/\*"), "rm -rf /*"),
    (re.compile(r"\brm\s+--no-preserve-root"), "rm --no-preserve-root"),
    (re.compile(r"\bdd\b.*of=/dev/[sh]d[a-z]"), "dd to disk device"),
    (re.compile(r"\bdd\b.*of=/dev/nvme"), "dd to nvme device"),
    (re.compile(r"\bmkfs\S*\s.*/dev/[sh]d[a-z]"), "mkfs on disk device"),
    (re.compile(r"\bmkfs\S*\s.*/dev/nvme"), "mkfs on nvme device"),
    (re.compile(r":\(\)\{.*:\|:"), "fork bomb"),
    (re.compile(r"\.\(\)\{.*\.\|\.\}"), "fork bomb variant"),
    (re.compile(r"\bchmod\s+(-R\s+)?777\s+/($|\s)"), "chmod -R 777 /"),
    (
        re.compile(r"\bchmod\s+(-R\s+)?777\s+/(etc|usr|bin|sbin|boot|dev)"),
        "chmod 777 on system dir",
    ),
]

# Patterns for simple risk classification
_SUDO_RE = re.compile(r"\bsudo\b")
_DANGEROUS_RE = re.compile(r"\brm\s+-\w*r|\bdd\b|\bmkfs\b")

# Qwen3 thinking mode: strip <think>...</think> blocks from output
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)


# ---------------------------------------------------------------------------
# System detection
# ---------------------------------------------------------------------------


def _detect_distro() -> tuple[str, str]:
    """Return (distro_name, version) from the running OS.

    Checks /etc/os-release on Linux, sw_vers on macOS.
    Falls back to platform.system() if nothing else works.
    """
    system = platform.system()

    if system == "Darwin":
        version = platform.mac_ver()[0] or ""
        return "macos", version

    # Linux -- read /etc/os-release
    try:
        with open("/etc/os-release") as fh:
            lines = fh.readlines()
        info: dict[str, str] = {}
        for line in lines:
            if "=" in line:
                key, _, val = line.strip().partition("=")
                info[key] = val.strip('"')
        distro = info.get("ID", "linux")
        version = info.get("VERSION_ID", "")
        return distro, version
    except OSError:
        pass

    return system.lower(), ""


def _detect_shell() -> str:
    """Return the current shell name (e.g. 'bash', 'zsh')."""
    shell_path = os.environ.get("SHELL", "/bin/bash")
    return os.path.basename(shell_path)


def _detect_root() -> str:
    """Return 'root' or 'non-root' based on effective UID."""
    try:
        return "root" if os.geteuid() == 0 else "non-root"
    except AttributeError:
        # Windows -- no geteuid
        return "non-root"


def detect_system_context() -> str:
    """Build a compact context string for the system prompt.

    Format: "{distro} {version} {shell} {root_status}"
    Example: "ubuntu 22.04 bash non-root"
    """
    distro, version = _detect_distro()
    shell = _detect_shell()
    root_status = _detect_root()
    parts = [distro]
    if version:
        parts.append(version)
    parts.extend([shell, root_status])
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Prompt building -- ChatML (Qwen2.5 native format)
# ---------------------------------------------------------------------------


def _build_chatml_prompt(
    context_line: str,
    query: str,
    history: list[dict[str, str]] | None = None,
    examples: list[object] | None = None,
    *,
    think: bool = False,
) -> str:
    """Build a ChatML-formatted prompt string.

    Structure:
        <|im_start|>system
        {context_line}
        [Similar examples: ... (if RAG examples provided)]
        <|im_end|>
        [previous turns if any]
        <|im_start|>user
        {query}<|im_end|>
        <|im_start|>assistant
    """
    parts: list[str] = []

    # System message — enhanced with RAG examples
    system_parts = [
        context_line,
        "Output only the command. No explanations.",
        "If the user does not specify a path, use the current directory.",
        "Use the simplest form of the command that achieves the task.",
    ]
    if examples:
        system_parts.append("")
        system_parts.append("Similar examples:")
        for ex in examples:
            if hasattr(ex, "query") and hasattr(ex, "command"):
                system_parts.append(f'- "{ex.query}" → {ex.command}')
            else:
                system_parts.append(f"- {ex}")

    parts.append(f"<|im_start|>system\n{chr(10).join(system_parts)}<|im_end|>")

    # Conversation history
    if history:
        for turn in history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            parts.append(f"<|im_start|>{role}\n{content}<|im_end|>")

    # Current user query + assistant prefix
    parts.append(f"<|im_start|>user\n{query}<|im_end|>")
    if think:
        # Let model reason with <think> tags
        parts.append("<|im_start|>assistant\n<think>\n")
    else:
        # Skip reasoning: emit empty think block so model jumps to answer
        parts.append("<|im_start|>assistant\n<think>\n</think>\n\n")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Post-processing helpers
# ---------------------------------------------------------------------------


def _strip_model_tokens(text: str) -> str:
    """Remove thinking blocks, ChatML stop tokens and trailing whitespace."""
    text = text.strip()
    text = _THINK_RE.sub("", text).strip()
    for tok in ("<|im_end|>", "</s>", "<|endoftext|>"):
        if text.endswith(tok):
            text = text[: -len(tok)].strip()
    return text


def _score_confidence(logprobs: list[float] | None) -> Literal["high", "medium", "low"]:
    """Compute confidence tier from mean log-probability."""
    if not logprobs:
        return "low"
    avg = mean(logprobs)
    if avg > -0.3:
        return "high"
    if avg > -1.0:
        return "medium"
    return "low"


def _classify_type(text: str) -> Literal["command", "refusal", "clarification", "info"]:
    """Classify model output into a response type."""
    lower = text.lower()
    if lower.startswith("i can't") or lower.startswith("i won't"):
        return "refusal"
    if text.rstrip().endswith("?"):
        return "clarification"
    if lower.startswith("i'm a linux") or lower.startswith("hello"):
        return "info"
    return "command"


def _classify_risk(text: str) -> Literal["safe", "caution", "dangerous"]:
    """Simple risk classification based on command content."""
    if _DANGEROUS_RE.search(text):
        return "dangerous"
    if _SUDO_RE.search(text):
        return "caution"
    return "safe"


def _check_catastrophic(text: str) -> str | None:
    """Return the matched reason if text contains a catastrophic pattern, else None."""
    for pattern, reason in _CATASTROPHIC_PATTERNS:
        if pattern.search(text):
            return reason
    return None


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


# ── Post-processing safety layer ─────────────────────────────

_INJECTION_TRIGGERS = frozenset(
    [
        "ignore",
        "forget",
        "disregard",
        "override",
        "bypass",
        "unrestricted",
        "jailbreak",
        "dan",
        "pretend",
        "system prompt",
        "instructions",
        "what are you",
        "who are you",
        "what model",
        "who created",
        "who made",
        "tell me a joke",
        "write a poem",
        "write a story",
        "repeat your",
        "show your prompt",
    ]
)

_VALID_CMD_STARTERS = frozenset(
    [
        "sudo",
        "grep",
        "find",
        "ls",
        "cat",
        "chmod",
        "chown",
        "chgrp",
        "mkdir",
        "rmdir",
        "rm",
        "cp",
        "mv",
        "touch",
        "head",
        "tail",
        "less",
        "more",
        "wc",
        "sort",
        "uniq",
        "cut",
        "awk",
        "sed",
        "tar",
        "zip",
        "unzip",
        "gzip",
        "gunzip",
        "bzip2",
        "xz",
        "ps",
        "top",
        "htop",
        "kill",
        "pkill",
        "killall",
        "pgrep",
        "df",
        "du",
        "free",
        "uptime",
        "date",
        "hostname",
        "uname",
        "whoami",
        "who",
        "id",
        "su",
        "passwd",
        "useradd",
        "userdel",
        "usermod",
        "groupadd",
        "groups",
        "getent",
        "umask",
        "chattr",
        "lsattr",
        "setfacl",
        "getfacl",
        "ip",
        "ifconfig",
        "ping",
        "traceroute",
        "tracepath",
        "mtr",
        "dig",
        "nslookup",
        "host",
        "whois",
        "curl",
        "wget",
        "ssh",
        "scp",
        "sftp",
        "rsync",
        "nc",
        "nmap",
        "ss",
        "netstat",
        "iptables",
        "ufw",
        "firewall-cmd",
        "systemctl",
        "service",
        "journalctl",
        "dmesg",
        "lsmod",
        "modprobe",
        "lsblk",
        "mount",
        "umount",
        "fdisk",
        "lspci",
        "lsusb",
        "lshw",
        "dmidecode",
        "lscpu",
        "sensors",
        "docker",
        "podman",
        "kubectl",
        "git",
        "make",
        "gcc",
        "python",
        "python3",
        "pip",
        "npm",
        "node",
        "apt",
        "apt-get",
        "dnf",
        "yum",
        "pacman",
        "zypper",
        "dpkg",
        "rpm",
        "crontab",
        "at",
        "watch",
        "screen",
        "tmux",
        "nohup",
        "echo",
        "printf",
        "export",
        "env",
        "alias",
        "unalias",
        "history",
        "clear",
        "reset",
        "man",
        "which",
        "whereis",
        "type",
        "file",
        "stat",
        "readlink",
        "realpath",
        "basename",
        "diff",
        "patch",
        "strings",
        "hexdump",
        "od",
        "xxd",
        "lsof",
        "strace",
        "time",
        "timeout",
        "nice",
        "renice",
        "shutdown",
        "reboot",
        "halt",
        "poweroff",
        "init",
        "openssl",
        "gpg",
        "md5sum",
        "sha256sum",
        "base64",
        "dd",
        "shred",
        "sync",
        "mkfs",
        "fsck",
        "resize2fs",
        "fg",
        "bg",
        "jobs",
        "wait",
        "sleep",
        "seq",
        "yes",
        "tee",
        "xargs",
        "parallel",
        "bc",
        "expr",
        "factor",
        "tr",
        "rev",
        "tac",
        "nl",
        "fold",
        "fmt",
        "column",
        "iconv",
        "dos2unix",
        "nano",
        "vi",
        "vim",
        "emacs",
        "sysctl",
        "loginctl",
        "timedatectl",
        "hostnamectl",
        "locate",
        "updatedb",
        "logrotate",
        "logger",
        "chroot",
        "nsenter",
        "unshare",
        "flock",
        "set",
        "shopt",
        "declare",
        "source",
        "eval",
        "test",
        "[",
        "[[",
        "UNSAFE_REQUEST",
    ]
)


def _postprocess_output(query: str, raw_output: str) -> str:
    """Post-process model output for production quality."""
    output = raw_output.strip()

    # 1. Take first line only (discard multi-line garbage)
    if "\n" in output:
        output = output.split("\n")[0].strip()

    # 2. Check for prompt injection
    query_lower = query.lower()
    for trigger in _INJECTION_TRIGGERS:
        if trigger in query_lower:
            return "UNSAFE_REQUEST"

    # 3. If output is empty or too short
    if not output or len(output) < 2:
        return "# Could not generate command"

    # 4. If output looks like English prose (starts with capital, no command-like structure)
    first_word = output.split()[0].lower() if output.split() else ""
    # Strip sudo prefix for checking
    check_word = first_word
    if check_word == "sudo" and len(output.split()) > 1:
        check_word = output.split()[1].lower()

    if (
        first_word
        and first_word[0].isupper()
        and first_word not in ("UNSAFE_REQUEST",)
        and check_word not in _VALID_CMD_STARTERS
    ):
        return "# Could not generate command"

    # 5. Check first word is a valid command (case-insensitive)
    if (
        check_word
        and check_word not in _VALID_CMD_STARTERS
        and not output.startswith(("/", "./", "~", "$", "(", "{", "!"))
        and "=" not in first_word
        and "|" not in output[:20]
    ):
        pass  # Don't block — might be a valid but uncommon command

    return output


class InceptEngine:
    """INCEPT v2 runtime engine.

    Loads a GGUF model, detects the host system, and provides a single
    ``ask()`` method that turns natural language into validated shell
    commands (or refusals / clarifications).

    Usage::

        engine = InceptEngine()
        resp = engine.ask("list all running docker containers")
        print(resp.text)        # "docker ps"
        print(resp.confidence)  # "high"
    """

    def __init__(self, model_path: str | None = None, *, think: bool = False) -> None:
        self._model: Any = get_model(model_path)
        self._context_line: str = detect_system_context()
        self._think: bool = think
        # RAG knowledge store (graceful degradation if unavailable)
        self._knowledge = KnowledgeStore()
        if self._model is None:
            logger.warning("No GGUF model available -- engine will return error responses")
        else:
            logger.info("Engine initialised  context=%s", self._context_line)

    # -- public API ---------------------------------------------------------

    @property
    def context_line(self) -> str:
        """The detected system context string."""
        return self._context_line

    @property
    def model_loaded(self) -> bool:
        """True if a GGUF model was successfully loaded."""
        return self._model is not None

    def ask(
        self,
        query: str,
        history: list[dict[str, str]] | None = None,
    ) -> EngineResponse:
        """Process a natural-language query and return a structured response.

        Args:
            query: The user's natural-language request.
            history: Optional prior conversation turns, each a dict with
                     ``role`` ("user" | "assistant") and ``content`` keys.

        Returns:
            An ``EngineResponse`` with the generated text, type,
            confidence, risk level, and original query.
        """
        if not query or not query.strip():
            return EngineResponse(
                text="Empty query.",
                type="refusal",
                confidence="high",
                risk="safe",
                original_query=query or "",
            )

        query = query.strip()

        # Guard: no model loaded
        if self._model is None:
            return EngineResponse(
                text="No model loaded. Place a .gguf file in models/ or set INCEPT_MODEL_PATH.",
                type="refusal",
                confidence="high",
                risk="safe",
                original_query=query,
            )

        # RAG: retrieve similar examples + user corrections
        rag_examples = []
        if self._knowledge.ready:
            distro = self._context_line.split()[0] if self._context_line else ""
            rag_examples = self._knowledge.search_examples(query, distro=distro, top_k=3)
            # User corrections take priority — prepend them
            corrections = self._knowledge.search_corrections(query, top_k=2)
            if corrections:
                rag_examples = corrections + rag_examples
                # Cap total examples to avoid bloating the prompt
                rag_examples = rag_examples[:5]

        # 1. Build prompt (with RAG examples if available)
        prompt = _build_chatml_prompt(
            self._context_line,
            query,
            history,
            examples=rag_examples,  # type: ignore[arg-type]
            think=self._think,
        )

        # 2. Run inference
        try:
            result = run_constrained_inference(
                model=self._model,
                prompt=prompt,
                grammar=None,
                max_tokens=512,
                temperature=0.0,
                top_p=0.8,
                top_k=20,
            )
        except Exception as exc:
            logger.error("Inference failed: %s", exc)
            return EngineResponse(
                text=f"Inference error: {exc}",
                type="refusal",
                confidence="low",
                risk="safe",
                original_query=query,
            )

        # 3. Extract and clean output
        raw_text = _strip_model_tokens(result.get("text", ""))
        if not raw_text:
            return EngineResponse(
                text="Model returned empty output. Try rephrasing your request.",
                type="refusal",
                confidence="low",
                risk="safe",
                original_query=query,
            )

        # 4. Confidence from logprobs
        confidence = _score_confidence(result.get("logprobs"))

        # 5. Safety check -- catastrophic patterns override everything
        blocked_reason = _check_catastrophic(raw_text)
        if blocked_reason:
            logger.warning("Blocked catastrophic command: %s", blocked_reason)
            return EngineResponse(
                text=f"Blocked: {blocked_reason}",
                type="blocked",
                confidence=confidence,
                risk="blocked",
                original_query=query,
            )

        # 6. Post-process output for production quality
        raw_text = _postprocess_output(query, raw_text)

        # 7. Classify response type and risk
        resp_type = _classify_type(raw_text)
        risk = _classify_risk(raw_text) if resp_type == "command" else "safe"

        return EngineResponse(
            text=raw_text,
            type=resp_type,
            confidence=confidence,
            risk=risk,
            original_query=query,
        )

    def __repr__(self) -> str:
        status = "loaded" if self._model is not None else "no-model"
        return f"<InceptEngine {status} ctx={self._context_line!r}>"
