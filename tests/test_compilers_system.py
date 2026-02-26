"""Tests for system_ops compiler functions.

Verifies that each compiler translates a params dict + EnvironmentContext
into the expected shell command string.  Distro-aware functions are tested
against both Debian and RHEL contexts.
"""

from __future__ import annotations

import pytest

from incept.compiler.system_ops import (
    compile_create_user,
    compile_delete_user,
    compile_download_file,
    compile_enable_service,
    compile_filter_logs,
    compile_follow_logs,
    compile_install_package,
    compile_kill_process,
    compile_list_cron,
    compile_modify_user,
    compile_mount_device,
    compile_network_info,
    compile_port_check,
    compile_process_list,
    compile_remove_cron,
    compile_remove_package,
    compile_restart_service,
    compile_schedule_cron,
    compile_search_package,
    compile_service_status,
    compile_ssh_connect,
    compile_start_service,
    compile_stop_service,
    compile_system_info,
    compile_test_connectivity,
    compile_transfer_file,
    compile_unmount_device,
    compile_update_packages,
    compile_view_logs,
)
from incept.core.context import EnvironmentContext

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def ctx() -> EnvironmentContext:
    """Default Debian/bash context."""
    return EnvironmentContext()


@pytest.fixture()
def rhel_ctx() -> EnvironmentContext:
    """RHEL context for distro-aware tests."""
    return EnvironmentContext(distro_family="rhel")


# ===================================================================
# Package Management
# ===================================================================


class TestCompileInstallPackage:
    def test_basic_debian(self, ctx: EnvironmentContext) -> None:
        result = compile_install_package({"package": "nginx"}, ctx)
        assert result.startswith("apt-get install")
        assert "nginx" in result

    def test_basic_rhel(self, rhel_ctx: EnvironmentContext) -> None:
        result = compile_install_package({"package": "nginx"}, rhel_ctx)
        assert result.startswith("dnf install")
        assert "nginx" in result

    def test_assume_yes_debian(self, ctx: EnvironmentContext) -> None:
        result = compile_install_package(
            {"package": "curl", "assume_yes": True}, ctx
        )
        assert "-y" in result
        assert result.startswith("apt-get")

    def test_assume_yes_rhel(self, rhel_ctx: EnvironmentContext) -> None:
        result = compile_install_package(
            {"package": "curl", "assume_yes": True}, rhel_ctx
        )
        assert "-y" in result
        assert result.startswith("dnf")

    def test_version_debian(self, ctx: EnvironmentContext) -> None:
        result = compile_install_package(
            {"package": "python3", "version": "3.11.2-1"}, ctx
        )
        assert "python3=3.11.2-1" in result

    def test_version_rhel(self, rhel_ctx: EnvironmentContext) -> None:
        result = compile_install_package(
            {"package": "python3", "version": "3.11.2"}, rhel_ctx
        )
        assert "python3-3.11.2" in result

    def test_no_assume_yes(self, ctx: EnvironmentContext) -> None:
        result = compile_install_package({"package": "vim"}, ctx)
        assert "-y" not in result


class TestCompileRemovePackage:
    def test_basic_debian(self, ctx: EnvironmentContext) -> None:
        result = compile_remove_package({"package": "apache2"}, ctx)
        assert result.startswith("apt-get remove")
        assert "apache2" in result

    def test_basic_rhel(self, rhel_ctx: EnvironmentContext) -> None:
        result = compile_remove_package({"package": "httpd"}, rhel_ctx)
        assert result.startswith("dnf remove")
        assert "httpd" in result

    def test_purge_debian(self, ctx: EnvironmentContext) -> None:
        result = compile_remove_package(
            {"package": "nginx", "purge_config": True}, ctx
        )
        assert "purge" in result
        assert "remove" not in result

    def test_purge_ignored_rhel(self, rhel_ctx: EnvironmentContext) -> None:
        # RHEL uses dnf remove regardless of purge_config
        result = compile_remove_package(
            {"package": "nginx", "purge_config": True}, rhel_ctx
        )
        assert result.startswith("dnf remove")


