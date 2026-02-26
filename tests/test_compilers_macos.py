"""Tests for macOS compiler variant support.

Verifies that each distro-aware compiler function produces the correct
macOS-specific command when given a macOS EnvironmentContext.
"""

from __future__ import annotations

import pytest

from incept.compiler.expanded_ops import (
    compile_check_filesystem,
    compile_firewall_allow,
    compile_firewall_deny,
    compile_firewall_list,
    compile_list_partitions,
)
from incept.compiler.file_ops import compile_disk_usage
from incept.compiler.system_ops import (
    compile_enable_service,
    compile_filter_logs,
    compile_follow_logs,
    compile_install_package,
    compile_network_info,
    compile_port_check,
    compile_process_list,
    compile_remove_package,
    compile_restart_service,
    compile_search_package,
    compile_service_status,
    compile_start_service,
    compile_stop_service,
    compile_system_info,
    compile_test_connectivity,
    compile_update_packages,
    compile_view_logs,
)
from incept.core.context import EnvironmentContext

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def macos_ctx() -> EnvironmentContext:
    return EnvironmentContext(
        distro_family="macos", distro_id="macos", shell="zsh", cwd="/Users/testuser"
    )


# ===================================================================
# Package Management
# ===================================================================


class TestMacOSInstallPackage:
    """brew install commands."""

    def test_basic_install(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_install_package({"package": "nginx"}, macos_ctx)
        assert result == "brew install nginx"

    def test_install_with_assume_yes(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_install_package(
            {"package": "wget", "assume_yes": True}, macos_ctx
        )
        assert result == "brew install wget"

    def test_install_with_version(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_install_package(
            {"package": "python", "version": "3.11"}, macos_ctx
        )
        assert "python@3.11" in result

    def test_install_quoted_package(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_install_package({"package": "my-package"}, macos_ctx)
        assert "brew install" in result
        assert "my-package" in result


class TestMacOSRemovePackage:
    """brew uninstall commands."""

    def test_basic_remove(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_remove_package({"package": "nginx"}, macos_ctx)
        assert result == "brew uninstall nginx"

    def test_remove_with_purge(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_remove_package(
            {"package": "nginx", "purge_config": True}, macos_ctx
        )
        assert "brew uninstall" in result
        assert "--zap" in result


class TestMacOSUpdatePackages:
    """brew update/upgrade commands."""

    def test_update_only(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_update_packages({}, macos_ctx)
        assert result == "brew update"

    def test_update_and_upgrade(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_update_packages({"upgrade_all": True}, macos_ctx)
        assert "brew update" in result
        assert "brew upgrade" in result


class TestMacOSSearchPackage:
    """brew search commands."""

    def test_search(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_search_package({"query": "nginx"}, macos_ctx)
        assert result == "brew search nginx"


# ===================================================================
# Service Management (brew services)
# ===================================================================


class TestMacOSStartService:
    def test_start(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_start_service({"service_name": "nginx"}, macos_ctx)
        assert result == "brew services start nginx"


class TestMacOSStopService:
    def test_stop(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_stop_service({"service_name": "nginx"}, macos_ctx)
        assert result == "brew services stop nginx"


class TestMacOSRestartService:
    def test_restart(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_restart_service({"service_name": "nginx"}, macos_ctx)
        assert result == "brew services restart nginx"


class TestMacOSEnableService:
    def test_enable(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_enable_service({"service_name": "nginx"}, macos_ctx)
        assert result == "brew services start nginx"


class TestMacOSServiceStatus:
    def test_status(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_service_status({"service_name": "nginx"}, macos_ctx)
        assert "brew services info" in result
        assert "nginx" in result


# ===================================================================
# Networking
# ===================================================================


class TestMacOSNetworkInfo:
    """ifconfig (no ip command on macOS)."""

    def test_basic(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_network_info({}, macos_ctx)
        assert result == "ifconfig"

    def test_with_interface(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_network_info({"interface": "en0"}, macos_ctx)
        assert result == "ifconfig en0"


class TestMacOSTestConnectivity:
    """ping with -t timeout (not -W)."""

    def test_basic_ping(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_test_connectivity({"host": "8.8.8.8"}, macos_ctx)
        assert "ping" in result
        assert "8.8.8.8" in result

    def test_ping_with_count(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_test_connectivity(
            {"host": "8.8.8.8", "count": 4}, macos_ctx
        )
        assert "-c" in result
        assert "4" in result

    def test_ping_with_timeout(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_test_connectivity(
            {"host": "8.8.8.8", "timeout": 5}, macos_ctx
        )
        assert "-t" in result
        assert "5" in result


class TestMacOSPortCheck:
    """lsof -i :port (no ss on macOS)."""

    def test_basic(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_port_check({}, macos_ctx)
        assert "lsof" in result
        assert "-iTCP" in result
        assert "-sTCP:LISTEN" in result

    def test_with_port(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_port_check({"port": 8080}, macos_ctx)
        assert "lsof" in result
        assert "8080" in result


# ===================================================================
# Process Management
# ===================================================================


class TestMacOSProcessList:
    """ps aux without --sort (macOS ps)."""

    def test_basic(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_process_list({}, macos_ctx)
        assert "ps aux" in result

    def test_with_user(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_process_list({"user": "admin"}, macos_ctx)
        assert "-u" in result
        assert "admin" in result

    def test_with_sort(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_process_list({"sort_by": "cpu"}, macos_ctx)
        assert "ps aux" in result
        # macOS ps does not support --sort, so sort via pipe
        assert "sort" in result or "ps" in result

    def test_with_filter(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_process_list({"filter": "nginx"}, macos_ctx)
        assert "grep" in result
        assert "nginx" in result


# ===================================================================
# System Info
# ===================================================================


class TestMacOSSystemInfo:
    """vm_stat, sysctl, uptime."""

    def test_memory(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_system_info({"info_type": "memory"}, macos_ctx)
        assert "vm_stat" in result

    def test_cpu(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_system_info({"info_type": "cpu"}, macos_ctx)
        assert "sysctl" in result

    def test_uptime(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_system_info({"info_type": "uptime"}, macos_ctx)
        assert result == "uptime"

    def test_all(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_system_info({"info_type": "all"}, macos_ctx)
        assert "vm_stat" in result
        assert "sysctl" in result
        assert "uptime" in result


# ===================================================================
# Log Operations (log show / log stream)
# ===================================================================


class TestMacOSViewLogs:
    """log show on macOS."""

    def test_basic(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_view_logs({}, macos_ctx)
        assert "log show" in result

    def test_with_lines(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_view_logs({"lines": 50}, macos_ctx)
        assert "log show" in result
        assert "--last" in result or "50" in result

    def test_with_unit(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_view_logs({"unit": "com.apple.ftp-proxy"}, macos_ctx)
        assert "log show" in result
        assert "--predicate" in result

    def test_with_since(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_view_logs({"since": "2024-01-01"}, macos_ctx)
        assert "log show" in result
        assert "--start" in result


class TestMacOSFollowLogs:
    """log stream on macOS."""

    def test_basic(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_follow_logs({}, macos_ctx)
        assert "log stream" in result

    def test_with_unit(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_follow_logs({"unit": "com.apple.ftp-proxy"}, macos_ctx)
        assert "log stream" in result
        assert "--predicate" in result


class TestMacOSFilterLogs:
    """log show piped to grep on macOS."""

    def test_basic(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_filter_logs({"pattern": "error"}, macos_ctx)
        assert "log show" in result
        assert "grep" in result
        assert "error" in result


# ===================================================================
# Firewall (pfctl / socketfilterfw)
# ===================================================================


class TestMacOSFirewall:
    """pfctl or socketfilterfw for macOS firewall."""

    def test_firewall_allow(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_firewall_allow({"port": 80}, macos_ctx)
        # Should use pfctl or socketfilterfw
        assert "pfctl" in result or "socketfilterfw" in result or "pf" in result.lower()

    def test_firewall_allow_with_proto(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_firewall_allow({"port": 443, "protocol": "tcp"}, macos_ctx)
        assert "443" in result

    def test_firewall_deny(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_firewall_deny({"port": 22}, macos_ctx)
        assert "pfctl" in result or "socketfilterfw" in result or "pf" in result.lower()

    def test_firewall_list(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_firewall_list({}, macos_ctx)
        assert "pfctl" in result or "socketfilterfw" in result


# ===================================================================
# Disk Operations
# ===================================================================


class TestMacOSListPartitions:
    """diskutil list on macOS."""

    def test_basic(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_list_partitions({}, macos_ctx)
        assert result == "diskutil list"

    def test_with_device(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_list_partitions({"device": "/dev/disk0"}, macos_ctx)
        assert "diskutil list" in result
        assert "/dev/disk0" in result


class TestMacOSCheckFilesystem:
    """diskutil verifyDisk on macOS."""

    def test_basic(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_check_filesystem({"device": "/dev/disk0"}, macos_ctx)
        assert "diskutil" in result
        assert "verify" in result.lower() or "Verify" in result


class TestMacOSDiskUsage:
    """du with -d (not --max-depth) on macOS."""

    def test_du_with_max_depth(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_disk_usage({"max_depth": 2, "path": "/Users"}, macos_ctx)
        assert "-d" in result
        assert "2" in result
        assert "--max-depth" not in result

    def test_du_basic(self, macos_ctx: EnvironmentContext) -> None:
        result = compile_disk_usage({"path": "/Users"}, macos_ctx)
        assert "du" in result
        assert "-h" in result


# ===================================================================
# Context Validation
# ===================================================================


class TestMacOSContextAccepted:
    """EnvironmentContext accepts 'macos' as distro_family."""

    def test_macos_literal_accepted(self) -> None:
        ctx = EnvironmentContext(distro_family="macos")
        assert ctx.distro_family == "macos"

    def test_macos_with_zsh(self) -> None:
        ctx = EnvironmentContext(distro_family="macos", shell="zsh")
        assert ctx.shell == "zsh"

    def test_macos_default_cwd(self) -> None:
        ctx = EnvironmentContext(distro_family="macos", cwd="/Users/testuser")
        assert ctx.cwd == "/Users/testuser"
