"""Intent label enum for all 78 INCEPT intents (75 + 3 special)."""

from __future__ import annotations

from enum import StrEnum


class IntentLabel(StrEnum):
    """All supported intent labels."""

    # File Operations (12)
    find_files = "find_files"
    copy_files = "copy_files"
    move_files = "move_files"
    delete_files = "delete_files"
    change_permissions = "change_permissions"
    change_ownership = "change_ownership"
    create_directory = "create_directory"
    list_directory = "list_directory"
    disk_usage = "disk_usage"
    view_file = "view_file"
    create_symlink = "create_symlink"
    compare_files = "compare_files"

    # Text Processing (6)
    search_text = "search_text"
    replace_text = "replace_text"
    sort_output = "sort_output"
    count_lines = "count_lines"
    extract_columns = "extract_columns"
    unique_lines = "unique_lines"

    # Archive Operations (2)
    compress_archive = "compress_archive"
    extract_archive = "extract_archive"

    # Package Management (4)
    install_package = "install_package"
    remove_package = "remove_package"
    update_packages = "update_packages"
    search_package = "search_package"

    # Service Management (5)
    start_service = "start_service"
    stop_service = "stop_service"
    restart_service = "restart_service"
    enable_service = "enable_service"
    service_status = "service_status"

    # User Management (3)
    create_user = "create_user"
    delete_user = "delete_user"
    modify_user = "modify_user"

    # Log Operations (3)
    view_logs = "view_logs"
    follow_logs = "follow_logs"
    filter_logs = "filter_logs"

    # Scheduling (3)
    schedule_cron = "schedule_cron"
    list_cron = "list_cron"
    remove_cron = "remove_cron"

    # Networking (6)
    network_info = "network_info"
    test_connectivity = "test_connectivity"
    download_file = "download_file"
    transfer_file = "transfer_file"
    ssh_connect = "ssh_connect"
    port_check = "port_check"

    # Process Management (3)
    process_list = "process_list"
    kill_process = "kill_process"
    system_info = "system_info"

    # Disk/Mount (2)
    mount_device = "mount_device"
    unmount_device = "unmount_device"

    # Docker (6)
    docker_run = "docker_run"
    docker_ps = "docker_ps"
    docker_stop = "docker_stop"
    docker_logs = "docker_logs"
    docker_build = "docker_build"
    docker_exec = "docker_exec"

    # Git (7)
    git_status = "git_status"
    git_commit = "git_commit"
    git_push = "git_push"
    git_pull = "git_pull"
    git_log = "git_log"
    git_diff = "git_diff"
    git_branch = "git_branch"

    # SSH Keys (2)
    generate_ssh_key = "generate_ssh_key"
    copy_ssh_key = "copy_ssh_key"

    # Disk Info (2)
    list_partitions = "list_partitions"
    check_filesystem = "check_filesystem"

    # Firewall (3)
    firewall_allow = "firewall_allow"
    firewall_deny = "firewall_deny"
    firewall_list = "firewall_list"

    # DNS (2)
    dns_lookup = "dns_lookup"
    dns_resolve = "dns_resolve"

    # Environment (2)
    set_env_var = "set_env_var"
    list_env_vars = "list_env_vars"

    # Systemd Timers (2)
    create_timer = "create_timer"
    list_timers = "list_timers"

    # Special (3)
    CLARIFY = "CLARIFY"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    UNSAFE_REQUEST = "UNSAFE_REQUEST"


_INTENT_DESCRIPTIONS: dict[str, str] = {
    "find_files": "Search for files by name, type, size, or modification time",
    "copy_files": "Copy files or directories to a new location",
    "move_files": "Move or rename files and directories",
    "delete_files": "Remove files or directories",
    "change_permissions": "Modify file or directory permissions",
    "change_ownership": "Change file or directory owner/group",
    "create_directory": "Create new directories",
    "list_directory": "List contents of a directory",
    "disk_usage": "Check disk space usage",
    "view_file": "Display file contents",
    "create_symlink": "Create symbolic links",
    "compare_files": "Compare two files for differences",
    "search_text": "Search for text patterns in files",
    "replace_text": "Find and replace text in files",
    "sort_output": "Sort lines of text",
    "count_lines": "Count lines, words, or characters",
    "extract_columns": "Extract specific columns from text",
    "unique_lines": "Filter or count unique lines",
    "compress_archive": "Create compressed archives",
    "extract_archive": "Extract files from archives",
    "install_package": "Install software packages",
    "remove_package": "Remove software packages",
    "update_packages": "Update installed packages",
    "search_package": "Search for available packages",
    "start_service": "Start a system service",
    "stop_service": "Stop a system service",
    "restart_service": "Restart a system service",
    "enable_service": "Enable a service to start at boot",
    "service_status": "Check the status of a service",
    "create_user": "Create a new user account",
    "delete_user": "Delete a user account",
    "modify_user": "Modify user account properties",
    "view_logs": "View system or application logs",
    "follow_logs": "Follow log output in real-time",
    "filter_logs": "Filter logs by pattern or time range",
    "schedule_cron": "Schedule a recurring task with cron",
    "list_cron": "List scheduled cron jobs",
    "remove_cron": "Remove a scheduled cron job",
    "network_info": "Display network configuration",
    "test_connectivity": "Test network connectivity",
    "download_file": "Download a file from a URL",
    "transfer_file": "Transfer files between hosts",
    "ssh_connect": "Connect to a remote host via SSH",
    "port_check": "Check if a network port is open",
    "process_list": "List running processes",
    "kill_process": "Terminate a process",
    "system_info": "Display system information",
    "mount_device": "Mount a filesystem or device",
    "unmount_device": "Unmount a filesystem or device",
    "docker_run": "Run a Docker container",
    "docker_ps": "List Docker containers",
    "docker_stop": "Stop a running Docker container",
    "docker_logs": "View Docker container logs",
    "docker_build": "Build a Docker image from a Dockerfile",
    "docker_exec": "Execute a command inside a running container",
    "git_status": "Show the working tree status",
    "git_commit": "Record changes to the repository",
    "git_push": "Push commits to a remote repository",
    "git_pull": "Fetch and merge from a remote repository",
    "git_log": "Show commit history",
    "git_diff": "Show changes between commits or working tree",
    "git_branch": "List, create, or delete branches",
    "generate_ssh_key": "Generate a new SSH key pair",
    "copy_ssh_key": "Copy SSH public key to a remote host",
    "list_partitions": "List disk partitions and block devices",
    "check_filesystem": "Check and repair a filesystem",
    "firewall_allow": "Allow traffic on a port through the firewall",
    "firewall_deny": "Block traffic on a port through the firewall",
    "firewall_list": "List current firewall rules",
    "dns_lookup": "Look up DNS records for a domain",
    "dns_resolve": "Resolve a domain name to an IP address",
    "set_env_var": "Set an environment variable",
    "list_env_vars": "List environment variables",
    "create_timer": "Create a systemd timer unit",
    "list_timers": "List active systemd timers",
}

_SPECIAL_INTENTS = {IntentLabel.CLARIFY, IntentLabel.OUT_OF_SCOPE, IntentLabel.UNSAFE_REQUEST}


def get_intent_descriptions() -> dict[str, str]:
    """Return descriptions for all non-special intents."""
    return dict(_INTENT_DESCRIPTIONS)