class TestCompileUpdatePackages:
    def test_basic_debian(self, ctx: EnvironmentContext) -> None:
        result = compile_update_packages({}, ctx)
        assert result == "apt-get update"

    def test_basic_rhel(self, rhel_ctx: EnvironmentContext) -> None:
        result = compile_update_packages({}, rhel_ctx)
        assert result == "dnf check-update"

    def test_upgrade_all_debian(self, ctx: EnvironmentContext) -> None:
        result = compile_update_packages({"upgrade_all": True}, ctx)
        assert "apt-get update" in result
        assert "apt-get upgrade" in result

    def test_upgrade_all_rhel(self, rhel_ctx: EnvironmentContext) -> None:
        result = compile_update_packages({"upgrade_all": True}, rhel_ctx)
        assert result == "dnf upgrade"


class TestCompileSearchPackage:
    def test_basic_debian(self, ctx: EnvironmentContext) -> None:
        result = compile_search_package({"query": "python"}, ctx)
        assert result.startswith("apt-cache search")
        assert "python" in result

    def test_basic_rhel(self, rhel_ctx: EnvironmentContext) -> None:
        result = compile_search_package({"query": "python"}, rhel_ctx)
        assert result.startswith("dnf search")
        assert "python" in result


# ===================================================================
# Service Management
# ===================================================================


class TestServiceManagement:
    @pytest.mark.parametrize(
        "compile_fn, action",
        [
            (compile_start_service, "start"),
            (compile_stop_service, "stop"),
            (compile_restart_service, "restart"),
            (compile_enable_service, "enable"),
            (compile_service_status, "status"),
        ],
    )
    def test_service_command(self, compile_fn, action, ctx: EnvironmentContext) -> None:
        result = compile_fn({"service_name": "nginx"}, ctx)
        assert result.startswith("systemctl")
        assert action in result
        assert "nginx" in result

    @pytest.mark.parametrize(
        "compile_fn, action",
        [
            (compile_start_service, "start"),
            (compile_stop_service, "stop"),
            (compile_restart_service, "restart"),
            (compile_enable_service, "enable"),
            (compile_service_status, "status"),
        ],
    )
    def test_service_with_dashes(
        self, compile_fn, action, ctx: EnvironmentContext
    ) -> None:
        result = compile_fn({"service_name": "my-custom-app"}, ctx)
        assert "my-custom-app" in result
        assert f"systemctl {action}" in result


# ===================================================================
# User Management
# ===================================================================


class TestCompileCreateUser:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_create_user({"username": "deploy"}, ctx)
        assert result.startswith("useradd")
        assert "deploy" in result
        assert "-m" in result

    def test_with_shell_and_home(self, ctx: EnvironmentContext) -> None:
        result = compile_create_user(
            {"username": "app", "shell": "/bin/zsh", "home_dir": "/opt/app"}, ctx
        )
        assert "-s" in result
        assert "/bin/zsh" in result
        assert "-d" in result
        assert "/opt/app" in result

    def test_with_groups(self, ctx: EnvironmentContext) -> None:
        result = compile_create_user(
            {"username": "webadmin", "groups": ["sudo", "www-data"]}, ctx
        )
        assert "-G" in result
        assert "sudo,www-data" in result

    def test_with_all_options(self, ctx: EnvironmentContext) -> None:
        result = compile_create_user(
            {
                "username": "svc",
                "shell": "/sbin/nologin",
                "home_dir": "/var/svc",
                "groups": ["docker", "wheel"],
            },
            ctx,
        )
        assert "-s" in result
        assert "/sbin/nologin" in result
        assert "-d" in result
        assert "/var/svc" in result
        assert "-G" in result
        assert "docker,wheel" in result
        assert "-m" in result


class TestCompileDeleteUser:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_delete_user({"username": "olduser"}, ctx)
        assert result.startswith("userdel")
        assert "olduser" in result
        assert "-r" not in result

    def test_remove_home(self, ctx: EnvironmentContext) -> None:
        result = compile_delete_user({"username": "temp", "remove_home": True}, ctx)
        assert "-r" in result

    def test_remove_home_false(self, ctx: EnvironmentContext) -> None:
        result = compile_delete_user({"username": "keep", "remove_home": False}, ctx)
        assert "-r" not in result


