"""Distro-specific mapping data for packages, services, and paths.

Maps generic names to distro-specific equivalents across the five
distro families that INCEPT targets: ``debian`` (Debian, Ubuntu, Mint),
``rhel`` (RHEL, CentOS, Fedora, Rocky, Alma), ``arch`` (Arch, Manjaro,
EndeavourOS), ``suse`` (openSUSE Leap/Tumbleweed, SLES), and ``macos``
(macOS / Darwin, Homebrew).

Helper functions silently fall back to the ``debian`` default when the
requested distro family is unknown.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Distro family constants
# ---------------------------------------------------------------------------

_DEFAULT_FAMILY: Final[str] = "debian"
_SUPPORTED_FAMILIES: Final[frozenset[str]] = frozenset(
    {"debian", "rhel", "arch", "suse", "macos"}
)

# ---------------------------------------------------------------------------
# PACKAGE_MAP — generic package name -> {distro_family: distro_package_name}
# ---------------------------------------------------------------------------

PACKAGE_MAP: Final[dict[str, dict[str, str]]] = {
    # Web / reverse-proxy
    "web_server": {
        "debian": "apache2", "rhel": "httpd",
        "arch": "apache", "suse": "apache2", "macos": "httpd",
    },
    "nginx": {
        "debian": "nginx", "rhel": "nginx",
        "arch": "nginx", "suse": "nginx", "macos": "nginx",
    },
    # Databases
    "mysql_server": {
        "debian": "mysql-server", "rhel": "mysql-server",
        "arch": "mariadb", "suse": "mariadb", "macos": "mysql",
    },
    "mysql_client": {
        "debian": "mysql-client", "rhel": "mysql",
        "arch": "mariadb-clients", "suse": "mariadb-client", "macos": "mysql-client",
    },
    "postgresql_server": {
        "debian": "postgresql", "rhel": "postgresql-server",
        "arch": "postgresql", "suse": "postgresql-server", "macos": "postgresql",
    },
    "postgresql_client": {
        "debian": "postgresql-client", "rhel": "postgresql",
        "arch": "postgresql-libs", "suse": "postgresql", "macos": "libpq",
    },
    "redis": {
        "debian": "redis-server", "rhel": "redis",
        "arch": "redis", "suse": "redis", "macos": "redis",
    },
    # Languages / runtimes
    "python3": {
        "debian": "python3", "rhel": "python3",
        "arch": "python", "suse": "python3", "macos": "python@3",
    },
    "python3_pip": {
        "debian": "python3-pip", "rhel": "python3-pip",
        "arch": "python-pip", "suse": "python3-pip", "macos": "python@3",
    },
    "python3_venv": {
        "debian": "python3-venv", "rhel": "python3-virtualenv",
        "arch": "python-virtualenv", "suse": "python3-virtualenv", "macos": "python@3",
    },
    "nodejs": {
        "debian": "nodejs", "rhel": "nodejs",
        "arch": "nodejs", "suse": "nodejs", "macos": "node",
    },
    "java_jdk": {
        "debian": "default-jdk", "rhel": "java-17-openjdk-devel",
        "arch": "jdk-openjdk", "suse": "java-17-openjdk-devel", "macos": "openjdk",
    },
    "java_jre": {
        "debian": "default-jre", "rhel": "java-17-openjdk",
        "arch": "jre-openjdk", "suse": "java-17-openjdk", "macos": "openjdk",
    },
    # Networking / security
    "firewall": {
        "debian": "ufw", "rhel": "firewalld",
        "arch": "ufw", "suse": "firewalld", "macos": "pfctl",
    },
    "openssh_server": {
        "debian": "openssh-server", "rhel": "openssh-server",
        "arch": "openssh", "suse": "openssh", "macos": "openssh",
    },
    "openssh_client": {
        "debian": "openssh-client", "rhel": "openssh-clients",
        "arch": "openssh", "suse": "openssh", "macos": "openssh",
    },
    "nfs_server": {
        "debian": "nfs-kernel-server", "rhel": "nfs-utils",
        "arch": "nfs-utils", "suse": "nfs-kernel-server", "macos": "nfs",
    },
    "nfs_client": {
        "debian": "nfs-common", "rhel": "nfs-utils",
        "arch": "nfs-utils", "suse": "nfs-client", "macos": "nfs",
    },
    "wireguard": {
        "debian": "wireguard", "rhel": "wireguard-tools",
        "arch": "wireguard-tools", "suse": "wireguard-tools", "macos": "wireguard-tools",
    },
    "certbot": {
        "debian": "certbot", "rhel": "certbot",
        "arch": "certbot", "suse": "certbot", "macos": "certbot",
    },
    # Monitoring / ops
    "rsyslog": {
        "debian": "rsyslog", "rhel": "rsyslog",
        "arch": "rsyslog", "suse": "rsyslog", "macos": "rsyslog",
    },
    "logrotate": {
        "debian": "logrotate", "rhel": "logrotate",
        "arch": "logrotate", "suse": "logrotate", "macos": "logrotate",
    },
    "cron": {
        "debian": "cron", "rhel": "cronie",
        "arch": "cronie", "suse": "cron", "macos": "cron",
    },
    "at": {
        "debian": "at", "rhel": "at",
        "arch": "at", "suse": "at", "macos": "at",
    },
    # Containers / orchestration
    "docker": {
        "debian": "docker.io", "rhel": "docker-ce",
        "arch": "docker", "suse": "docker", "macos": "docker",
    },
    "podman": {
        "debian": "podman", "rhel": "podman",
        "arch": "podman", "suse": "podman", "macos": "podman",
    },
    # Build / dev tools
    "build_essential": {
        "debian": "build-essential", "rhel": "gcc gcc-c++ make",
        "arch": "base-devel", "suse": "gcc gcc-c++ make", "macos": "gcc",
    },
    "git": {
        "debian": "git", "rhel": "git",
        "arch": "git", "suse": "git", "macos": "git",
    },
    "curl": {
        "debian": "curl", "rhel": "curl",
        "arch": "curl", "suse": "curl", "macos": "curl",
    },
    "wget": {
        "debian": "wget", "rhel": "wget",
        "arch": "wget", "suse": "wget", "macos": "wget",
    },
    "vim": {
        "debian": "vim", "rhel": "vim-enhanced",
        "arch": "vim", "suse": "vim", "macos": "vim",
    },
    "unzip": {
        "debian": "unzip", "rhel": "unzip",
        "arch": "unzip", "suse": "unzip", "macos": "unzip",
    },
}

# ---------------------------------------------------------------------------
# SERVICE_MAP — generic service name -> {distro_family: service_unit_name}
# ---------------------------------------------------------------------------

SERVICE_MAP: Final[dict[str, dict[str, str]]] = {
    # Web
    "web_server": {
        "debian": "apache2", "rhel": "httpd",
        "arch": "httpd", "suse": "apache2", "macos": "httpd",
    },
    "nginx": {
        "debian": "nginx", "rhel": "nginx",
        "arch": "nginx", "suse": "nginx", "macos": "nginx",
    },
    # Databases
    "mysql": {
        "debian": "mysql", "rhel": "mysqld",
        "arch": "mariadb", "suse": "mariadb", "macos": "mysql",
    },
    "postgresql": {
        "debian": "postgresql", "rhel": "postgresql",
        "arch": "postgresql", "suse": "postgresql", "macos": "postgresql",
    },
    "redis": {
        "debian": "redis-server", "rhel": "redis",
        "arch": "redis", "suse": "redis", "macos": "redis",
    },
    # Networking / security
    "firewall": {
        "debian": "ufw", "rhel": "firewalld",
        "arch": "ufw", "suse": "firewalld", "macos": "pfctl",
    },
    "ssh": {
        "debian": "ssh", "rhel": "sshd",
        "arch": "sshd", "suse": "sshd", "macos": "ssh",
    },
    "nfs_server": {
        "debian": "nfs-kernel-server", "rhel": "nfs-server",
        "arch": "nfs-server", "suse": "nfs-server", "macos": "nfsd",
    },
    "nfs_client": {
        "debian": "nfs-client.target", "rhel": "nfs-client.target",
        "arch": "nfs-client.target", "suse": "nfs-client.target",
        "macos": "nfs-client",
    },
    "wireguard": {
        "debian": "wg-quick@wg0", "rhel": "wg-quick@wg0",
        "arch": "wg-quick@wg0", "suse": "wg-quick@wg0", "macos": "wireguard",
    },
    "networking": {
        "debian": "networking", "rhel": "NetworkManager",
        "arch": "NetworkManager", "suse": "NetworkManager", "macos": "network",
    },
    "resolved": {
        "debian": "systemd-resolved", "rhel": "systemd-resolved",
        "arch": "systemd-resolved", "suse": "systemd-resolved",
        "macos": "mDNSResponder",
    },
    # Time / scheduling
    "cron": {
        "debian": "cron", "rhel": "crond",
        "arch": "cronie", "suse": "cron", "macos": "cron",
    },
    "at": {
        "debian": "atd", "rhel": "atd",
        "arch": "atd", "suse": "atd", "macos": "atd",
    },
    "ntp": {
        "debian": "systemd-timesyncd", "rhel": "chronyd",
        "arch": "systemd-timesyncd", "suse": "chronyd", "macos": "timed",
    },
    # Logging / monitoring
    "rsyslog": {
        "debian": "rsyslog", "rhel": "rsyslog",
        "arch": "rsyslog", "suse": "rsyslog", "macos": "syslogd",
    },
    "journald": {
        "debian": "systemd-journald", "rhel": "systemd-journald",
        "arch": "systemd-journald", "suse": "systemd-journald",
        "macos": "asl",
    },
    # Containers
    "docker": {
        "debian": "docker", "rhel": "docker",
        "arch": "docker", "suse": "docker", "macos": "docker",
    },
    "podman": {
        "debian": "podman", "rhel": "podman",
        "arch": "podman", "suse": "podman", "macos": "podman",
    },
    "containerd": {
        "debian": "containerd", "rhel": "containerd",
        "arch": "containerd", "suse": "containerd", "macos": "containerd",
    },
    # Mail
    "postfix": {
        "debian": "postfix", "rhel": "postfix",
        "arch": "postfix", "suse": "postfix", "macos": "postfix",
    },
    # Misc system
    "logrotate": {
        "debian": "logrotate.timer", "rhel": "logrotate.timer",
        "arch": "logrotate.timer", "suse": "logrotate.timer",
        "macos": "logrotate",
    },
    "fstrim": {
        "debian": "fstrim.timer", "rhel": "fstrim.timer",
        "arch": "fstrim.timer", "suse": "fstrim.timer", "macos": "fstrim",
    },
    "swap": {
        "debian": "swap.target", "rhel": "swap.target",
        "arch": "swap.target", "suse": "swap.target", "macos": "swap",
    },
    "cups": {
        "debian": "cups", "rhel": "cups",
        "arch": "cups", "suse": "cups", "macos": "cups",
    },
}

# ---------------------------------------------------------------------------
# PATH_DEFAULTS — path category -> {distro_family: default_path}
# ---------------------------------------------------------------------------

PATH_DEFAULTS: Final[dict[str, dict[str, str]]] = {
    # Web
    "web_root": {
        "debian": "/var/www/html", "rhel": "/var/www/html",
        "arch": "/srv/http", "suse": "/srv/www/htdocs",
        "macos": "/Library/WebServer/Documents",
    },
    "apache_conf": {
        "debian": "/etc/apache2", "rhel": "/etc/httpd",
        "arch": "/etc/httpd", "suse": "/etc/apache2",
        "macos": "/usr/local/etc/httpd",
    },
    "apache_sites": {
        "debian": "/etc/apache2/sites-available", "rhel": "/etc/httpd/conf.d",
        "arch": "/etc/httpd/conf/extra", "suse": "/etc/apache2/vhosts.d",
        "macos": "/usr/local/etc/httpd/extra",
    },
    "nginx_conf": {
        "debian": "/etc/nginx", "rhel": "/etc/nginx",
        "arch": "/etc/nginx", "suse": "/etc/nginx",
        "macos": "/usr/local/etc/nginx",
    },
    "nginx_sites": {
        "debian": "/etc/nginx/sites-available", "rhel": "/etc/nginx/conf.d",
        "arch": "/etc/nginx/conf.d", "suse": "/etc/nginx/vhosts.d",
        "macos": "/usr/local/etc/nginx/servers",
    },
    # Logging
    "log_dir": {
        "debian": "/var/log", "rhel": "/var/log",
        "arch": "/var/log", "suse": "/var/log",
        "macos": "/var/log",
    },
    "syslog": {
        "debian": "/var/log/syslog", "rhel": "/var/log/messages",
        "arch": "/var/log/syslog", "suse": "/var/log/messages",
        "macos": "/var/log/system.log",
    },
    "auth_log": {
        "debian": "/var/log/auth.log", "rhel": "/var/log/secure",
        "arch": "/var/log/auth.log", "suse": "/var/log/secure",
        "macos": "/var/log/system.log",
    },
    # Package management
    "apt_sources": {
        "debian": "/etc/apt/sources.list.d", "rhel": "/etc/yum.repos.d",
        "arch": "/etc/pacman.d", "suse": "/etc/zypp/repos.d",
        "macos": "/usr/local/Homebrew",
    },
    "pkg_cache": {
        "debian": "/var/cache/apt/archives", "rhel": "/var/cache/dnf",
        "arch": "/var/cache/pacman/pkg", "suse": "/var/cache/zypp/packages",
        "macos": "~/Library/Caches/Homebrew",
    },
    # Networking
    "network_interfaces": {
        "debian": "/etc/network/interfaces",
        "rhel": "/etc/sysconfig/network-scripts",
        "arch": "/etc/systemd/network",
        "suse": "/etc/sysconfig/network",
        "macos": "/Library/Preferences/SystemConfiguration",
    },
    "hosts_file": {
        "debian": "/etc/hosts", "rhel": "/etc/hosts",
        "arch": "/etc/hosts", "suse": "/etc/hosts",
        "macos": "/etc/hosts",
    },
    "resolv_conf": {
        "debian": "/etc/resolv.conf", "rhel": "/etc/resolv.conf",
        "arch": "/etc/resolv.conf", "suse": "/etc/resolv.conf",
        "macos": "/etc/resolv.conf",
    },
    # SSH
    "ssh_config_dir": {
        "debian": "/etc/ssh", "rhel": "/etc/ssh",
        "arch": "/etc/ssh", "suse": "/etc/ssh",
        "macos": "/etc/ssh",
    },
    "ssh_authorized_keys": {
        "debian": "/home/{user}/.ssh/authorized_keys",
        "rhel": "/home/{user}/.ssh/authorized_keys",
        "arch": "/home/{user}/.ssh/authorized_keys",
        "suse": "/home/{user}/.ssh/authorized_keys",
        "macos": "/Users/{user}/.ssh/authorized_keys",
    },
    # Systemd
    "systemd_units": {
        "debian": "/etc/systemd/system", "rhel": "/etc/systemd/system",
        "arch": "/etc/systemd/system", "suse": "/etc/systemd/system",
        "macos": "/Library/LaunchDaemons",
    },
    "systemd_vendor_units": {
        "debian": "/usr/lib/systemd/system",
        "rhel": "/usr/lib/systemd/system",
        "arch": "/usr/lib/systemd/system",
        "suse": "/usr/lib/systemd/system",
        "macos": "/System/Library/LaunchDaemons",
    },
    # Cron
    "crontab_dir": {
        "debian": "/etc/cron.d", "rhel": "/etc/cron.d",
        "arch": "/etc/cron.d", "suse": "/etc/cron.d",
        "macos": "/usr/lib/cron/tabs",
    },
    "crontab_user": {
        "debian": "/var/spool/cron/crontabs", "rhel": "/var/spool/cron",
        "arch": "/var/spool/cron", "suse": "/var/spool/cron/tabs",
        "macos": "/var/at/tabs",
    },
    # Misc
    "tmp_dir": {
        "debian": "/tmp", "rhel": "/tmp",
        "arch": "/tmp", "suse": "/tmp",
        "macos": "/tmp",
    },
    "profile_dir": {
        "debian": "/etc/profile.d", "rhel": "/etc/profile.d",
        "arch": "/etc/profile.d", "suse": "/etc/profile.d",
        "macos": "/etc/profile.d",
    },
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
        "manjaro": "arch",
        "endeavouros": "arch",
        "artix": "arch",
        "garuda": "arch",
        "opensuse-leap": "suse",
        "opensuse-tumbleweed": "suse",
        "sles": "suse",
        "opensuse": "suse",
        "darwin": "macos",
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
