"""Explanation templates for all 52 intents."""

from __future__ import annotations

from incept.schemas.intents import IntentLabel


class ExplanationTemplate:
    """Template for explaining a command to the user."""

    def __init__(
        self,
        summary: str,
        flag_explanations: dict[str, str] | None = None,
        side_effects: list[str] | None = None,
    ) -> None:
        self.summary = summary
        self.flag_explanations = flag_explanations or {}
        self.side_effects = side_effects or []

    def render(self, **kwargs: str) -> str:
        """Render the summary with template variables."""
        try:
            return self.summary.format(**kwargs)
        except KeyError:
            return self.summary


# fmt: off
EXPLANATION_TEMPLATES: dict[IntentLabel, ExplanationTemplate] = {
    # ── File Operations (12) ──────────────────────────────────────────────────
    IntentLabel.find_files: ExplanationTemplate(
        summary="Search for files matching specified criteria in {path}",
        flag_explanations={"-name": "match filename pattern", "-type": "filter by type (f=file, d=directory, l=link)", "-size": "filter by size", "-mtime": "filter by modification time", "-user": "filter by owner", "-perm": "filter by permissions"},
        side_effects=[],
    ),
    IntentLabel.copy_files: ExplanationTemplate(
        summary="Copy {source} to {destination}",
        flag_explanations={"-r": "copy directories recursively", "-p": "preserve file attributes", "-a": "archive mode (preserve all)"},
        side_effects=["Creates new files at destination", "May overwrite existing files"],
    ),
    IntentLabel.move_files: ExplanationTemplate(
        summary="Move {source} to {destination}",
        flag_explanations={},
        side_effects=["Removes file from original location", "May overwrite existing files"],
    ),
    IntentLabel.delete_files: ExplanationTemplate(
        summary="Delete {target}",
        flag_explanations={"-r": "remove directories recursively", "-f": "force removal without confirmation"},
        side_effects=["Permanently removes files", "Cannot be undone"],
    ),
    IntentLabel.change_permissions: ExplanationTemplate(
        summary="Change permissions of {target} to {permissions}",
        flag_explanations={"-R": "apply recursively to directories"},
        side_effects=["Modifies file access control"],
    ),
    IntentLabel.change_ownership: ExplanationTemplate(
        summary="Change ownership of {target} to {owner}",
        flag_explanations={"-R": "apply recursively to directories"},
        side_effects=["Modifies file ownership"],
    ),
    IntentLabel.create_directory: ExplanationTemplate(
        summary="Create directory {path}",
        flag_explanations={"-p": "create parent directories as needed"},
        side_effects=["Creates new directory on disk"],
    ),
    IntentLabel.list_directory: ExplanationTemplate(
        summary="List contents of {path}",
        flag_explanations={"-l": "long format with details", "-a": "show hidden files", "-S": "sort by size", "-t": "sort by time"},
        side_effects=[],
    ),
    IntentLabel.disk_usage: ExplanationTemplate(
        summary="Show disk usage for {path}",
        flag_explanations={"-h": "human-readable sizes", "--max-depth": "limit directory depth", "-s": "show only total"},
        side_effects=[],
    ),
    IntentLabel.view_file: ExplanationTemplate(
        summary="Display contents of {file}",
        flag_explanations={"-n": "show line numbers", "head": "show first N lines", "tail": "show last N lines"},
        side_effects=[],
    ),
    IntentLabel.create_symlink: ExplanationTemplate(
        summary="Create symbolic link {link_name} pointing to {target}",
        flag_explanations={"-s": "create symbolic (soft) link"},
        side_effects=["Creates a new symlink on disk"],
    ),
    IntentLabel.compare_files: ExplanationTemplate(
        summary="Compare {file1} and {file2}",
        flag_explanations={"-u": "unified diff format", "-C": "context diff format"},
        side_effects=[],
    ),

    # ── Text Processing (6) ───────────────────────────────────────────────────
    IntentLabel.search_text: ExplanationTemplate(
        summary="Search for pattern {pattern} in files",
        flag_explanations={"-r": "search recursively", "-i": "ignore case", "-n": "show line numbers", "-P": "use Perl regex", "-E": "use extended regex"},
        side_effects=[],
    ),
    IntentLabel.replace_text: ExplanationTemplate(
        summary="Replace {pattern} with {replacement} in {file}",
        flag_explanations={"-i": "edit file in-place", "g": "replace all occurrences (global)"},
        side_effects=["Modifies file contents in-place"],
    ),
    IntentLabel.sort_output: ExplanationTemplate(
        summary="Sort the contents of {input_file}",
        flag_explanations={"-r": "reverse order", "-n": "numeric sort", "-u": "remove duplicates", "-k": "sort by field"},
        side_effects=[],
    ),
    IntentLabel.count_lines: ExplanationTemplate(
        summary="Count {mode} in {input_file}",
        flag_explanations={"-l": "count lines", "-w": "count words", "-c": "count characters/bytes"},
        side_effects=[],
    ),
    IntentLabel.extract_columns: ExplanationTemplate(
        summary="Extract columns {field_spec} from {input_file}",
        flag_explanations={"-F": "field separator", "print": "output selected fields"},
        side_effects=[],
    ),
    IntentLabel.unique_lines: ExplanationTemplate(
        summary="Filter unique lines from {input_file}",
        flag_explanations={"-c": "prefix lines with occurrence count", "-d": "only show duplicated lines"},
        side_effects=[],
    ),

    # ── Archive Operations (2) ────────────────────────────────────────────────
    IntentLabel.compress_archive: ExplanationTemplate(
        summary="Compress {source} into archive",
        flag_explanations={"-z": "use gzip compression", "-j": "use bzip2 compression", "-J": "use xz compression", "--exclude": "exclude matching files"},
        side_effects=["Creates a new archive file"],
    ),
    IntentLabel.extract_archive: ExplanationTemplate(
        summary="Extract archive {source}",
        flag_explanations={"-C": "extract to specified directory", "-x": "extract files"},
        side_effects=["Extracts files to disk", "May overwrite existing files"],
    ),

    # ── Package Management (4) ────────────────────────────────────────────────
    IntentLabel.install_package: ExplanationTemplate(
        summary="Install package {package}",
        flag_explanations={"-y": "automatic yes to prompts", "=version": "install specific version"},
        side_effects=["Downloads and installs package", "May install dependencies", "Requires root/sudo"],
    ),
    IntentLabel.remove_package: ExplanationTemplate(
        summary="Remove package {package}",
        flag_explanations={"--purge": "also remove configuration files"},
        side_effects=["Removes package from system", "May remove dependent packages"],
    ),
    IntentLabel.update_packages: ExplanationTemplate(
        summary="Update package lists and optionally upgrade packages",
        flag_explanations={"upgrade": "upgrade all packages to latest versions"},
        side_effects=["Downloads package metadata", "May upgrade system packages"],
    ),
    IntentLabel.search_package: ExplanationTemplate(
        summary="Search for packages matching {query}",
        flag_explanations={},
        side_effects=[],
    ),

    # ── Service Management (5) ────────────────────────────────────────────────
    IntentLabel.start_service: ExplanationTemplate(
        summary="Start the {service_name} service",
        flag_explanations={},
        side_effects=["Starts the service daemon", "Service will run until stopped"],
    ),
    IntentLabel.stop_service: ExplanationTemplate(
        summary="Stop the {service_name} service",
        flag_explanations={},
        side_effects=["Stops the running service"],
    ),
    IntentLabel.restart_service: ExplanationTemplate(
        summary="Restart the {service_name} service",
        flag_explanations={},
        side_effects=["Stops and restarts the service", "Brief service interruption"],
    ),
    IntentLabel.enable_service: ExplanationTemplate(
        summary="Enable {service_name} to start on boot",
        flag_explanations={},
        side_effects=["Creates systemd symlinks", "Service will auto-start on reboot"],
    ),
    IntentLabel.service_status: ExplanationTemplate(
        summary="Show status of {service_name} service",
        flag_explanations={},
        side_effects=[],
    ),

    # ── User Management (3) ───────────────────────────────────────────────────
    IntentLabel.create_user: ExplanationTemplate(
        summary="Create user account {username}",
        flag_explanations={"-s": "set login shell", "-d": "set home directory", "-m": "create home directory", "-G": "add to supplementary groups"},
        side_effects=["Creates new user account", "Creates home directory", "Requires root/sudo"],
    ),
    IntentLabel.delete_user: ExplanationTemplate(
        summary="Delete user account {username}",
        flag_explanations={"-r": "remove home directory and mail spool"},
        side_effects=["Removes user account", "May remove home directory"],
    ),
    IntentLabel.modify_user: ExplanationTemplate(
        summary="Modify user account {username}",
        flag_explanations={"-aG": "add to groups (append)", "-s": "change shell", "-d": "change home directory"},
        side_effects=["Modifies user account settings"],
    ),

    # ── Log Operations (3) ────────────────────────────────────────────────────
    IntentLabel.view_logs: ExplanationTemplate(
        summary="View system logs",
        flag_explanations={"-u": "filter by systemd unit", "--since": "show logs since time", "--until": "show logs until time", "-n": "number of lines", "-p": "filter by priority"},
        side_effects=[],
    ),
    IntentLabel.follow_logs: ExplanationTemplate(
        summary="Follow log output in real-time",
        flag_explanations={"-f": "follow new log entries", "-u": "filter by systemd unit"},
        side_effects=["Runs until interrupted (Ctrl+C)"],
    ),
    IntentLabel.filter_logs: ExplanationTemplate(
        summary="Filter logs for pattern {pattern}",
        flag_explanations={"-u": "filter by unit", "--since": "start time", "--until": "end time"},
        side_effects=[],
    ),

    # ── Scheduling (3) ────────────────────────────────────────────────────────
    IntentLabel.schedule_cron: ExplanationTemplate(
        summary="Schedule cron job: {command} at {schedule}",
        flag_explanations={"crontab": "edit user cron table"},
        side_effects=["Adds entry to crontab", "Job will run on schedule"],
    ),
    IntentLabel.list_cron: ExplanationTemplate(
        summary="List scheduled cron jobs",
        flag_explanations={"-l": "list crontab entries", "-u": "specify user"},
        side_effects=[],
    ),
    IntentLabel.remove_cron: ExplanationTemplate(
        summary="Remove cron job matching {job_id_or_pattern}",
        flag_explanations={},
        side_effects=["Removes entry from crontab"],
    ),

    # ── Networking (6) ────────────────────────────────────────────────────────
    IntentLabel.network_info: ExplanationTemplate(
        summary="Show network interface information",
        flag_explanations={"addr": "show IP addresses", "show": "display interface details"},
        side_effects=[],
    ),
    IntentLabel.test_connectivity: ExplanationTemplate(
        summary="Test connectivity to {host}",
        flag_explanations={"-c": "number of ping packets", "-W": "timeout in seconds"},
        side_effects=[],
    ),
    IntentLabel.download_file: ExplanationTemplate(
        summary="Download file from {url}",
        flag_explanations={"-o": "output filename", "-L": "follow redirects", "-O": "use remote filename"},
        side_effects=["Downloads file to disk"],
    ),
    IntentLabel.transfer_file: ExplanationTemplate(
        summary="Transfer {source} to {destination}",
        flag_explanations={"-r": "recursive transfer", "-P": "specify port"},
        side_effects=["Copies files over network"],
    ),
    IntentLabel.ssh_connect: ExplanationTemplate(
        summary="Connect to {host} via SSH",
        flag_explanations={"-p": "specify port", "-i": "identity/key file"},
        side_effects=["Opens remote shell session"],
    ),
    IntentLabel.port_check: ExplanationTemplate(
        summary="Check listening ports",
        flag_explanations={"-t": "TCP ports", "-l": "listening only", "-n": "numeric output", "-p": "show process"},
        side_effects=[],
    ),

    # ── Process Management (3) ────────────────────────────────────────────────
    IntentLabel.process_list: ExplanationTemplate(
        summary="List running processes",
        flag_explanations={"aux": "all users, detailed format", "--sort": "sort by field", "-u": "filter by user"},
        side_effects=[],
    ),
    IntentLabel.kill_process: ExplanationTemplate(
        summary="Send signal to process {target}",
        flag_explanations={"-9": "SIGKILL (force kill)", "-15": "SIGTERM (graceful)"},
        side_effects=["Terminates the target process"],
    ),
    IntentLabel.system_info: ExplanationTemplate(
        summary="Show system information",
        flag_explanations={"free": "memory usage", "lscpu": "CPU information", "uptime": "system uptime"},
        side_effects=[],
    ),

    # ── Disk/Mount (2) ────────────────────────────────────────────────────────
    IntentLabel.mount_device: ExplanationTemplate(
        summary="Mount {device} at {mount_point}",
        flag_explanations={"-t": "filesystem type", "-o": "mount options"},
        side_effects=["Mounts filesystem", "Makes device accessible at mount point"],
    ),
    IntentLabel.unmount_device: ExplanationTemplate(
        summary="Unmount {mount_point}",
        flag_explanations={"-f": "force unmount", "-l": "lazy unmount"},
        side_effects=["Detaches filesystem from mount point"],
    ),
}
# fmt: on