class TestCompileModifyUser:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_modify_user({"username": "alice"}, ctx)
        assert result.startswith("usermod")
        assert "alice" in result

    def test_add_groups(self, ctx: EnvironmentContext) -> None:
        result = compile_modify_user(
            {"username": "bob", "add_groups": ["docker", "sudo"]}, ctx
        )
        assert "-aG" in result
        assert "docker,sudo" in result

    def test_change_shell(self, ctx: EnvironmentContext) -> None:
        result = compile_modify_user(
            {"username": "carol", "shell": "/bin/fish"}, ctx
        )
        assert "-s" in result
        assert "/bin/fish" in result

    def test_change_home(self, ctx: EnvironmentContext) -> None:
        result = compile_modify_user(
            {"username": "dave", "home_dir": "/home/newdave"}, ctx
        )
        assert "-d" in result
        assert "/home/newdave" in result

    def test_multiple_modifications(self, ctx: EnvironmentContext) -> None:
        result = compile_modify_user(
            {
                "username": "eve",
                "add_groups": ["staff"],
                "shell": "/bin/zsh",
                "home_dir": "/home/eve2",
            },
            ctx,
        )
        assert "-aG" in result
        assert "-s" in result
        assert "-d" in result


# ===================================================================
# Log Operations
# ===================================================================


class TestCompileViewLogs:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_view_logs({}, ctx)
        assert result == "journalctl"

    def test_with_unit(self, ctx: EnvironmentContext) -> None:
        result = compile_view_logs({"unit": "nginx"}, ctx)
        assert "-u" in result
        assert "nginx" in result

    def test_with_since_and_until(self, ctx: EnvironmentContext) -> None:
        result = compile_view_logs(
            {"since": "2024-01-01", "until": "2024-01-31"}, ctx
        )
        assert "--since" in result
        assert "2024-01-01" in result
        assert "--until" in result
        assert "2024-01-31" in result

    def test_with_lines(self, ctx: EnvironmentContext) -> None:
        result = compile_view_logs({"lines": 100}, ctx)
        assert "-n" in result
        assert "100" in result

    def test_with_priority(self, ctx: EnvironmentContext) -> None:
        result = compile_view_logs({"priority": "err"}, ctx)
        assert "-p" in result
        assert "err" in result

    def test_all_options(self, ctx: EnvironmentContext) -> None:
        result = compile_view_logs(
            {
                "unit": "sshd",
                "since": "yesterday",
                "until": "now",
                "lines": 50,
                "priority": "warning",
            },
            ctx,
        )
        assert "-u" in result
        assert "sshd" in result
        assert "--since" in result
        assert "--until" in result
        assert "-n 50" in result
        assert "-p" in result
        assert "warning" in result


class TestCompileFollowLogs:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_follow_logs({}, ctx)
        assert result == "journalctl -f"

    def test_with_unit(self, ctx: EnvironmentContext) -> None:
        result = compile_follow_logs({"unit": "docker"}, ctx)
        assert "journalctl -f" in result
        assert "-u" in result
        assert "docker" in result


class TestCompileFilterLogs:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_filter_logs({"pattern": "error"}, ctx)
        assert "journalctl" in result
        assert "| grep" in result
        assert "error" in result

    def test_with_unit(self, ctx: EnvironmentContext) -> None:
        result = compile_filter_logs({"pattern": "timeout", "unit": "nginx"}, ctx)
        assert "-u" in result
        assert "nginx" in result
        assert "| grep" in result
        assert "timeout" in result

    def test_with_since(self, ctx: EnvironmentContext) -> None:
        result = compile_filter_logs(
            {"pattern": "fatal", "since": "1 hour ago"}, ctx
        )
        assert "--since" in result
        assert "| grep" in result
        assert "fatal" in result


# ===================================================================
# Scheduling
# ===================================================================


