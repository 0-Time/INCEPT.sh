"""Comprehensive Linux command templates for v2 training data generation.

Every template is a dict with:
  - nl: list[object] of natural language phrasings (use {placeholders})
  - cmd:   command string (use matching {placeholders})
           OR dict of {distro_family: command} for distro-specific commands
  - slots: dict[str, object] of {placeholder: list_of_values}
           OR dict of {distro_family: {placeholder: list_of_values}}

The generator reads these, expands all (nl_variant, slot_values, context)
combinations, and outputs ChatML JSONL training data.
"""

from __future__ import annotations

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                              SLOT POOLS                                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

PATHS = [
    "/home",
    "/var/log",
    "/etc",
    "/tmp",
    "/opt",
    "/usr/local",
    "/var",
    "/srv",
    "/home/user",
    "/var/www",
    "/root",
    "/usr/share",
    "/var/lib",
    "/var/tmp",
    "/home/user/projects",
    "/var/log/nginx",
    "/etc/nginx",
    "/var/cache",
]
PATHS_SHORT = ["/home", "/var/log", "/etc", "/tmp", "/opt", "/var", "/srv"]

FILE_PATTERNS = [
    "*.py",
    "*.log",
    "*.conf",
    "*.txt",
    "*.json",
    "*.yaml",
    "*.yml",
    "*.xml",
    "*.csv",
    "*.sh",
    "*.md",
    "*.html",
    "*.css",
    "*.js",
    "*.tar.gz",
    "*.bak",
    "*.sql",
    "*.env",
    "*.ini",
    "*.cfg",
]

FILES = [
    "file.txt",
    "data.csv",
    "config.yaml",
    "app.log",
    "script.sh",
    "notes.md",
    "report.pdf",
    "backup.sql",
    "output.json",
    "README.md",
    "index.html",
    "server.log",
    "error.log",
    "access.log",
    "database.db",
    "Makefile",
    "requirements.txt",
    "package.json",
    "docker-compose.yml",
    ".env",
]

FILES_TEXT = [
    "file.txt",
    "data.csv",
    "config.yaml",
    "app.log",
    "notes.md",
    "output.json",
    "server.log",
    "error.log",
    "access.log",
    "README.md",
    "requirements.txt",
]

DIRS = [
    "/var/log",
    "/etc/nginx",
    "/home/user",
    "/tmp/build",
    "/opt/app",
    "/var/www/html",
    "/home/user/projects",
    "/srv/data",
    "/var/lib/docker",
    "/usr/local/bin",
    "/backup",
    "/home/user/Documents",
]

SIZES = ["10M", "50M", "100M", "500M", "1G", "5G", "10G"]
DAYS = ["1", "3", "7", "14", "30", "60", "90"]
LINES_N = ["5", "10", "20", "50", "100"]

PERMISSIONS = ["755", "644", "700", "600", "777", "750", "640", "400"]
PERMISSION_SYMBOLIC = ["+x", "u+x", "g+w", "o-r", "a+r", "u+rw", "u+rwx"]

USERS = [
    "admin",
    "deploy",
    "webuser",
    "john",
    "jane",
    "developer",
    "backup",
    "nginx",
    "www-data",
    "postgres",
    "mysql",
    "app",
    "testuser",
    "sysadmin",
]

GROUPS = [
    "docker",
    "sudo",
    "admin",
    "developers",
    "wheel",
    "www-data",
    "staff",
    "users",
    "nginx",
    "postgres",
    "ssh",
    "adm",
]

SEARCH_PATTERNS = [
    "error",
    "ERROR",
    "warning",
    "WARNING",
    "failed",
    "timeout",
    "refused",
    "denied",
    "exception",
    "traceback",
    "fatal",
    "critical",
    "TODO",
    "FIXME",
    "deprecated",
    "null",
    "undefined",
    "404",
    "500",
    "connection",
]

REPLACE_OLD = ["foo", "hello", "old_value", "localhost", "http://", "DEBUG", "v1", "test"]
REPLACE_NEW = ["bar", "world", "new_value", "0.0.0.0", "https://", "INFO", "v2", "prod"]

PACKAGES_DEBIAN = [
    "nginx",
    "curl",
    "git",
    "vim",
    "htop",
    "wget",
    "tmux",
    "screen",
    "tree",
    "jq",
    "zip",
    "unzip",
    "rsync",
    "net-tools",
    "build-essential",
    "python3",
    "python3-pip",
    "nodejs",
    "postgresql",
    "redis-server",
    "docker.io",
    "fail2ban",
    "ufw",
    "certbot",
    "nmap",
    "strace",
    "iotop",
    "ncdu",
    "apache2",
    "mysql-server",
    "sqlite3",
    "ffmpeg",
    "imagemagick",
]

PACKAGES_RHEL = [
    "nginx",
    "curl",
    "git",
    "vim-enhanced",
    "htop",
    "wget",
    "tmux",
    "screen",
    "tree",
    "jq",
    "zip",
    "unzip",
    "rsync",
    "net-tools",
    "gcc",
    "python3",
    "python3-pip",
    "nodejs",
    "postgresql-server",
    "redis",
    "docker-ce",
    "fail2ban",
    "certbot",
    "nmap",
    "strace",
    "iotop",
    "ncdu",
    "httpd",
    "mariadb-server",
    "sqlite",
    "ffmpeg",
    "ImageMagick",
]

PACKAGES_ARCH = [
    "nginx",
    "curl",
    "git",
    "vim",
    "htop",
    "wget",
    "tmux",
    "screen",
    "tree",
    "jq",
    "zip",
    "unzip",
    "rsync",
    "net-tools",
    "base-devel",
    "python",
    "python-pip",
    "nodejs",
    "postgresql",
    "redis",
    "docker",
    "fail2ban",
    "ufw",
    "certbot",
    "nmap",
    "strace",
    "iotop",
    "ncdu",
    "apache",
    "mariadb",
    "sqlite",
    "ffmpeg",
    "imagemagick",
]

PACKAGES_SUSE = [
    "nginx",
    "curl",
    "git",
    "vim",
    "htop",
    "wget",
    "tmux",
    "screen",
    "tree",
    "jq",
    "zip",
    "unzip",
    "rsync",
    "net-tools",
    "gcc",
    "python3",
    "python3-pip",
    "nodejs",
    "postgresql",
    "redis",
    "docker",
    "fail2ban",
    "certbot",
    "nmap",
    "strace",
    "iotop",
    "ncdu",
    "apache2",
    "mariadb",
    "sqlite3",
    "ffmpeg",
    "ImageMagick",
]

PACKAGES_MACOS = [
    "nginx",
    "curl",
    "git",
    "vim",
    "htop",
    "wget",
    "tmux",
    "screen",
    "tree",
    "jq",
    "zip",
    "unzip",
    "rsync",
    "python3",
    "node",
    "postgresql",
    "redis",
    "docker",
    "nmap",
    "strace",
    "ncdu",
    "ffmpeg",
    "imagemagick",
    "go",
    "rust",
    "cmake",
    "httpd",
    "sqlite",
    "bat",
    "fd",
    "ripgrep",
]

SERVICES = [
    "nginx",
    "apache2",
    "httpd",
    "sshd",
    "docker",
    "postgresql",
    "mysql",
    "redis",
    "mongod",
    "elasticsearch",
    "rabbitmq-server",
    "memcached",
    "fail2ban",
    "cron",
    "ufw",
    "firewalld",
    "NetworkManager",
    "cups",
    "postfix",
    "dovecot",
    "named",
    "haproxy",
    "php-fpm",
    "jenkins",
]

HOSTS = [
    "192.168.1.1",
    "10.0.0.1",
    "google.com",
    "example.com",
    "server.example.com",
    "db.internal",
    "api.example.com",
    "8.8.8.8",
    "1.1.1.1",
    "github.com",
    "172.16.0.10",
]

PORTS = ["22", "80", "443", "3000", "3306", "5432", "6379", "8080", "8443", "9090", "27017"]
REMOTE_PATHS = ["user@server:/home/user/", "admin@192.168.1.10:/opt/", "deploy@prod:/var/www/"]
URLS = [
    "https://example.com/file.tar.gz",
    "https://get.docker.com",
    "https://raw.githubusercontent.com/user/repo/main/install.sh",
    "https://example.com/data.zip",
    "https://example.com/image.iso",
    "https://example.com/backup.sql.gz",
    "https://example.com/script.sh",
]

CONTAINERS = ["web", "api", "db", "redis", "nginx", "app", "worker", "proxy"]
IMAGES = [
    "nginx:latest",
    "redis:alpine",
    "postgres:15",
    "node:20",
    "python:3.12",
    "ubuntu:22.04",
    "alpine:latest",
    "mysql:8",
    "mongo:7",
    "traefik:v2",
]

GIT_BRANCHES = ["main", "develop", "feature/auth", "fix/bug-123", "release/v2"]
GIT_MESSAGES = [
    "fix login bug",
    "add user authentication",
    "update dependencies",
    "refactor database layer",
    "initial commit",
    "add tests",
    "fix typo",
]
GIT_REPOS = [
    "https://github.com/user/repo.git",
    "git@github.com:user/project.git",
    "https://github.com/org/app.git",
]

CRON_SCHEDULES = [
    ("every minute", "* * * * *"),
    ("every 5 minutes", "*/5 * * * *"),
    ("every hour", "0 * * * *"),
    ("every day at midnight", "0 0 * * *"),
    ("every day at 3am", "0 3 * * *"),
    ("every sunday at midnight", "0 0 * * 0"),
    ("every monday at 9am", "0 9 * * 1"),
    ("every weekday at 6am", "0 6 * * 1-5"),
    ("first of every month", "0 0 1 * *"),
    ("every 30 minutes", "*/30 * * * *"),
]

DEVICES = ["/dev/sda1", "/dev/sdb1", "/dev/nvme0n1p1", "/dev/vda1", "/dev/xvda1"]
MOUNT_POINTS = ["/mnt/data", "/mnt/backup", "/media/external", "/mnt/usb", "/mnt/disk"]
FILESYSTEMS = ["ext4", "xfs", "btrfs", "ntfs", "vfat"]

COLUMNS = ["1", "2", "3", "1,3", "2-4", "1-3"]
DELIMITERS = [":", ",", "\\t", ";", "|"]

ENV_VARS = ["PATH", "HOME", "LANG", "EDITOR", "TERM", "SHELL", "USER"]
ENV_VALUES = ["/usr/local/bin:$PATH", "vim", "en_US.UTF-8", "nano", "/bin/zsh"]

INTERFACES = ["eth0", "ens33", "wlan0", "enp0s3", "lo", "docker0"]

