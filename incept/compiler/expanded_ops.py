"""Compiler functions for expanded intents (Sprint 7.4).

Covers Docker, Git, SSH keys, Disk info, Firewall, DNS, Environment,
and Systemd timer operations.
"""

from __future__ import annotations

from typing import Any

from incept.compiler.quoting import quote_value
from incept.core.context import EnvironmentContext
from incept.schemas.intents import IntentLabel

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _q(value: str, ctx: EnvironmentContext) -> str:
    return quote_value(value, ctx.shell)


# ---------------------------------------------------------------------------
# Docker (6)
# ---------------------------------------------------------------------------


def compile_docker_run(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``docker run`` command."""
    parts: list[str] = ["docker", "run"]

    if params.get("detach", False):
        parts.append("-d")

    name: str | None = params.get("name")
    if name is not None:
        parts.extend(["--name", _q(name, ctx)])

    for port in params.get("ports", []):
        parts.extend(["-p", port])

    for vol in params.get("volumes", []):
        parts.extend(["-v", vol])

    for env in params.get("env_vars", []):
        parts.extend(["-e", env])

    parts.append(_q(params["image"], ctx))
    return " ".join(parts)


def compile_docker_ps(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``docker ps`` command."""
    parts: list[str] = ["docker", "ps"]
    if params.get("all", False):
        parts.append("-a")
    return " ".join(parts)


def compile_docker_stop(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``docker stop`` command."""
    return f"docker stop {_q(params['container'], ctx)}"


def compile_docker_logs(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``docker logs`` command."""
    parts: list[str] = ["docker", "logs"]

    if params.get("follow", False):
        parts.append("-f")

    tail: int | None = params.get("tail")
    if tail is not None:
        parts.extend(["--tail", str(tail)])

    parts.append(_q(params["container"], ctx))
    return " ".join(parts)


def compile_docker_build(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``docker build`` command."""
    parts: list[str] = ["docker", "build"]

    tag: str | None = params.get("tag")
    if tag is not None:
        parts.extend(["-t", _q(tag, ctx)])

    file: str | None = params.get("file")
    if file is not None:
        parts.extend(["-f", _q(file, ctx)])

    parts.append(_q(params["path"], ctx))
    return " ".join(parts)


def compile_docker_exec(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``docker exec`` command."""
    parts: list[str] = ["docker", "exec"]

    if params.get("interactive", False):
        parts.append("-it")

    parts.append(_q(params["container"], ctx))
    parts.append(_q(params["command"], ctx))
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Git (7)
# ---------------------------------------------------------------------------


def compile_git_status(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``git status`` command."""
    parts: list[str] = ["git", "status"]
    if params.get("short", False):
        parts.append("-s")
    return " ".join(parts)


def compile_git_commit(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``git commit`` command."""
    parts: list[str] = ["git", "commit"]

    if params.get("all", False):
        parts.append("-a")

    parts.extend(["-m", _q(params["message"], ctx)])
    return " ".join(parts)


def compile_git_push(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``git push`` command."""
    parts: list[str] = ["git", "push"]

    remote: str | None = params.get("remote")
    branch: str | None = params.get("branch")

    if remote is not None:
        parts.append(_q(remote, ctx))
    if branch is not None:
        parts.append(_q(branch, ctx))

    return " ".join(parts)


def compile_git_pull(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``git pull`` command."""
    parts: list[str] = ["git", "pull"]

    remote: str | None = params.get("remote")
    branch: str | None = params.get("branch")

    if remote is not None:
        parts.append(_q(remote, ctx))
    if branch is not None:
        parts.append(_q(branch, ctx))

    return " ".join(parts)


def compile_git_log(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``git log`` command."""
    parts: list[str] = ["git", "log"]

    if params.get("oneline", False):
        parts.append("--oneline")

    count: int | None = params.get("count")
    if count is not None:
        parts.append(f"-n {count}")

    return " ".join(parts)


def compile_git_diff(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``git diff`` command."""
    parts: list[str] = ["git", "diff"]

    if params.get("staged", False):
        parts.append("--staged")

    path: str | None = params.get("path")
    if path is not None:
        parts.append(_q(path, ctx))

    return " ".join(parts)


def compile_git_branch(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``git branch`` command."""
    parts: list[str] = ["git", "branch"]

    if params.get("all", False):
        parts.append("-a")

    if params.get("delete", False):
        parts.append("-d")

    name: str | None = params.get("name")
    if name is not None:
        parts.append(_q(name, ctx))

    return " ".join(parts)


# ---------------------------------------------------------------------------
# SSH Keys (2)
# ---------------------------------------------------------------------------


def compile_generate_ssh_key(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile an ``ssh-keygen`` command."""
    parts: list[str] = ["ssh-keygen"]

    key_type: str | None = params.get("key_type")
    if key_type is not None:
        parts.extend(["-t", key_type])

    comment: str | None = params.get("comment")
    if comment is not None:
        parts.extend(["-C", _q(comment, ctx)])

    file: str | None = params.get("file")
    if file is not None:
        parts.extend(["-f", _q(file, ctx)])

    return " ".join(parts)


def compile_copy_ssh_key(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile an ``ssh-copy-id`` command."""
    parts: list[str] = ["ssh-copy-id"]

    identity: str | None = params.get("identity_file")
    if identity is not None:
        parts.extend(["-i", _q(identity, ctx)])

    host = params["host"]
    user: str | None = params.get("user")

    if user is not None:
        parts.append(_q(f"{user}@{host}", ctx))
    else:
        parts.append(_q(host, ctx))

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Disk Info (2)
# ---------------------------------------------------------------------------


def compile_list_partitions(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a partition list command (lsblk or diskutil list)."""
    if ctx.distro_family == "macos":
        device: str | None = params.get("device")
        if device is not None:
            return f"diskutil list {_q(device, ctx)}"
        return "diskutil list"

    parts: list[str] = ["lsblk"]

    device = params.get("device")
    if device is not None:
        parts.append(_q(device, ctx))

    return " ".join(parts)


def compile_check_filesystem(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a filesystem check command (fsck or diskutil verifyDisk)."""
    if ctx.distro_family == "macos":
        return f"diskutil verifyDisk {_q(params['device'], ctx)}"
    return f"fsck {_q(params['device'], ctx)}"


# ---------------------------------------------------------------------------
# Firewall (3) — distro-aware
# ---------------------------------------------------------------------------


def compile_firewall_allow(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a firewall allow rule (ufw, firewall-cmd, or pfctl)."""
    port = params["port"]
    proto: str | None = params.get("protocol")

    if ctx.distro_family == "macos":
        proto_str = proto or "tcp"
        return (
            f'echo "pass in proto {proto_str} from any to any port {port}" '
            f"| sudo pfctl -ef -"
        )
    elif ctx.distro_family in ("debian", "arch"):
        port_str = f"{port}/{proto}" if proto else str(port)
        return f"ufw allow {port_str}"
    else:
        port_str = f"{port}/{proto}" if proto else f"{port}/tcp"
        return (
            f"firewall-cmd --permanent --add-port={port_str} "
            f"&& firewall-cmd --reload"
        )


def compile_firewall_deny(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a firewall deny rule (ufw, firewall-cmd, or pfctl)."""
    port = params["port"]
    proto: str | None = params.get("protocol")

    if ctx.distro_family == "macos":
        proto_str = proto or "tcp"
        return (
            f'echo "block in proto {proto_str} from any to any port {port}" '
            f"| sudo pfctl -ef -"
        )
    elif ctx.distro_family in ("debian", "arch"):
        port_str = f"{port}/{proto}" if proto else str(port)
        return f"ufw deny {port_str}"
    else:
        port_str = f"{port}/{proto}" if proto else f"{port}/tcp"
        return (
            f"firewall-cmd --permanent --remove-port={port_str} "
            f"&& firewall-cmd --reload"
        )


def compile_firewall_list(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a firewall list command (ufw, firewall-cmd, or pfctl)."""
    if ctx.distro_family == "macos":
        return "sudo pfctl -sr"
    if ctx.distro_family in ("debian", "arch"):
        return "ufw status verbose"
    return "firewall-cmd --list-all"


# ---------------------------------------------------------------------------
# DNS (2)
# ---------------------------------------------------------------------------


def compile_dns_lookup(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a ``dig`` DNS lookup command."""
    domain = params["domain"]
    record_type: str | None = params.get("record_type")

    parts: list[str] = ["dig"]
    if record_type is not None:
        parts.append(record_type)
    parts.append(_q(domain, ctx))
    return " ".join(parts)


def compile_dns_resolve(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a ``host`` DNS resolution command."""
    return f"host {_q(params['domain'], ctx)}"


# ---------------------------------------------------------------------------
# Environment (2)
# ---------------------------------------------------------------------------


def compile_set_env_var(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile an ``export`` command."""
    import re

    name = params["name"]
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise ValueError(f"Invalid environment variable name: {name!r}")
    value = params["value"]
    return f"export {name}={_q(value, ctx)}"


def compile_list_env_vars(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile an ``env`` or ``printenv`` command."""
    filter_str: str | None = params.get("filter")
    if filter_str is not None:
        return f"env | grep {_q(filter_str, ctx)}"
    return "env"


# ---------------------------------------------------------------------------
# Systemd Timers (2)
# ---------------------------------------------------------------------------


def compile_create_timer(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Generate systemd timer unit file creation commands."""
    name = params["name"]
    on_calendar = params["on_calendar"]
    command = params["command"]
    desc: str = params.get("description", f"{name} timer")

    service = (
        f"[Unit]\\nDescription={desc}\\n\\n"
        f"[Service]\\nType=oneshot\\nExecStart={command}\\n"
    )
    timer = (
        f"[Unit]\\nDescription={desc}\\n\\n"
        f"[Timer]\\nOnCalendar={on_calendar}\\nPersistent=true\\n\\n"
        f"[Install]\\nWantedBy=timers.target\\n"
    )
    svc_path = f"/etc/systemd/system/{name}.service"
    tmr_path = f"/etc/systemd/system/{name}.timer"

    return (
        f"printf '{service}' > {svc_path} && "
        f"printf '{timer}' > {tmr_path} && "
        f"systemctl daemon-reload && "
        f"systemctl enable --now {name}.timer"
    )


def compile_list_timers(
    params: dict[str, Any], ctx: EnvironmentContext
) -> str:
    """Compile a ``systemctl list-timers`` command."""
    parts: list[str] = ["systemctl", "list-timers"]
    if params.get("all", False):
        parts.append("--all")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Registry mapping: IntentLabel -> compiler function
# ---------------------------------------------------------------------------

EXPANDED_OPS_COMPILERS: dict[IntentLabel, Any] = {
    # Docker
    IntentLabel.docker_run: compile_docker_run,
    IntentLabel.docker_ps: compile_docker_ps,
    IntentLabel.docker_stop: compile_docker_stop,
    IntentLabel.docker_logs: compile_docker_logs,
    IntentLabel.docker_build: compile_docker_build,
    IntentLabel.docker_exec: compile_docker_exec,
    # Git
    IntentLabel.git_status: compile_git_status,
    IntentLabel.git_commit: compile_git_commit,
    IntentLabel.git_push: compile_git_push,
    IntentLabel.git_pull: compile_git_pull,
    IntentLabel.git_log: compile_git_log,
    IntentLabel.git_diff: compile_git_diff,
    IntentLabel.git_branch: compile_git_branch,
    # SSH Keys
    IntentLabel.generate_ssh_key: compile_generate_ssh_key,
    IntentLabel.copy_ssh_key: compile_copy_ssh_key,
    # Disk Info
    IntentLabel.list_partitions: compile_list_partitions,
    IntentLabel.check_filesystem: compile_check_filesystem,
    # Firewall
    IntentLabel.firewall_allow: compile_firewall_allow,
    IntentLabel.firewall_deny: compile_firewall_deny,
    IntentLabel.firewall_list: compile_firewall_list,
    # DNS
    IntentLabel.dns_lookup: compile_dns_lookup,
    IntentLabel.dns_resolve: compile_dns_resolve,
    # Environment
    IntentLabel.set_env_var: compile_set_env_var,
    IntentLabel.list_env_vars: compile_list_env_vars,
    # Systemd Timers
    IntentLabel.create_timer: compile_create_timer,
    IntentLabel.list_timers: compile_list_timers,
}