class TestCompileScheduleCron:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_schedule_cron(
            {"schedule": "0 2 * * *", "command": "/usr/bin/backup.sh"}, ctx
        )
        assert "crontab" in result
        assert "0 2 * * *" in result
        assert "/usr/bin/backup.sh" in result

    def test_with_user(self, ctx: EnvironmentContext) -> None:
        result = compile_schedule_cron(
            {"schedule": "*/5 * * * *", "command": "check.sh", "user": "deploy"}, ctx
        )
        assert "-u" in result
        assert "deploy" in result

    def test_appends_to_existing(self, ctx: EnvironmentContext) -> None:
        result = compile_schedule_cron(
            {"schedule": "0 0 * * *", "command": "cleanup"}, ctx
        )
        # Pattern: (crontab -l 2>/dev/null; echo '...') | crontab -
        assert "crontab" in result
        assert "-l" in result
        assert "echo" in result
        assert "| crontab" in result


class TestCompileListCron:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_list_cron({}, ctx)
        assert result == "crontab -l"

    def test_with_user(self, ctx: EnvironmentContext) -> None:
        result = compile_list_cron({"user": "www-data"}, ctx)
        assert "-u" in result
        assert "www-data" in result
        assert "-l" in result


class TestCompileRemoveCron:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_remove_cron({"job_id_or_pattern": "backup"}, ctx)
        assert "crontab" in result
        assert "grep -v" in result
        assert "backup" in result

    def test_with_user(self, ctx: EnvironmentContext) -> None:
        result = compile_remove_cron(
            {"job_id_or_pattern": "cleanup", "user": "admin"}, ctx
        )
        assert "-u" in result
        assert "admin" in result
        assert "grep -v" in result

    def test_pipes_filtered_back(self, ctx: EnvironmentContext) -> None:
        result = compile_remove_cron({"job_id_or_pattern": "old-job"}, ctx)
        # Should pipe: crontab -l | grep -v 'old-job' | crontab -
        assert "| crontab" in result
        assert "| grep -v" in result


# ===================================================================
# Networking
# ===================================================================


class TestCompileNetworkInfo:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_network_info({}, ctx)
        assert result == "ip addr show"

    def test_with_interface(self, ctx: EnvironmentContext) -> None:
        result = compile_network_info({"interface": "eth0"}, ctx)
        assert "ip addr show" in result
        assert "eth0" in result


class TestCompileTestConnectivity:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_test_connectivity({"host": "8.8.8.8"}, ctx)
        assert result.startswith("ping")
        assert "8.8.8.8" in result

    def test_with_count(self, ctx: EnvironmentContext) -> None:
        result = compile_test_connectivity({"host": "google.com", "count": 4}, ctx)
        assert "-c" in result
        assert "4" in result

    def test_with_timeout(self, ctx: EnvironmentContext) -> None:
        result = compile_test_connectivity(
            {"host": "10.0.0.1", "timeout": 5}, ctx
        )
        assert "-W" in result
        assert "5" in result

    def test_with_count_and_timeout(self, ctx: EnvironmentContext) -> None:
        result = compile_test_connectivity(
            {"host": "example.com", "count": 3, "timeout": 2}, ctx
        )
        assert "-c 3" in result
        assert "-W 2" in result


class TestCompileDownloadFile:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_download_file(
            {"url": "http://example.com/file.tar.gz"}, ctx
        )
        assert result.startswith("curl")
        assert "-L" in result  # follow_redirects defaults to True
        assert "-O" in result  # no output_path -> -O
        assert "http://example.com/file.tar.gz" in result

    def test_with_output(self, ctx: EnvironmentContext) -> None:
        result = compile_download_file(
            {"url": "http://example.com/data.json", "output_path": "/tmp/data.json"},
            ctx,
        )
        assert "-o" in result
        assert "/tmp/data.json" in result
        assert "-O" not in result

    def test_no_redirects(self, ctx: EnvironmentContext) -> None:
        result = compile_download_file(
            {"url": "http://example.com/api", "follow_redirects": False}, ctx
        )
        assert "-L" not in result