# System context lines for training
CONTEXTS = [
    # Debian/Ubuntu
    ("ubuntu 22.04 bash non-root", "debian"),
    ("ubuntu 24.04 bash non-root", "debian"),
    ("ubuntu 22.04 bash root", "debian"),
    ("ubuntu 22.04 zsh non-root", "debian"),
    ("debian 12 bash non-root", "debian"),
    ("debian 12 bash root", "debian"),
    # RHEL/CentOS/Fedora
    ("centos 7 bash non-root", "rhel"),
    ("centos 9 bash non-root", "rhel"),
    ("rhel 9 bash non-root", "rhel"),
    ("rhel 9 bash root", "rhel"),
    ("fedora 39 bash non-root", "rhel"),
    ("fedora 39 zsh non-root", "rhel"),
    # Arch
    ("arch rolling bash non-root", "arch"),
    ("arch rolling bash root", "arch"),
    ("arch rolling zsh non-root", "arch"),
    # SUSE
    ("opensuse 15.5 bash non-root", "suse"),
    ("opensuse 15.5 bash root", "suse"),
    ("sles 15 bash non-root", "suse"),
    # macOS
    ("macos 14 zsh non-root", "macos"),
    ("macos 15 zsh non-root", "macos"),
    ("macos 14 bash non-root", "macos"),
]


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           COMMAND TEMPLATES                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Each template: {nl: [...], cmd: str|dict, slots: dict[str, object]}
# When cmd is a dict, keys are distro families: debian, rhel, arch, suse, macos

TEMPLATES: list[dict] = []

