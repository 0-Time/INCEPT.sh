"""Compiler functions for system administration intents.

Translates system-operation IR params into shell command strings. Each public
function takes a flat ``params`` dict (matching the corresponding Pydantic
schema) and an ``EnvironmentContext``, and returns a ready-to-execute shell
command.

Covers: package management, service management, user management, log
operations, scheduling, networking, process management, and disk/mount.
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


_PS_SORT_MAP = {
    "cpu": "%cpu",
    "memory": "%mem",
    "pid": "pid",
    "name": "comm",
}


# ---------------------------------------------------------------------------
# Package Management (4) — distro-aware
# ---------------------------------------------------------------------------


def compile_install_package(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a package install command (apt-get, dnf, pacman, zypper, or brew)."""
    pkg = params["package"]
    assume_yes: bool = params.get("assume_yes", False)
    version: str | None = params.get("version")

    if ctx.distro_family == "macos":
        parts: list[str] = ["brew", "install"]
        if version is not None:
            parts.append(_q(f"{pkg}@{version}", ctx))
        else:
            parts.append(_q(pkg, ctx))
    elif ctx.distro_family == "debian":
        parts = ["apt-get", "install"]
        if assume_yes:
            parts.append("-y")
        if version is not None:
            parts.append(_q(f"{pkg}={version}", ctx))
        else:
            parts.append(_q(pkg, ctx))
    elif ctx.distro_family == "arch":
        parts = ["pacman", "-S"]
        if assume_yes:
            parts.append("--noconfirm")
        parts.append(_q(pkg, ctx))
    elif ctx.distro_family == "suse":
        parts = ["zypper", "install"]
        if assume_yes:
            parts.append("-y")
        if version is not None:
            parts.append(_q(f"{pkg}={version}", ctx))
        else:
            parts.append(_q(pkg, ctx))
    else:
        parts = ["dnf", "install"]
        if assume_yes:
            parts.append("-y")
        if version is not None:
            parts.append(_q(f"{pkg}-{version}", ctx))
        else:
            parts.append(_q(pkg, ctx))

    return " ".join(parts)