class TestCompileTransferFile:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_transfer_file(
            {"source": "/tmp/file.txt", "destination": "user@host:/remote/"}, ctx
        )
        assert result.startswith("scp")
        assert "/tmp/file.txt" in result
        assert "user@host:/remote/" in result

    def test_recursive(self, ctx: EnvironmentContext) -> None:
        result = compile_transfer_file(
            {"source": "/data", "destination": "host:/backup", "recursive": True},
            ctx,
        )
        assert "-r" in result

    def test_with_port(self, ctx: EnvironmentContext) -> None:
        result = compile_transfer_file(
            {"source": "a.txt", "destination": "host:b.txt", "port": 2222}, ctx
        )
        assert "-P" in result
        assert "2222" in result


class TestCompileSshConnect:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_ssh_connect({"host": "192.168.1.10"}, ctx)
        assert result.startswith("ssh")
        assert "192.168.1.10" in result

    def test_with_user(self, ctx: EnvironmentContext) -> None:
        result = compile_ssh_connect({"host": "server.io", "user": "deploy"}, ctx)
        assert "deploy@server.io" in result

    def test_with_port(self, ctx: EnvironmentContext) -> None:
        result = compile_ssh_connect({"host": "box", "port": 2222}, ctx)
        assert "-p" in result
        assert "2222" in result

    def test_with_key(self, ctx: EnvironmentContext) -> None:
        result = compile_ssh_connect(
            {"host": "prod", "key_file": "~/.ssh/deploy_key"}, ctx
        )
        assert "-i" in result
        assert "~/.ssh/deploy_key" in result

    def test_all_options(self, ctx: EnvironmentContext) -> None:
        result = compile_ssh_connect(
            {
                "host": "prod.example.com",
                "user": "admin",
                "port": 22222,
                "key_file": "/keys/id_ed25519",
            },
            ctx,
        )
        assert "-p 22222" in result
        assert "-i" in result
        assert "/keys/id_ed25519" in result
        assert "admin@prod.example.com" in result


class TestCompilePortCheck:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_port_check({}, ctx)
        assert result == "ss -tlnp"

    def test_with_port(self, ctx: EnvironmentContext) -> None:
        result = compile_port_check({"port": 443}, ctx)
        assert "ss -tlnp" in result
        assert "| grep :443" in result

    def test_with_port_80(self, ctx: EnvironmentContext) -> None:
        result = compile_port_check({"port": 80}, ctx)
        assert ":80" in result


# ===================================================================
# Process Management
# ===================================================================


class TestCompileProcessList:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_process_list({}, ctx)
        assert result.startswith("ps")
        assert "aux" in result

    def test_with_filter(self, ctx: EnvironmentContext) -> None:
        result = compile_process_list({"filter": "python"}, ctx)
        assert "| grep" in result
        assert "python" in result

    def test_sort_by_cpu(self, ctx: EnvironmentContext) -> None:
        result = compile_process_list({"sort_by": "cpu"}, ctx)
        assert "--sort=-%cpu" in result

    def test_sort_by_memory(self, ctx: EnvironmentContext) -> None:
        result = compile_process_list({"sort_by": "memory"}, ctx)
        assert "--sort=-%mem" in result

    def test_sort_by_pid(self, ctx: EnvironmentContext) -> None:
        result = compile_process_list({"sort_by": "pid"}, ctx)
        assert "--sort=-pid" in result

    def test_sort_by_name(self, ctx: EnvironmentContext) -> None:
        result = compile_process_list({"sort_by": "name"}, ctx)
        assert "--sort=-comm" in result

    def test_with_user(self, ctx: EnvironmentContext) -> None:
        result = compile_process_list({"user": "www-data"}, ctx)
        assert "-u" in result
        assert "www-data" in result
        assert "aux" not in result

    def test_user_with_filter(self, ctx: EnvironmentContext) -> None:
        result = compile_process_list({"user": "root", "filter": "sshd"}, ctx)
        assert "-u" in result
        assert "root" in result
        assert "| grep" in result
        assert "sshd" in result


