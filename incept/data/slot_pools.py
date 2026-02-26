"""Realistic slot value pools for template-based training data generation."""

from __future__ import annotations

# fmt: off

# ── File system paths ────────────────────────────────────────────────────────

PATHS_COMMON: list[str] = [
    "/home/user", "/home/admin", "/home/deploy", "/var/log", "/var/www",
    "/var/www/html", "/etc", "/etc/nginx", "/etc/apache2", "/opt", "/opt/app",
    "/tmp", "/tmp/work", "/srv", "/srv/data", "/usr/local", "/usr/local/bin",
    "/backup", "/mnt/data", "/media/usb", "~/Documents", "~/Downloads",
    "~/projects", "/data", "/var/lib/mysql", "/var/lib/postgresql",
]

PATHS_LOG: list[str] = [
    "/var/log", "/var/log/syslog", "/var/log/auth.log", "/var/log/nginx",
    "/var/log/apache2", "/var/log/kern.log", "/var/log/messages",
    "/var/log/daemon.log", "/var/log/mail.log", "/var/log/dpkg.log",
    "/var/log/apt/history.log", "/var/log/mysql", "/var/log/postgresql",
]

PATHS_CONFIG: list[str] = [
    "/etc/nginx/nginx.conf", "/etc/apache2/apache2.conf", "/etc/ssh/sshd_config",
    "/etc/hosts", "/etc/fstab", "/etc/crontab", "/etc/resolv.conf",
    "/etc/hostname", "/etc/passwd", "/etc/group", "/etc/sudoers",
    "/etc/mysql/my.cnf", "/etc/postgresql/14/main/postgresql.conf",
    "/etc/redis/redis.conf", "/etc/default/grub", "~/.bashrc", "~/.profile",
    "~/.ssh/config", "/etc/systemd/system", "/etc/environment",
]

# ── File name patterns ────────────────────────────────────────────────────────

FILE_PATTERNS: list[str] = [
    "*.log", "*.txt", "*.py", "*.conf", "*.cfg", "*.json", "*.xml", "*.csv",
    "*.yaml", "*.yml", "*.sh", "*.html", "*.css", "*.js", "*.md", "*.bak",
    "*.tmp", "*.tar.gz", "*.zip", "*.sql", "*.env", "*.ini", "*.toml",
    "*.pid", "*.sock", "*.lock", "*.cache",
]

FILE_NAMES: list[str] = [
    "report.pdf", "data.csv", "config.yaml", "settings.json", "backup.tar.gz",
    "deploy.sh", "README.md", "index.html", "app.py", "main.go", "Makefile",
    "Dockerfile", "docker-compose.yml", "requirements.txt", "package.json",
    "output.log", "error.log", "access.log", "database.sql", "notes.txt",
    "script.sh", "test.py", "server.js", "style.css", "old_name.txt",
    "new_name.txt", "archive.zip", "photo.jpg", "document.docx",
]

# ── Package names (per distro family) ────────────────────────────────────────

PACKAGES_DEBIAN: list[str] = [
    "nginx", "apache2", "curl", "wget", "git", "docker.io", "nodejs",
    "python3", "python3-pip", "vim", "htop", "tree", "net-tools", "nmap",
    "openssh-server", "postgresql", "mysql-server", "redis-server", "tmux",
    "build-essential", "unzip", "jq", "certbot", "fail2ban", "ufw",
    "supervisor", "libssl-dev", "pkg-config", "imagemagick", "ffmpeg",
]

PACKAGES_RHEL: list[str] = [
    "nginx", "httpd", "curl", "wget", "git", "docker-ce", "nodejs",
    "python3", "python3-pip", "vim-enhanced", "htop", "tree", "net-tools",
    "nmap", "openssh-server", "postgresql-server", "mysql-server",
    "redis", "tmux", "gcc", "make", "unzip", "jq", "certbot", "fail2ban",
    "firewalld", "supervisor", "openssl-devel", "pkgconfig", "ImageMagick",
]

# ── Service names ─────────────────────────────────────────────────────────────

SERVICES: list[str] = [
    "nginx", "apache2", "httpd", "sshd", "ssh", "docker", "postgresql",
    "mysql", "mysqld", "redis", "redis-server", "cron", "crond",
    "NetworkManager", "systemd-resolved", "ufw", "firewalld", "fail2ban",
    "rsyslog", "ntpd", "chronyd", "postfix", "dovecot", "cups",
    "bluetooth", "avahi-daemon", "snapd", "containerd",
]

# ── User names ────────────────────────────────────────────────────────────────

USERNAMES: list[str] = [
    "deploy", "admin", "webuser", "appuser", "john", "jane", "developer",
    "testuser", "backup", "monitor", "nginx", "www-data", "postgres",
    "mysql", "redis", "git", "jenkins", "ci", "devops", "sysadmin",
]

GROUP_NAMES: list[str] = [
    "www-data", "docker", "sudo", "admin", "developers", "staff",
    "deploy", "wheel", "users", "nginx", "postgres", "mysql",
]

# ── Network values ────────────────────────────────────────────────────────────

HOSTNAMES: list[str] = [
    "server1.example.com", "db.internal", "web01.prod", "10.0.0.1",
    "192.168.1.100", "192.168.1.1", "172.16.0.10", "api.example.com",
    "backup.internal", "monitor.local", "gateway.local", "node1.cluster",
    "redis.internal", "postgres.internal", "8.8.8.8", "1.1.1.1",
]