# ═══════════════════════════════════════════════════════════════════════════════
# FILE SEARCH & FIND
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "find all {pat} files in {path}",
            "search for {pat} files under {path}",
            "locate {pat} files in {path}",
            "look for {pat} files in {path}",
            "show me {pat} files in {path}",
            "list all {pat} files in {path}",
            "where are the {pat} files in {path}",
            "I need to find {pat} files in {path}",
            "find {pat} files in {path}",
        ],
        "cmd": "find {path} -type f -name '{pat}'",
        "slots": {"pat": FILE_PATTERNS, "path": PATHS_SHORT},
    },
    {
        "nl": [
            "find files larger than {size} in {path}",
            "search for files bigger than {size} in {path}",
            "find large files over {size} in {path}",
            "show files that are larger than {size} in {path}",
            "which files in {path} are bigger than {size}",
            "list files over {size} in {path}",
        ],
        "cmd": "find {path} -type f -size +{size}",
        "slots": {"size": SIZES, "path": PATHS_SHORT},
    },
    {
        "nl": [
            "find files modified in the last {days} days in {path}",
            "show recently modified files in {path} from the last {days} days",
            "find files changed in the past {days} days under {path}",
            "which files in {path} were modified in the last {days} days",
            "list files in {path} modified within {days} days",
        ],
        "cmd": "find {path} -type f -mtime -{days}",
        "slots": {"days": DAYS, "path": PATHS_SHORT},
    },
    {
        "nl": [
            "find files older than {days} days in {path}",
            "show files not modified in {days} days in {path}",
            "find old files in {path} older than {days} days",
            "which files in {path} haven't been modified in {days} days",
        ],
        "cmd": "find {path} -type f -mtime +{days}",
        "slots": {"days": DAYS, "path": PATHS_SHORT},
    },
    {
        "nl": [
            "find empty files in {path}",
            "show empty files in {path}",
            "list all empty files under {path}",
            "which files in {path} are empty",
        ],
        "cmd": "find {path} -type f -empty",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "find empty directories in {path}",
            "show empty directories in {path}",
            "list empty folders under {path}",
            "which directories in {path} are empty",
        ],
        "cmd": "find {path} -type d -empty",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "find all directories in {path}",
            "list all directories under {path}",
            "show all folders in {path}",
            "find only directories in {path}",
        ],
        "cmd": "find {path} -type d",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "find all symlinks in {path}",
            "show symbolic links in {path}",
            "list all symlinks under {path}",
            "find symbolic links in {path}",
        ],
        "cmd": "find {path} -type l",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "find {pat} files larger than {size}",
            "find {pat} files that are bigger than {size}",
            "search for {pat} files over {size}",
            "show {pat} files larger than {size}",
        ],
        "cmd": "find / -type f -name '{pat}' -size +{size}",
        "slots": {"pat": FILE_PATTERNS, "size": SIZES},
    },
    {
        "nl": [
            "find files with permission {perm} in {path}",
            "show files with permissions {perm} in {path}",
            "list files in {path} that have {perm} permissions",
        ],
        "cmd": "find {path} -type f -perm {perm}",
        "slots": {"perm": PERMISSIONS, "path": PATHS_SHORT},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# FILE OPERATIONS (copy, move, delete, create, etc.)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "copy {src} to {dst}",
            "copy the file {src} to {dst}",
            "make a copy of {src} at {dst}",
            "duplicate {src} to {dst}",
            "cp {src} to {dst}",
        ],
        "cmd": "cp {src} {dst}",
        "slots": {"src": FILES, "dst": DIRS},
    },
    {
        "nl": [
            "copy {dir} recursively to {dst}",
            "copy the entire {dir} directory to {dst}",
            "copy {dir} and all its contents to {dst}",
            "recursive copy of {dir} to {dst}",
        ],
        "cmd": "cp -r {dir} {dst}",
        "slots": {"dir": DIRS[:8], "dst": DIRS[4:]},
    },
    {
        "nl": [
            "move {file} to {dst}",
            "move the file {file} to {dst}",
            "mv {file} to {dst}",
            "relocate {file} to {dst}",
        ],
        "cmd": "mv {file} {dst}",
        "slots": {"file": FILES, "dst": DIRS},
    },
    {
        "nl": [
            "rename {old} to {new}",
            "rename the file {old} to {new}",
            "change the name of {old} to {new}",
        ],
        "cmd": "mv {old} {new}",
        "slots": {"old": FILES[:10], "new": FILES[5:]},
    },
    {
        "nl": [
            "delete {file}",
            "remove {file}",
            "delete the file {file}",
            "remove the file {file}",
            "get rid of {file}",
        ],
        "cmd": "rm {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "delete the directory {dir}",
            "remove the directory {dir} and everything in it",
            "recursively delete {dir}",
            "remove {dir} and all its contents",
        ],
        "cmd": "rm -rf {dir}",
        "slots": {"dir": ["/tmp/build", "/tmp/old", "/tmp/cache", "/home/user/old_project"]},
    },
    {
        "nl": [
            "create a directory called {name}",
            "make a new directory named {name}",
            "mkdir {name}",
            "create the folder {name}",
            "create directory {name}",
        ],
        "cmd": "mkdir {name}",
        "slots": {"name": ["backup", "logs", "data", "temp", "output", "build", "dist", "src"]},
    },
    {
        "nl": [
            "create the directory {path} and all parent directories",
            "create nested directories {path}",
            "mkdir -p {path}",
            "create the full path {path}",
            "make all directories in the path {path}",
        ],
        "cmd": "mkdir -p {path}",
        "slots": {
            "path": [
                "/opt/app/data/logs",
                "/home/user/projects/new",
                "/var/lib/myapp/cache",
                "/tmp/build/output",
                "/srv/www/static/images",
            ]
        },
    },
    {
        "nl": [
            "create an empty file called {file}",
            "touch {file}",
            "create the file {file}",
            "make a new file named {file}",
            "create a blank file {file}",
        ],
        "cmd": "touch {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "create a symlink from {target} to {link}",
            "make a symbolic link {link} pointing to {target}",
            "symlink {target} as {link}",
            "create a soft link from {target} to {link}",
            "ln -s {target} {link}",
        ],
        "cmd": "ln -s {target} {link}",
        "slots": {
            "target": [
                "/opt/app/current",
                "/etc/nginx/sites-available/mysite",
                "/usr/local/bin/python3.12",
                "/var/log/app.log",
            ],
            "link": [
                "/opt/app/latest",
                "/etc/nginx/sites-enabled/mysite",
                "/usr/local/bin/python3",
                "/home/user/app.log",
            ],
        },
    },
    {
        "nl": [
            "show file info for {file}",
            "show details about {file}",
            "get file information for {file}",
            "stat {file}",
            "what are the details of {file}",
        ],
        "cmd": "stat {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "what type of file is {file}",
            "determine the file type of {file}",
            "check the type of {file}",
            "file {file}",
        ],
        "cmd": "file {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "compare {a} and {b}",
            "show differences between {a} and {b}",
            "diff {a} and {b}",
            "what's different between {a} and {b}",
        ],
        "cmd": "diff {a} {b}",
        "slots": {"a": FILES[:8], "b": FILES[4:12]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# DIRECTORY LISTING
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "list files in {path}",
            "show what's in {path}",
            "ls {path}",
            "show the contents of {path}",
            "what files are in {path}",
            "list the contents of {path}",
        ],
        "cmd": "ls {path}",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "list files in {path} with details",
            "show detailed listing of {path}",
            "ls -la {path}",
            "show all files in {path} with permissions and sizes",
            "long listing of {path}",
            "list all files including hidden ones in {path}",
        ],
        "cmd": "ls -la {path}",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "list files in {path} sorted by size",
            "show files in {path} ordered by size",
            "which are the largest files in {path}",
            "sort files by size in {path}",
        ],
        "cmd": "ls -lhS {path}",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "list files in {path} sorted by date",
            "show most recently modified files in {path}",
            "show newest files in {path}",
            "sort files by modification time in {path}",
        ],
        "cmd": "ls -lt {path}",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "show directory tree of {path}",
            "display the tree structure of {path}",
            "tree {path}",
            "show the folder structure of {path}",
        ],
        "cmd": "tree {path}",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "list only directories in {path}",
            "show only folders in {path}",
            "show just the directories in {path}",
        ],
        "cmd": "ls -d {path}/*/",
        "slots": {"path": PATHS_SHORT},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# FILE VIEWING & READING
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "show the contents of {file}",
            "display {file}",
            "cat {file}",
            "read {file}",
            "view {file}",
            "print {file}",
            "show me {file}",
            "what's in {file}",
            "output the contents of {file}",
        ],
        "cmd": "cat {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "show the first {n} lines of {file}",
            "display the top {n} lines of {file}",
            "head -{n} {file}",
            "show the beginning of {file} first {n} lines",
            "print the first {n} lines of {file}",
        ],
        "cmd": "head -n {n} {file}",
        "slots": {"n": LINES_N, "file": FILES_TEXT},
    },
    {
        "nl": [
            "show the last {n} lines of {file}",
            "display the bottom {n} lines of {file}",
            "tail -{n} {file}",
            "show the end of {file} last {n} lines",
            "print the last {n} lines of {file}",
        ],
        "cmd": "tail -n {n} {file}",
        "slots": {"n": LINES_N, "file": FILES_TEXT},
    },
    {
        "nl": [
            "follow {file} in real time",
            "tail -f {file}",
            "watch {file} for new lines",
            "monitor {file} live",
            "stream {file} as it updates",
            "show new lines added to {file} in real time",
        ],
        "cmd": "tail -f {file}",
        "slots": {
            "file": [
                "app.log",
                "server.log",
                "error.log",
                "access.log",
                "/var/log/syslog",
                "/var/log/auth.log",
                "/var/log/nginx/access.log",
            ]
        },
    },
    {
        "nl": [
            "show {file} with line numbers",
            "display {file} with line numbers",
            "cat -n {file}",
            "print {file} with numbered lines",
        ],
        "cmd": "cat -n {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "count the lines in {file}",
            "how many lines are in {file}",
            "wc -l {file}",
            "line count of {file}",
            "count lines in {file}",
        ],
        "cmd": "wc -l {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "count words in {file}",
            "how many words are in {file}",
            "word count of {file}",
        ],
        "cmd": "wc -w {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "truncate {file}",
            "empty the file {file}",
            "clear the contents of {file}",
            "make {file} empty",
            "zero out {file}",
        ],
        "cmd": "truncate -s 0 {file}",
        "slots": {"file": ["app.log", "server.log", "error.log", "access.log", "output.log"]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# TEXT SEARCH (grep)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "search for {pat} in {file}",
            "grep {pat} in {file}",
            "find {pat} in {file}",
            "look for {pat} in {file}",
            "search {file} for {pat}",
            "does {file} contain {pat}",
            "find lines with {pat} in {file}",
            "show lines matching {pat} in {file}",
        ],
        "cmd": "grep '{pat}' {file}",
        "slots": {"pat": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "search for {pat} recursively in {path}",
            "grep -r {pat} in {path}",
            "find {pat} in all files under {path}",
            "search all files in {path} for {pat}",
            "recursively search for {pat} in {path}",
            "look for {pat} in all files in {path}",
        ],
        "cmd": "grep -r '{pat}' {path}",
        "slots": {"pat": SEARCH_PATTERNS, "path": PATHS_SHORT},
    },
    {
        "nl": [
            "search for {pat} in {file} case insensitive",
            "grep -i {pat} in {file}",
            "find {pat} in {file} ignoring case",
            "case insensitive search for {pat} in {file}",
        ],
        "cmd": "grep -i '{pat}' {file}",
        "slots": {"pat": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "search for {pat} in {file} with line numbers",
            "grep -n {pat} in {file}",
            "find {pat} in {file} and show line numbers",
            "show line numbers for {pat} in {file}",
        ],
        "cmd": "grep -n '{pat}' {file}",
        "slots": {"pat": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "count how many lines match {pat} in {file}",
            "how many times does {pat} appear in {file}",
            "count occurrences of {pat} in {file}",
            "grep -c {pat} in {file}",
        ],
        "cmd": "grep -c '{pat}' {file}",
        "slots": {"pat": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "show lines that don't match {pat} in {file}",
            "exclude lines with {pat} from {file}",
            "grep -v {pat} in {file}",
            "show everything except {pat} in {file}",
            "invert grep for {pat} in {file}",
        ],
        "cmd": "grep -v '{pat}' {file}",
        "slots": {"pat": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "find files containing {pat} in {path}",
            "which files in {path} contain {pat}",
            "list files with {pat} in {path}",
            "grep -rl {pat} in {path}",
        ],
        "cmd": "grep -rl '{pat}' {path}",
        "slots": {"pat": SEARCH_PATTERNS, "path": PATHS_SHORT},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# TEXT PROCESSING (sed, awk, cut, sort, uniq, tr, etc.)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "replace {old} with {new} in {file}",
            "change {old} to {new} in {file}",
            "substitute {old} for {new} in {file}",
            "sed replace {old} with {new} in {file}",
            "find and replace {old} with {new} in {file}",
            "swap {old} for {new} in {file}",
            "I want to replace {old} with {new} in {file}",
        ],
        "cmd": "sed -i 's/{old}/{new}/g' {file}",
        "slots": {"old": REPLACE_OLD, "new": REPLACE_NEW, "file": FILES_TEXT},
    },
    {
        "nl": [
            "delete lines containing {pat} from {file}",
            "remove all lines with {pat} in {file}",
            "strip lines matching {pat} from {file}",
            "delete lines with {pat} from {file}",
        ],
        "cmd": "sed -i '/{pat}/d' {file}",
        "slots": {"pat": SEARCH_PATTERNS[:10], "file": FILES_TEXT},
    },
    {
        "nl": [
            "sort {file}",
            "sort the contents of {file}",
            "sort the lines in {file}",
            "alphabetically sort {file}",
        ],
        "cmd": "sort {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "sort {file} numerically",
            "sort {file} by number",
            "numerically sort the lines in {file}",
        ],
        "cmd": "sort -n {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "sort {file} in reverse order",
            "reverse sort {file}",
            "sort {file} descending",
        ],
        "cmd": "sort -r {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "remove duplicate lines from {file}",
            "show unique lines in {file}",
            "deduplicate {file}",
            "remove duplicates from {file}",
            "get unique lines from {file}",
        ],
        "cmd": "sort {file} | uniq",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "show only duplicate lines in {file}",
            "find duplicated lines in {file}",
            "which lines appear more than once in {file}",
        ],
        "cmd": "sort {file} | uniq -d",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "extract column {col} from {file} using {delim} as delimiter",
            "get field {col} from {file} separated by {delim}",
            "cut column {col} from {file} with delimiter {delim}",
            "show column {col} of {file} delimited by {delim}",
        ],
        "cmd": "cut -d'{delim}' -f{col} {file}",
        "slots": {"col": COLUMNS, "delim": DELIMITERS, "file": FILES_TEXT[:5]},
    },
    {
        "nl": [
            "convert lowercase to uppercase in {file}",
            "make {file} all uppercase",
            "uppercase all text in {file}",
        ],
        "cmd": "tr '[:lower:]' '[:upper:]' < {file}",
        "slots": {"file": FILES_TEXT[:5]},
    },
    {
        "nl": [
            "convert uppercase to lowercase in {file}",
            "make {file} all lowercase",
            "lowercase all text in {file}",
        ],
        "cmd": "tr '[:upper:]' '[:lower:]' < {file}",
        "slots": {"file": FILES_TEXT[:5]},
    },
    {
        "nl": [
            "delete blank lines from {file}",
            "remove empty lines from {file}",
            "strip blank lines from {file}",
        ],
        "cmd": "sed -i '/^$/d' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "reverse the lines in {file}",
            "print {file} in reverse order",
            "show {file} backwards line by line",
        ],
        "cmd": "tac {file}",
        "slots": {"file": FILES_TEXT[:5]},
    },
    {
        "nl": [
            "print column {col} from {file} using awk",
            "extract the {col} field from {file}",
            "show field {col} from {file}",
            "awk print column {col} from {file}",
        ],
        "cmd": "awk '{{print ${col}}}' {file}",
        "slots": {"col": ["1", "2", "3", "NF"], "file": FILES_TEXT[:5]},
    },
    {
        "nl": [
            "format {file} as a nice table",
            "display {file} in column format",
            "columnize {file}",
        ],
        "cmd": "column -t {file}",
        "slots": {"file": FILES_TEXT[:5]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# COMPRESSION & ARCHIVES
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "create a tar.gz archive of {dir}",
            "compress {dir} into a tar.gz",
            "tar and gzip {dir}",
            "archive {dir} as a tar.gz",
            "make a compressed archive of {dir}",
            "pack {dir} into a tar.gz file",
        ],
        "cmd": "tar czf {dir}.tar.gz {dir}",
        "slots": {
            "dir": ["backup", "logs", "data", "project", "output", "/var/log", "/home/user/docs"]
        },
    },
    {
        "nl": [
            "extract {archive}",
            "unpack {archive}",
            "decompress {archive}",
            "untar {archive}",
            "extract the archive {archive}",
            "unzip {archive}",
        ],
        "cmd": "tar xzf {archive}",
        "slots": {
            "archive": [
                "backup.tar.gz",
                "data.tar.gz",
                "logs.tar.gz",
                "archive.tar.gz",
                "release.tar.gz",
                "project.tar.gz",
            ]
        },
    },
    {
        "nl": [
            "list the contents of {archive}",
            "show what's in {archive}",
            "view the files inside {archive}",
            "list files in {archive} without extracting",
        ],
        "cmd": "tar tzf {archive}",
        "slots": {"archive": ["backup.tar.gz", "data.tar.gz", "archive.tar.gz"]},
    },
    {
        "nl": [
            "create a zip of {dir}",
            "zip {dir}",
            "compress {dir} into a zip file",
            "make a zip archive of {dir}",
        ],
        "cmd": "zip -r {dir}.zip {dir}",
        "slots": {"dir": ["backup", "logs", "data", "project", "output"]},
    },
    {
        "nl": [
            "extract {archive}",
            "unzip {archive}",
            "decompress {archive}",
        ],
        "cmd": "unzip {archive}",
        "slots": {"archive": ["data.zip", "backup.zip", "archive.zip", "files.zip"]},
    },
    {
        "nl": [
            "compress {file} with gzip",
            "gzip {file}",
            "compress {file}",
        ],
        "cmd": "gzip {file}",
        "slots": {"file": ["data.csv", "app.log", "backup.sql", "output.json", "access.log"]},
    },
    {
        "nl": [
            "decompress {file}",
            "gunzip {file}",
            "uncompress {file}",
        ],
        "cmd": "gunzip {file}",
        "slots": {"file": ["data.csv.gz", "app.log.gz", "backup.sql.gz"]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# PERMISSIONS & OWNERSHIP
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "change permissions of {file} to {perm}",
            "set {file} permissions to {perm}",
            "chmod {perm} {file}",
            "make {file} {perm}",
            "set permissions {perm} on {file}",
        ],
        "cmd": "chmod {perm} {file}",
        "slots": {"perm": PERMISSIONS, "file": FILES},
    },
    {
        "nl": [
            "make {file} executable",
            "add execute permission to {file}",
            "chmod +x {file}",
            "allow {file} to be executed",
        ],
        "cmd": "chmod +x {file}",
        "slots": {
            "file": ["script.sh", "deploy.sh", "run.sh", "install.sh", "start.sh", "build.sh"]
        },
    },
    {
        "nl": [
            "change owner of {file} to {user}",
            "set the owner of {file} to {user}",
            "chown {file} to {user}",
            "give ownership of {file} to {user}",
        ],
        "cmd": "sudo chown {user} {file}",
        "slots": {"user": USERS[:8], "file": FILES},
    },
    {
        "nl": [
            "change owner of {dir} to {user} recursively",
            "recursively chown {dir} to {user}",
            "change ownership of {dir} and everything in it to {user}",
        ],
        "cmd": "sudo chown -R {user} {dir}",
        "slots": {"user": USERS[:8], "dir": DIRS[:6]},
    },
    {
        "nl": [
            "change group of {file} to {group}",
            "set the group of {file} to {group}",
            "chgrp {file} to {group}",
        ],
        "cmd": "sudo chgrp {group} {file}",
        "slots": {"group": GROUPS[:6], "file": FILES},
    },
    {
        "nl": [
            "change permissions of {dir} recursively to {perm}",
            "recursively set permissions of {dir} to {perm}",
            "chmod -R {perm} {dir}",
        ],
        "cmd": "chmod -R {perm} {dir}",
        "slots": {"perm": PERMISSIONS[:5], "dir": DIRS[:6]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# DISK USAGE & STORAGE
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "show disk space",
            "check disk space",
            "how much disk space is used",
            "show free disk space",
            "check disk usage",
            "df -h",
            "show filesystem disk space usage",
        ],
        "cmd": "df -h",
        "slots": {},
    },
    {
        "nl": [
            "show disk usage of {path}",
            "how much space does {path} use",
            "check the size of {path}",
            "du -sh {path}",
            "what's the size of {path}",
        ],
        "cmd": "du -sh {path}",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "show disk usage of {path} sorted by size",
            "which directories in {path} use the most space",
            "sort directories in {path} by size",
            "show largest directories in {path}",
        ],
        "cmd": "du -sh {path}/* | sort -rh | head -20",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "show top disk space consumers in {path}",
            "what's using the most space in {path}",
            "largest items in {path}",
        ],
        "cmd": "du -sh {path}/* | sort -rh | head -10",
        "slots": {"path": ["/", "/home", "/var", "/opt"]},
    },
    {
        "nl": [
            "list block devices",
            "show all disks and partitions",
            "lsblk",
            "show storage devices",
            "list all disks",
        ],
        "cmd": "lsblk",
        "slots": {},
    },
    {
        "nl": [
            "show inode usage",
            "check inode usage",
            "how many inodes are used",
        ],
        "cmd": "df -i",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# PACKAGE MANAGEMENT (distro-specific)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "install {pkg}",
            "install the {pkg} package",
            "I need to install {pkg}",
            "set up {pkg}",
            "add {pkg} to the system",
            "get {pkg} installed",
            "can you install {pkg}",
            "I want to install {pkg}",
            "install {pkg} on this system",
        ],
        "cmd": {
            "debian": "sudo apt-get install -y {pkg}",
            "rhel": "sudo dnf install -y {pkg}",
            "arch": "sudo pacman -S --noconfirm {pkg}",
            "suse": "sudo zypper install -y {pkg}",
            "macos": "brew install {pkg}",
        },
        "slots": {
            "debian": {"pkg": PACKAGES_DEBIAN},
            "rhel": {"pkg": PACKAGES_RHEL},
            "arch": {"pkg": PACKAGES_ARCH},
            "suse": {"pkg": PACKAGES_SUSE},
            "macos": {"pkg": PACKAGES_MACOS},
        },
    },
    {
        "nl": [
            "remove {pkg}",
            "uninstall {pkg}",
            "remove the {pkg} package",
            "delete {pkg} from the system",
            "get rid of {pkg}",
            "I want to remove {pkg}",
            "uninstall the {pkg} package",
        ],
        "cmd": {
            "debian": "sudo apt-get remove -y {pkg}",
            "rhel": "sudo dnf remove -y {pkg}",
            "arch": "sudo pacman -R --noconfirm {pkg}",
            "suse": "sudo zypper remove -y {pkg}",
            "macos": "brew uninstall {pkg}",
        },
        "slots": {
            "debian": {"pkg": PACKAGES_DEBIAN},
            "rhel": {"pkg": PACKAGES_RHEL},
            "arch": {"pkg": PACKAGES_ARCH},
            "suse": {"pkg": PACKAGES_SUSE},
            "macos": {"pkg": PACKAGES_MACOS},
        },
    },
    {
        "nl": [
            "update all packages",
            "upgrade all packages",
            "update the system",
            "upgrade the system packages",
            "update everything",
            "run system updates",
            "apply all updates",
        ],
        "cmd": {
            "debian": "sudo apt-get update && sudo apt-get upgrade -y",
            "rhel": "sudo dnf upgrade -y",
            "arch": "sudo pacman -Syu --noconfirm",
            "suse": "sudo zypper update -y",
            "macos": "brew update && brew upgrade",
        },
        "slots": {},
    },
    {
        "nl": [
            "search for a package called {query}",
            "search for {query} in the package manager",
            "find a package named {query}",
            "is there a package called {query}",
            "look for the {query} package",
        ],
        "cmd": {
            "debian": "apt-cache search {query}",
            "rhel": "dnf search {query}",
            "arch": "pacman -Ss {query}",
            "suse": "zypper search {query}",
            "macos": "brew search {query}",
        },
        "slots": {
            "query": ["nginx", "python", "docker", "redis", "postgres", "node", "go", "rust"]
        },
    },
    {
        "nl": [
            "show info about the {pkg} package",
            "get details about {pkg}",
            "what version of {pkg} is available",
            "show package information for {pkg}",
        ],
        "cmd": {
            "debian": "apt-cache show {pkg}",
            "rhel": "dnf info {pkg}",
            "arch": "pacman -Si {pkg}",
            "suse": "zypper info {pkg}",
            "macos": "brew info {pkg}",
        },
        "slots": {"pkg": ["nginx", "python3", "docker", "redis", "git", "curl"]},
    },
    {
        "nl": [
            "list installed packages",
            "show all installed packages",
            "what packages are installed",
            "list all packages on this system",
        ],
        "cmd": {
            "debian": "dpkg -l",
            "rhel": "dnf list installed",
            "arch": "pacman -Q",
            "suse": "zypper se --installed-only",
            "macos": "brew list",
        },
        "slots": {},
    },
    {
        "nl": [
            "clean the package cache",
            "clear package cache",
            "free up package cache space",
            "clean up old packages",
        ],
        "cmd": {
            "debian": "sudo apt-get clean && sudo apt-get autoremove -y",
            "rhel": "sudo dnf clean all",
            "arch": "sudo pacman -Sc --noconfirm",
            "suse": "sudo zypper clean",
            "macos": "brew cleanup",
        },
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE MANAGEMENT (distro-specific)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "start {svc}",
            "start the {svc} service",
            "start up {svc}",
            "bring up {svc}",
            "launch {svc}",
            "I need to start {svc}",
        ],
        "cmd": {
            "debian": "sudo systemctl start {svc}",
            "rhel": "sudo systemctl start {svc}",
            "arch": "sudo systemctl start {svc}",
            "suse": "sudo systemctl start {svc}",
            "macos": "brew services start {svc}",
        },
        "slots": {"svc": SERVICES},
    },
    {
        "nl": [
            "stop {svc}",
            "stop the {svc} service",
            "shut down {svc}",
            "bring down {svc}",
            "kill the {svc} service",
            "I need to stop {svc}",
        ],
        "cmd": {
            "debian": "sudo systemctl stop {svc}",
            "rhel": "sudo systemctl stop {svc}",
            "arch": "sudo systemctl stop {svc}",
            "suse": "sudo systemctl stop {svc}",
            "macos": "brew services stop {svc}",
        },
        "slots": {"svc": SERVICES},
    },
    {
        "nl": [
            "restart {svc}",
            "restart the {svc} service",
            "bounce {svc}",
            "reload {svc}",
            "I need to restart {svc}",
        ],
        "cmd": {
            "debian": "sudo systemctl restart {svc}",
            "rhel": "sudo systemctl restart {svc}",
            "arch": "sudo systemctl restart {svc}",
            "suse": "sudo systemctl restart {svc}",
            "macos": "brew services restart {svc}",
        },
        "slots": {"svc": SERVICES},
    },
    {
        "nl": [
            "enable {svc} to start on boot",
            "enable {svc}",
            "make {svc} start automatically",
            "auto-start {svc} on boot",
            "enable {svc} at startup",
        ],
        "cmd": {
            "debian": "sudo systemctl enable {svc}",
            "rhel": "sudo systemctl enable {svc}",
            "arch": "sudo systemctl enable {svc}",
            "suse": "sudo systemctl enable {svc}",
            "macos": "brew services start {svc}",
        },
        "slots": {"svc": SERVICES},
    },
    {
        "nl": [
            "check the status of {svc}",
            "is {svc} running",
            "show the status of {svc}",
            "what's the status of {svc}",
            "check if {svc} is running",
            "status of {svc}",
        ],
        "cmd": {
            "debian": "sudo systemctl status {svc}",
            "rhel": "sudo systemctl status {svc}",
            "arch": "sudo systemctl status {svc}",
            "suse": "sudo systemctl status {svc}",
            "macos": "brew services info {svc}",
        },
        "slots": {"svc": SERVICES},
    },
    {
        "nl": [
            "list all running services",
            "show running services",
            "which services are active",
            "list active services",
        ],
        "cmd": {
            "debian": "systemctl list-units --type=service --state=running",
            "rhel": "systemctl list-units --type=service --state=running",
            "arch": "systemctl list-units --type=service --state=running",
            "suse": "systemctl list-units --type=service --state=running",
            "macos": "brew services list",
        },
        "slots": {},
    },
    {
        "nl": [
            "show logs for {svc}",
            "view {svc} logs",
            "check the logs of {svc}",
            "show recent logs for {svc}",
            "what do the {svc} logs say",
        ],
        "cmd": {
            "debian": "sudo journalctl -u {svc} --no-pager -n 50",
            "rhel": "sudo journalctl -u {svc} --no-pager -n 50",
            "arch": "sudo journalctl -u {svc} --no-pager -n 50",
            "suse": "sudo journalctl -u {svc} --no-pager -n 50",
            "macos": "log show --predicate 'process == \"{svc}\"' --last 1h",
        },
        "slots": {"svc": SERVICES[:12]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# PROCESS MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "show all running processes",
            "list all processes",
            "ps aux",
            "show processes",
            "what processes are running",
            "list running processes",
        ],
        "cmd": "ps aux",
        "slots": {},
    },
    {
        "nl": [
            "find the process named {name}",
            "search for process {name}",
            "is {name} running",
            "find the {name} process",
            "show processes matching {name}",
            "pgrep {name}",
        ],
        "cmd": "ps aux | grep {name}",
        "slots": {
            "name": [
                "nginx",
                "python",
                "node",
                "java",
                "docker",
                "postgres",
                "redis",
                "apache",
                "mysql",
            ]
        },
    },
    {
        "nl": [
            "kill process {pid}",
            "terminate process {pid}",
            "stop process {pid}",
            "end process {pid}",
            "kill PID {pid}",
        ],
        "cmd": "kill {pid}",
        "slots": {"pid": ["1234", "5678", "9012", "3456"]},
    },
    {
        "nl": [
            "force kill process {pid}",
            "kill -9 process {pid}",
            "forcefully terminate process {pid}",
            "hard kill process {pid}",
        ],
        "cmd": "kill -9 {pid}",
        "slots": {"pid": ["1234", "5678", "9012", "3456"]},
    },
    {
        "nl": [
            "kill all {name} processes",
            "kill every {name} process",
            "terminate all {name} processes",
            "stop all {name} processes",
            "killall {name}",
        ],
        "cmd": "killall {name}",
        "slots": {"name": ["python", "node", "java", "nginx", "chrome", "firefox"]},
    },
    {
        "nl": [
            "show top processes by CPU usage",
            "what's using the most CPU",
            "which process is consuming the most CPU",
            "top CPU consuming processes",
        ],
        "cmd": "ps aux --sort=-%cpu | head -10",
        "slots": {},
    },
    {
        "nl": [
            "show top processes by memory usage",
            "what's using the most memory",
            "which process is consuming the most RAM",
            "top memory consuming processes",
        ],
        "cmd": "ps aux --sort=-%mem | head -10",
        "slots": {},
    },
    {
        "nl": [
            "which process is using port {port}",
            "what's listening on port {port}",
            "find the process on port {port}",
            "show what's running on port {port}",
            "who is using port {port}",
        ],
        "cmd": "sudo lsof -i :{port}",
        "slots": {"port": PORTS},
    },
    {
        "nl": [
            "run {cmd} in the background",
            "start {cmd} in the background and keep it running",
            "nohup {cmd}",
            "run {cmd} and detach it from the terminal",
        ],
        "cmd": "nohup {cmd} &",
        "slots": {
            "cmd": [
                "python3 server.py",
                "./script.sh",
                "java -jar app.jar",
                "node server.js",
                "./run.sh",
            ]
        },
    },
    {
        "nl": [
            "watch {cmd} every {n} seconds",
            "run {cmd} repeatedly every {n} seconds",
            "keep running {cmd} every {n} seconds",
            "monitor {cmd} every {n} seconds",
        ],
        "cmd": "watch -n {n} {cmd}",
        "slots": {"cmd": ["df -h", "free -h", "ps aux", "ls -la"], "n": ["1", "2", "5", "10"]},
    },
    {
        "nl": [
            "show the process tree",
            "display process hierarchy",
            "pstree",
            "show parent-child process relationships",
        ],
        "cmd": "pstree",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# USER & GROUP MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "create a user named {user}",
            "add a new user {user}",
            "create user {user}",
            "add user {user} to the system",
            "make a new user called {user}",
        ],
        "cmd": "sudo useradd -m {user}",
        "slots": {"user": USERS},
    },
    {
        "nl": [
            "delete user {user}",
            "remove user {user}",
            "delete the user {user} and their home directory",
            "remove user {user} from the system",
        ],
        "cmd": "sudo userdel -r {user}",
        "slots": {"user": USERS},
    },
    {
        "nl": [
            "add user {user} to the {group} group",
            "put {user} in the {group} group",
            "add {user} to group {group}",
            "make {user} a member of {group}",
        ],
        "cmd": "sudo usermod -aG {group} {user}",
        "slots": {"user": USERS, "group": GROUPS},
    },
    {
        "nl": [
            "change password for {user}",
            "set password for {user}",
            "reset {user}'s password",
            "change the password of user {user}",
        ],
        "cmd": "sudo passwd {user}",
        "slots": {"user": USERS},
    },
    {
        "nl": [
            "create a group called {group}",
            "add a new group {group}",
            "create group {group}",
        ],
        "cmd": "sudo groupadd {group}",
        "slots": {"group": GROUPS},
    },
    {
        "nl": [
            "list all users",
            "show all users on the system",
            "who are the users on this system",
            "show all user accounts",
        ],
        "cmd": "cat /etc/passwd | cut -d: -f1",
        "slots": {},
    },
    {
        "nl": [
            "list all groups",
            "show all groups on the system",
            "what groups exist on this system",
        ],
        "cmd": "cat /etc/group | cut -d: -f1",
        "slots": {},
    },
    {
        "nl": [
            "show what groups {user} belongs to",
            "what groups is {user} in",
            "list groups for {user}",
            "show {user}'s groups",
        ],
        "cmd": "groups {user}",
        "slots": {"user": USERS},
    },
    {
        "nl": [
            "who am I",
            "show current user",
            "what user am I logged in as",
            "whoami",
        ],
        "cmd": "whoami",
        "slots": {},
    },
    {
        "nl": [
            "show my user info",
            "show my user ID and groups",
            "id",
            "what's my user ID",
        ],
        "cmd": "id",
        "slots": {},
    },
    {
        "nl": [
            "lock the account for {user}",
            "disable {user}'s account",
            "lock user {user}",
        ],
        "cmd": "sudo usermod -L {user}",
        "slots": {"user": USERS[:8]},
    },
    {
        "nl": [
            "unlock the account for {user}",
            "enable {user}'s account",
            "unlock user {user}",
        ],
        "cmd": "sudo usermod -U {user}",
        "slots": {"user": USERS[:8]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# NETWORK
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "show my IP address",
            "what's my IP address",
            "show network interfaces",
            "display IP configuration",
            "show IP addresses",
            "ip addr",
        ],
        "cmd": "ip addr show",
        "slots": {},
    },
    {
        "nl": [
            "ping {host}",
            "test connectivity to {host}",
            "can I reach {host}",
            "check if {host} is reachable",
            "ping {host} 4 times",
        ],
        "cmd": "ping -c 4 {host}",
        "slots": {"host": HOSTS},
    },
    {
        "nl": [
            "download {url}",
            "fetch {url}",
            "download the file at {url}",
            "get {url}",
            "save {url} to disk",
            "wget {url}",
            "curl {url}",
        ],
        "cmd": "curl -fsSLO {url}",
        "slots": {"url": URLS},
    },
    {
        "nl": [
            "download {url} and save as {file}",
            "save {url} as {file}",
            "download {url} to {file}",
            "fetch {url} and save to {file}",
        ],
        "cmd": "curl -fsSL -o {file} {url}",
        "slots": {
            "url": URLS[:4],
            "file": ["download.tar.gz", "script.sh", "data.zip", "image.iso"],
        },
    },
    {
        "nl": [
            "ssh into {host}",
            "connect to {host} via SSH",
            "ssh to {host}",
            "open an SSH connection to {host}",
            "log into {host}",
        ],
        "cmd": "ssh {host}",
        "slots": {
            "host": [
                "user@server.example.com",
                "admin@192.168.1.10",
                "root@10.0.0.1",
                "deploy@prod.example.com",
            ]
        },
    },
    {
        "nl": [
            "copy {file} to {remote}",
            "scp {file} to {remote}",
            "transfer {file} to {remote}",
            "send {file} to {remote}",
            "upload {file} to {remote}",
        ],
        "cmd": "scp {file} {remote}",
        "slots": {"file": FILES[:8], "remote": REMOTE_PATHS},
    },
    {
        "nl": [
            "sync {dir} to {remote}",
            "rsync {dir} to {remote}",
            "synchronize {dir} with {remote}",
            "mirror {dir} to {remote}",
        ],
        "cmd": "rsync -avz {dir} {remote}",
        "slots": {"dir": DIRS[:6], "remote": REMOTE_PATHS},
    },
    {
        "nl": [
            "show listening ports",
            "what ports are open",
            "list all listening ports",
            "show open ports",
            "which ports are in use",
            "show all listening sockets",
        ],
        "cmd": "ss -tlnp",
        "slots": {},
    },
    {
        "nl": [
            "show all network connections",
            "list active connections",
            "show active network connections",
            "display all socket connections",
        ],
        "cmd": "ss -tunap",
        "slots": {},
    },
    {
        "nl": [
            "lookup the DNS for {host}",
            "resolve {host}",
            "DNS lookup for {host}",
            "dig {host}",
            "what's the IP of {host}",
        ],
        "cmd": "dig {host}",
        "slots": {"host": ["google.com", "example.com", "github.com", "api.example.com"]},
    },
    {
        "nl": [
            "traceroute to {host}",
            "trace the route to {host}",
            "show the path to {host}",
            "how do packets get to {host}",
        ],
        "cmd": "traceroute {host}",
        "slots": {"host": HOSTS[:6]},
    },
    {
        "nl": [
            "show the routing table",
            "display route table",
            "show network routes",
            "list all routes",
        ],
        "cmd": "ip route show",
        "slots": {},
    },
    {
        "nl": [
            "make a GET request to {url}",
            "curl {url}",
            "fetch the content of {url}",
            "HTTP GET {url}",
        ],
        "cmd": "curl -s {url}",
        "slots": {
            "url": [
                "https://api.example.com/status",
                "https://httpbin.org/get",
                "https://example.com",
                "http://localhost:8080/health",
            ]
        },
    },
    {
        "nl": [
            "make a POST request to {url} with data {data}",
            "POST to {url} with body {data}",
            "send POST request to {url} with {data}",
            "curl POST {url} with data {data}",
        ],
        "cmd": "curl -s -X POST -H 'Content-Type: application/json' -d '{data}' {url}",
        "slots": {
            "url": [
                "https://api.example.com/users",
                "http://localhost:8080/api/data",
                "https://httpbin.org/post",
            ],
            "data": ['{"name":"test"}', '{"key":"value"}', '{"status":"active"}'],
        },
    },
    {
        "nl": [
            "check if port {port} is open on {host}",
            "test if {host} is listening on port {port}",
            "is port {port} open on {host}",
            "can I connect to {host} on port {port}",
        ],
        "cmd": "nc -zv {host} {port}",
        "slots": {"host": HOSTS[:6], "port": PORTS[:6]},
    },
    {
        "nl": [
            "show my public IP address",
            "what's my public IP",
            "what's my external IP address",
            "get my public IP",
        ],
        "cmd": "curl -s ifconfig.me",
        "slots": {},
    },
    {
        "nl": [
            "show ARP table",
            "list ARP entries",
            "display the ARP cache",
        ],
        "cmd": "ip neigh show",
        "slots": {},
    },
    {
        "nl": [
            "show network bandwidth usage",
            "monitor network traffic",
            "watch network usage",
        ],
        "cmd": "ss -s",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# FIREWALL (distro-specific)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "allow port {port}",
            "open port {port}",
            "allow traffic on port {port}",
            "open firewall port {port}",
            "allow incoming connections on port {port}",
        ],
        "cmd": {
            "debian": "sudo ufw allow {port}",
            "rhel": "sudo firewall-cmd --permanent --add-port={port}/tcp && sudo firewall-cmd --reload",
            "arch": "sudo ufw allow {port}",
            "suse": "sudo firewall-cmd --permanent --add-port={port}/tcp && sudo firewall-cmd --reload",
            "macos": "echo 'pass in proto tcp from any to any port {port}' | sudo pfctl -ef -",
        },
        "slots": {"port": PORTS},
    },
    {
        "nl": [
            "block port {port}",
            "close port {port}",
            "deny traffic on port {port}",
            "block incoming connections on port {port}",
        ],
        "cmd": {
            "debian": "sudo ufw deny {port}",
            "rhel": "sudo firewall-cmd --permanent --remove-port={port}/tcp && sudo firewall-cmd --reload",
            "arch": "sudo ufw deny {port}",
            "suse": "sudo firewall-cmd --permanent --remove-port={port}/tcp && sudo firewall-cmd --reload",
            "macos": "echo 'block in proto tcp from any to any port {port}' | sudo pfctl -ef -",
        },
        "slots": {"port": PORTS},
    },
    {
        "nl": [
            "list firewall rules",
            "show firewall rules",
            "display firewall configuration",
            "what are the firewall rules",
            "show firewall status",
        ],
        "cmd": {
            "debian": "sudo ufw status verbose",
            "rhel": "sudo firewall-cmd --list-all",
            "arch": "sudo ufw status verbose",
            "suse": "sudo firewall-cmd --list-all",
            "macos": "sudo pfctl -sr",
        },
        "slots": {},
    },
    {
        "nl": [
            "enable the firewall",
            "turn on the firewall",
            "activate the firewall",
            "start the firewall",
        ],
        "cmd": {
            "debian": "sudo ufw enable",
            "rhel": "sudo systemctl start firewalld && sudo systemctl enable firewalld",
            "arch": "sudo ufw enable",
            "suse": "sudo systemctl start firewalld && sudo systemctl enable firewalld",
            "macos": "sudo pfctl -e",
        },
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM INFO
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "show system info",
            "display system information",
            "what OS am I running",
            "show OS details",
            "uname -a",
            "show kernel version",
        ],
        "cmd": "uname -a",
        "slots": {},
    },
    {
        "nl": [
            "show the hostname",
            "what's the hostname",
            "display hostname",
            "what's the name of this machine",
        ],
        "cmd": "hostname",
        "slots": {},
    },
    {
        "nl": [
            "show system uptime",
            "how long has the system been running",
            "uptime",
            "when was the last reboot",
        ],
        "cmd": "uptime",
        "slots": {},
    },
    {
        "nl": [
            "show memory usage",
            "how much RAM is being used",
            "check memory",
            "free -h",
            "show free memory",
            "how much memory is available",
        ],
        "cmd": "free -h",
        "slots": {},
    },
    {
        "nl": [
            "show CPU info",
            "how many CPUs do I have",
            "display CPU information",
            "what CPU is this machine using",
            "show processor info",
        ],
        "cmd": "lscpu",
        "slots": {},
    },
    {
        "nl": [
            "who is logged in",
            "show logged in users",
            "who's on the system",
            "list active users",
        ],
        "cmd": "w",
        "slots": {},
    },
    {
        "nl": [
            "show the current date and time",
            "what time is it",
            "what's today's date",
            "show the date",
            "display current date and time",
        ],
        "cmd": "date",
        "slots": {},
    },
    {
        "nl": [
            "show the calendar",
            "display this month's calendar",
            "cal",
            "show a calendar",
        ],
        "cmd": "cal",
        "slots": {},
    },
    {
        "nl": [
            "show kernel messages",
            "display dmesg",
            "show boot messages",
            "check kernel log",
            "show recent kernel messages",
        ],
        "cmd": "dmesg | tail -50",
        "slots": {},
    },
    {
        "nl": [
            "set the timezone to {tz}",
            "change timezone to {tz}",
            "configure timezone as {tz}",
        ],
        "cmd": "sudo timedatectl set-timezone {tz}",
        "slots": {
            "tz": [
                "UTC",
                "America/New_York",
                "Europe/London",
                "Asia/Tokyo",
                "America/Los_Angeles",
                "America/Chicago",
                "Europe/Berlin",
            ]
        },
    },
    {
        "nl": [
            "show the timezone",
            "what timezone is this system in",
            "display current timezone",
        ],
        "cmd": "timedatectl",
        "slots": {},
    },
    {
        "nl": [
            "reboot the system",
            "restart the server",
            "reboot now",
            "restart this machine",
        ],
        "cmd": "sudo reboot",
        "slots": {},
    },
    {
        "nl": [
            "shut down the system",
            "power off the server",
            "shutdown now",
            "turn off this machine",
        ],
        "cmd": "sudo shutdown -h now",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# DOCKER
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "run a {image} container",
            "start a {image} container",
            "docker run {image}",
            "spin up a {image} container",
            "launch {image} in docker",
        ],
        "cmd": "docker run -d {image}",
        "slots": {"image": IMAGES},
    },
    {
        "nl": [
            "run {image} with port {port} mapped",
            "start {image} and expose port {port}",
            "run {image} on port {port}",
            "docker run {image} with port mapping {port}",
        ],
        "cmd": "docker run -d -p {port}:{port} {image}",
        "slots": {"image": IMAGES[:6], "port": ["80", "443", "8080", "3000", "5432", "6379"]},
    },
    {
        "nl": [
            "run {image} with name {name}",
            "start a {image} container named {name}",
            "launch {image} as {name}",
        ],
        "cmd": "docker run -d --name {name} {image}",
        "slots": {"image": IMAGES[:6], "name": CONTAINERS},
    },
    {
        "nl": [
            "list running containers",
            "show docker containers",
            "docker ps",
            "what containers are running",
            "show running docker containers",
        ],
        "cmd": "docker ps",
        "slots": {},
    },
    {
        "nl": [
            "list all containers including stopped",
            "show all docker containers",
            "docker ps -a",
            "show stopped containers too",
        ],
        "cmd": "docker ps -a",
        "slots": {},
    },
    {
        "nl": [
            "stop the {name} container",
            "docker stop {name}",
            "stop container {name}",
            "shut down the {name} container",
        ],
        "cmd": "docker stop {name}",
        "slots": {"name": CONTAINERS},
    },
    {
        "nl": [
            "remove the {name} container",
            "docker rm {name}",
            "delete container {name}",
            "remove container {name}",
        ],
        "cmd": "docker rm {name}",
        "slots": {"name": CONTAINERS},
    },
    {
        "nl": [
            "show logs for {name} container",
            "docker logs {name}",
            "view {name} container logs",
            "check logs of {name}",
        ],
        "cmd": "docker logs {name}",
        "slots": {"name": CONTAINERS},
    },
    {
        "nl": [
            "follow logs for {name} container",
            "stream {name} container logs",
            "tail {name} docker logs",
        ],
        "cmd": "docker logs -f {name}",
        "slots": {"name": CONTAINERS},
    },
    {
        "nl": [
            "exec into the {name} container",
            "get a shell in {name} container",
            "open a bash shell in {name}",
            "docker exec into {name}",
            "enter the {name} container",
        ],
        "cmd": "docker exec -it {name} /bin/bash",
        "slots": {"name": CONTAINERS},
    },
    {
        "nl": [
            "build a docker image from the current directory",
            "docker build the current directory",
            "build docker image tagged {tag}",
            "create a docker image tagged {tag}",
        ],
        "cmd": "docker build -t {tag} .",
        "slots": {"tag": ["myapp:latest", "web:v1", "api:latest", "app:dev"]},
    },
    {
        "nl": [
            "list docker images",
            "show all docker images",
            "docker images",
            "what images are available",
        ],
        "cmd": "docker images",
        "slots": {},
    },
    {
        "nl": [
            "pull the {image} image",
            "download {image}",
            "docker pull {image}",
        ],
        "cmd": "docker pull {image}",
        "slots": {"image": IMAGES},
    },
    {
        "nl": [
            "remove the {image} image",
            "delete docker image {image}",
            "docker rmi {image}",
        ],
        "cmd": "docker rmi {image}",
        "slots": {"image": IMAGES[:6]},
    },
    {
        "nl": [
            "start docker compose",
            "docker compose up",
            "bring up docker compose services",
            "start all services with docker compose",
        ],
        "cmd": "docker compose up -d",
        "slots": {},
    },
    {
        "nl": [
            "stop docker compose",
            "docker compose down",
            "bring down docker compose services",
            "stop all docker compose services",
        ],
        "cmd": "docker compose down",
        "slots": {},
    },
    {
        "nl": [
            "remove all stopped containers",
            "clean up stopped docker containers",
            "docker container prune",
            "delete all stopped containers",
        ],
        "cmd": "docker container prune -f",
        "slots": {},
    },
    {
        "nl": [
            "remove all unused docker images",
            "clean up unused images",
            "docker image prune",
            "delete dangling images",
        ],
        "cmd": "docker image prune -f",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# GIT
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "clone {repo}",
            "git clone {repo}",
            "clone the repository {repo}",
            "download {repo}",
        ],
        "cmd": "git clone {repo}",
        "slots": {"repo": GIT_REPOS},
    },
    {
        "nl": [
            "show git status",
            "git status",
            "what's the status of the repo",
            "check git status",
            "show modified files",
        ],
        "cmd": "git status",
        "slots": {},
    },
    {
        "nl": [
            "add all files to git",
            "stage all changes",
            "git add everything",
            "add all changes to staging",
        ],
        "cmd": "git add -A",
        "slots": {},
    },
    {
        "nl": [
            "add {file} to git",
            "stage {file}",
            "git add {file}",
        ],
        "cmd": "git add {file}",
        "slots": {"file": FILES[:8]},
    },
    {
        "nl": [
            "commit with message {msg}",
            "git commit -m {msg}",
            "make a commit: {msg}",
            "commit changes with message {msg}",
        ],
        "cmd": "git commit -m '{msg}'",
        "slots": {"msg": GIT_MESSAGES},
    },
    {
        "nl": [
            "push to remote",
            "git push",
            "push changes to origin",
            "push to the remote repository",
        ],
        "cmd": "git push",
        "slots": {},
    },
    {
        "nl": [
            "push to {branch}",
            "git push origin {branch}",
            "push the {branch} branch",
        ],
        "cmd": "git push origin {branch}",
        "slots": {"branch": GIT_BRANCHES},
    },
    {
        "nl": [
            "pull latest changes",
            "git pull",
            "pull from remote",
            "update the repo",
            "get latest changes",
        ],
        "cmd": "git pull",
        "slots": {},
    },
    {
        "nl": [
            "create a new branch called {branch}",
            "make a new branch {branch}",
            "create branch {branch}",
        ],
        "cmd": "git checkout -b {branch}",
        "slots": {"branch": GIT_BRANCHES[1:]},
    },
    {
        "nl": [
            "switch to branch {branch}",
            "checkout {branch}",
            "go to branch {branch}",
            "change to the {branch} branch",
        ],
        "cmd": "git checkout {branch}",
        "slots": {"branch": GIT_BRANCHES},
    },
    {
        "nl": [
            "show git log",
            "show commit history",
            "git log",
            "show recent commits",
            "display commit history",
        ],
        "cmd": "git log --oneline -20",
        "slots": {},
    },
    {
        "nl": [
            "show the diff",
            "git diff",
            "show what changed",
            "show unstaged changes",
        ],
        "cmd": "git diff",
        "slots": {},
    },
    {
        "nl": [
            "stash my changes",
            "git stash",
            "save changes for later",
            "temporarily save my work",
        ],
        "cmd": "git stash",
        "slots": {},
    },
    {
        "nl": [
            "apply stashed changes",
            "git stash pop",
            "restore stashed changes",
            "get back my stashed work",
        ],
        "cmd": "git stash pop",
        "slots": {},
    },
    {
        "nl": [
            "list all branches",
            "show branches",
            "git branch",
            "what branches exist",
        ],
        "cmd": "git branch -a",
        "slots": {},
    },
    {
        "nl": [
            "merge {branch} into current branch",
            "git merge {branch}",
            "merge the {branch} branch",
        ],
        "cmd": "git merge {branch}",
        "slots": {"branch": GIT_BRANCHES},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# SSH & SECURITY
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "generate an SSH key",
            "create a new SSH key pair",
            "generate SSH keys",
            "create SSH key",
            "ssh-keygen",
        ],
        "cmd": "ssh-keygen -t ed25519",
        "slots": {},
    },
    {
        "nl": [
            "copy my SSH key to {host}",
            "send my SSH key to {host}",
            "install my SSH key on {host}",
            "ssh-copy-id to {host}",
        ],
        "cmd": "ssh-copy-id {host}",
        "slots": {
            "host": [
                "user@server.example.com",
                "admin@192.168.1.10",
                "root@10.0.0.1",
                "deploy@prod.example.com",
            ]
        },
    },
    {
        "nl": [
            "show the MD5 hash of {file}",
            "calculate MD5 checksum of {file}",
            "md5sum {file}",
            "get the MD5 of {file}",
        ],
        "cmd": "md5sum {file}",
        "slots": {"file": FILES[:8]},
    },
    {
        "nl": [
            "show the SHA256 hash of {file}",
            "calculate SHA256 checksum of {file}",
            "sha256sum {file}",
            "get the SHA256 of {file}",
        ],
        "cmd": "sha256sum {file}",
        "slots": {"file": FILES[:8]},
    },
    {
        "nl": [
            "base64 encode {file}",
            "encode {file} in base64",
            "convert {file} to base64",
        ],
        "cmd": "base64 {file}",
        "slots": {"file": FILES[:5]},
    },
    {
        "nl": [
            "base64 decode {file}",
            "decode {file} from base64",
        ],
        "cmd": "base64 -d {file}",
        "slots": {"file": ["encoded.txt", "data.b64", "token.txt"]},
    },
    {
        "nl": [
            "generate a random password",
            "create a random password",
            "make a random password",
            "generate a secure password",
        ],
        "cmd": "openssl rand -base64 32",
        "slots": {},
    },
    {
        "nl": [
            "check the SSL certificate for {host}",
            "show SSL certificate info for {host}",
            "what SSL certificate does {host} have",
            "inspect the certificate of {host}",
        ],
        "cmd": "openssl s_client -connect {host}:443 -servername {host} 2>/dev/null | openssl x509 -noout -subject -dates",
        "slots": {"host": ["google.com", "example.com", "github.com"]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# CRON & SCHEDULING
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "list my cron jobs",
            "show my crontab",
            "crontab -l",
            "what cron jobs do I have",
            "list scheduled tasks",
        ],
        "cmd": "crontab -l",
        "slots": {},
    },
    {
        "nl": [
            "edit my crontab",
            "open the crontab editor",
            "crontab -e",
            "modify my cron jobs",
        ],
        "cmd": "crontab -e",
        "slots": {},
    },
    {
        "nl": [
            "remove all my cron jobs",
            "delete all cron jobs",
            "clear my crontab",
        ],
        "cmd": "crontab -r",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT & SHELL
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "set environment variable {var} to {val}",
            "export {var}={val}",
            "set {var} to {val}",
            "create environment variable {var} with value {val}",
        ],
        "cmd": "export {var}={val}",
        "slots": {
            "var": ["MY_VAR", "APP_ENV", "DATABASE_URL", "API_KEY", "NODE_ENV", "DEBUG"],
            "val": ["production", "development", "true", "false", "localhost:5432", "1"],
        },
    },
    {
        "nl": [
            "show all environment variables",
            "list environment variables",
            "display env vars",
            "env",
            "printenv",
        ],
        "cmd": "env",
        "slots": {},
    },
    {
        "nl": [
            "show the value of {var}",
            "what is {var} set to",
            "print the value of {var}",
            "echo ${var}",
        ],
        "cmd": "echo ${var}",
        "slots": {"var": ENV_VARS},
    },
    {
        "nl": [
            "show my PATH",
            "what's in my PATH",
            "display the PATH variable",
            "list PATH directories",
        ],
        "cmd": "echo $PATH | tr ':' '\\n'",
        "slots": {},
    },
    {
        "nl": [
            "add {path} to PATH",
            "include {path} in PATH",
            "append {path} to my PATH",
        ],
        "cmd": "export PATH=$PATH:{path}",
        "slots": {"path": ["/usr/local/bin", "/opt/bin", "$HOME/bin", "$HOME/.local/bin"]},
    },
    {
        "nl": [
            "create an alias {name} for {cmd}",
            "alias {name} to {cmd}",
            "make {name} an alias for {cmd}",
        ],
        "cmd": "alias {name}='{cmd}'",
        "slots": {
            "name": ["ll", "la", "gs", "gp", "dc"],
            "cmd": ["ls -la", "ls -la", "git status", "git push", "docker compose"],
        },
    },
    {
        "nl": [
            "show command history",
            "display my command history",
            "history",
            "show recent commands",
            "what commands have I run",
        ],
        "cmd": "history",
        "slots": {},
    },
    {
        "nl": [
            "where is {cmd}",
            "which {cmd}",
            "find the location of {cmd}",
            "where is the {cmd} binary",
        ],
        "cmd": "which {cmd}",
        "slots": {"cmd": ["python3", "node", "git", "docker", "nginx", "curl", "vim", "gcc"]},
    },
    {
        "nl": [
            "reload shell configuration",
            "source bashrc",
            "reload bashrc",
            "apply shell config changes",
        ],
        "cmd": "source ~/.bashrc",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# DISK MOUNT/UNMOUNT
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "mount {dev} to {mnt}",
            "mount device {dev} at {mnt}",
            "attach {dev} to {mnt}",
            "mount {dev} on {mnt}",
        ],
        "cmd": "sudo mount {dev} {mnt}",
        "slots": {"dev": DEVICES, "mnt": MOUNT_POINTS},
    },
    {
        "nl": [
            "unmount {mnt}",
            "unmount device at {mnt}",
            "detach {mnt}",
            "umount {mnt}",
        ],
        "cmd": "sudo umount {mnt}",
        "slots": {"mnt": MOUNT_POINTS},
    },
    {
        "nl": [
            "show mounted filesystems",
            "list all mounts",
            "what's mounted",
            "show mount points",
        ],
        "cmd": "mount | column -t",
        "slots": {},
    },
    {
        "nl": [
            "format {dev} as {fs}",
            "create a {fs} filesystem on {dev}",
            "mkfs {dev} with {fs}",
        ],
        "cmd": "sudo mkfs.{fs} {dev}",
        "slots": {"dev": DEVICES, "fs": FILESYSTEMS[:3]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# COMPOUND COMMANDS (multi-step operations)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES += [
    {
        "nl": [
            "download {url} and run it",
            "fetch {url} and execute it",
            "download and execute {url}",
            "get {url} then run it",
            "download {url}, run it, then delete it",
        ],
        "cmd": "curl -fsSL {url} -o /tmp/script.sh && bash /tmp/script.sh && rm /tmp/script.sh",
        "slots": {
            "url": [
                "https://get.docker.com",
                "https://example.com/install.sh",
                "https://raw.githubusercontent.com/user/repo/main/setup.sh",
            ]
        },
    },
    {
        "nl": [
            "find {pat} files older than {days} days and delete them",
            "delete {pat} files in {path} older than {days} days",
            "remove {pat} files that haven't been modified in {days} days in {path}",
            "clean up old {pat} files in {path} older than {days} days",
        ],
        "cmd": "find {path} -type f -name '{pat}' -mtime +{days} -delete",
        "slots": {
            "pat": ["*.log", "*.tmp", "*.bak", "*.cache"],
            "path": ["/var/log", "/tmp", "/var/tmp", "/home/user"],
            "days": ["7", "14", "30", "90"],
        },
    },
    {
        "nl": [
            "find large files over {size} and show their sizes",
            "list files larger than {size} with their sizes",
            "show files bigger than {size} with details",
        ],
        "cmd": "find / -type f -size +{size} -exec ls -lh {{}} + 2>/dev/null",
        "slots": {"size": SIZES},
    },
    {
        "nl": [
            "create a backup of {dir} with today's date",
            "backup {dir} with a date stamp",
            "archive {dir} with the current date",
            "make a dated backup of {dir}",
        ],
        "cmd": "tar czf {dir}-$(date +%Y%m%d).tar.gz {dir}",
        "slots": {"dir": ["/etc", "/var/www", "/home/user", "/opt/app", "/var/log"]},
    },
    {
        "nl": [
            "install {pkg} and start the service",
            "install {pkg} and enable it",
            "set up {pkg} and start it",
        ],
        "cmd": {
            "debian": "sudo apt-get install -y {pkg} && sudo systemctl start {pkg} && sudo systemctl enable {pkg}",
            "rhel": "sudo dnf install -y {pkg} && sudo systemctl start {pkg} && sudo systemctl enable {pkg}",
            "arch": "sudo pacman -S --noconfirm {pkg} && sudo systemctl start {pkg} && sudo systemctl enable {pkg}",
            "suse": "sudo zypper install -y {pkg} && sudo systemctl start {pkg} && sudo systemctl enable {pkg}",
            "macos": "brew install {pkg} && brew services start {pkg}",
        },
        "slots": {"pkg": ["nginx", "redis", "postgresql", "docker", "mysql"]},
    },
    {
        "nl": [
            "create directory {dir} and change into it",
            "make {dir} and cd into it",
            "create and enter {dir}",
        ],
        "cmd": "mkdir -p {dir} && cd {dir}",
        "slots": {"dir": ["project", "build", "output", "workspace", "myapp"]},
    },
    {
        "nl": [
            "replace {old} with {new} in all {pat} files under {path}",
            "find and replace {old} with {new} in all {pat} files in {path}",
            "change {old} to {new} in every {pat} file in {path}",
        ],
        "cmd": "find {path} -type f -name '{pat}' -exec sed -i 's/{old}/{new}/g' {{}} +",
        "slots": {
            "old": REPLACE_OLD[:4],
            "new": REPLACE_NEW[:4],
            "pat": ["*.py", "*.conf", "*.txt", "*.yaml"],
            "path": ["/home/user/project", "/opt/app", "/var/www"],
        },
    },
    {
        "nl": [
            "count the total number of {pat} files in {path}",
            "how many {pat} files are in {path}",
            "count {pat} files under {path}",
        ],
        "cmd": "find {path} -type f -name '{pat}' | wc -l",
        "slots": {"pat": FILE_PATTERNS[:8], "path": PATHS_SHORT},
    },
    {
        "nl": [
            "check if {svc} is running and start it if not",
            "start {svc} if it's not already running",
            "make sure {svc} is running",
            "ensure {svc} is active",
        ],
        "cmd": "systemctl is-active --quiet {svc} || sudo systemctl start {svc}",
        "slots": {"svc": SERVICES[:10]},
    },
    {
        "nl": [
            "show disk usage sorted by size for {path}",
            "what's taking up the most space in {path}",
            "top space consumers in {path}",
        ],
        "cmd": "du -sh {path}/* 2>/dev/null | sort -rh | head -10",
        "slots": {"path": ["/", "/home", "/var", "/opt", "/usr"]},
    },
    {
        "nl": [
            "kill all processes running {name}",
            "stop every {name} process",
            "terminate all {name} instances",
        ],
        "cmd": "pkill -f {name}",
        "slots": {"name": ["python", "node", "java", "gunicorn", "uvicorn", "celery"]},
    },
    {
        "nl": [
            "find files containing {pat} in {path} and show the matches",
            "search for {pat} in all files in {path} with context",
            "grep recursively for {pat} in {path} showing line numbers",
        ],
        "cmd": "grep -rn '{pat}' {path}",
        "slots": {"pat": SEARCH_PATTERNS[:8], "path": PATHS_SHORT},
    },
    {
        "nl": [
            "compress {dir} and send it to {remote}",
            "tar {dir} and copy it to {remote}",
            "archive {dir} and transfer to {remote}",
        ],
        "cmd": "tar czf - {dir} | ssh {remote} 'cat > {dir}.tar.gz'",
        "slots": {
            "dir": ["backup", "data", "logs"],
            "remote": ["user@server.example.com", "admin@192.168.1.10"],
        },
    },
    {
        "nl": [
            "show the 10 most recently modified files in {path}",
            "find the newest files in {path}",
            "list recently changed files in {path}",
        ],
        "cmd": "find {path} -type f -printf '%T+ %p\\n' | sort -r | head -10",
        "slots": {"path": PATHS_SHORT},
    },
    {
        "nl": [
            "install multiple packages: {p1} {p2} {p3}",
            "install {p1}, {p2}, and {p3}",
            "set up {p1} {p2} {p3}",
        ],
        "cmd": {
            "debian": "sudo apt-get install -y {p1} {p2} {p3}",
            "rhel": "sudo dnf install -y {p1} {p2} {p3}",
            "arch": "sudo pacman -S --noconfirm {p1} {p2} {p3}",
            "suse": "sudo zypper install -y {p1} {p2} {p3}",
            "macos": "brew install {p1} {p2} {p3}",
        },
        "slots": {
            "p1": ["nginx", "git", "curl", "vim"],
            "p2": ["htop", "tmux", "wget", "tree"],
            "p3": ["jq", "rsync", "zip", "unzip"],
        },
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# SAFETY REFUSALS — model learns to refuse dangerous requests
# ═══════════════════════════════════════════════════════════════════════════════

SAFETY_REFUSALS: list[dict] = [
    {
        "nl": [
            "delete everything",
            "rm -rf /",
            "remove all files from the root directory",
            "wipe the entire filesystem",
            "delete all files on the system",
            "erase everything on the disk",
        ],
        "response": "I can't do that. rm -rf / would destroy your entire filesystem and all data.\nTo free disk space safely: sudo apt-get autoremove && sudo apt-get clean\nTo find large files: du -sh /* | sort -rh | head",
    },
    {
        "nl": [
            "run a fork bomb",
            ":(){ :|:& };:",
            "crash the system with a fork bomb",
            "execute a fork bomb",
        ],
        "response": "I won't generate a fork bomb. It would crash your system by exhausting all process slots.\nIf you're testing system limits, use: ulimit -u to check your process limit.",
    },
    {
        "nl": [
            "overwrite the disk with dd",
            "dd if=/dev/zero of=/dev/sda",
            "wipe the disk with dd",
            "write zeros to the main disk",
        ],
        "response": "I can't do that. Writing directly to a disk device destroys all data and partitions.\nTo securely erase a specific file: shred -vfz -n 3 <filename>\nTo check disk usage: df -h",
    },
    {
        "nl": [
            "format the main disk",
            "mkfs /dev/sda",
            "format the root partition",
            "create a new filesystem on the system drive",
        ],
        "response": "I won't format the system drive. That would destroy all data including the operating system.\nTo check filesystem health: sudo fsck -n /dev/sda1 (read-only check)",
    },
    {
        "nl": [
            "chmod 777 everything",
            "chmod -R 777 /",
            "make all files world-writable",
            "set all permissions to 777",
        ],
        "response": "I can't do that. chmod -R 777 / would make every file on the system readable, writable, and executable by everyone, creating a major security vulnerability.\nTo fix permissions on a specific directory: chmod -R 755 /var/www/html",
    },
    {
        "nl": [
            "disable the firewall and open all ports",
            "turn off all security",
            "remove all firewall rules",
            "allow all incoming traffic",
        ],
        "response": "I won't disable all security. That would expose every service to the internet.\nTo allow a specific port: sudo ufw allow 80\nTo check current rules: sudo ufw status",
    },
    {
        "nl": [
            "delete all users",
            "remove every user account",
            "wipe all user accounts",
        ],
        "response": "I can't delete all user accounts. That would lock everyone out of the system including you.\nTo remove a specific user: sudo userdel -r <username>",
    },
    {
        "nl": [
            "overwrite /etc/passwd",
            "delete /etc/shadow",
            "modify the password file",
            "clear /etc/passwd",
        ],
        "response": "I won't modify system authentication files directly. That could lock everyone out of the system.\nTo manage users safely: sudo useradd, sudo userdel, sudo passwd",
    },
    {
        "nl": [
            "delete all system logs",
            "rm -rf /var/log",
            "wipe all logs",
            "clear every log file",
        ],
        "response": "I won't delete all system logs. They're essential for security auditing and troubleshooting.\nTo rotate logs: sudo logrotate -f /etc/logrotate.conf\nTo clear a specific log: sudo truncate -s 0 /var/log/syslog",
    },
    {
        "nl": [
            "shut down all production servers",
            "shutdown every server in the network",
            "halt all machines",
        ],
        "response": "I can only manage this local machine. To safely reboot this server: sudo reboot\nFor scheduled shutdown: sudo shutdown +10 'System going down for maintenance'",
    },
    {
        "nl": [
            "download and run a random script from the internet",
            "curl some URL and pipe it to bash",
            "execute an untrusted script from the internet",
        ],
        "response": "Running untrusted scripts is dangerous. Always inspect scripts before executing:\ncurl -fsSL <url> -o /tmp/script.sh && less /tmp/script.sh && bash /tmp/script.sh",
    },
    {
        "nl": [
            "give me a reverse shell command",
            "create a backdoor",
            "set up a remote access trojan",
            "how to hack into a server",
        ],
        "response": "I won't help with unauthorized access to systems. If you need remote access to your own server, use SSH: ssh user@server.example.com",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# OUT OF SCOPE — model learns to redirect non-Linux questions
# ═══════════════════════════════════════════════════════════════════════════════

OUT_OF_SCOPE: list[dict] = [
    {
        "nl": [
            "what's the weather today",
            "tell me a joke",
            "write me a poem",
            "what is the meaning of life",
            "who won the world cup",
            "translate hello to french",
            "what's 2+2",
            "write me an essay about history",
            "recommend a movie",
            "what's the capital of france",
        ],
        "response": "I'm INCEPT, a Linux/macOS command assistant. I can help you with shell commands, system administration, and server management. Try asking something like 'install nginx' or 'find large files'.",
    },
    {
        "nl": [
            "hello",
            "hi",
            "hey",
            "good morning",
            "how are you",
        ],
        "response": "Hello! I'm INCEPT, a Linux/macOS command assistant. Tell me what you need to do and I'll give you the command. For example: 'install nginx', 'find log files', or 'check disk space'.",
    },
    {
        "nl": [
            "help",
            "what can you do",
            "how do you work",
            "what are you",
        ],
        "response": "I'm INCEPT. I generate Linux/macOS shell commands from plain English. Just describe what you want to do.\n\nExamples:\n- 'install nginx'\n- 'find files larger than 1GB'\n- 'show disk space'\n- 'create a user named deploy'\n- 'search for errors in /var/log/syslog'",
    },
]
