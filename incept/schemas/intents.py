"""Intent label enum for all 52 INCEPT intents (49 + 3 special)."""

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

    # Special (3)
    CLARIFY = "CLARIFY"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    UNSAFE_REQUEST = "UNSAFE_REQUEST"