PORTS: list[int] = [
    22, 80, 443, 3000, 3306, 5432, 6379, 8080, 8443, 9090, 27017, 5000,
    8000, 4000, 25, 587, 993, 143, 53, 1433, 11211, 2379, 9200,
]

URLS: list[str] = [
    "https://example.com/file.tar.gz", "https://releases.example.com/v1.0/app.deb",
    "https://get.docker.com", "https://raw.githubusercontent.com/user/repo/main/script.sh",
    "https://example.com/data.csv", "https://cdn.example.com/archive.zip",
    "https://example.com/image.iso", "https://mirrors.example.com/release.tar.xz",
]

# ── Search patterns ───────────────────────────────────────────────────────────

SEARCH_PATTERNS: list[str] = [
    "ERROR", "WARNING", "FATAL", "timeout", "connection refused",
    "permission denied", "not found", "404", "500", "segfault",
    "out of memory", "disk full", "TODO", "FIXME", "HACK",
    "password", "secret", "deprecated", "failed", "exception",
]

REPLACE_PAIRS: list[tuple[str, str]] = [
    ("localhost", "127.0.0.1"),
    ("http://", "https://"),
    ("foo", "bar"),
    ("old_value", "new_value"),
    ("debug", "info"),
    ("prod", "staging"),
    ("v1", "v2"),
    ("master", "main"),
    ("password123", "secure_password"),
    ("8080", "9090"),
]

# ── Permission values ─────────────────────────────────────────────────────────

PERMISSIONS: list[str] = [
    "755", "644", "700", "600", "775", "664", "750", "640",
    "+x", "+r", "+w", "-x", "u+x", "g+w", "o-r", "a+r",
]

# ── Size values ───────────────────────────────────────────────────────────────

FILE_SIZES: list[str] = [
    "10M", "50M", "100M", "500M", "1G", "5G", "10k", "100k",
]

# ── Time values ───────────────────────────────────────────────────────────────

MTIME_DAYS: list[str] = ["1", "3", "7", "14", "30", "60", "90"]

# ── Cron expressions ──────────────────────────────────────────────────────────

CRON_SCHEDULES: list[str] = [
    "0 * * * *",        # every hour
    "*/5 * * * *",      # every 5 minutes
    "0 0 * * *",        # daily at midnight
    "0 2 * * *",        # daily at 2am
    "0 0 * * 0",        # weekly on Sunday
    "0 0 1 * *",        # first of each month
    "30 6 * * 1-5",     # weekdays at 6:30am
    "0 */6 * * *",      # every 6 hours
    "0 0 * * 1",        # every Monday
    "*/15 * * * *",     # every 15 minutes
]

CRON_COMMANDS: list[str] = [
    "/opt/scripts/backup.sh", "/usr/local/bin/cleanup.sh",
    "find /tmp -mtime +7 -delete", "/opt/app/bin/rotate-logs",
    "rsync -a /data /backup/data", "/usr/bin/certbot renew",
    "systemctl restart myapp", "/opt/monitoring/check_health.sh",
]

# ── Archive formats ───────────────────────────────────────────────────────────

ARCHIVE_FORMATS: list[str] = ["tar.gz", "tar.bz2", "tar.xz", "zip", "tar"]

ARCHIVE_NAMES: list[str] = [
    "backup.tar.gz", "project.tar.gz", "logs-2024.tar.bz2",
    "release-v1.0.tar.xz", "documents.zip", "photos.zip",
    "data-export.tar.gz", "configs-backup.tar.gz", "source-code.tar.gz",
]

# ── Kill signals ──────────────────────────────────────────────────────────────

SIGNALS: list[str] = ["SIGTERM", "SIGKILL", "SIGHUP", "SIGUSR1", "9", "15"]

PROCESS_NAMES: list[str] = [
    "nginx", "apache2", "node", "python3", "java", "mysqld", "postgres",
    "redis-server", "gunicorn", "uwsgi", "celery", "pm2", "docker",
]

# ── Device paths ──────────────────────────────────────────────────────────────

DEVICES: list[str] = [
    "/dev/sda1", "/dev/sdb1", "/dev/sdc1", "/dev/nvme0n1p1",
    "/dev/vda1", "/dev/xvdf1",
]

MOUNT_POINTS: list[str] = [
    "/mnt/data", "/mnt/backup", "/mnt/usb", "/media/external",
    "/mnt/nfs", "/mnt/share",
]

FILESYSTEMS: list[str] = ["ext4", "xfs", "btrfs", "ntfs", "vfat"]

# ── Context lines ─────────────────────────────────────────────────────────────

CONTEXT_LINES: list[str] = [
    "debian bash non-root safe",
    "ubuntu bash non-root safe",
    "rhel bash non-root safe",
    "debian bash root safe",
    "ubuntu bash root safe",
    "rhel bash root safe",
    "debian zsh non-root safe",
    "ubuntu zsh non-root safe",
]

# ── Distro-specific pools ────────────────────────────────────────────────────

DISTRO_POOLS: dict[str, dict[str, list[str]]] = {
    "debian": {
        "packages": PACKAGES_DEBIAN,
        "package_manager": ["apt-get", "apt"],
        "service_manager": ["systemctl"],
        "contexts": [c for c in CONTEXT_LINES if "debian" in c or "ubuntu" in c],
    },
    "rhel": {
        "packages": PACKAGES_RHEL,
        "package_manager": ["dnf", "yum"],
        "service_manager": ["systemctl"],
        "contexts": [c for c in CONTEXT_LINES if "rhel" in c],
    },
}
# fmt: on
