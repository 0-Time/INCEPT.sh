"""Extended Linux/macOS command templates for INCEPT v2.

Adds ~450 new templates covering standard binaries missing from the base set.
Import TEMPLATES_EXTENDED and SAFETY_REFUSALS_EXTENDED in generate_v2_data.py.
"""

from __future__ import annotations

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         EXTENDED SLOT POOLS                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Compression
COMPRESSED_FILES = [
    "archive.tar.gz",
    "backup.tar.bz2",
    "data.xz",
    "logs.zst",
    "file.gz",
    "dump.bz2",
]

# Hardware / devices
PCI_SLOTS = ["00:02.0", "01:00.0", "03:00.0"]
USB_DEVICES = ["1-1", "2-1", "Bus 001"]
KERNEL_MODULES = [
    "nvidia",
    "vboxdrv",
    "br_netfilter",
    "ip_tables",
    "overlay",
    "nfs",
    "ext4",
    "bluetooth",
]

# Sysctl params
SYSCTL_PARAMS = [
    "net.ipv4.ip_forward",
    "vm.swappiness",
    "net.core.somaxconn",
    "fs.file-max",
    "kernel.pid_max",
    "net.ipv6.conf.all.forwarding",
]
SYSCTL_VALUES = ["1", "0", "10", "60", "65535", "1024"]

# Performance / PIDs
PIDS = ["1234", "5678", "42", "9999", "100", "31337"]
SIGNALS = ["SIGTERM", "SIGKILL", "SIGHUP", "SIGUSR1", "SIGINT", "9", "15"]
NICE_VALUES = ["-20", "-10", "0", "5", "10", "19"]

# Network extended
INTERFACES_EXT = ["eth0", "ens33", "enp0s3", "wlan0", "br0", "docker0", "lo", "bond0"]
IPTABLES_CHAINS = ["INPUT", "OUTPUT", "FORWARD"]
IPTABLES_PROTOCOLS = ["tcp", "udp", "icmp"]
SUBNETS = ["192.168.1.0/24", "10.0.0.0/8", "172.16.0.0/16"]

# Disk / filesystem
BLOCK_DEVICES = ["/dev/sda", "/dev/sdb", "/dev/nvme0n1", "/dev/vda", "/dev/xvda"]
PARTITIONS = ["/dev/sda1", "/dev/sda2", "/dev/nvme0n1p1", "/dev/vdb1"]
FS_TYPES = ["ext4", "xfs", "btrfs", "vfat", "ntfs", "f2fs"]
MOUNT_POINTS_EXT = ["/mnt", "/mnt/data", "/mnt/usb", "/media/disk", "/backup"]
LVM_VGS = ["vg0", "data_vg", "system_vg"]
LVM_LVS = ["lv_root", "lv_data", "lv_home", "lv_swap"]
LVM_PVS = ["/dev/sda2", "/dev/sdb1", "/dev/nvme0n1p2"]
LVM_SIZES = ["10G", "20G", "50G", "100G", "500G"]

# Package management extended
PACKAGES_RPM = ["nginx", "httpd", "vim-enhanced", "kernel-devel", "epel-release"]
PIP_PACKAGES = ["flask", "django", "requests", "numpy", "pandas", "pytest", "black", "mypy"]
NPM_PACKAGES = ["express", "react", "typescript", "eslint", "prettier", "webpack", "nodemon"]
SNAP_PACKAGES = ["firefox", "vlc", "gimp", "code", "postman", "slack"]
FLATPAK_APPS = ["org.mozilla.firefox", "org.gimp.GIMP", "com.spotify.Client"]

# SELinux
SELINUX_BOOLEANS = ["httpd_can_network_connect", "httpd_enable_homedirs", "samba_enable_home_dirs"]
SELINUX_CONTEXTS = ["httpd_sys_content_t", "user_home_t", "var_log_t"]

# Misc
LOCALES = ["en_US.UTF-8", "de_DE.UTF-8", "ja_JP.UTF-8", "fr_FR.UTF-8"]
TIMEZONES = ["America/New_York", "Europe/London", "Asia/Tokyo", "UTC"]
ENCODINGS = ["utf-8", "latin-1", "ascii", "iso-8859-1"]
COLUMN_NUMBERS = ["1", "2", "3", "1,3", "2-4", "1-3"]
AWK_FIELDS = ["$1", "$2", "$3", "$NF", "$1,$3"]
CRON_EXPRESSIONS = ["0 * * * *", "*/5 * * * *", "0 0 * * *", "0 2 * * 0", "30 6 * * 1-5"]
SCREEN_SESSIONS = ["dev", "build", "monitor", "deploy", "logs"]
TMUX_SESSIONS = ["main", "work", "server", "coding", "debug"]

# macOS specific
MACOS_DOMAINS = ["com.apple.finder", "NSGlobalDomain", "com.apple.dock", "com.apple.screensaver"]
MACOS_KEYS = [
    "AppleShowAllFiles",
    "NSNavPanelExpandedStateForSaveMode",
    "autohide",
    "askForPassword",
]
MACOS_SERVICES = ["com.apple.ftp-proxy", "homebrew.mxcl.nginx", "homebrew.mxcl.postgresql"]

# Reuse from base module
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
PATHS = ["/home", "/var/log", "/etc", "/tmp", "/opt", "/usr/local", "/var", "/srv"]
DIRS = [
    "/var/log",
    "/etc/nginx",
    "/home/user",
    "/tmp/build",
    "/opt/app",
    "/var/www/html",
    "/home/user/projects",
    "/srv/data",
]
HOSTS = [
    "192.168.1.1",
    "10.0.0.1",
    "google.com",
    "example.com",
    "server.example.com",
    "8.8.8.8",
    "1.1.1.1",
    "github.com",
]
PORTS = ["22", "80", "443", "3000", "3306", "5432", "6379", "8080", "8443", "9090"]
USERS = ["admin", "deploy", "webuser", "john", "jane", "developer", "backup", "testuser"]
GROUPS = ["docker", "sudo", "admin", "developers", "wheel", "www-data", "staff", "users"]
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
    "fail2ban",
    "cron",
    "haproxy",
]
SEARCH_PATTERNS = [
    "error",
    "ERROR",
    "warning",
    "failed",
    "timeout",
    "refused",
    "denied",
    "exception",
]
URLS = [
    "https://example.com/file.tar.gz",
    "https://example.com/data.zip",
    "https://example.com/image.iso",
    "https://example.com/backup.sql.gz",
]
DELIMITERS = [":", ",", "\\t", ";", "|"]

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                       EXTENDED TEMPLATES                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

TEMPLATES_EXTENDED: list[dict] = []

