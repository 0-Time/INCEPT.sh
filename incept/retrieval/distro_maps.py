"""Distro-specific mapping data for packages, services, and paths.

Maps generic names to distro-specific equivalents across the two primary
distro families that INCEPT targets: ``debian`` (Debian, Ubuntu, Mint) and
``rhel`` (RHEL, CentOS, Fedora, Rocky, Alma).

Helper functions silently fall back to the ``debian`` default when the
requested distro family is unknown.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Distro family constants
# ---------------------------------------------------------------------------

_DEFAULT_FAMILY: Final[str] = "debian"
_SUPPORTED_FAMILIES: Final[frozenset[str]] = frozenset({"debian", "rhel"})

# ---------------------------------------------------------------------------
# PACKAGE_MAP — generic package name -> {distro_family: distro_package_name}
# ---------------------------------------------------------------------------

PACKAGE_MAP: Final[dict[str, dict[str, str]]] = {
    # Web / reverse-proxy
    "web_server": {"debian": "apache2", "rhel": "httpd"},
    "nginx": {"debian": "nginx", "rhel": "nginx"},
    # Databases
    "mysql_server": {"debian": "mysql-server", "rhel": "mysql-server"},
    "mysql_client": {"debian": "mysql-client", "rhel": "mysql"},
    "postgresql_server": {"debian": "postgresql", "rhel": "postgresql-server"},
    "postgresql_client": {"debian": "postgresql-client", "rhel": "postgresql"},
    "redis": {"debian": "redis-server", "rhel": "redis"},
    # Languages / runtimes
    "python3": {"debian": "python3", "rhel": "python3"},
    "python3_pip": {"debian": "python3-pip", "rhel": "python3-pip"},
    "python3_venv": {"debian": "python3-venv", "rhel": "python3-virtualenv"},
    "nodejs": {"debian": "nodejs", "rhel": "nodejs"},
    "java_jdk": {"debian": "default-jdk", "rhel": "java-17-openjdk-devel"},
    "java_jre": {"debian": "default-jre", "rhel": "java-17-openjdk"},
    # Networking / security
    "firewall": {"debian": "ufw", "rhel": "firewalld"},
    "openssh_server": {"debian": "openssh-server", "rhel": "openssh-server"},
    "openssh_client": {"debian": "openssh-client", "rhel": "openssh-clients"},
    "nfs_server": {"debian": "nfs-kernel-server", "rhel": "nfs-utils"},
    "nfs_client": {"debian": "nfs-common", "rhel": "nfs-utils"},
    "wireguard": {"debian": "wireguard", "rhel": "wireguard-tools"},
    "certbot": {"debian": "certbot", "rhel": "certbot"},
    # Monitoring / ops
    "rsyslog": {"debian": "rsyslog", "rhel": "rsyslog"},
    "logrotate": {"debian": "logrotate", "rhel": "logrotate"},
    "cron": {"debian": "cron", "rhel": "cronie"},
    "at": {"debian": "at", "rhel": "at"},
    # Containers / orchestration
    "docker": {"debian": "docker.io", "rhel": "docker-ce"},
    "podman": {"debian": "podman", "rhel": "podman"},
    # Build / dev tools
    "build_essential": {"debian": "build-essential", "rhel": "gcc gcc-c++ make"},
    "git": {"debian": "git", "rhel": "git"},
    "curl": {"debian": "curl", "rhel": "curl"},
    "wget": {"debian": "wget", "rhel": "wget"},
    "vim": {"debian": "vim", "rhel": "vim-enhanced"},
    "unzip": {"debian": "unzip", "rhel": "unzip"},
}

# ---------------------------------------------------------------------------
# SERVICE_MAP — generic service name -> {distro_family: systemd_unit_name}
# ---------------------------------------------------------------------------

SERVICE_MAP: Final[dict[str, dict[str, str]]] = {
    # Web
    "web_server": {"debian": "apache2", "rhel": "httpd"},
    "nginx": {"debian": "nginx", "rhel": "nginx"},
    # Databases
    "mysql": {"debian": "mysql", "rhel": "mysqld"},
    "postgresql": {"debian": "postgresql", "rhel": "postgresql"},
    "redis": {"debian": "redis-server", "rhel": "redis"},
    # Networking / security
    "firewall": {"debian": "ufw", "rhel": "firewalld"},
    "ssh": {"debian": "ssh", "rhel": "sshd"},
    "nfs_server": {"debian": "nfs-kernel-server", "rhel": "nfs-server"},
    "nfs_client": {"debian": "nfs-client.target", "rhel": "nfs-client.target"},
    "wireguard": {"debian": "wg-quick@wg0", "rhel": "wg-quick@wg0"},
    "networking": {"debian": "networking", "rhel": "NetworkManager"},
    "resolved": {"debian": "systemd-resolved", "rhel": "systemd-resolved"},
    # Time / scheduling
    "cron": {"debian": "cron", "rhel": "crond"},
    "at": {"debian": "atd", "rhel": "atd"},
    "ntp": {"debian": "systemd-timesyncd", "rhel": "chronyd"},
    # Logging / monitoring
    "rsyslog": {"debian": "rsyslog", "rhel": "rsyslog"},
    "journald": {"debian": "systemd-journald", "rhel": "systemd-journald"},
    # Containers
    "docker": {"debian": "docker", "rhel": "docker"},
    "podman": {"debian": "podman", "rhel": "podman"},
    "containerd": {"debian": "containerd", "rhel": "containerd"},
    # Mail
    "postfix": {"debian": "postfix", "rhel": "postfix"},
    # Misc system
    "logrotate": {"debian": "logrotate.timer", "rhel": "logrotate.timer"},
    "fstrim": {"debian": "fstrim.timer", "rhel": "fstrim.timer"},
    "swap": {"debian": "swap.target", "rhel": "swap.target"},
    "cups": {"debian": "cups", "rhel": "cups"},
}

# ---------------------------------------------------------------------------
# PATH_DEFAULTS — path category -> {distro_family: default_path}
# ---------------------------------------------------------------------------

PATH_DEFAULTS: Final[dict[str, dict[str, str]]] = {
    # Web
    "web_root": {"debian": "/var/www/html", "rhel": "/var/www/html"},
    "apache_conf": {"debian": "/etc/apache2", "rhel": "/etc/httpd"},
    "apache_sites": {"debian": "/etc/apache2/sites-available", "rhel": "/etc/httpd/conf.d"},
    "nginx_conf": {"debian": "/etc/nginx", "rhel": "/etc/nginx"},
    "nginx_sites": {"debian": "/etc/nginx/sites-available", "rhel": "/etc/nginx/conf.d"},
    # Logging
    "log_dir": {"debian": "/var/log", "rhel": "/var/log"},
    "syslog": {"debian": "/var/log/syslog", "rhel": "/var/log/messages"},
    "auth_log": {"debian": "/var/log/auth.log", "rhel": "/var/log/secure"},
    # Package management
    "apt_sources": {"debian": "/etc/apt/sources.list.d", "rhel": "/etc/yum.repos.d"},
    "pkg_cache": {"debian": "/var/cache/apt/archives", "rhel": "/var/cache/dnf"},
    # Networking
    "network_interfaces": {
        "debian": "/etc/network/interfaces",
        "rhel": "/etc/sysconfig/network-scripts",
    },
    "hosts_file": {"debian": "/etc/hosts", "rhel": "/etc/hosts"},
    "resolv_conf": {"debian": "/etc/resolv.conf", "rhel": "/etc/resolv.conf"},
    # SSH
    "ssh_config_dir": {"debian": "/etc/ssh", "rhel": "/etc/ssh"},
    "ssh_authorized_keys": {
        "debian": "/home/{user}/.ssh/authorized_keys",
        "rhel": "/home/{user}/.ssh/authorized_keys",
    },
    # Systemd
    "systemd_units": {"debian": "/etc/systemd/system", "rhel": "/etc/systemd/system"},
    "systemd_vendor_units": {
        "debian": "/usr/lib/systemd/system",
        "rhel": "/usr/lib/systemd/system",
    },
    # Cron
    "crontab_dir": {"debian": "/etc/cron.d", "rhel": "/etc/cron.d"},
    "crontab_user": {"debian": "/var/spool/cron/crontabs", "rhel": "/var/spool/cron"},
    # Misc
    "tmp_dir": {"debian": "/tmp", "rhel": "/tmp"},
    "profile_dir": {"debian": "/etc/profile.d", "rhel": "/etc/profile.d"},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _resolve_family(distro: str) -> str:
    """Normalise a distro identifier to a supported family key.

    Accepts both family names (``debian``, ``rhel``) and common distro
    identifiers (``ubuntu``, ``centos``, ``fedora``, etc.).
    Returns the canonical family key, defaulting to ``debian``.
    """
    lowered = distro.lower().strip()
    if lowered in _SUPPORTED_FAMILIES:
        return lowered
    _aliases: dict[str, str] = {
        "ubuntu": "debian",
        "mint": "debian",
        "pop": "debian",
        "kali": "debian",
        "centos": "rhel",
        "fedora": "rhel",
        "rocky": "rhel",
        "alma": "rhel",
        "almalinux": "rhel",
        "oracle": "rhel",
        "amzn": "rhel",
        "amazon": "rhel",
    }
    return _aliases.get(lowered, _DEFAULT_FAMILY)


def get_package(generic_name: str, distro: str) -> str | None:
    """Return the distro-specific package name for *generic_name*.

    Parameters
    ----------
    generic_name:
        A key from :data:`PACKAGE_MAP` (e.g. ``"web_server"``).
    distro:
        A distro family (``"debian"`` / ``"rhel"``) or a concrete distro
        identifier (``"ubuntu"``, ``"centos"``, etc.).

    Returns
    -------
    str | None
        The distro-specific package name, or ``None`` if *generic_name*
        is not in the map.
    """
    entry = PACKAGE_MAP.get(generic_name)
    if entry is None:
        return None
    family = _resolve_family(distro)
    return entry.get(family)


def get_service(generic_name: str, distro: str) -> str | None:
    """Return the distro-specific systemd service name for *generic_name*.

    Parameters
    ----------
    generic_name:
        A key from :data:`SERVICE_MAP` (e.g. ``"cron"``).
    distro:
        A distro family or concrete distro identifier.

    Returns
    -------
    str | None
        The distro-specific service unit name, or ``None`` if
        *generic_name* is not in the map.
    """
    entry = SERVICE_MAP.get(generic_name)
    if entry is None:
        return None
    family = _resolve_family(distro)
    return entry.get(family)


def get_path(category: str, distro: str, **fmt_kwargs: str) -> str | None:
    """Return the distro-specific default path for *category*.

    Some path templates contain ``{user}`` placeholders; pass ``user="bob"``
    via *fmt_kwargs* to expand them.

    Parameters
    ----------
    category:
        A key from :data:`PATH_DEFAULTS` (e.g. ``"web_root"``).
    distro:
        A distro family or concrete distro identifier.
    **fmt_kwargs:
        Optional keyword arguments used to format the path template.

    Returns
    -------
    str | None
        The resolved path, or ``None`` if *category* is not in the map.
    """
    entry = PATH_DEFAULTS.get(category)
    if entry is None:
        return None
    family = _resolve_family(distro)
    raw_path = entry.get(family)
    if raw_path is None:
        return None
    if fmt_kwargs:
        try:
            return raw_path.format(**fmt_kwargs)
        except KeyError:
            return raw_path
    return raw_path