def compile_remove_package(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a package removal command (apt-get, dnf, pacman, zypper, or brew)."""
    pkg = params["package"]
    purge_config: bool = params.get("purge_config", False)

    if ctx.distro_family == "macos":
        parts: list[str] = ["brew", "uninstall"]
        if purge_config:
            parts.append("--zap")
        parts.append(_q(pkg, ctx))
    elif ctx.distro_family == "debian":
        parts = ["apt-get", "purge"] if purge_config else ["apt-get", "remove"]
        parts.append(_q(pkg, ctx))
    elif ctx.distro_family == "arch":
        parts = ["pacman", "-Rns"] if purge_config else ["pacman", "-R"]
        parts.append(_q(pkg, ctx))
    elif ctx.distro_family == "suse":
        parts = ["zypper", "remove"]
        if purge_config:
            parts.append("--clean-deps")
        parts.append(_q(pkg, ctx))
    else:
        parts = ["dnf", "remove", _q(pkg, ctx)]

    return " ".join(parts)


def compile_update_packages(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a package update/upgrade command (apt-get, dnf, pacman, zypper, or brew)."""
    upgrade_all: bool = params.get("upgrade_all", False)

    if ctx.distro_family == "macos":
        if upgrade_all:
            return "brew update && brew upgrade"
        return "brew update"
    elif ctx.distro_family == "debian":
        if upgrade_all:
            return "apt-get update && apt-get upgrade"
        return "apt-get update"
    elif ctx.distro_family == "arch":
        if upgrade_all:
            return "pacman -Syu"
        return "pacman -Sy"
    elif ctx.distro_family == "suse":
        if upgrade_all:
            return "zypper refresh && zypper update"
        return "zypper refresh"
    else:
        if upgrade_all:
            return "dnf upgrade"
        return "dnf check-update"


def compile_search_package(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a package search command (apt-cache, dnf, pacman, zypper, or brew)."""
    query = params["query"]

    if ctx.distro_family == "macos":
        return f"brew search {_q(query, ctx)}"
    elif ctx.distro_family == "debian":
        return f"apt-cache search {_q(query, ctx)}"
    elif ctx.distro_family == "arch":
        return f"pacman -Ss {_q(query, ctx)}"
    elif ctx.distro_family == "suse":
        return f"zypper search {_q(query, ctx)}"
    return f"dnf search {_q(query, ctx)}"


# ---------------------------------------------------------------------------
# Service Management (5)
# ---------------------------------------------------------------------------


def compile_start_service(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a service start command (systemctl or brew services)."""
    svc = _q(params["service_name"], ctx)
    if ctx.distro_family == "macos":
        return f"brew services start {svc}"
    return f"systemctl start {svc}"


def compile_stop_service(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a service stop command (systemctl or brew services)."""
    svc = _q(params["service_name"], ctx)
    if ctx.distro_family == "macos":
        return f"brew services stop {svc}"
    return f"systemctl stop {svc}"


def compile_restart_service(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a service restart command (systemctl or brew services)."""
    svc = _q(params["service_name"], ctx)
    if ctx.distro_family == "macos":
        return f"brew services restart {svc}"
    return f"systemctl restart {svc}"


def compile_enable_service(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a service enable command (systemctl or brew services)."""
    svc = _q(params["service_name"], ctx)
    if ctx.distro_family == "macos":
        return f"brew services start {svc}"
    return f"systemctl enable {svc}"


def compile_service_status(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a service status command (systemctl or brew services)."""
    svc = _q(params["service_name"], ctx)
    if ctx.distro_family == "macos":
        return f"brew services info {svc}"
    return f"systemctl status {svc}"


# ---------------------------------------------------------------------------
# User Management (3)
# ---------------------------------------------------------------------------


def compile_create_user(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``useradd`` command from *create_user* params."""
    parts: list[str] = ["useradd"]

    shell: str | None = params.get("shell")
    if shell is not None:
        parts.extend(["-s", _q(shell, ctx)])

    home_dir: str | None = params.get("home_dir")
    if home_dir is not None:
        parts.extend(["-d", _q(home_dir, ctx)])

    parts.append("-m")

    groups: list[str] | None = params.get("groups")
    if groups:
        parts.extend(["-G", _q(",".join(groups), ctx)])

    parts.append(_q(params["username"], ctx))
    return " ".join(parts)


def compile_delete_user(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``userdel`` command from *delete_user* params."""
    parts: list[str] = ["userdel"]

    if params.get("remove_home", False):
        parts.append("-r")

    parts.append(_q(params["username"], ctx))
    return " ".join(parts)


def compile_modify_user(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``usermod`` command from *modify_user* params."""
    parts: list[str] = ["usermod"]

    add_groups: list[str] | None = params.get("add_groups")
    if add_groups:
        parts.extend(["-aG", _q(",".join(add_groups), ctx)])

    shell: str | None = params.get("shell")
    if shell is not None:
        parts.extend(["-s", _q(shell, ctx)])

    home_dir: str | None = params.get("home_dir")
    if home_dir is not None:
        parts.extend(["-d", _q(home_dir, ctx)])

    parts.append(_q(params["username"], ctx))
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Log Operations (3)
# ---------------------------------------------------------------------------


def _journalctl_parts(params: dict[str, Any], ctx: EnvironmentContext) -> list[str]:
    """Build common journalctl flag parts from params."""
    parts: list[str] = ["journalctl"]

    unit: str | None = params.get("unit")
    if unit is not None:
        parts.extend(["-u", _q(unit, ctx)])

    since: str | None = params.get("since")
    if since is not None:
        parts.extend(["--since", _q(since, ctx)])

    until: str | None = params.get("until")
    if until is not None:
        parts.extend(["--until", _q(until, ctx)])

    return parts


def compile_view_logs(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a log viewing command (journalctl or macOS log show)."""
    if ctx.distro_family == "macos":
        parts: list[str] = ["log", "show"]
        unit: str | None = params.get("unit")
        if unit is not None:
            parts.extend(["--predicate", f"'subsystem == \"{unit}\"'"])
        since: str | None = params.get("since")
        if since is not None:
            parts.extend(["--start", _q(since, ctx)])
        until: str | None = params.get("until")
        if until is not None:
            parts.extend(["--end", _q(until, ctx)])
        lines: int | None = params.get("lines")
        if lines is not None:
            parts.extend(["--last", f"{lines}m"])
        return " ".join(parts)

    parts = _journalctl_parts(params, ctx)

    lines = params.get("lines")
    if lines is not None:
        parts.extend(["-n", str(lines)])

    priority: str | None = params.get("priority")
    if priority is not None:
        parts.extend(["-p", _q(priority, ctx)])

    return " ".join(parts)


def compile_follow_logs(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a log follow command (journalctl -f or macOS log stream)."""
    if ctx.distro_family == "macos":
        parts: list[str] = ["log", "stream"]
        unit: str | None = params.get("unit")
        if unit is not None:
            parts.extend(["--predicate", f"'subsystem == \"{unit}\"'"])
        return " ".join(parts)

    parts = ["journalctl", "-f"]

    unit = params.get("unit")
    if unit is not None:
        parts.extend(["-u", _q(unit, ctx)])

    return " ".join(parts)


def compile_filter_logs(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a log filter command (journalctl | grep or log show | grep)."""
    pattern = params["pattern"]
    if ctx.distro_family == "macos":
        parts: list[str] = ["log", "show"]
        unit: str | None = params.get("unit")
        if unit is not None:
            parts.extend(["--predicate", f"'subsystem == \"{unit}\"'"])
        since: str | None = params.get("since")
        if since is not None:
            parts.extend(["--start", _q(since, ctx)])
        return " ".join(parts) + f" | grep {_q(pattern, ctx)}"

    parts = _journalctl_parts(params, ctx)
    return " ".join(parts) + f" | grep {_q(pattern, ctx)}"


# ---------------------------------------------------------------------------
# Scheduling (3)
# ---------------------------------------------------------------------------


def compile_schedule_cron(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a crontab append command from *schedule_cron* params."""
    schedule = params["schedule"]
    command = params["command"]
    user: str | None = params.get("user")

    user_flag = f" -u {_q(user, ctx)}" if user else ""
    entry = f"{schedule} {command}"

    return f"(crontab{user_flag} -l 2>/dev/null; echo {_q(entry, ctx)}) | crontab{user_flag} -"


def compile_list_cron(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a crontab list command from *list_cron* params."""
    user: str | None = params.get("user")

    if user:
        return f"crontab -u {_q(user, ctx)} -l"
    return "crontab -l"


def compile_remove_cron(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a crontab removal command from *remove_cron* params."""
    pattern = params["job_id_or_pattern"]
    user: str | None = params.get("user")

    user_flag = f" -u {_q(user, ctx)}" if user else ""

    return f"crontab{user_flag} -l | grep -v {_q(pattern, ctx)} | crontab{user_flag} -"


# ---------------------------------------------------------------------------
# Networking (6)
# ---------------------------------------------------------------------------


def compile_network_info(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a network info command (ip addr show or ifconfig on macOS)."""
    interface: str | None = params.get("interface")

    if ctx.distro_family == "macos":
        if interface is not None:
            return f"ifconfig {_q(interface, ctx)}"
        return "ifconfig"

    if interface is not None:
        return f"ip addr show {_q(interface, ctx)}"
    return "ip addr show"


def compile_test_connectivity(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``ping`` command from *test_connectivity* params."""
    host = params["host"]
    count: int | None = params.get("count")
    timeout: int | None = params.get("timeout")

    parts: list[str] = ["ping"]

    if count is not None:
        parts.extend(["-c", str(count)])

    if timeout is not None:
        # macOS uses -t for timeout, Linux uses -W
        if ctx.distro_family == "macos":
            parts.extend(["-t", str(timeout)])
        else:
            parts.extend(["-W", str(timeout)])

    parts.append(_q(host, ctx))
    return " ".join(parts)


def compile_download_file(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``curl`` download command from *download_file* params."""
    url = params["url"]
    output_path: str | None = params.get("output_path")
    follow_redirects: bool = params.get("follow_redirects", True)

    parts: list[str] = ["curl"]

    if follow_redirects:
        parts.append("-L")

    if output_path is not None:
        parts.extend(["-o", _q(output_path, ctx)])
    else:
        parts.append("-O")

    parts.append(_q(url, ctx))
    return " ".join(parts)


def compile_transfer_file(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile an ``scp`` command from *transfer_file* params."""
    parts: list[str] = ["scp"]

    if params.get("recursive", False):
        parts.append("-r")

    port: int | None = params.get("port")
    if port is not None:
        parts.extend(["-P", str(port)])

    parts.append(_q(params["source"], ctx))
    parts.append(_q(params["destination"], ctx))
    return " ".join(parts)


def compile_ssh_connect(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile an ``ssh`` command from *ssh_connect* params."""
    host = params["host"]
    user: str | None = params.get("user")
    port: int | None = params.get("port")
    key_file: str | None = params.get("key_file")

    parts: list[str] = ["ssh"]

    if port is not None:
        parts.extend(["-p", str(port)])

    if key_file is not None:
        parts.extend(["-i", _q(key_file, ctx)])

    if user is not None:
        parts.append(_q(f"{user}@{host}", ctx))
    else:
        parts.append(_q(host, ctx))

    return " ".join(parts)


def compile_port_check(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a port check command (ss or lsof on macOS)."""
    port: int | None = params.get("port")

    if ctx.distro_family == "macos":
        if port is not None:
            return f"lsof -iTCP:{port} -sTCP:LISTEN"
        return "lsof -iTCP -sTCP:LISTEN"

    base = "ss -tlnp"

    if port is not None:
        return f"{base} | grep :{port}"
    return base


# ---------------------------------------------------------------------------
# Process Management (3)
# ---------------------------------------------------------------------------


def compile_process_list(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``ps`` command from *process_list* params."""
    user: str | None = params.get("user")
    sort_by: str | None = params.get("sort_by")
    filter_str: str | None = params.get("filter")

    if user is not None:
        parts: list[str] = ["ps", "-u", _q(user, ctx)]
    else:
        parts = ["ps", "aux"]

    if sort_by is not None and ctx.distro_family != "macos":
        field = _PS_SORT_MAP.get(sort_by, sort_by)
        parts.append(f"--sort=-{field}")

    cmd = " ".join(parts)

    # macOS ps doesn't support --sort; pipe through sort instead
    if sort_by is not None and ctx.distro_family == "macos":
        sort_col = {"cpu": "3", "memory": "4", "pid": "2", "name": "11"}
        col = sort_col.get(sort_by, "3")
        cmd += f" | sort -rnk {col}"

    if filter_str is not None:
        cmd += f" | grep {_q(filter_str, ctx)}"

    return cmd


def compile_kill_process(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``kill`` command from *kill_process* params."""
    target = params["target"]
    signal: str | None = params.get("signal")
    force: bool = params.get("force", False)

    parts: list[str] = ["kill"]

    if force:
        parts.append("-9")
    elif signal is not None:
        parts.append(f"-{signal}")

    parts.append(_q(target, ctx))
    return " ".join(parts)


def compile_system_info(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a system info command from *system_info* params."""
    info_type: str = params.get("info_type", "all")

    if ctx.distro_family == "macos":
        if info_type == "memory":
            return "vm_stat"
        if info_type == "cpu":
            return "sysctl -n machdep.cpu.brand_string"
        if info_type == "uptime":
            return "uptime"
        return "vm_stat && sysctl -n machdep.cpu.brand_string && uptime"

    if info_type == "memory":
        return "free -h"
    if info_type == "cpu":
        return "lscpu"
    if info_type == "uptime":
        return "uptime"
    # "all" or any unrecognised value
    return "free -h && lscpu && uptime"


# ---------------------------------------------------------------------------
# Disk / Mount (2)
# ---------------------------------------------------------------------------


def compile_mount_device(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile a ``mount`` command from *mount_device* params."""
    parts: list[str] = ["mount"]

    fs_type: str | None = params.get("filesystem_type")
    if fs_type is not None:
        parts.extend(["-t", _q(fs_type, ctx)])

    options: str | None = params.get("options")
    if options is not None:
        parts.extend(["-o", _q(options, ctx)])

    parts.append(_q(params["device"], ctx))
    parts.append(_q(params["mount_point"], ctx))
    return " ".join(parts)


def compile_unmount_device(params: dict[str, Any], ctx: EnvironmentContext) -> str:
    """Compile an ``umount`` command from *unmount_device* params."""
    parts: list[str] = ["umount"]

    if params.get("force", False):
        parts.append("-f")
    if params.get("lazy", False):
        parts.append("-l")

    parts.append(_q(params["mount_point"], ctx))
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Registry mapping: IntentLabel -> compiler function
# ---------------------------------------------------------------------------

SYSTEM_OPS_COMPILERS: dict[IntentLabel, Any] = {
    # Package Management
    IntentLabel.install_package: compile_install_package,
    IntentLabel.remove_package: compile_remove_package,
    IntentLabel.update_packages: compile_update_packages,
    IntentLabel.search_package: compile_search_package,
    # Service Management
    IntentLabel.start_service: compile_start_service,
    IntentLabel.stop_service: compile_stop_service,
    IntentLabel.restart_service: compile_restart_service,
    IntentLabel.enable_service: compile_enable_service,
    IntentLabel.service_status: compile_service_status,
    # User Management
    IntentLabel.create_user: compile_create_user,
    IntentLabel.delete_user: compile_delete_user,
    IntentLabel.modify_user: compile_modify_user,
    # Log Operations
    IntentLabel.view_logs: compile_view_logs,
    IntentLabel.follow_logs: compile_follow_logs,
    IntentLabel.filter_logs: compile_filter_logs,
    # Scheduling
    IntentLabel.schedule_cron: compile_schedule_cron,
    IntentLabel.list_cron: compile_list_cron,
    IntentLabel.remove_cron: compile_remove_cron,
    # Networking
    IntentLabel.network_info: compile_network_info,
    IntentLabel.test_connectivity: compile_test_connectivity,
    IntentLabel.download_file: compile_download_file,
    IntentLabel.transfer_file: compile_transfer_file,
    IntentLabel.ssh_connect: compile_ssh_connect,
    IntentLabel.port_check: compile_port_check,
    # Process Management
    IntentLabel.process_list: compile_process_list,
    IntentLabel.kill_process: compile_kill_process,
    IntentLabel.system_info: compile_system_info,
    # Disk/Mount
    IntentLabel.mount_device: compile_mount_device,
    IntentLabel.unmount_device: compile_unmount_device,
}