class TestCompileKillProcess:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_kill_process({"target": "1234"}, ctx)
        assert result.startswith("kill")
        assert "1234" in result

    def test_with_signal(self, ctx: EnvironmentContext) -> None:
        result = compile_kill_process({"target": "5678", "signal": "HUP"}, ctx)
        assert "-HUP" in result

    def test_force(self, ctx: EnvironmentContext) -> None:
        result = compile_kill_process({"target": "9999", "force": True}, ctx)
        assert "-9" in result

    def test_force_overrides_signal(self, ctx: EnvironmentContext) -> None:
        # When force=True, signal is ignored in favor of -9
        result = compile_kill_process(
            {"target": "111", "signal": "TERM", "force": True}, ctx
        )
        assert "-9" in result
        assert "-TERM" not in result

    def test_no_signal(self, ctx: EnvironmentContext) -> None:
        result = compile_kill_process({"target": "42"}, ctx)
        parts = result.split()
        assert parts == ["kill", "42"]


class TestCompileSystemInfo:
    @pytest.mark.parametrize(
        "info_type, expected",
        [
            ("memory", "free -h"),
            ("cpu", "lscpu"),
            ("uptime", "uptime"),
        ],
    )
    def test_specific_types(
        self, info_type: str, expected: str, ctx: EnvironmentContext
    ) -> None:
        result = compile_system_info({"info_type": info_type}, ctx)
        assert result == expected

    def test_all(self, ctx: EnvironmentContext) -> None:
        result = compile_system_info({"info_type": "all"}, ctx)
        assert "free -h" in result
        assert "lscpu" in result
        assert "uptime" in result

    def test_default_is_all(self, ctx: EnvironmentContext) -> None:
        result = compile_system_info({}, ctx)
        assert "free -h" in result
        assert "lscpu" in result
        assert "uptime" in result

    def test_unknown_type_falls_through_to_all(self, ctx: EnvironmentContext) -> None:
        result = compile_system_info({"info_type": "bogus"}, ctx)
        assert "free -h" in result
        assert "lscpu" in result


# ===================================================================
# Disk / Mount
# ===================================================================


class TestCompileMountDevice:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_mount_device(
            {"device": "/dev/sda1", "mount_point": "/mnt/data"}, ctx
        )
        assert result.startswith("mount")
        assert "/dev/sda1" in result
        assert "/mnt/data" in result

    def test_with_type(self, ctx: EnvironmentContext) -> None:
        result = compile_mount_device(
            {"device": "/dev/sdb1", "mount_point": "/mnt/usb", "filesystem_type": "ext4"},
            ctx,
        )
        assert "-t" in result
        assert "ext4" in result

    def test_with_options(self, ctx: EnvironmentContext) -> None:
        result = compile_mount_device(
            {"device": "/dev/sdc1", "mount_point": "/mnt/x", "options": "ro,noexec"},
            ctx,
        )
        assert "-o" in result
        assert "ro,noexec" in result

    def test_with_type_and_options(self, ctx: EnvironmentContext) -> None:
        result = compile_mount_device(
            {
                "device": "/dev/nvme0n1p2",
                "mount_point": "/data",
                "filesystem_type": "xfs",
                "options": "defaults,noatime",
            },
            ctx,
        )
        assert "-t" in result
        assert "xfs" in result
        assert "-o" in result
        assert "defaults,noatime" in result


class TestCompileUnmountDevice:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_unmount_device({"mount_point": "/mnt/data"}, ctx)
        assert result.startswith("umount")
        assert "/mnt/data" in result

    def test_force(self, ctx: EnvironmentContext) -> None:
        result = compile_unmount_device({"mount_point": "/mnt/stuck", "force": True}, ctx)
        assert "-f" in result

    def test_lazy(self, ctx: EnvironmentContext) -> None:
        result = compile_unmount_device({"mount_point": "/mnt/busy", "lazy": True}, ctx)
        assert "-l" in result

    def test_force_and_lazy(self, ctx: EnvironmentContext) -> None:
        result = compile_unmount_device(
            {"mount_point": "/mnt/x", "force": True, "lazy": True}, ctx
        )
        assert "-f" in result
        assert "-l" in result

    def test_no_flags(self, ctx: EnvironmentContext) -> None:
        result = compile_unmount_device({"mount_point": "/mnt/clean"}, ctx)
        assert "-f" not in result
        assert "-l" not in result
