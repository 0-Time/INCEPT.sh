"""Tests for distro-specific mapping data.

Verifies that PACKAGE_MAP, SERVICE_MAP, and PATH_DEFAULTS contain
correct entries for all four distro families (debian, rhel, arch, suse),
and that the resolver correctly maps distro identifiers to families.
"""

from __future__ import annotations

import pytest

from incept.retrieval.distro_maps import (
    PACKAGE_MAP,
    PATH_DEFAULTS,
    SERVICE_MAP,
    _resolve_family,
    get_package,
    get_path,
    get_service,
)

# ===================================================================
# Family Resolution
# ===================================================================


class TestResolveFamily:
    """_resolve_family maps distro IDs to canonical family keys."""

    @pytest.mark.parametrize("distro", ["debian", "Debian", " debian "])
    def test_debian_canonical(self, distro: str) -> None:
        assert _resolve_family(distro) == "debian"

    @pytest.mark.parametrize("distro", ["ubuntu", "mint", "pop", "kali"])
    def test_debian_aliases(self, distro: str) -> None:
        assert _resolve_family(distro) == "debian"

    @pytest.mark.parametrize("distro", ["rhel", "RHEL"])
    def test_rhel_canonical(self, distro: str) -> None:
        assert _resolve_family(distro) == "rhel"

    @pytest.mark.parametrize(
        "distro", ["centos", "fedora", "rocky", "alma", "almalinux", "oracle", "amzn"]
    )
    def test_rhel_aliases(self, distro: str) -> None:
        assert _resolve_family(distro) == "rhel"

    @pytest.mark.parametrize("distro", ["arch", "Arch"])
    def test_arch_canonical(self, distro: str) -> None:
        assert _resolve_family(distro) == "arch"

    @pytest.mark.parametrize("distro", ["manjaro", "endeavouros", "artix"])
    def test_arch_aliases(self, distro: str) -> None:
        assert _resolve_family(distro) == "arch"

    @pytest.mark.parametrize("distro", ["suse", "SUSE"])
    def test_suse_canonical(self, distro: str) -> None:
        assert _resolve_family(distro) == "suse"

    @pytest.mark.parametrize(
        "distro", ["opensuse-leap", "opensuse-tumbleweed", "sles"]
    )
    def test_suse_aliases(self, distro: str) -> None:
        assert _resolve_family(distro) == "suse"

    @pytest.mark.parametrize("distro", ["macos", "macOS"])
    def test_macos_canonical(self, distro: str) -> None:
        assert _resolve_family(distro) == "macos"

    def test_darwin_alias(self) -> None:
        assert _resolve_family("darwin") == "macos"

    def test_unknown_defaults_to_debian(self) -> None:
        assert _resolve_family("some-unknown-distro") == "debian"


# ===================================================================
# Package Map Coverage
# ===================================================================


class TestPackageMapCoverage:
    """All PACKAGE_MAP entries have arch and suse variants."""

    def test_all_entries_have_five_families(self) -> None:
        families = {"debian", "rhel", "arch", "suse", "macos"}
        for generic_name, mapping in PACKAGE_MAP.items():
            missing = families - set(mapping.keys())
            assert not missing, (
                f"PACKAGE_MAP['{generic_name}'] missing: {missing}"
            )

    @pytest.mark.parametrize(
        "generic, family, expected",
        [
            ("web_server", "arch", "apache"),
            ("nginx", "arch", "nginx"),
            ("firewall", "arch", "ufw"),
            ("docker", "arch", "docker"),
            ("git", "arch", "git"),
            ("web_server", "suse", "apache2"),
            ("nginx", "suse", "nginx"),
            ("firewall", "suse", "firewalld"),
            ("docker", "suse", "docker"),
            ("git", "suse", "git"),
            ("nginx", "macos", "nginx"),
            ("docker", "macos", "docker"),
            ("git", "macos", "git"),
            ("web_server", "macos", "httpd"),
            ("redis", "macos", "redis"),
        ],
    )
    def test_specific_package_mappings(
        self, generic: str, family: str, expected: str
    ) -> None:
        result = get_package(generic, family)
        assert result is not None
        assert expected in result

    def test_get_package_arch_via_alias(self) -> None:
        result = get_package("nginx", "manjaro")
        assert result is not None
        assert "nginx" in result

    def test_get_package_suse_via_alias(self) -> None:
        result = get_package("nginx", "opensuse-leap")
        assert result is not None
        assert "nginx" in result

    def test_get_package_unknown_generic_returns_none(self) -> None:
        assert get_package("nonexistent-pkg", "arch") is None


# ===================================================================
# Service Map Coverage
# ===================================================================


class TestServiceMapCoverage:
    """All SERVICE_MAP entries have all five family variants."""

    def test_all_entries_have_five_families(self) -> None:
        families = {"debian", "rhel", "arch", "suse", "macos"}
        for generic_name, mapping in SERVICE_MAP.items():
            missing = families - set(mapping.keys())
            assert not missing, (
                f"SERVICE_MAP['{generic_name}'] missing: {missing}"
            )

    @pytest.mark.parametrize(
        "generic, family, expected",
        [
            ("ssh", "arch", "sshd"),
            ("cron", "arch", "cronie"),
            ("firewall", "arch", "ufw"),
            ("ssh", "suse", "sshd"),
            ("cron", "suse", "cron"),
            ("firewall", "suse", "firewalld"),
            ("nginx", "macos", "nginx"),
            ("docker", "macos", "docker"),
            ("ssh", "macos", "ssh"),
        ],
    )
    def test_specific_service_mappings(
        self, generic: str, family: str, expected: str
    ) -> None:
        result = get_service(generic, family)
        assert result is not None
        assert expected in result


# ===================================================================
# Path Defaults Coverage
# ===================================================================


class TestPathDefaultsCoverage:
    """All PATH_DEFAULTS entries have all five family variants."""

    def test_all_entries_have_five_families(self) -> None:
        families = {"debian", "rhel", "arch", "suse", "macos"}
        for category, mapping in PATH_DEFAULTS.items():
            missing = families - set(mapping.keys())
            assert not missing, (
                f"PATH_DEFAULTS['{category}'] missing: {missing}"
            )

    @pytest.mark.parametrize(
        "category, family, expected_substring",
        [
            ("syslog", "arch", "/var/log"),
            ("pkg_cache", "arch", "pacman"),
            ("apt_sources", "arch", "pacman"),
            ("syslog", "suse", "/var/log/messages"),
            ("pkg_cache", "suse", "zypp"),
            ("apt_sources", "suse", "zypp"),
        ],
    )
    def test_specific_path_mappings(
        self, category: str, family: str, expected_substring: str
    ) -> None:
        result = get_path(category, family)
        assert result is not None
        assert expected_substring in result

    def test_macos_specific_paths(self) -> None:
        result = get_path("web_root", "macos")
        assert result is not None
        assert "Library" in result or "WebServer" in result

    def test_macos_syslog_path(self) -> None:
        result = get_path("syslog", "macos")
        assert result is not None
        assert "system.log" in result

    def test_get_path_with_user_template(self) -> None:
        result = get_path("ssh_authorized_keys", "arch", user="testuser")
        assert result is not None
        assert "testuser" in result

    def test_get_path_macos_user_template(self) -> None:
        result = get_path("ssh_authorized_keys", "macos", user="testuser")
        assert result is not None
        assert "/Users/testuser" in result

    def test_get_path_unknown_category_returns_none(self) -> None:
        assert get_path("nonexistent-category", "arch") is None