# ── Clarification templates ──────────────────────────────────────────────────

CLARIFICATION_TEMPLATES: dict[str, str] = {
    "which_package": "Which package would you like to {action}?",
    "which_directory": "Which directory do you mean? Please provide the full path.",
    "which_distro": "Which Linux distribution are you using? (e.g., Ubuntu, CentOS, Debian)",
    "which_compression": "Which compression format would you like? (tar.gz, tar.bz2, tar.xz, zip)",
    "which_service": "Which service would you like to {action}?",
    "which_user": "Which user account do you mean?",
    "which_file": "Which file do you mean? Please provide the full path.",
    "confirm_scope": "This will affect {scope}. Are you sure you want to proceed?",
    "clarify_intent": "I'm not sure what you're asking. Could you rephrase your request?",
}


# ── Per-distro defaults ──────────────────────────────────────────────────────

DISTRO_DEFAULTS: dict[str, dict[str, str]] = {
    "debian": {
        "package_manager": "apt-get",
        "package_search": "apt-cache search",
        "service_manager": "systemctl",
        "firewall": "ufw",
        "default_shell": "/bin/bash",
    },
    "rhel": {
        "package_manager": "dnf",
        "package_search": "dnf search",
        "service_manager": "systemctl",
        "firewall": "firewalld",
        "default_shell": "/bin/bash",
    },
}