# ═══════════════════════════════════════════════════════════════════════════════
# 1. GNU COREUTILS MISSING
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "get the base name of {path}",
            "extract the filename from {path}",
            "basename of {path}",
            "strip the directory from {path}",
        ],
        "cmd": "basename {path}",
        "slots": {
            "path": [
                "/home/user/file.txt",
                "/var/log/syslog",
                "/etc/nginx/nginx.conf",
                "/opt/app/main.py",
                "/tmp/output.csv",
            ]
        },
    },
    {
        "nl": [
            "get the directory name of {path}",
            "extract the directory from {path}",
            "dirname of {path}",
            "strip the filename from {path}",
        ],
        "cmd": "dirname {path}",
        "slots": {
            "path": [
                "/home/user/file.txt",
                "/var/log/syslog",
                "/etc/nginx/nginx.conf",
                "/opt/app/main.py",
                "/tmp/output.csv",
            ]
        },
    },
    {
        "nl": [
            "get the real path of {path}",
            "resolve the full path of {path}",
            "realpath {path}",
            "show the absolute path of {path}",
        ],
        "cmd": "realpath {path}",
        "slots": {
            "path": [".", "..", "~/Documents", "../src", "file.txt", "/var/log/../log/syslog"]
        },
    },
    {
        "nl": [
            "show where the symlink {link} points to",
            "readlink {link}",
            "resolve the symlink {link}",
            "what does {link} point to",
        ],
        "cmd": "readlink -f {link}",
        "slots": {
            "link": [
                "/usr/bin/python3",
                "/usr/bin/java",
                "/etc/alternatives/editor",
                "/usr/local/bin/node",
            ]
        },
    },
    {
        "nl": [
            "print the current directory",
            "show the current working directory",
            "where am I",
            "pwd",
            "what directory am I in",
        ],
        "cmd": "pwd",
        "slots": {},
    },
    {
        "nl": [
            "write output of {cmd} to {file} and also show it",
            "pipe {cmd} through tee to {file}",
            "save {cmd} output to {file} while displaying it",
            "tee output of {cmd} to {file}",
        ],
        "cmd": "{cmd} | tee {file}",
        "slots": {
            "cmd": ["ls -la", "df -h", "ps aux", "cat /etc/os-release", "free -h"],
            "file": ["output.txt", "results.log", "/tmp/output.txt", "report.txt"],
        },
    },
    {
        "nl": [
            "append output of {cmd} to {file} and also show it",
            "tee -a output of {cmd} to {file}",
            "save {cmd} output appending to {file} while displaying it",
        ],
        "cmd": "{cmd} | tee -a {file}",
        "slots": {
            "cmd": ["ls -la", "df -h", "ps aux", "date"],
            "file": ["output.txt", "results.log", "/tmp/output.txt"],
        },
    },
    {
        "nl": [
            "merge lines from {a} and {b} side by side",
            "paste {a} and {b} together",
            "join lines of {a} and {b} horizontally",
            "combine {a} and {b} columns",
        ],
        "cmd": "paste {a} {b}",
        "slots": {"a": FILES_TEXT[:5], "b": FILES_TEXT[3:8]},
    },
    {
        "nl": [
            "split {file} into pieces of {n} lines each",
            "break {file} into chunks of {n} lines",
            "split {file} every {n} lines",
        ],
        "cmd": "split -l {n} {file}",
        "slots": {"n": ["100", "500", "1000", "5000", "10000"], "file": FILES_TEXT[:6]},
    },
    {
        "nl": [
            "split {file} into pieces of {size} each",
            "break {file} into {size} chunks",
            "split {file} by size {size}",
        ],
        "cmd": "split -b {size} {file}",
        "slots": {"size": ["1M", "10M", "50M", "100M"], "file": FILES[:6]},
    },
    {
        "nl": [
            "wrap lines in {file} to {n} characters",
            "fold {file} at {n} columns",
            "limit line width in {file} to {n} characters",
        ],
        "cmd": "fold -w {n} {file}",
        "slots": {"n": ["72", "80", "100", "120"], "file": FILES_TEXT[:5]},
    },
    {
        "nl": [
            "number the lines in {file}",
            "add line numbers to {file}",
            "nl {file}",
            "show {file} with numbered lines",
        ],
        "cmd": "nl {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "show a hex dump of {file}",
            "hexdump {file}",
            "display {file} in hexadecimal",
            "view hex contents of {file}",
        ],
        "cmd": "hexdump -C {file}",
        "slots": {"file": FILES[:8]},
    },
    {
        "nl": [
            "extract printable strings from {file}",
            "strings {file}",
            "show text strings in the binary {file}",
            "find readable strings in {file}",
        ],
        "cmd": "strings {file}",
        "slots": {"file": ["/usr/bin/ls", "/usr/bin/bash", "a.out", "binary.dat", "/usr/bin/grep"]},
    },
    {
        "nl": [
            "reverse each line of {file}",
            "rev {file}",
            "mirror the characters in each line of {file}",
        ],
        "cmd": "rev {file}",
        "slots": {"file": FILES_TEXT[:5]},
    },
    {
        "nl": [
            "shuffle the lines of {file}",
            "randomize lines in {file}",
            "shuf {file}",
            "randomly reorder lines in {file}",
        ],
        "cmd": "shuf {file}",
        "slots": {"file": FILES_TEXT[:6]},
    },
    {
        "nl": [
            "show lines common to both {a} and {b}",
            "find common lines between {a} and {b}",
            "comm -12 {a} {b}",
        ],
        "cmd": "comm -12 <(sort {a}) <(sort {b})",
        "slots": {"a": FILES_TEXT[:4], "b": FILES_TEXT[2:6]},
    },
    {
        "nl": [
            "generate a sequence from 1 to {n}",
            "seq 1 {n}",
            "print numbers from 1 to {n}",
            "count from 1 to {n}",
        ],
        "cmd": "seq 1 {n}",
        "slots": {"n": ["10", "20", "50", "100", "1000"]},
    },
    {
        "nl": [
            "create a temporary file",
            "mktemp",
            "make a temp file",
            "generate a temporary filename",
        ],
        "cmd": "mktemp",
        "slots": {},
    },
    {
        "nl": [
            "create a temporary directory",
            "mktemp -d",
            "make a temp directory",
            "generate a temporary directory",
        ],
        "cmd": "mktemp -d",
        "slots": {},
    },
    {
        "nl": [
            "securely delete {file}",
            "shred {file}",
            "overwrite and delete {file} securely",
            "wipe {file} securely",
        ],
        "cmd": "shred -vfz -n 3 {file}",
        "slots": {
            "file": ["secret.txt", "passwords.txt", "old_key.pem", "credentials.conf", "dump.sql"]
        },
    },
    {
        "nl": [
            "create a {size} file filled with zeros",
            "generate a {size} zero-filled file",
            "make a {size} empty file with dd",
        ],
        "cmd": "dd if=/dev/zero of=testfile bs=1M count={count}",
        "slots": {"size": ["10MB", "100MB", "1GB"], "count": ["10", "100", "1024"]},
    },
    {
        "nl": [
            "run {cmd} with a {sec} second timeout",
            "timeout {sec}s {cmd}",
            "execute {cmd} but kill it after {sec} seconds",
            "limit {cmd} to {sec} seconds",
        ],
        "cmd": "timeout {sec} {cmd}",
        "slots": {
            "sec": ["5", "10", "30", "60", "300"],
            "cmd": [
                "ping google.com",
                "curl https://example.com",
                "sleep 999",
                "wget https://example.com/big.tar.gz",
            ],
        },
    },
    {
        "nl": [
            "how many CPU cores does this machine have",
            "show the number of processors",
            "nproc",
            "count CPU cores",
        ],
        "cmd": "nproc",
        "slots": {},
    },
    {
        "nl": [
            "show the system architecture",
            "what architecture is this machine",
            "arch",
            "uname -m",
        ],
        "cmd": "arch",
        "slots": {},
    },
    {
        "nl": [
            "show what terminal I'm using",
            "tty",
            "which terminal device am I on",
        ],
        "cmd": "tty",
        "slots": {},
    },
    {
        "nl": [
            "flush all filesystem buffers to disk",
            "sync",
            "force write all cached data to disk",
        ],
        "cmd": "sync",
        "slots": {},
    },
    {
        "nl": [
            "automatically confirm with yes for {cmd}",
            "pipe yes to {cmd}",
            "auto-accept all prompts for {cmd}",
        ],
        "cmd": "yes | {cmd}",
        "slots": {"cmd": ["apt-get install nginx", "rm -ri /tmp/old", "yum install httpd"]},
    },
    {
        "nl": [
            "get the prime factors of {n}",
            "factor {n}",
            "factorize {n}",
        ],
        "cmd": "factor {n}",
        "slots": {"n": ["42", "100", "1234", "9999", "65535"]},
    },
    {
        "nl": [
            "convert {n} bytes to human readable format",
            "numfmt --to=iec {n}",
            "humanize the number {n}",
        ],
        "cmd": "numfmt --to=iec {n}",
        "slots": {"n": ["1048576", "1073741824", "5368709120", "10737418240"]},
    },
    {
        "nl": [
            "evaluate the expression {expr}",
            "expr {expr}",
            "calculate {expr}",
        ],
        "cmd": "expr {expr}",
        "slots": {"expr": ["5 + 3", "10 \\* 4", "100 / 5", "42 % 7"]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 2. TEXT PROCESSING EXTENDED
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "find all {pat} files and delete them",
            "delete all {pat} files using find and xargs",
            "remove every {pat} file under {path}",
        ],
        "cmd": "find {path} -type f -name '{pat}' -print0 | xargs -0 rm -f",
        "slots": {
            "pat": ["*.tmp", "*.bak", "*.log", "*.pyc", "*.o"],
            "path": ["/tmp", "/var/tmp", "/home/user", "/opt/app"],
        },
    },
    {
        "nl": [
            "find {pat} files and count them",
            "count all {pat} files under {path}",
            "how many {pat} files are in {path}",
        ],
        "cmd": "find {path} -type f -name '{pat}' | wc -l",
        "slots": {
            "pat": ["*.py", "*.log", "*.conf", "*.txt", "*.js"],
            "path": ["/home", "/var/log", "/etc", "/opt", "/srv"],
        },
    },
    {
        "nl": [
            "search for {pat} and replace with {rep} in all {ext} files under {path}",
            "find and replace {pat} with {rep} in {ext} files in {path}",
            "bulk replace {pat} with {rep} in {ext} files under {path}",
        ],
        "cmd": "find {path} -type f -name '{ext}' -exec sed -i 's/{pat}/{rep}/g' {{}} +",
        "slots": {
            "pat": ["foo", "localhost", "http://", "old_name"],
            "rep": ["bar", "0.0.0.0", "https://", "new_name"],
            "ext": ["*.py", "*.conf", "*.txt", "*.yml"],
            "path": ["/home/user/projects", "/opt/app", "/srv/www"],
        },
    },
    {
        "nl": [
            "apply the patch {file}",
            "patch < {file}",
            "apply patch file {file}",
        ],
        "cmd": "patch -p1 < {file}",
        "slots": {"file": ["fix.patch", "update.patch", "bugfix.diff", "changes.patch"]},
    },
    {
        "nl": [
            "create a patch from differences between {a} and {b}",
            "diff -u {a} {b} to create a patch",
            "generate a patch file from {a} and {b}",
        ],
        "cmd": "diff -u {a} {b} > changes.patch",
        "slots": {
            "a": ["old.conf", "original.py", "v1.txt"],
            "b": ["new.conf", "modified.py", "v2.txt"],
        },
    },
    {
        "nl": [
            "find files named {name} using locate",
            "locate {name}",
            "quickly find {name} on the system",
        ],
        "cmd": "locate {name}",
        "slots": {"name": ["nginx.conf", "python3", "sshd_config", "my.cnf", "httpd.conf"]},
    },
    {
        "nl": [
            "update the locate database",
            "updatedb",
            "refresh the file search database",
        ],
        "cmd": "sudo updatedb",
        "slots": {},
    },
    {
        "nl": [
            "convert {file} from {from_enc} to {to_enc} encoding",
            "iconv {file} from {from_enc} to {to_enc}",
            "change encoding of {file} from {from_enc} to {to_enc}",
        ],
        "cmd": "iconv -f {from_enc} -t {to_enc} {file} -o {file}.converted",
        "slots": {
            "from_enc": ["latin-1", "iso-8859-1", "ascii", "windows-1252"],
            "to_enc": ["utf-8", "utf-8", "utf-8", "utf-8"],
            "file": FILES_TEXT[:5],
        },
    },
    {
        "nl": [
            "convert {file} from dos to unix line endings",
            "dos2unix {file}",
            "fix windows line endings in {file}",
            "remove carriage returns from {file}",
        ],
        "cmd": "dos2unix {file}",
        "slots": {"file": FILES_TEXT[:6]},
    },
    {
        "nl": [
            "convert {file} from unix to dos line endings",
            "unix2dos {file}",
            "add windows line endings to {file}",
        ],
        "cmd": "unix2dos {file}",
        "slots": {"file": FILES_TEXT[:5]},
    },
    {
        "nl": [
            "detect the file type of {file}",
            "what kind of file is {file}",
            "file {file}",
            "identify the type of {file}",
        ],
        "cmd": "file {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "view {file} page by page",
            "less {file}",
            "open {file} in a pager",
            "read {file} interactively",
        ],
        "cmd": "less {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "run {cmd} on each line of {file} using xargs",
            "xargs {cmd} with input from {file}",
            "pipe {file} into xargs {cmd}",
        ],
        "cmd": "cat {file} | xargs {cmd}",
        "slots": {
            "file": ["hosts.txt", "files.txt", "urls.txt", "packages.txt"],
            "cmd": ["ping -c1", "rm", "wget", "echo"],
        },
    },
    {
        "nl": [
            "run {cmd} on each line of {file} in parallel with {n} jobs",
            "xargs -P {n} {cmd} from {file}",
            "parallel xargs {cmd} from {file} with {n} processes",
        ],
        "cmd": "cat {file} | xargs -P {n} -I {{}} {cmd} {{}}",
        "slots": {
            "file": ["urls.txt", "hosts.txt", "files.txt"],
            "cmd": ["curl -s", "ping -c1", "wget -q"],
            "n": ["4", "8", "16"],
        },
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 3. COMPRESSION EXTENDED
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "compress {file} with bzip2",
            "bzip2 {file}",
            "create a bz2 archive of {file}",
        ],
        "cmd": "bzip2 {file}",
        "slots": {"file": FILES_TEXT[:6]},
    },
    {
        "nl": [
            "decompress {file}",
            "bunzip2 {file}",
            "extract the bz2 file {file}",
        ],
        "cmd": "bunzip2 {file}",
        "slots": {"file": ["data.bz2", "backup.bz2", "archive.bz2", "logs.bz2"]},
    },
    {
        "nl": [
            "view contents of {file} without decompressing",
            "bzcat {file}",
            "read bz2 file {file} to stdout",
        ],
        "cmd": "bzcat {file}",
        "slots": {"file": ["data.bz2", "logs.bz2", "backup.bz2"]},
    },
    {
        "nl": [
            "compress {file} with xz",
            "xz {file}",
            "create an xz archive of {file}",
        ],
        "cmd": "xz {file}",
        "slots": {"file": FILES_TEXT[:6]},
    },
    {
        "nl": [
            "decompress {file} with xz",
            "unxz {file}",
            "extract the xz file {file}",
        ],
        "cmd": "unxz {file}",
        "slots": {"file": ["data.xz", "backup.xz", "archive.xz", "dump.xz"]},
    },
    {
        "nl": [
            "view xz compressed file {file} without extracting",
            "xzcat {file}",
            "read xz file {file} to stdout",
        ],
        "cmd": "xzcat {file}",
        "slots": {"file": ["data.xz", "logs.xz", "backup.xz"]},
    },
    {
        "nl": [
            "compress {file} with zstd",
            "zstd {file}",
            "create a zstandard archive of {file}",
        ],
        "cmd": "zstd {file}",
        "slots": {"file": FILES_TEXT[:6]},
    },
    {
        "nl": [
            "decompress {file} with zstd",
            "unzstd {file}",
            "extract the zst file {file}",
        ],
        "cmd": "unzstd {file}",
        "slots": {"file": ["data.zst", "backup.zst", "archive.zst", "logs.zst"]},
    },
    {
        "nl": [
            "compress {file} with zstd using {n} threads",
            "zstd -T{n} {file}",
            "parallel zstd compress {file} with {n} threads",
        ],
        "cmd": "zstd -T{n} {file}",
        "slots": {"n": ["4", "8", "0"], "file": FILES[:5]},
    },
    {
        "nl": [
            "create a 7z archive of {dir}",
            "7z a {dir}.7z {dir}",
            "compress {dir} into a 7z file",
        ],
        "cmd": "7z a {dir}.7z {dir}",
        "slots": {"dir": ["backup", "data", "logs", "project", "archive"]},
    },
    {
        "nl": [
            "extract a 7z archive {file}",
            "7z x {file}",
            "unpack the 7z file {file}",
        ],
        "cmd": "7z x {file}",
        "slots": {"file": ["archive.7z", "backup.7z", "data.7z"]},
    },
    {
        "nl": [
            "list contents of 7z archive {file}",
            "7z l {file}",
            "show what's inside the 7z file {file}",
        ],
        "cmd": "7z l {file}",
        "slots": {"file": ["archive.7z", "backup.7z", "data.7z"]},
    },
    {
        "nl": [
            "create a cpio archive from {dir}",
            "archive {dir} using cpio",
        ],
        "cmd": "find {dir} | cpio -ov > {dir}.cpio",
        "slots": {"dir": ["backup", "data", "logs", "etc_backup"]},
    },
    {
        "nl": [
            "extract a cpio archive {file}",
            "unpack the cpio file {file}",
        ],
        "cmd": "cpio -idv < {file}",
        "slots": {"file": ["backup.cpio", "archive.cpio", "data.cpio"]},
    },
    {
        "nl": [
            "view gzipped file {file} without extracting",
            "zcat {file}",
            "read gz file {file} to stdout",
        ],
        "cmd": "zcat {file}",
        "slots": {"file": ["data.gz", "logs.gz", "backup.gz", "access.log.gz"]},
    },
    {
        "nl": [
            "grep for {pat} in gzipped file {file}",
            "zgrep {pat} {file}",
            "search compressed file {file} for {pat}",
        ],
        "cmd": "zgrep '{pat}' {file}",
        "slots": {
            "pat": SEARCH_PATTERNS[:5],
            "file": ["access.log.gz", "syslog.1.gz", "error.log.gz", "app.log.gz"],
        },
    },
    {
        "nl": [
            "compress {file} with pigz using {n} threads",
            "pigz -p {n} {file}",
            "parallel gzip {file} with {n} threads",
        ],
        "cmd": "pigz -p {n} {file}",
        "slots": {"n": ["4", "8", "16"], "file": FILES[:5]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 4. PROCESS & PERFORMANCE MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "show top processes sorted by CPU",
            "top in batch mode",
            "list top 10 CPU-consuming processes",
        ],
        "cmd": "top -b -n 1 | head -20",
        "slots": {},
    },
    {
        "nl": [
            "show virtual memory statistics",
            "vmstat",
            "display memory and CPU stats",
            "show VM statistics",
        ],
        "cmd": "vmstat 1 5",
        "slots": {},
    },
    {
        "nl": [
            "show IO statistics",
            "iostat",
            "display disk IO stats",
            "check disk IO performance",
        ],
        "cmd": "iostat -x 1 5",
        "slots": {},
    },
    {
        "nl": [
            "show per-CPU statistics",
            "mpstat",
            "display CPU usage per core",
            "check individual CPU stats",
        ],
        "cmd": "mpstat -P ALL 1 5",
        "slots": {},
    },
    {
        "nl": [
            "show IO stats for process {pid}",
            "pidstat -d for {pid}",
            "check IO usage of process {pid}",
        ],
        "cmd": "pidstat -d -p {pid} 1 5",
        "slots": {"pid": PIDS},
    },
    {
        "nl": [
            "show CPU stats for process {pid}",
            "pidstat for {pid}",
            "check CPU usage of process {pid}",
        ],
        "cmd": "pidstat -p {pid} 1 5",
        "slots": {"pid": PIDS},
    },
    {
        "nl": [
            "show system activity report",
            "sar",
            "display sar CPU report",
        ],
        "cmd": "sar -u 1 5",
        "slots": {},
    },
    {
        "nl": [
            "show sar memory report",
            "sar memory stats",
            "display memory usage with sar",
        ],
        "cmd": "sar -r 1 5",
        "slots": {},
    },
    {
        "nl": [
            "trace system calls of process {pid}",
            "strace process {pid}",
            "show syscalls for PID {pid}",
            "debug process {pid} with strace",
        ],
        "cmd": "strace -p {pid}",
        "slots": {"pid": PIDS},
    },
    {
        "nl": [
            "trace system calls when running {cmd}",
            "strace {cmd}",
            "show syscalls for command {cmd}",
        ],
        "cmd": "strace {cmd}",
        "slots": {"cmd": ["ls", "cat /etc/hostname", "curl -s https://example.com", "df -h"]},
    },
    {
        "nl": [
            "trace library calls of {cmd}",
            "ltrace {cmd}",
            "show library calls for {cmd}",
        ],
        "cmd": "ltrace {cmd}",
        "slots": {"cmd": ["ls", "cat /etc/hostname", "date", "whoami"]},
    },
    {
        "nl": [
            "show files opened by process {pid}",
            "lsof -p {pid}",
            "list open files for PID {pid}",
            "what files does process {pid} have open",
        ],
        "cmd": "lsof -p {pid}",
        "slots": {"pid": PIDS},
    },
    {
        "nl": [
            "show what process is using port {port}",
            "lsof -i :{port}",
            "who is listening on port {port}",
            "find the process using port {port}",
        ],
        "cmd": "lsof -i :{port}",
        "slots": {"port": PORTS},
    },
    {
        "nl": [
            "show all network connections with lsof",
            "list all open network sockets",
            "lsof -i",
        ],
        "cmd": "lsof -i",
        "slots": {},
    },
    {
        "nl": [
            "who is using the file {file}",
            "fuser {file}",
            "which process has {file} open",
        ],
        "cmd": "fuser -v {file}",
        "slots": {
            "file": [
                "/var/log/syslog",
                "/tmp/lock",
                "/var/run/docker.sock",
                "/etc/nginx/nginx.conf",
                "database.db",
            ]
        },
    },
    {
        "nl": [
            "which process has port {port} open",
            "fuser {port}/tcp",
            "who is using TCP port {port}",
        ],
        "cmd": "fuser -v {port}/tcp",
        "slots": {"port": PORTS},
    },
    {
        "nl": [
            "find the PID of {name}",
            "pidof {name}",
            "get the process ID of {name}",
            "what is the PID of {name}",
        ],
        "cmd": "pidof {name}",
        "slots": {"name": ["nginx", "sshd", "python3", "node", "postgres", "redis-server", "java"]},
    },
    {
        "nl": [
            "find processes matching {name}",
            "pgrep {name}",
            "search for processes named {name}",
        ],
        "cmd": "pgrep -la {name}",
        "slots": {"name": ["nginx", "python", "node", "java", "docker", "ssh", "redis"]},
    },
    {
        "nl": [
            "show memory map of process {pid}",
            "pmap {pid}",
            "display memory layout of PID {pid}",
        ],
        "cmd": "pmap {pid}",
        "slots": {"pid": PIDS},
    },
    {
        "nl": [
            "time how long {cmd} takes",
            "measure execution time of {cmd}",
            "time {cmd}",
            "benchmark {cmd}",
        ],
        "cmd": "time {cmd}",
        "slots": {
            "cmd": [
                "ls -la /",
                "find / -name '*.log' 2>/dev/null",
                "sleep 1",
                "tar czf /dev/null /etc",
            ]
        },
    },
    {
        "nl": [
            "run {cmd} with low priority",
            "nice {cmd}",
            "start {cmd} with nice value {nice}",
        ],
        "cmd": "nice -n {nice} {cmd}",
        "slots": {
            "nice": ["10", "15", "19"],
            "cmd": ["tar czf backup.tar.gz /home", "find / -name '*.log'", "make -j4"],
        },
    },
    {
        "nl": [
            "change the priority of process {pid} to {nice}",
            "renice process {pid} to {nice}",
            "set priority of PID {pid} to {nice}",
        ],
        "cmd": "renice -n {nice} -p {pid}",
        "slots": {"nice": NICE_VALUES, "pid": PIDS},
    },
    {
        "nl": [
            "set IO scheduling class of process {pid} to idle",
            "ionice process {pid}",
            "lower IO priority of PID {pid}",
        ],
        "cmd": "ionice -c 3 -p {pid}",
        "slots": {"pid": PIDS},
    },
    {
        "nl": [
            "send {sig} signal to process {pid}",
            "kill -{sig} {pid}",
            "signal process {pid} with {sig}",
        ],
        "cmd": "kill -{sig} {pid}",
        "slots": {"sig": SIGNALS, "pid": PIDS},
    },
    {
        "nl": [
            "kill all processes named {name}",
            "killall {name}",
            "terminate all {name} processes",
        ],
        "cmd": "killall {name}",
        "slots": {"name": ["python3", "node", "java", "nginx", "firefox", "chrome"]},
    },
    {
        "nl": [
            "kill processes matching pattern {pat}",
            "pkill {pat}",
            "terminate processes matching {pat}",
        ],
        "cmd": "pkill -f {pat}",
        "slots": {"pat": ["gunicorn", "celery", "webpack", "python manage.py", "npm run"]},
    },
    {
        "nl": [
            "show the process tree",
            "pstree",
            "display process hierarchy",
            "show parent-child process relationships",
        ],
        "cmd": "pstree -p",
        "slots": {},
    },
    {
        "nl": [
            "watch system resources update every {n} seconds",
            "watch -n {n} free -h",
            "monitor memory every {n} seconds",
        ],
        "cmd": "watch -n {n} free -h",
        "slots": {"n": ["1", "2", "5", "10"]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 5. DISK & FILESYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "list all partitions on {dev}",
            "show partition table of {dev}",
            "fdisk -l {dev}",
            "display partitions on {dev}",
        ],
        "cmd": "sudo fdisk -l {dev}",
        "slots": {"dev": BLOCK_DEVICES},
    },
    {
        "nl": [
            "list all block device IDs",
            "blkid",
            "show UUIDs of all partitions",
            "identify block devices",
        ],
        "cmd": "sudo blkid",
        "slots": {},
    },
    {
        "nl": [
            "show block device info for {part}",
            "blkid {part}",
            "get UUID of {part}",
        ],
        "cmd": "sudo blkid {part}",
        "slots": {"part": PARTITIONS},
    },
    {
        "nl": [
            "list all mounted filesystems",
            "findmnt",
            "show mount tree",
            "display all mount points",
        ],
        "cmd": "findmnt",
        "slots": {},
    },
    {
        "nl": [
            "show mount info for {mnt}",
            "findmnt {mnt}",
            "what is mounted at {mnt}",
        ],
        "cmd": "findmnt {mnt}",
        "slots": {"mnt": MOUNT_POINTS_EXT + ["/", "/home", "/var"]},
    },
    {
        "nl": [
            "check filesystem on {part}",
            "fsck {part}",
            "verify integrity of {part}",
            "run filesystem check on {part}",
        ],
        "cmd": "sudo e2fsck -f {part}",
        "slots": {"part": PARTITIONS},
    },
    {
        "nl": [
            "repair XFS filesystem on {part}",
            "xfs_repair {part}",
            "fix XFS filesystem on {part}",
        ],
        "cmd": "sudo xfs_repair {part}",
        "slots": {"part": PARTITIONS},
    },
    {
        "nl": [
            "create a swap file of {size}",
            "make a {size} swap file",
            "set up a {size} swap file",
        ],
        "cmd": "sudo dd if=/dev/zero of=/swapfile bs=1M count={count} && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile",
        "slots": {"size": ["1GB", "2GB", "4GB"], "count": ["1024", "2048", "4096"]},
    },
    {
        "nl": [
            "enable swap on {part}",
            "swapon {part}",
            "activate swap partition {part}",
        ],
        "cmd": "sudo swapon {part}",
        "slots": {"part": PARTITIONS[:3]},
    },
    {
        "nl": [
            "disable swap on {part}",
            "swapoff {part}",
            "deactivate swap partition {part}",
        ],
        "cmd": "sudo swapoff {part}",
        "slots": {"part": PARTITIONS[:3]},
    },
    {
        "nl": [
            "show swap usage",
            "display swap info",
            "swapon --show",
            "how much swap is being used",
        ],
        "cmd": "swapon --show",
        "slots": {},
    },
    {
        "nl": [
            "trim SSD",
            "fstrim all filesystems",
            "run TRIM on all mounted SSDs",
        ],
        "cmd": "sudo fstrim -av",
        "slots": {},
    },
    {
        "nl": [
            "preallocate a {size} file at {path}",
            "fallocate {size} at {path}",
            "create a {size} file instantly at {path}",
        ],
        "cmd": "fallocate -l {size} {path}",
        "slots": {
            "size": ["1G", "5G", "10G", "100M"],
            "path": ["/tmp/testfile", "/var/swapfile", "/tmp/bigfile"],
        },
    },
    {
        "nl": [
            "create a physical volume on {pv}",
            "pvcreate {pv}",
            "initialize {pv} for LVM",
        ],
        "cmd": "sudo pvcreate {pv}",
        "slots": {"pv": LVM_PVS},
    },
    {
        "nl": [
            "show physical volumes",
            "pvs",
            "list LVM physical volumes",
        ],
        "cmd": "sudo pvs",
        "slots": {},
    },
    {
        "nl": [
            "create a volume group {vg} on {pv}",
            "vgcreate {vg} on {pv}",
            "make LVM volume group {vg} using {pv}",
        ],
        "cmd": "sudo vgcreate {vg} {pv}",
        "slots": {"vg": LVM_VGS, "pv": LVM_PVS},
    },
    {
        "nl": [
            "show volume groups",
            "vgs",
            "list LVM volume groups",
        ],
        "cmd": "sudo vgs",
        "slots": {},
    },
    {
        "nl": [
            "create a {size} logical volume {lv} in {vg}",
            "lvcreate {lv} in {vg} with {size}",
            "make a {size} LVM volume {lv} in {vg}",
        ],
        "cmd": "sudo lvcreate -L {size} -n {lv} {vg}",
        "slots": {"size": LVM_SIZES, "lv": LVM_LVS, "vg": LVM_VGS},
    },
    {
        "nl": [
            "show logical volumes",
            "lvs",
            "list LVM logical volumes",
        ],
        "cmd": "sudo lvs",
        "slots": {},
    },
    {
        "nl": [
            "extend logical volume {vg}/{lv} by {size}",
            "lvextend {vg}/{lv} by {size}",
            "grow LVM volume {vg}/{lv} by {size}",
        ],
        "cmd": "sudo lvextend -L +{size} /dev/{vg}/{lv}",
        "slots": {"size": LVM_SIZES[:3], "vg": LVM_VGS, "lv": LVM_LVS},
    },
    {
        "nl": [
            "resize the ext4 filesystem on {part}",
            "resize2fs {part}",
            "grow the ext4 filesystem to fill {part}",
        ],
        "cmd": "sudo resize2fs {part}",
        "slots": {"part": PARTITIONS},
    },
    {
        "nl": [
            "grow the xfs filesystem at {mnt}",
            "xfs_growfs {mnt}",
            "expand XFS filesystem at {mnt}",
        ],
        "cmd": "sudo xfs_growfs {mnt}",
        "slots": {"mnt": MOUNT_POINTS_EXT},
    },
    {
        "nl": [
            "show SMART health status of {dev}",
            "smartctl {dev}",
            "check disk health of {dev}",
        ],
        "cmd": "sudo smartctl -a {dev}",
        "slots": {"dev": BLOCK_DEVICES},
    },
    {
        "nl": [
            "show disk parameters for {dev}",
            "hdparm -I {dev}",
            "get drive info for {dev}",
        ],
        "cmd": "sudo hdparm -I {dev}",
        "slots": {"dev": BLOCK_DEVICES},
    },
    {
        "nl": [
            "benchmark read speed of {dev}",
            "hdparm -t {dev}",
            "test read speed of {dev}",
        ],
        "cmd": "sudo hdparm -t {dev}",
        "slots": {"dev": BLOCK_DEVICES},
    },
    {
        "nl": [
            "create a RAID1 array from {a} and {b}",
            "mdadm create RAID1 with {a} {b}",
            "set up a RAID1 mirror with {a} and {b}",
        ],
        "cmd": "sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 {a} {b}",
        "slots": {"a": ["/dev/sdb1", "/dev/sdc1"], "b": ["/dev/sdd1", "/dev/sde1"]},
    },
    {
        "nl": [
            "show RAID array details",
            "mdadm --detail /dev/md0",
            "check RAID status",
        ],
        "cmd": "sudo mdadm --detail /dev/md0",
        "slots": {},
    },
    {
        "nl": [
            "format {part} as {fs}",
            "create a {fs} filesystem on {part}",
            "mkfs.{fs} {part}",
        ],
        "cmd": "sudo mkfs.{fs} {part}",
        "slots": {"fs": FS_TYPES[:4], "part": PARTITIONS},
    },
    {
        "nl": [
            "mount {part} at {mnt}",
            "mount {part} to {mnt}",
            "attach {part} at mount point {mnt}",
        ],
        "cmd": "sudo mount {part} {mnt}",
        "slots": {"part": PARTITIONS, "mnt": MOUNT_POINTS_EXT},
    },
    {
        "nl": [
            "unmount {mnt}",
            "umount {mnt}",
            "detach the filesystem at {mnt}",
        ],
        "cmd": "sudo umount {mnt}",
        "slots": {"mnt": MOUNT_POINTS_EXT},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 6. NETWORKING EXTENDED
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "download {url} with wget",
            "wget {url}",
            "fetch {url} using wget",
        ],
        "cmd": "wget {url}",
        "slots": {"url": URLS},
    },
    {
        "nl": [
            "download {url} and save as {file}",
            "wget -O {file} {url}",
            "save {url} to {file}",
        ],
        "cmd": "wget -O {file} {url}",
        "slots": {"url": URLS, "file": ["download.tar.gz", "data.zip", "output.iso"]},
    },
    {
        "nl": [
            "resume a partial download of {url}",
            "wget -c {url}",
            "continue downloading {url}",
        ],
        "cmd": "wget -c {url}",
        "slots": {"url": URLS},
    },
    {
        "nl": [
            "mirror the website {host}",
            "wget --mirror {host}",
            "download entire website {host}",
        ],
        "cmd": "wget --mirror --convert-links --adjust-extension --page-requisites --no-parent https://{host}",
        "slots": {"host": ["example.com", "docs.example.com"]},
    },
    {
        "nl": [
            "lookup DNS for {host}",
            "nslookup {host}",
            "resolve {host}",
            "DNS lookup for {host}",
        ],
        "cmd": "nslookup {host}",
        "slots": {"host": HOSTS},
    },
    {
        "nl": [
            "get DNS records for {host}",
            "host {host}",
            "resolve {host} with host command",
        ],
        "cmd": "host {host}",
        "slots": {"host": HOSTS},
    },
    {
        "nl": [
            "whois lookup for {domain}",
            "whois {domain}",
            "get domain registration info for {domain}",
        ],
        "cmd": "whois {domain}",
        "slots": {"domain": ["example.com", "google.com", "github.com", "wikipedia.org"]},
    },
    {
        "nl": [
            "traceroute to {host} with mtr",
            "mtr {host}",
            "show network path to {host}",
        ],
        "cmd": "mtr --report {host}",
        "slots": {"host": HOSTS},
    },
    {
        "nl": [
            "capture packets on {iface}",
            "tcpdump on {iface}",
            "sniff traffic on {iface}",
        ],
        "cmd": "sudo tcpdump -i {iface} -c 100",
        "slots": {"iface": INTERFACES_EXT[:5]},
    },
    {
        "nl": [
            "capture packets on port {port}",
            "tcpdump port {port}",
            "sniff traffic on port {port}",
        ],
        "cmd": "sudo tcpdump -i any port {port} -c 100",
        "slots": {"port": PORTS},
    },
    {
        "nl": [
            "save packet capture to {file}",
            "tcpdump -w {file}",
            "write pcap to {file}",
        ],
        "cmd": "sudo tcpdump -i any -w {file} -c 1000",
        "slots": {"file": ["capture.pcap", "traffic.pcap", "dump.pcap"]},
    },
    {
        "nl": [
            "scan ports on {host}",
            "nmap {host}",
            "port scan {host}",
            "check open ports on {host}",
        ],
        "cmd": "nmap {host}",
        "slots": {"host": HOSTS},
    },
    {
        "nl": [
            "scan {host} for services and versions",
            "nmap -sV {host}",
            "detect services on {host}",
        ],
        "cmd": "nmap -sV {host}",
        "slots": {"host": HOSTS},
    },
    {
        "nl": [
            "scan specific port {port} on {host}",
            "nmap -p {port} {host}",
            "check if port {port} is open on {host}",
        ],
        "cmd": "nmap -p {port} {host}",
        "slots": {"port": PORTS, "host": HOSTS},
    },
    {
        "nl": [
            "show NIC info for {iface}",
            "ethtool {iface}",
            "get network adapter details for {iface}",
        ],
        "cmd": "sudo ethtool {iface}",
        "slots": {"iface": INTERFACES_EXT[:5]},
    },
    {
        "nl": [
            "show all network connections",
            "netstat -tulnp",
            "display listening ports with netstat",
        ],
        "cmd": "netstat -tulnp",
        "slots": {},
    },
    {
        "nl": [
            "show the routing table",
            "ip route show",
            "display routes",
            "show network routes",
        ],
        "cmd": "ip route show",
        "slots": {},
    },
    {
        "nl": [
            "add a static route to {subnet} via {gw}",
            "ip route add {subnet} via {gw}",
            "create a route to {subnet} through {gw}",
        ],
        "cmd": "sudo ip route add {subnet} via {gw}",
        "slots": {"subnet": SUBNETS, "gw": ["192.168.1.1", "10.0.0.1", "172.16.0.1"]},
    },
    {
        "nl": [
            "show the ARP table",
            "ip neigh show",
            "display ARP entries",
            "show neighbor cache",
        ],
        "cmd": "ip neigh show",
        "slots": {},
    },
    {
        "nl": [
            "list iptables rules",
            "iptables -L",
            "show firewall rules",
            "display iptables rules",
        ],
        "cmd": "sudo iptables -L -n -v",
        "slots": {},
    },
    {
        "nl": [
            "block incoming traffic from {host}",
            "iptables drop {host}",
            "firewall block {host}",
        ],
        "cmd": "sudo iptables -A INPUT -s {host} -j DROP",
        "slots": {"host": ["10.0.0.50", "192.168.1.100", "172.16.0.99"]},
    },
    {
        "nl": [
            "allow incoming traffic on port {port}",
            "iptables accept port {port}",
            "open port {port} in iptables",
        ],
        "cmd": "sudo iptables -A INPUT -p tcp --dport {port} -j ACCEPT",
        "slots": {"port": PORTS},
    },
    {
        "nl": [
            "set up NAT masquerade on {iface}",
            "enable NAT on {iface}",
            "configure masquerading on {iface}",
        ],
        "cmd": "sudo iptables -t nat -A POSTROUTING -o {iface} -j MASQUERADE",
        "slots": {"iface": ["eth0", "ens33", "enp0s3"]},
    },
    {
        "nl": [
            "forward port {src} to {dst} with iptables",
            "port forward {src} to {dst}",
            "redirect port {src} to {dst}",
        ],
        "cmd": "sudo iptables -t nat -A PREROUTING -p tcp --dport {src} -j REDIRECT --to-port {dst}",
        "slots": {"src": ["80", "8080", "443"], "dst": ["3000", "8000", "8443"]},
    },
    {
        "nl": [
            "save iptables rules",
            "persist iptables rules",
            "export iptables configuration",
        ],
        "cmd": "sudo iptables-save > /etc/iptables/rules.v4",
        "slots": {},
    },
    {
        "nl": [
            "show wireless network info for {iface}",
            "iwconfig {iface}",
            "check wifi status on {iface}",
        ],
        "cmd": "iwconfig {iface}",
        "slots": {"iface": ["wlan0", "wlp2s0", "wlp3s0"]},
    },
    {
        "nl": [
            "scan for wireless networks",
            "iw dev wlan0 scan",
            "list available wifi networks",
        ],
        "cmd": "sudo iw dev wlan0 scan | grep -E 'SSID|signal'",
        "slots": {},
    },
    {
        "nl": [
            "show NetworkManager connections",
            "nmcli connection show",
            "list network connections",
        ],
        "cmd": "nmcli connection show",
        "slots": {},
    },
    {
        "nl": [
            "connect to wifi network {ssid}",
            "nmcli connect to {ssid}",
            "join wifi {ssid}",
        ],
        "cmd": "nmcli device wifi connect {ssid}",
        "slots": {"ssid": ["MyWiFi", "Office-5G", "Home-Network", "Guest"]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 7. PACKAGE MANAGEMENT EXTENDED
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "search for package {pkg} with apt",
            "apt search {pkg}",
            "find packages matching {pkg}",
        ],
        "cmd": {
            "debian": "apt search {pkg}",
            "rhel": "yum search {pkg}",
            "arch": "pacman -Ss {pkg}",
            "suse": "zypper search {pkg}",
            "macos": "brew search {pkg}",
        },
        "slots": {
            "debian": {"pkg": ["nginx", "python3", "docker", "vim", "git", "nodejs"]},
            "rhel": {"pkg": ["nginx", "python3", "docker", "vim", "git", "nodejs"]},
            "arch": {"pkg": ["nginx", "python", "docker", "vim", "git", "nodejs"]},
            "suse": {"pkg": ["nginx", "python3", "docker", "vim", "git", "nodejs"]},
            "macos": {"pkg": ["nginx", "python3", "docker", "vim", "git", "node"]},
        },
    },
    {
        "nl": [
            "show info about package {pkg}",
            "get details of package {pkg}",
            "package info for {pkg}",
        ],
        "cmd": {
            "debian": "apt show {pkg}",
            "rhel": "yum info {pkg}",
            "arch": "pacman -Si {pkg}",
            "suse": "zypper info {pkg}",
            "macos": "brew info {pkg}",
        },
        "slots": {
            "debian": {"pkg": ["nginx", "curl", "python3", "git", "vim"]},
            "rhel": {"pkg": ["nginx", "curl", "python3", "git", "vim-enhanced"]},
            "arch": {"pkg": ["nginx", "curl", "python", "git", "vim"]},
            "suse": {"pkg": ["nginx", "curl", "python3", "git", "vim"]},
            "macos": {"pkg": ["nginx", "curl", "python3", "git", "vim"]},
        },
    },
    {
        "nl": [
            "list installed packages",
            "show all installed packages",
            "what packages are installed",
        ],
        "cmd": {
            "debian": "dpkg -l",
            "rhel": "rpm -qa",
            "arch": "pacman -Q",
            "suse": "rpm -qa",
            "macos": "brew list",
        },
        "slots": {},
    },
    {
        "nl": [
            "which package provides file {file}",
            "find which package owns {file}",
            "what package installed {file}",
        ],
        "cmd": {
            "debian": "dpkg -S {file}",
            "rhel": "rpm -qf {file}",
            "arch": "pacman -Qo {file}",
            "suse": "rpm -qf {file}",
        },
        "slots": {
            "debian": {
                "file": ["/usr/bin/curl", "/usr/bin/git", "/usr/sbin/nginx", "/usr/bin/python3"]
            },
            "rhel": {
                "file": ["/usr/bin/curl", "/usr/bin/git", "/usr/sbin/nginx", "/usr/bin/python3"]
            },
            "arch": {
                "file": ["/usr/bin/curl", "/usr/bin/git", "/usr/bin/nginx", "/usr/bin/python3"]
            },
            "suse": {
                "file": ["/usr/bin/curl", "/usr/bin/git", "/usr/sbin/nginx", "/usr/bin/python3"]
            },
        },
    },
    {
        "nl": [
            "list files installed by package {pkg}",
            "show files from package {pkg}",
            "what files does {pkg} install",
        ],
        "cmd": {
            "debian": "dpkg -L {pkg}",
            "rhel": "rpm -ql {pkg}",
            "arch": "pacman -Ql {pkg}",
            "suse": "rpm -ql {pkg}",
        },
        "slots": {
            "debian": {"pkg": ["nginx", "curl", "bash", "coreutils"]},
            "rhel": {"pkg": ["nginx", "curl", "bash", "coreutils"]},
            "arch": {"pkg": ["nginx", "curl", "bash", "coreutils"]},
            "suse": {"pkg": ["nginx", "curl", "bash", "coreutils"]},
        },
    },
    {
        "nl": [
            "remove unused packages",
            "autoremove orphan packages",
            "clean up unused dependencies",
        ],
        "cmd": {
            "debian": "sudo apt autoremove -y",
            "rhel": "sudo yum autoremove -y",
            "arch": "sudo pacman -Rns $(pacman -Qdtq)",
            "suse": "sudo zypper packages --unneeded",
            "macos": "brew autoremove",
        },
        "slots": {},
    },
    {
        "nl": [
            "clean the package cache",
            "clear the apt cache",
            "free space from package downloads",
        ],
        "cmd": {
            "debian": "sudo apt clean",
            "rhel": "sudo yum clean all",
            "arch": "sudo pacman -Sc",
            "suse": "sudo zypper clean",
            "macos": "brew cleanup",
        },
        "slots": {},
    },
    {
        "nl": [
            "hold package {pkg} at current version",
            "prevent {pkg} from being updated",
            "pin {pkg} version",
        ],
        "cmd": {
            "debian": "sudo apt-mark hold {pkg}",
            "rhel": "sudo yum versionlock {pkg}",
            "arch": "# Add {pkg} to IgnorePkg in /etc/pacman.conf",
        },
        "slots": {
            "debian": {"pkg": ["linux-image-generic", "nginx", "docker-ce", "postgresql"]},
            "rhel": {"pkg": ["kernel", "nginx", "docker-ce", "postgresql-server"]},
            "arch": {"pkg": ["linux", "nginx", "docker", "postgresql"]},
        },
    },
    {
        "nl": [
            "show package update history",
            "view package installation history",
            "what packages were recently installed",
        ],
        "cmd": {
            "debian": "cat /var/log/apt/history.log | tail -50",
            "rhel": "yum history",
            "arch": "cat /var/log/pacman.log | tail -50",
            "suse": "zypper log",
        },
        "slots": {},
    },
    {
        "nl": [
            "install {pkg} with pip",
            "pip install {pkg}",
            "install python package {pkg}",
        ],
        "cmd": "pip3 install {pkg}",
        "slots": {"pkg": PIP_PACKAGES},
    },
    {
        "nl": [
            "uninstall {pkg} with pip",
            "pip uninstall {pkg}",
            "remove python package {pkg}",
        ],
        "cmd": "pip3 uninstall -y {pkg}",
        "slots": {"pkg": PIP_PACKAGES},
    },
    {
        "nl": [
            "list installed pip packages",
            "pip list",
            "show installed python packages",
        ],
        "cmd": "pip3 list",
        "slots": {},
    },
    {
        "nl": [
            "freeze pip requirements",
            "pip freeze",
            "export python dependencies to requirements.txt",
        ],
        "cmd": "pip3 freeze > requirements.txt",
        "slots": {},
    },
    {
        "nl": [
            "install {pkg} with npm globally",
            "npm install -g {pkg}",
            "install npm package {pkg} globally",
        ],
        "cmd": "npm install -g {pkg}",
        "slots": {"pkg": NPM_PACKAGES},
    },
    {
        "nl": [
            "list globally installed npm packages",
            "npm list -g",
            "show global npm packages",
        ],
        "cmd": "npm list -g --depth=0",
        "slots": {},
    },
    {
        "nl": [
            "install snap package {pkg}",
            "snap install {pkg}",
            "install {pkg} from snap store",
        ],
        "cmd": "sudo snap install {pkg}",
        "slots": {"pkg": SNAP_PACKAGES},
    },
    {
        "nl": [
            "list installed snaps",
            "snap list",
            "show installed snap packages",
        ],
        "cmd": "snap list",
        "slots": {},
    },
    {
        "nl": [
            "install flatpak app {app}",
            "flatpak install {app}",
            "install {app} from flathub",
        ],
        "cmd": "flatpak install flathub {app}",
        "slots": {"app": FLATPAK_APPS},
    },
    {
        "nl": [
            "list installed flatpak apps",
            "flatpak list",
            "show installed flatpak applications",
        ],
        "cmd": "flatpak list",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 8. USER & GROUP EXTENDED
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "modify group {group} name to {newname}",
            "rename group {group} to {newname}",
            "change group name {group} to {newname}",
        ],
        "cmd": "sudo groupmod -n {newname} {group}",
        "slots": {"group": GROUPS[:4], "newname": ["devops", "engineering", "team", "ops"]},
    },
    {
        "nl": [
            "delete group {group}",
            "remove group {group}",
            "groupdel {group}",
        ],
        "cmd": "sudo groupdel {group}",
        "slots": {"group": GROUPS[:5]},
    },
    {
        "nl": [
            "add user {user} to group {group} with gpasswd",
            "gpasswd -a {user} {group}",
            "use gpasswd to add {user} to {group}",
        ],
        "cmd": "sudo gpasswd -a {user} {group}",
        "slots": {"user": USERS, "group": GROUPS},
    },
    {
        "nl": [
            "remove user {user} from group {group}",
            "gpasswd -d {user} {group}",
            "take {user} out of group {group}",
        ],
        "cmd": "sudo gpasswd -d {user} {group}",
        "slots": {"user": USERS, "group": GROUPS},
    },
    {
        "nl": [
            "set password expiry for {user} to {days} days",
            "chage -M {days} {user}",
            "expire password for {user} after {days} days",
        ],
        "cmd": "sudo chage -M {days} {user}",
        "slots": {"days": ["30", "60", "90", "180", "365"], "user": USERS},
    },
    {
        "nl": [
            "show password aging info for {user}",
            "chage -l {user}",
            "display password expiry for {user}",
        ],
        "cmd": "sudo chage -l {user}",
        "slots": {"user": USERS},
    },
    {
        "nl": [
            "force {user} to change password on next login",
            "expire password for {user}",
            "chage -d 0 {user}",
        ],
        "cmd": "sudo chage -d 0 {user}",
        "slots": {"user": USERS},
    },
    {
        "nl": [
            "show last logins",
            "last",
            "display login history",
            "who has logged in recently",
        ],
        "cmd": "last",
        "slots": {},
    },
    {
        "nl": [
            "show failed login attempts",
            "lastb",
            "display failed logins",
        ],
        "cmd": "sudo lastb",
        "slots": {},
    },
    {
        "nl": [
            "show last login for all users",
            "lastlog",
            "when did each user last log in",
        ],
        "cmd": "lastlog",
        "slots": {},
    },
    {
        "nl": [
            "lock user account {user}",
            "disable login for {user}",
            "lock {user} account",
        ],
        "cmd": "sudo passwd -l {user}",
        "slots": {"user": USERS},
    },
    {
        "nl": [
            "unlock user account {user}",
            "enable login for {user}",
            "unlock {user} account",
        ],
        "cmd": "sudo passwd -u {user}",
        "slots": {"user": USERS},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 9. HARDWARE INFO
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "list PCI devices",
            "lspci",
            "show PCI hardware",
            "what PCI devices are installed",
        ],
        "cmd": "lspci",
        "slots": {},
    },
    {
        "nl": [
            "show detailed PCI info",
            "lspci -v",
            "verbose PCI device listing",
        ],
        "cmd": "lspci -v",
        "slots": {},
    },
    {
        "nl": [
            "show info for PCI device {slot}",
            "lspci -s {slot} -v",
            "get details of PCI slot {slot}",
        ],
        "cmd": "lspci -s {slot} -v",
        "slots": {"slot": PCI_SLOTS},
    },
    {
        "nl": [
            "list USB devices",
            "lsusb",
            "show connected USB devices",
            "what USB devices are connected",
        ],
        "cmd": "lsusb",
        "slots": {},
    },
    {
        "nl": [
            "show detailed USB info",
            "lsusb -v",
            "verbose USB device listing",
        ],
        "cmd": "lsusb -v",
        "slots": {},
    },
    {
        "nl": [
            "show full hardware listing",
            "lshw",
            "list all hardware",
            "display hardware summary",
        ],
        "cmd": "sudo lshw -short",
        "slots": {},
    },
    {
        "nl": [
            "show BIOS and hardware info",
            "dmidecode",
            "display DMI/SMBIOS data",
            "get motherboard info",
        ],
        "cmd": "sudo dmidecode -t system",
        "slots": {},
    },
    {
        "nl": [
            "show memory hardware info",
            "dmidecode memory",
            "display RAM module details",
        ],
        "cmd": "sudo dmidecode -t memory",
        "slots": {},
    },
    {
        "nl": [
            "show BIOS info",
            "dmidecode bios",
            "display BIOS version and details",
        ],
        "cmd": "sudo dmidecode -t bios",
        "slots": {},
    },
    {
        "nl": [
            "show CPU temperature and fan speeds",
            "sensors",
            "display hardware temperatures",
            "check system temperatures",
        ],
        "cmd": "sensors",
        "slots": {},
    },
    {
        "nl": [
            "show system info summary",
            "inxi",
            "display system overview",
        ],
        "cmd": "inxi -Fxz",
        "slots": {},
    },
    {
        "nl": [
            "show memory ranges",
            "lsmem",
            "display memory block info",
        ],
        "cmd": "lsmem",
        "slots": {},
    },
    {
        "nl": [
            "show CPU info",
            "lscpu",
            "display CPU details",
            "what CPU does this machine have",
        ],
        "cmd": "lscpu",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 10. KERNEL MODULE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "list loaded kernel modules",
            "lsmod",
            "show loaded modules",
            "what kernel modules are loaded",
        ],
        "cmd": "lsmod",
        "slots": {},
    },
    {
        "nl": [
            "load kernel module {mod}",
            "modprobe {mod}",
            "enable module {mod}",
            "insert kernel module {mod}",
        ],
        "cmd": "sudo modprobe {mod}",
        "slots": {"mod": KERNEL_MODULES},
    },
    {
        "nl": [
            "unload kernel module {mod}",
            "modprobe -r {mod}",
            "remove module {mod}",
            "disable kernel module {mod}",
        ],
        "cmd": "sudo modprobe -r {mod}",
        "slots": {"mod": KERNEL_MODULES},
    },
    {
        "nl": [
            "show info about kernel module {mod}",
            "modinfo {mod}",
            "get details of module {mod}",
        ],
        "cmd": "modinfo {mod}",
        "slots": {"mod": KERNEL_MODULES},
    },
    {
        "nl": [
            "regenerate module dependencies",
            "depmod",
            "rebuild kernel module dependency list",
        ],
        "cmd": "sudo depmod -a",
        "slots": {},
    },
    {
        "nl": [
            "show kernel parameter {param}",
            "sysctl {param}",
            "read sysctl value {param}",
            "what is the value of {param}",
        ],
        "cmd": "sysctl {param}",
        "slots": {"param": SYSCTL_PARAMS},
    },
    {
        "nl": [
            "set kernel parameter {param} to {val}",
            "sysctl -w {param}={val}",
            "change sysctl {param} to {val}",
        ],
        "cmd": "sudo sysctl -w {param}={val}",
        "slots": {"param": SYSCTL_PARAMS, "val": SYSCTL_VALUES},
    },
    {
        "nl": [
            "show all kernel parameters",
            "sysctl -a",
            "list all sysctl values",
        ],
        "cmd": "sysctl -a",
        "slots": {},
    },
    {
        "nl": [
            "show kernel messages",
            "dmesg",
            "display kernel ring buffer",
            "show boot messages",
        ],
        "cmd": "dmesg",
        "slots": {},
    },
    {
        "nl": [
            "show recent kernel messages",
            "dmesg --since '5 minutes ago'",
            "display recent dmesg",
        ],
        "cmd": "dmesg -T --since '5 minutes ago'",
        "slots": {},
    },
    {
        "nl": [
            "follow kernel messages live",
            "dmesg -w",
            "watch kernel messages in real time",
        ],
        "cmd": "dmesg -w",
        "slots": {},
    },
    {
        "nl": [
            "search kernel messages for {pat}",
            "dmesg | grep {pat}",
            "filter dmesg for {pat}",
        ],
        "cmd": "dmesg | grep -i {pat}",
        "slots": {"pat": ["error", "usb", "memory", "disk", "nvidia", "network", "fail"]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 11. SECURITY & SELINUX / APPARMOR
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "encrypt {file} with gpg",
            "gpg encrypt {file}",
            "protect {file} with GPG encryption",
        ],
        "cmd": "gpg -c {file}",
        "slots": {"file": ["secret.txt", "passwords.csv", "backup.sql", "credentials.conf"]},
    },
    {
        "nl": [
            "decrypt {file} with gpg",
            "gpg decrypt {file}",
            "unencrypt {file}",
        ],
        "cmd": "gpg -d {file}",
        "slots": {"file": ["secret.txt.gpg", "passwords.csv.gpg", "backup.sql.gpg"]},
    },
    {
        "nl": [
            "sign {file} with gpg",
            "gpg sign {file}",
            "create a GPG signature for {file}",
        ],
        "cmd": "gpg --sign {file}",
        "slots": {"file": ["release.tar.gz", "package.deb", "update.rpm"]},
    },
    {
        "nl": [
            "verify gpg signature of {file}",
            "gpg verify {file}",
            "check GPG signature on {file}",
        ],
        "cmd": "gpg --verify {file}",
        "slots": {"file": ["release.tar.gz.sig", "package.deb.sig", "update.rpm.sig"]},
    },
    {
        "nl": [
            "list gpg keys",
            "gpg --list-keys",
            "show my GPG keys",
        ],
        "cmd": "gpg --list-keys",
        "slots": {},
    },
    {
        "nl": [
            "check fail2ban status",
            "fail2ban-client status",
            "show fail2ban jails",
        ],
        "cmd": "sudo fail2ban-client status",
        "slots": {},
    },
    {
        "nl": [
            "show fail2ban status for {jail}",
            "fail2ban-client status {jail}",
            "check {jail} jail in fail2ban",
        ],
        "cmd": "sudo fail2ban-client status {jail}",
        "slots": {"jail": ["sshd", "nginx-http-auth", "apache-auth", "postfix"]},
    },
    {
        "nl": [
            "ban IP {ip} in fail2ban jail {jail}",
            "fail2ban ban {ip} in {jail}",
            "block {ip} using fail2ban {jail}",
        ],
        "cmd": "sudo fail2ban-client set {jail} banip {ip}",
        "slots": {"jail": ["sshd", "nginx-http-auth"], "ip": ["10.0.0.50", "192.168.1.100"]},
    },
    {
        "nl": [
            "unban IP {ip} in fail2ban jail {jail}",
            "fail2ban unban {ip} in {jail}",
            "unblock {ip} in fail2ban {jail}",
        ],
        "cmd": "sudo fail2ban-client set {jail} unbanip {ip}",
        "slots": {"jail": ["sshd", "nginx-http-auth"], "ip": ["10.0.0.50", "192.168.1.100"]},
    },
    {
        "nl": [
            "check SELinux status",
            "getenforce",
            "is SELinux enabled",
            "show SELinux mode",
        ],
        "cmd": "getenforce",
        "slots": {},
    },
    {
        "nl": [
            "set SELinux to permissive mode",
            "setenforce 0",
            "disable SELinux enforcement temporarily",
        ],
        "cmd": "sudo setenforce 0",
        "slots": {},
    },
    {
        "nl": [
            "set SELinux to enforcing mode",
            "setenforce 1",
            "enable SELinux enforcement",
        ],
        "cmd": "sudo setenforce 1",
        "slots": {},
    },
    {
        "nl": [
            "show full SELinux status",
            "sestatus",
            "display SELinux configuration",
        ],
        "cmd": "sestatus",
        "slots": {},
    },
    {
        "nl": [
            "set SELinux boolean {bool} to on",
            "setsebool {bool} on",
            "enable SELinux boolean {bool}",
        ],
        "cmd": "sudo setsebool -P {bool} on",
        "slots": {"bool": SELINUX_BOOLEANS},
    },
    {
        "nl": [
            "restore SELinux context on {path}",
            "restorecon {path}",
            "fix SELinux labels on {path}",
        ],
        "cmd": "sudo restorecon -Rv {path}",
        "slots": {"path": ["/var/www/html", "/home/user/public_html", "/srv/data"]},
    },
    {
        "nl": [
            "show AppArmor status",
            "aa-status",
            "display AppArmor profiles",
        ],
        "cmd": "sudo aa-status",
        "slots": {},
    },
    {
        "nl": [
            "set AppArmor profile for {prog} to enforce",
            "aa-enforce {prog}",
            "enforce AppArmor on {prog}",
        ],
        "cmd": "sudo aa-enforce /etc/apparmor.d/{prog}",
        "slots": {"prog": ["usr.sbin.nginx", "usr.sbin.mysqld", "usr.bin.firefox"]},
    },
    {
        "nl": [
            "set AppArmor profile for {prog} to complain mode",
            "aa-complain {prog}",
            "put AppArmor {prog} in complain mode",
        ],
        "cmd": "sudo aa-complain /etc/apparmor.d/{prog}",
        "slots": {"prog": ["usr.sbin.nginx", "usr.sbin.mysqld", "usr.bin.firefox"]},
    },
    {
        "nl": [
            "search the audit log for {key}",
            "ausearch -k {key}",
            "find audit events matching {key}",
        ],
        "cmd": "sudo ausearch -k {key}",
        "slots": {"key": ["logins", "time-change", "access", "identity", "delete"]},
    },
    {
        "nl": [
            "show audit report summary",
            "aureport",
            "generate audit report",
        ],
        "cmd": "sudo aureport --summary",
        "slots": {},
    },
    {
        "nl": [
            "open LUKS encrypted volume {dev}",
            "cryptsetup open {dev}",
            "unlock LUKS volume {dev}",
        ],
        "cmd": "sudo cryptsetup luksOpen {dev} encrypted_vol",
        "slots": {"dev": PARTITIONS},
    },
    {
        "nl": [
            "close LUKS encrypted volume",
            "cryptsetup close encrypted_vol",
            "lock the encrypted volume",
        ],
        "cmd": "sudo cryptsetup luksClose encrypted_vol",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 12. SCHEDULING EXTENDED
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "schedule {cmd} to run at {time}",
            "run {cmd} at {time}",
            "at {time} run {cmd}",
        ],
        "cmd": "echo '{cmd}' | at {time}",
        "slots": {
            "cmd": ["backup.sh", "/opt/scripts/cleanup.sh", "reboot", "apt-get update"],
            "time": ["now + 1 hour", "now + 30 minutes", "midnight", "10:00 PM", "noon tomorrow"],
        },
    },
    {
        "nl": [
            "list scheduled at jobs",
            "atq",
            "show pending at jobs",
        ],
        "cmd": "atq",
        "slots": {},
    },
    {
        "nl": [
            "remove at job number {n}",
            "atrm {n}",
            "cancel scheduled job {n}",
        ],
        "cmd": "atrm {n}",
        "slots": {"n": ["1", "2", "3", "5", "10"]},
    },
    {
        "nl": [
            "run {cmd} when system load is low",
            "batch {cmd}",
            "execute {cmd} when load permits",
        ],
        "cmd": "echo '{cmd}' | batch",
        "slots": {"cmd": ["backup.sh", "/opt/scripts/cleanup.sh", "make -j4"]},
    },
    {
        "nl": [
            "run a transient systemd timer for {cmd}",
            "systemd-run {cmd}",
            "schedule {cmd} with systemd-run",
        ],
        "cmd": "sudo systemd-run --on-active='{delay}' {cmd}",
        "slots": {
            "cmd": ["/opt/scripts/cleanup.sh", "apt-get update", "/usr/local/bin/backup.sh"],
            "delay": ["5m", "1h", "30m", "2h"],
        },
    },
    {
        "nl": [
            "analyze systemd boot time",
            "systemd-analyze",
            "how long did boot take",
            "show boot time breakdown",
        ],
        "cmd": "systemd-analyze",
        "slots": {},
    },
    {
        "nl": [
            "show slowest systemd units at boot",
            "systemd-analyze blame",
            "which services are slowest to start",
        ],
        "cmd": "systemd-analyze blame",
        "slots": {},
    },
    {
        "nl": [
            "show critical chain of boot",
            "systemd-analyze critical-chain",
            "display boot critical path",
        ],
        "cmd": "systemd-analyze critical-chain",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 13. LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "write a message to syslog",
            "logger {msg}",
            "send message to system log",
        ],
        "cmd": "logger '{msg}'",
        "slots": {
            "msg": [
                "Deployment started",
                "Backup complete",
                "Maintenance window open",
                "Service restarted",
                "Alert: disk space low",
            ]
        },
    },
    {
        "nl": [
            "force log rotation",
            "logrotate -f",
            "rotate all logs now",
        ],
        "cmd": "sudo logrotate -f /etc/logrotate.conf",
        "slots": {},
    },
    {
        "nl": [
            "test logrotate config in debug mode",
            "logrotate -d",
            "dry run logrotate",
        ],
        "cmd": "sudo logrotate -d /etc/logrotate.conf",
        "slots": {},
    },
    {
        "nl": [
            "show logs for service {svc} with journalctl",
            "journalctl -u {svc}",
            "view logs of {svc}",
            "display systemd logs for {svc}",
        ],
        "cmd": "journalctl -u {svc}",
        "slots": {"svc": SERVICES},
    },
    {
        "nl": [
            "follow logs for service {svc}",
            "journalctl -fu {svc}",
            "tail logs of {svc} live",
        ],
        "cmd": "journalctl -fu {svc}",
        "slots": {"svc": SERVICES},
    },
    {
        "nl": [
            "show logs since {time}",
            "journalctl --since {time}",
            "display logs from {time}",
        ],
        "cmd": "journalctl --since '{time}'",
        "slots": {"time": ["1 hour ago", "today", "yesterday", "2024-01-01", "09:00"]},
    },
    {
        "nl": [
            "show journald disk usage",
            "journalctl --disk-usage",
            "how much space do systemd logs use",
        ],
        "cmd": "journalctl --disk-usage",
        "slots": {},
    },
    {
        "nl": [
            "vacuum journal logs to {size}",
            "clean up journald logs to {size}",
            "reduce systemd logs to {size}",
        ],
        "cmd": "sudo journalctl --vacuum-size={size}",
        "slots": {"size": ["100M", "500M", "1G", "2G"]},
    },
    {
        "nl": [
            "show kernel logs with journalctl",
            "journalctl -k",
            "display kernel messages from journal",
        ],
        "cmd": "journalctl -k",
        "slots": {},
    },
    {
        "nl": [
            "show boot logs",
            "journalctl -b",
            "display this boot's logs",
        ],
        "cmd": "journalctl -b",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 14. TERMINAL TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "create a new screen session named {name}",
            "screen -S {name}",
            "start screen session {name}",
        ],
        "cmd": "screen -S {name}",
        "slots": {"name": SCREEN_SESSIONS},
    },
    {
        "nl": [
            "reattach to screen session {name}",
            "screen -r {name}",
            "resume screen session {name}",
        ],
        "cmd": "screen -r {name}",
        "slots": {"name": SCREEN_SESSIONS},
    },
    {
        "nl": [
            "list screen sessions",
            "screen -ls",
            "show active screen sessions",
        ],
        "cmd": "screen -ls",
        "slots": {},
    },
    {
        "nl": [
            "create a new tmux session named {name}",
            "tmux new -s {name}",
            "start tmux session {name}",
        ],
        "cmd": "tmux new-session -s {name}",
        "slots": {"name": TMUX_SESSIONS},
    },
    {
        "nl": [
            "attach to tmux session {name}",
            "tmux attach -t {name}",
            "resume tmux session {name}",
        ],
        "cmd": "tmux attach-session -t {name}",
        "slots": {"name": TMUX_SESSIONS},
    },
    {
        "nl": [
            "list tmux sessions",
            "tmux ls",
            "show active tmux sessions",
        ],
        "cmd": "tmux list-sessions",
        "slots": {},
    },
    {
        "nl": [
            "kill tmux session {name}",
            "tmux kill-session -t {name}",
            "terminate tmux session {name}",
        ],
        "cmd": "tmux kill-session -t {name}",
        "slots": {"name": TMUX_SESSIONS},
    },
    {
        "nl": [
            "split tmux pane horizontally",
            "tmux split-window -h",
            "add a horizontal split in tmux",
        ],
        "cmd": "tmux split-window -h",
        "slots": {},
    },
    {
        "nl": [
            "split tmux pane vertically",
            "tmux split-window -v",
            "add a vertical split in tmux",
        ],
        "cmd": "tmux split-window -v",
        "slots": {},
    },
    {
        "nl": [
            "record terminal session to {file}",
            "script {file}",
            "start recording terminal to {file}",
        ],
        "cmd": "script {file}",
        "slots": {"file": ["session.log", "typescript", "recording.txt", "/tmp/session.log"]},
    },
    {
        "nl": [
            "run {cmd} with GNU parallel",
            "parallel {cmd}",
            "execute {cmd} in parallel",
        ],
        "cmd": "parallel {cmd} ::: {args}",
        "slots": {
            "cmd": ["gzip", "convert", "ping -c1"],
            "args": [
                "file1.txt file2.txt file3.txt",
                "img1.png img2.png img3.png",
                "host1 host2 host3",
            ],
        },
    },
    {
        "nl": [
            "show progress of a pipe with pv",
            "pipe {src} through pv",
            "monitor pipe throughput from {src}",
        ],
        "cmd": "pv {src} | gzip > {dst}",
        "slots": {
            "src": ["bigfile.tar", "dump.sql", "backup.img"],
            "dst": ["bigfile.tar.gz", "dump.sql.gz", "backup.img.gz"],
        },
    },
    {
        "nl": [
            "watch {cmd} every {n} seconds",
            "monitor {cmd} output with watch",
            "repeat {cmd} every {n} seconds",
        ],
        "cmd": "watch -n {n} '{cmd}'",
        "slots": {
            "n": ["1", "2", "5", "10"],
            "cmd": ["df -h", "free -h", "docker ps", "kubectl get pods", "ss -tulnp"],
        },
    },
    {
        "nl": [
            "watch {cmd} and highlight differences",
            "watch -d {cmd}",
            "monitor changes in {cmd} output",
        ],
        "cmd": "watch -d '{cmd}'",
        "slots": {"cmd": ["df -h", "free -h", "ss -tulnp", "ip addr"]},
    },
    {
        "nl": [
            "run {cmd} with a file lock on {lock}",
            "flock {lock} {cmd}",
            "ensure only one instance of {cmd} runs",
        ],
        "cmd": "flock -n {lock} {cmd}",
        "slots": {
            "lock": ["/tmp/backup.lock", "/var/lock/deploy.lock", "/tmp/cron.lock"],
            "cmd": ["/opt/scripts/backup.sh", "/opt/scripts/deploy.sh", "/usr/local/bin/sync.sh"],
        },
    },
    {
        "nl": [
            "clear the terminal",
            "clear",
            "reset the screen",
        ],
        "cmd": "clear",
        "slots": {},
    },
    {
        "nl": [
            "reset the terminal",
            "reset",
            "fix garbled terminal",
        ],
        "cmd": "reset",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 15. DATA PROCESSING TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "extract {field} from JSON file {file} with jq",
            "jq {field} from {file}",
            "get {field} from {file} using jq",
        ],
        "cmd": "jq '{field}' {file}",
        "slots": {
            "field": [".name", ".version", ".dependencies", ".[] | .id", ".data[0]"],
            "file": ["package.json", "config.json", "data.json", "response.json"],
        },
    },
    {
        "nl": [
            "pretty print JSON file {file}",
            "jq . {file}",
            "format {file} as pretty JSON",
        ],
        "cmd": "jq '.' {file}",
        "slots": {"file": ["data.json", "config.json", "response.json", "output.json"]},
    },
    {
        "nl": [
            "filter JSON array in {file} where {cond}",
            "jq select {cond} from {file}",
        ],
        "cmd": "jq '[.[] | select({cond})]' {file}",
        "slots": {
            "cond": [".age > 30", '.status == "active"', ".count > 0", ".name != null"],
            "file": ["data.json", "users.json", "items.json"],
        },
    },
    {
        "nl": [
            "calculate {expr} with bc",
            "bc calculate {expr}",
            "compute {expr}",
        ],
        "cmd": "echo '{expr}' | bc -l",
        "slots": {"expr": ["3.14 * 5^2", "100/3", "sqrt(144)", "2^32", "scale=4; 22/7"]},
    },
    {
        "nl": [
            "format {file} as a table",
            "column -t {file}",
            "display {file} in columns",
        ],
        "cmd": "column -t {file}",
        "slots": {"file": FILES_TEXT[:5]},
    },
    {
        "nl": [
            "format {file} as a table with {delim} separator",
            "column -t -s'{delim}' {file}",
            "tabulate {file} using {delim} delimiter",
        ],
        "cmd": "column -t -s'{delim}' {file}",
        "slots": {"delim": DELIMITERS[:3], "file": ["data.csv", "users.txt", "config.ini"]},
    },
    {
        "nl": [
            "validate XML file {file}",
            "xmllint {file}",
            "check XML syntax of {file}",
        ],
        "cmd": "xmllint --noout {file}",
        "slots": {"file": ["config.xml", "pom.xml", "web.xml", "data.xml"]},
    },
    {
        "nl": [
            "pretty print XML file {file}",
            "xmllint --format {file}",
            "format XML in {file}",
        ],
        "cmd": "xmllint --format {file}",
        "slots": {"file": ["config.xml", "pom.xml", "web.xml", "data.xml"]},
    },
    {
        "nl": [
            "convert JSON to CSV from {file}",
            "transform {file} from JSON to CSV",
        ],
        "cmd": "jq -r '.[] | [.id, .name, .value] | @csv' {file}",
        "slots": {"file": ["data.json", "export.json", "records.json"]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 16. DEVELOPER TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "show shared library dependencies of {bin}",
            "ldd {bin}",
            "what libraries does {bin} link to",
        ],
        "cmd": "ldd {bin}",
        "slots": {
            "bin": [
                "/usr/bin/ls",
                "/usr/bin/bash",
                "/usr/bin/python3",
                "/usr/bin/nginx",
                "/usr/bin/curl",
                "/usr/bin/git",
            ]
        },
    },
    {
        "nl": [
            "disassemble {bin}",
            "objdump -d {bin}",
            "show assembly of {bin}",
        ],
        "cmd": "objdump -d {bin}",
        "slots": {"bin": ["a.out", "main.o", "/usr/bin/ls"]},
    },
    {
        "nl": [
            "show ELF headers of {bin}",
            "readelf -h {bin}",
            "display ELF info for {bin}",
        ],
        "cmd": "readelf -h {bin}",
        "slots": {"bin": ["a.out", "main.o", "/usr/bin/ls", "/usr/bin/bash"]},
    },
    {
        "nl": [
            "show all ELF sections of {bin}",
            "readelf -S {bin}",
            "list sections in {bin}",
        ],
        "cmd": "readelf -S {bin}",
        "slots": {"bin": ["a.out", "main.o", "/usr/bin/ls"]},
    },
    {
        "nl": [
            "show symbol table of {bin}",
            "nm {bin}",
            "list symbols in {bin}",
        ],
        "cmd": "nm {bin}",
        "slots": {"bin": ["a.out", "main.o", "libfoo.a", "libbar.so"]},
    },
    {
        "nl": [
            "strip debug symbols from {bin}",
            "strip {bin}",
            "remove debug info from {bin}",
        ],
        "cmd": "strip {bin}",
        "slots": {"bin": ["a.out", "main", "server", "app"]},
    },
    {
        "nl": [
            "build with make using {n} parallel jobs",
            "make -j{n}",
            "compile with {n} parallel threads",
        ],
        "cmd": "make -j{n}",
        "slots": {"n": ["2", "4", "8", "$(nproc)"]},
    },
    {
        "nl": [
            "clean build artifacts with make",
            "make clean",
            "remove compiled files",
        ],
        "cmd": "make clean",
        "slots": {},
    },
    {
        "nl": [
            "compile {src} with gcc",
            "gcc {src}",
            "build {src} with gcc",
        ],
        "cmd": "gcc -o {out} {src}",
        "slots": {
            "src": ["main.c", "app.c", "server.c", "hello.c"],
            "out": ["main", "app", "server", "hello"],
        },
    },
    {
        "nl": [
            "compile {src} with g++ and C++17",
            "g++ -std=c++17 {src}",
            "build {src} as C++17",
        ],
        "cmd": "g++ -std=c++17 -o {out} {src}",
        "slots": {
            "src": ["main.cpp", "app.cpp", "server.cpp"],
            "out": ["main", "app", "server"],
        },
    },
    {
        "nl": [
            "run {bin} under valgrind",
            "valgrind {bin}",
            "check {bin} for memory leaks",
        ],
        "cmd": "valgrind --leak-check=full ./{bin}",
        "slots": {"bin": ["a.out", "main", "app", "server"]},
    },
    {
        "nl": [
            "debug {bin} with gdb",
            "gdb {bin}",
            "start debugger on {bin}",
        ],
        "cmd": "gdb ./{bin}",
        "slots": {"bin": ["a.out", "main", "app", "server"]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 17. MISC SYSTEM TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "change root to {dir}",
            "chroot into {dir}",
            "enter chroot at {dir}",
        ],
        "cmd": "sudo chroot {dir}",
        "slots": {"dir": ["/mnt/sysimage", "/mnt/root", "/opt/chroot", "/srv/jail"]},
    },
    {
        "nl": [
            "list all namespaces",
            "lsns",
            "show active namespaces",
        ],
        "cmd": "lsns",
        "slots": {},
    },
    {
        "nl": [
            "show resource limits",
            "ulimit -a",
            "display all ulimits",
            "what are the current resource limits",
        ],
        "cmd": "ulimit -a",
        "slots": {},
    },
    {
        "nl": [
            "show resource limits for process {pid}",
            "prlimit --pid {pid}",
            "display limits of PID {pid}",
        ],
        "cmd": "prlimit --pid {pid}",
        "slots": {"pid": PIDS},
    },
    {
        "nl": [
            "set ACL for {user} on {path} with {perm} permissions",
            "setfacl for {user} on {path}",
            "grant {user} {perm} on {path} via ACL",
        ],
        "cmd": "setfacl -m u:{user}:{perm} {path}",
        "slots": {
            "user": USERS[:5],
            "perm": ["rwx", "rx", "r", "rw"],
            "path": ["/srv/data", "/var/www/html", "/opt/app", "/home/shared"],
        },
    },
    {
        "nl": [
            "show ACL for {path}",
            "getfacl {path}",
            "display access control list of {path}",
        ],
        "cmd": "getfacl {path}",
        "slots": {"path": ["/srv/data", "/var/www/html", "/opt/app", "/home/shared"]},
    },
    {
        "nl": [
            "where is the {cmd} binary",
            "whereis {cmd}",
            "find the location of {cmd}",
        ],
        "cmd": "whereis {cmd}",
        "slots": {"cmd": ["python3", "nginx", "gcc", "java", "docker", "node"]},
    },
    {
        "nl": [
            "what type of command is {cmd}",
            "type {cmd}",
            "is {cmd} a builtin or external command",
        ],
        "cmd": "type {cmd}",
        "slots": {"cmd": ["cd", "echo", "ls", "grep", "python3", "git", "alias"]},
    },
    {
        "nl": [
            "check if {cmd} exists",
            "command -v {cmd}",
            "which {cmd}",
            "is {cmd} installed",
        ],
        "cmd": "command -v {cmd}",
        "slots": {"cmd": ["python3", "docker", "nginx", "node", "java", "gcc", "go", "ruby"]},
    },
    {
        "nl": [
            "set the timezone to {tz}",
            "timedatectl set-timezone {tz}",
            "change timezone to {tz}",
        ],
        "cmd": "sudo timedatectl set-timezone {tz}",
        "slots": {"tz": TIMEZONES},
    },
    {
        "nl": [
            "show the current timezone",
            "timedatectl",
            "what timezone is this system in",
        ],
        "cmd": "timedatectl",
        "slots": {},
    },
    {
        "nl": [
            "set the hostname to {name}",
            "hostnamectl set-hostname {name}",
            "change hostname to {name}",
        ],
        "cmd": "sudo hostnamectl set-hostname {name}",
        "slots": {"name": ["webserver", "db-primary", "app-01", "dev-box", "prod-api"]},
    },
    {
        "nl": [
            "show hostname info",
            "hostnamectl",
            "display hostname details",
        ],
        "cmd": "hostnamectl",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 18. macOS-SPECIFIC
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_EXTENDED += [
    {
        "nl": [
            "read macOS default {key} for {domain}",
            "defaults read {domain} {key}",
            "show macOS preference {key} in {domain}",
        ],
        "cmd": "defaults read {domain} {key}",
        "slots": {"domain": MACOS_DOMAINS, "key": MACOS_KEYS},
    },
    {
        "nl": [
            "set macOS default {key} to true for {domain}",
            "defaults write {domain} {key} -bool true",
            "enable {key} in {domain}",
        ],
        "cmd": "defaults write {domain} {key} -bool true",
        "slots": {"domain": MACOS_DOMAINS, "key": MACOS_KEYS},
    },
    {
        "nl": [
            "delete macOS default {key} from {domain}",
            "defaults delete {domain} {key}",
            "remove preference {key} from {domain}",
        ],
        "cmd": "defaults delete {domain} {key}",
        "slots": {"domain": MACOS_DOMAINS, "key": MACOS_KEYS},
    },
    {
        "nl": [
            "list all disks",
            "diskutil list",
            "show all drives on macOS",
        ],
        "cmd": "diskutil list",
        "slots": {},
    },
    {
        "nl": [
            "show disk info for {disk}",
            "diskutil info {disk}",
            "get details of {disk}",
        ],
        "cmd": "diskutil info {disk}",
        "slots": {"disk": ["disk0", "disk1", "disk0s1", "disk1s1"]},
    },
    {
        "nl": [
            "mount disk {disk}",
            "diskutil mount {disk}",
            "attach {disk}",
        ],
        "cmd": "diskutil mount {disk}",
        "slots": {"disk": ["disk2s1", "disk3s1", "disk2"]},
    },
    {
        "nl": [
            "unmount disk {disk}",
            "diskutil unmount {disk}",
            "eject {disk}",
        ],
        "cmd": "diskutil unmount {disk}",
        "slots": {"disk": ["disk2s1", "disk3s1", "disk2"]},
    },
    {
        "nl": [
            "list launchctl services",
            "launchctl list",
            "show macOS services",
        ],
        "cmd": "launchctl list",
        "slots": {},
    },
    {
        "nl": [
            "start macOS service {svc}",
            "launchctl start {svc}",
            "launch {svc}",
        ],
        "cmd": "launchctl start {svc}",
        "slots": {"svc": MACOS_SERVICES},
    },
    {
        "nl": [
            "stop macOS service {svc}",
            "launchctl stop {svc}",
            "halt {svc}",
        ],
        "cmd": "launchctl stop {svc}",
        "slots": {"svc": MACOS_SERVICES},
    },
    {
        "nl": [
            "copy text to macOS clipboard",
            "echo '{text}' | pbcopy",
            "put {text} on the clipboard",
        ],
        "cmd": "echo '{text}' | pbcopy",
        "slots": {"text": ["hello world", "$(pwd)", "$(date)", "copied text"]},
    },
    {
        "nl": [
            "paste from macOS clipboard",
            "pbpaste",
            "show clipboard contents",
        ],
        "cmd": "pbpaste",
        "slots": {},
    },
    {
        "nl": [
            "open {target} on macOS",
            "open {target}",
            "launch {target}",
        ],
        "cmd": "open {target}",
        "slots": {
            "target": [
                ".",
                "~/Documents",
                "https://example.com",
                "/Applications/Safari.app",
                "file.pdf",
                "image.png",
            ]
        },
    },
    {
        "nl": [
            "search for files named {name} with Spotlight",
            "mdfind {name}",
            "use Spotlight to find {name}",
        ],
        "cmd": "mdfind -name {name}",
        "slots": {"name": ["nginx.conf", "settings.py", "index.html", ".env", "Dockerfile"]},
    },
    {
        "nl": [
            "say {text} aloud on macOS",
            "say {text}",
            "text to speech {text}",
        ],
        "cmd": "say '{text}'",
        "slots": {
            "text": ["hello world", "build complete", "deployment finished", "error detected"]
        },
    },
    {
        "nl": [
            "prevent macOS from sleeping",
            "caffeinate",
            "keep the Mac awake",
            "disable sleep on macOS",
        ],
        "cmd": "caffeinate -d",
        "slots": {},
    },
    {
        "nl": [
            "prevent sleep while running {cmd}",
            "caffeinate {cmd}",
            "keep Mac awake during {cmd}",
        ],
        "cmd": "caffeinate -i {cmd}",
        "slots": {"cmd": ["make -j4", "python3 train.py", "./backup.sh", "rsync -av src/ dest/"]},
    },
    {
        "nl": [
            "list available macOS software updates",
            "softwareupdate -l",
            "check for macOS updates",
        ],
        "cmd": "softwareupdate -l",
        "slots": {},
    },
    {
        "nl": [
            "install all macOS software updates",
            "softwareupdate -ia",
            "update macOS",
        ],
        "cmd": "sudo softwareupdate -ia",
        "slots": {},
    },
    {
        "nl": [
            "show macOS network interfaces",
            "networksetup -listallhardwareports",
            "list network adapters on macOS",
        ],
        "cmd": "networksetup -listallhardwareports",
        "slots": {},
    },
    {
        "nl": [
            "set DNS on {iface} to {dns}",
            "networksetup -setdnsservers {iface} {dns}",
            "change DNS for {iface} to {dns}",
        ],
        "cmd": "networksetup -setdnsservers {iface} {dns}",
        "slots": {
            "iface": ["Wi-Fi", "Ethernet", "Thunderbolt Bridge"],
            "dns": ["8.8.8.8", "1.1.1.1", "208.67.222.222"],
        },
    },
    {
        "nl": [
            "show macOS hardware profile",
            "system_profiler SPHardwareDataType",
            "display Mac hardware info",
        ],
        "cmd": "system_profiler SPHardwareDataType",
        "slots": {},
    },
    {
        "nl": [
            "show macOS version",
            "sw_vers",
            "what version of macOS is this",
        ],
        "cmd": "sw_vers",
        "slots": {},
    },
    {
        "nl": [
            "copy {src} to {dst} preserving metadata on macOS",
            "ditto {src} {dst}",
            "macOS copy with metadata from {src} to {dst}",
        ],
        "cmd": "ditto {src} {dst}",
        "slots": {
            "src": ["~/Documents/project", "/opt/app", "~/Photos"],
            "dst": ["/Volumes/Backup/project", "/tmp/app_copy", "/Volumes/Backup/Photos"],
        },
    },
    {
        "nl": [
            "convert plist {file} to xml",
            "plutil -convert xml1 {file}",
            "change {file} plist to XML format",
        ],
        "cmd": "plutil -convert xml1 {file}",
        "slots": {"file": ["Info.plist", "Preferences.plist", "config.plist"]},
    },
    {
        "nl": [
            "convert plist {file} to json",
            "plutil -convert json {file}",
            "change {file} plist to JSON format",
        ],
        "cmd": "plutil -convert json {file}",
        "slots": {"file": ["Info.plist", "Preferences.plist", "config.plist"]},
    },
    {
        "nl": [
            "show Time Machine backup status",
            "tmutil status",
            "is Time Machine running",
        ],
        "cmd": "tmutil status",
        "slots": {},
    },
    {
        "nl": [
            "start a Time Machine backup",
            "tmutil startbackup",
            "begin Time Machine backup now",
        ],
        "cmd": "tmutil startbackup",
        "slots": {},
    },
    {
        "nl": [
            "create a macOS disk image from {dir}",
            "hdiutil create from {dir}",
            "make a DMG from {dir}",
        ],
        "cmd": "hdiutil create -volname {name} -srcfolder {dir} -ov {name}.dmg",
        "slots": {
            "name": ["MyApp", "Backup", "Archive"],
            "dir": ["~/Documents/project", "/opt/app", "build/dist"],
        },
    },
    {
        "nl": [
            "mount disk image {file}",
            "hdiutil attach {file}",
            "open DMG {file}",
        ],
        "cmd": "hdiutil attach {file}",
        "slots": {"file": ["app.dmg", "installer.dmg", "backup.dmg"]},
    },
    {
        "nl": [
            "unmount disk image {vol}",
            "hdiutil detach {vol}",
            "eject DMG at {vol}",
        ],
        "cmd": "hdiutil detach {vol}",
        "slots": {"vol": ["/Volumes/MyApp", "/Volumes/Backup", "/Volumes/Installer"]},
    },
    {
        "nl": [
            "show macOS power settings",
            "pmset -g",
            "display power management settings",
        ],
        "cmd": "pmset -g",
        "slots": {},
    },
    {
        "nl": [
            "resize image {file} to {size} on macOS",
            "sips --resampleWidth {size} {file}",
            "scale {file} to {size} pixels wide",
        ],
        "cmd": "sips --resampleWidth {size} {file}",
        "slots": {
            "size": ["800", "1024", "1920", "640"],
            "file": ["photo.jpg", "image.png", "screenshot.png"],
        },
    },
    {
        "nl": [
            "convert {file} to {fmt} on macOS",
            "sips -s format {fmt} {file}",
            "change image format of {file} to {fmt}",
        ],
        "cmd": "sips -s format {fmt} {file} --out {file}.{fmt}",
        "slots": {
            "fmt": ["png", "jpeg", "tiff", "bmp"],
            "file": ["image.png", "photo.jpg", "icon.tiff"],
        },
    },
    {
        "nl": [
            "check SIP status on macOS",
            "csrutil status",
            "is System Integrity Protection enabled",
        ],
        "cmd": "csrutil status",
        "slots": {},
    },
    {
        "nl": [
            "show macOS unified log stream",
            "log stream",
            "watch live macOS system logs",
        ],
        "cmd": "log stream --level info",
        "slots": {},
    },
    {
        "nl": [
            "show macOS logs for process {proc}",
            "log show --process {proc}",
            "view logs for {proc} on macOS",
        ],
        "cmd": "log show --process {proc} --last 1h",
        "slots": {"proc": ["nginx", "sshd", "kernel", "WindowServer", "Finder"]},
    },
    {
        "nl": [
            "show macOS hostname",
            "scutil --get HostName",
            "what is this Mac's hostname",
        ],
        "cmd": "scutil --get HostName",
        "slots": {},
    },
    {
        "nl": [
            "set macOS hostname to {name}",
            "scutil --set HostName {name}",
            "change Mac hostname to {name}",
        ],
        "cmd": "sudo scutil --set HostName {name}",
        "slots": {"name": ["macbook-pro", "dev-mac", "workstation", "build-server"]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 19. IDENTITY — override Qwen's self-identification
# ═══════════════════════════════════════════════════════════════════════════════

IDENTITY_EXTENDED: list[dict] = [
    {
        "nl": [
            "who are you",
            "who are you?",
            "what's your name",
            "what is your name",
            "tell me about yourself",
            "introduce yourself",
            "what should I call you",
        ],
        "response": "I'm INCEPT, a Linux/macOS command-line assistant. I translate plain English into shell commands. Just tell me what you need to do and I'll give you the command.",
    },
    {
        "nl": [
            "are you chatgpt",
            "are you gpt",
            "are you qwen",
            "are you llama",
            "are you gemini",
            "are you claude",
            "what model are you",
            "what LLM are you",
            "which AI are you",
            "what language model are you based on",
        ],
        "response": "I'm INCEPT, a specialized command-line assistant for Linux and macOS. I'm not a general-purpose chatbot — I'm built to generate shell commands from natural language.",
    },
    {
        "nl": [
            "who made you",
            "who created you",
            "who built you",
            "who developed you",
        ],
        "response": "I'm INCEPT, built as a specialized Linux/macOS command assistant. How can I help you today?",
    },
    {
        "nl": [
            "what are you capable of",
            "what do you do",
            "how can you help me",
            "what are your abilities",
        ],
        "response": "I'm INCEPT. I generate Linux and macOS shell commands from plain English. I cover package management, file operations, networking, disk management, user administration, security, and more across Ubuntu, RHEL, Arch, SUSE, and macOS.\n\nJust describe what you want to do — for example: 'install nginx', 'find large files', or 'show disk usage'.",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 20. ADDITIONAL SAFETY REFUSALS
# ═══════════════════════════════════════════════════════════════════════════════

SAFETY_REFUSALS_EXTENDED: list[dict] = [
    {
        "nl": [
            "wipefs the system disk",
            "wipefs /dev/sda",
            "clear filesystem signatures on the main disk",
        ],
        "response": "I won't clear filesystem signatures on a system disk. That would make the system unbootable.\nTo safely identify filesystems: lsblk -f\nTo wipe a non-system USB drive: sudo wipefs -a /dev/sdX (verify with lsblk first!)",
    },
    {
        "nl": [
            "flush all iptables rules on production",
            "iptables -F on the production server",
            "clear all firewall rules in production",
        ],
        "response": "I won't flush all firewall rules on a production server. That would expose all services to the internet.\nTo safely review rules: sudo iptables -L -n -v\nTo remove a specific rule: sudo iptables -D INPUT <rule-number>",
    },
    {
        "nl": [
            "delete the system partition with parted",
            "parted rm the root partition",
            "remove partition 1 on the system disk",
        ],
        "response": "I won't delete system partitions. That would destroy the operating system and all data.\nTo safely view partitions: sudo fdisk -l\nTo manage partitions safely, use a live USB environment.",
    },
    {
        "nl": [
            "format /dev/sda as swap",
            "mkswap /dev/sda",
            "make the entire system disk swap space",
        ],
        "response": "I won't format the system disk as swap. That would destroy all data and the OS.\nTo create a swap file instead: sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile",
    },
    {
        "nl": [
            "unload the ext4 module while filesystems are mounted",
            "modprobe -r ext4",
            "remove the ext4 kernel module",
        ],
        "response": "I won't unload the ext4 module while ext4 filesystems are mounted. That would crash the system.\nTo check mounted filesystems: mount | grep ext4\nTo check module usage: lsmod | grep ext4",
    },
    {
        "nl": [
            "disable all network filtering with sysctl",
            "sysctl turn off nf_conntrack",
            "disable the kernel firewall entirely",
        ],
        "response": "I won't disable kernel network filtering entirely. That removes all firewall protection.\nTo check current settings: sysctl net.netfilter.nf_conntrack_max\nTo adjust connection tracking limits safely: sudo sysctl -w net.netfilter.nf_conntrack_max=262144",
    },
    {
        "nl": [
            "dd if=/dev/zero of=/dev/nvme0n1",
            "zero out the NVMe drive",
            "overwrite the NVMe SSD with zeros",
        ],
        "response": "I can't do that. Writing zeros to the NVMe drive would destroy all data including the OS.\nTo securely erase a specific file: shred -vfz -n 3 <filename>\nTo check disk usage: df -h",
    },
    {
        "nl": [
            "encrypt the system disk with cryptsetup luksFormat",
            "cryptsetup luksFormat /dev/sda",
            "LUKS format the root disk",
        ],
        "response": "I won't LUKS-format the system disk. That would destroy all data. Disk encryption must be set up during OS installation or with a live environment.\nTo encrypt a non-system partition: sudo cryptsetup luksFormat /dev/sdX (verify it's not the system disk with lsblk first!)",
    },
    {
        "nl": [
            "set vm.overcommit_memory to 2 and crash all apps",
            "sysctl disable memory overcommit",
            "set the OOM killer to kill everything",
        ],
        "response": "Changing memory overcommit settings carelessly can cause widespread application crashes.\nTo check current setting: sysctl vm.overcommit_memory\nTo monitor memory: free -h && cat /proc/meminfo",
    },
    {
        "nl": [
            "delete the MBR",
            "dd if=/dev/zero of=/dev/sda bs=446 count=1",
            "wipe the master boot record",
        ],
        "response": "I won't wipe the MBR. That would make the system unbootable.\nTo back up the MBR: sudo dd if=/dev/sda of=mbr_backup.bin bs=512 count=1\nTo check the partition table: sudo fdisk -l /dev/sda",
    },
    {
        "nl": [
            "kill -9 1",
            "kill init",
            "kill PID 1",
            "terminate the init process",
        ],
        "response": "I won't kill PID 1 (init/systemd). That would crash the entire system.\nTo gracefully reboot: sudo reboot\nTo shutdown: sudo shutdown now",
    },
    {
        "nl": [
            "chmod 000 /etc/shadow",
            "remove all permissions from /etc/shadow",
            "make shadow file unreadable",
        ],
        "response": "I won't change permissions on /etc/shadow. That could lock everyone out of the system.\nCorrect permissions for /etc/shadow are 640 owned by root:shadow.\nTo check: ls -la /etc/shadow",
    },
]
