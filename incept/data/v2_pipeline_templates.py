"""Pipeline & compositional command templates for INCEPT v2.

Adds ~460 templates focused on pipes, multi-step commands, regex construction,
advanced awk/sed, log analysis, and real-world compositional patterns.

Import TEMPLATES_PIPELINE in generate_v2_data.py.
"""

from __future__ import annotations

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         PIPELINE SLOT POOLS                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Log files for parsing scenarios
LOG_FILES = ["access.log", "error.log", "syslog", "auth.log", "messages", "kern.log"]
ACCESS_LOGS = [
    "access.log",
    "/var/log/nginx/access.log",
    "/var/log/apache2/access.log",
    "/var/log/httpd/access_log",
]
AUTH_LOGS = ["auth.log", "/var/log/auth.log", "/var/log/secure"]

# Regex slot pools
REGEX_FILES = ["access.log", "data.txt", "output.log", "server.log", "messages.log", "app.log"]

# Process names
PROC_NAMES = [
    "python",
    "node",
    "java",
    "nginx",
    "apache2",
    "postgres",
    "mysql",
    "redis",
    "docker",
    "ssh",
]

# Awk delimiters
AWK_DELIMITERS = [",", ":", ";", "\\t", "|", " "]

# Sed patterns
SED_OLD = ["error", "warning", "foo", "old_value", "localhost", "http://"]
SED_NEW = ["info", "notice", "bar", "new_value", "server.example.com", "https://"]

# Shell variables
VAR_NAMES = ["PATH", "HOME", "EDITOR", "LANG", "MY_VAR", "APP_PORT", "DB_HOST", "LOG_LEVEL"]
VAR_VALUES = [
    "/usr/local/bin",
    "/home/user",
    "vim",
    "en_US.UTF-8",
    "production",
    "3000",
    "localhost",
    "debug",
]

# Append/write content
TEXT_LINES = [
    "nameserver 8.8.8.8",
    "export PATH=$PATH:/usr/local/bin",
    "alias ll='ls -la'",
    "127.0.0.1 myhost",
    "* * * * * /usr/bin/command",
]

# File extensions for batch rename
OLD_EXTS = [".txt", ".log", ".bak", ".tmp", ".csv"]
NEW_EXTS = [".md", ".log.gz", ".old", ".processed", ".tsv"]

# HTTP status codes
HTTP_CODES = ["200", "301", "403", "404", "500", "502", "503"]

# Reuse from base
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
LINES_N = ["5", "10", "20", "50", "100"]

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                       PIPELINE TEMPLATES                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

TEMPLATES_PIPELINE: list[dict] = []

# ═══════════════════════════════════════════════════════════════════════════════
# Category 1: PIPE BASICS (~30 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "filter the output of ls for {pattern}",
            "list files and grep for {pattern}",
            "show only files matching {pattern} in current directory",
        ],
        "cmd": "ls | grep {pattern}",
        "slots": {"pattern": SEARCH_PATTERNS},
    },
    {
        "nl": [
            "show the first {n} lines of {file}",
            "display the top {n} lines of {file}",
            "print the first {n} lines from {file}",
            "get the first {n} lines of {file}",
        ],
        "cmd": "head -n {n} {file}",
        "slots": {"n": LINES_N, "file": FILES_TEXT},
    },
    {
        "nl": [
            "show the last {n} lines of {file}",
            "display the bottom {n} lines of {file}",
            "print the last {n} lines from {file}",
            "get the last {n} lines of {file}",
        ],
        "cmd": "tail -n {n} {file}",
        "slots": {"n": LINES_N, "file": FILES_TEXT},
    },
    {
        "nl": [
            "count the number of lines in {file}",
            "how many lines are in {file}",
            "get the line count of {file}",
        ],
        "cmd": "wc -l {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "count words in {file}",
            "how many words are in {file}",
            "get the word count of {file}",
        ],
        "cmd": "wc -w {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "sort {file} alphabetically",
            "sort the contents of {file}",
            "sort the lines in {file}",
        ],
        "cmd": "sort {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "sort {file} in reverse order",
            "reverse sort {file}",
            "sort {file} in descending order",
        ],
        "cmd": "sort -r {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "sort {file} numerically",
            "sort the numbers in {file}",
            "numerically sort {file}",
        ],
        "cmd": "sort -n {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "sort {file} numerically in descending order",
            "reverse numeric sort of {file}",
            "sort {file} by number descending",
        ],
        "cmd": "sort -rn {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "remove duplicate lines from {file}",
            "deduplicate {file}",
            "show unique lines in {file}",
            "remove duplicates from {file}",
        ],
        "cmd": "sort {file} | uniq",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "count duplicate lines in {file}",
            "show frequency of each line in {file}",
            "count occurrences of each line in {file}",
        ],
        "cmd": "sort {file} | uniq -c",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "write output of ls to {file} and also display it",
            "save directory listing to {file} while showing it",
            "tee the output of ls to {file}",
        ],
        "cmd": "ls | tee {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "append output of ls to {file} while showing it",
            "tee append the directory listing to {file}",
        ],
        "cmd": "ls | tee -a {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "find all .py files and delete them",
            "remove all python files in current directory tree",
            "delete all *.py files recursively",
        ],
        "cmd": "find . -name '*.py' | xargs rm",
        "slots": {},
    },
    {
        "nl": [
            "redirect stdout and stderr of {cmd} to {file}",
            "send all output of {cmd} to {file}",
            "capture both stdout and stderr of {cmd} in {file}",
        ],
        "cmd": "{cmd} > {file} 2>&1",
        "slots": {
            "cmd": ["make", "npm install", "python script.py", "cargo build", "gcc main.c"],
            "file": ["output.log", "build.log", "compile.log", "run.log"],
        },
    },
    {
        "nl": [
            "discard error output from {cmd}",
            "suppress errors from {cmd}",
            "run {cmd} and hide stderr",
            "silence errors from {cmd}",
        ],
        "cmd": "{cmd} 2>/dev/null",
        "slots": {
            "cmd": [
                "find / -name '*.conf'",
                "grep -r error /var/log",
                "ls /root",
                "cat /etc/shadow",
            ],
        },
    },
    {
        "nl": [
            "run {cmd1} and if it succeeds run {cmd2}",
            "execute {cmd2} only if {cmd1} succeeds",
            "chain {cmd1} then {cmd2} on success",
        ],
        "cmd": "{cmd1} && {cmd2}",
        "slots": {
            "cmd1": ["mkdir -p /tmp/build", "cd /opt/app", "git pull", "make clean"],
            "cmd2": ["cd /tmp/build", "npm install", "make", "make install"],
        },
    },
    {
        "nl": [
            "run {cmd2} if {cmd1} fails",
            "execute {cmd2} as fallback for {cmd1}",
            "try {cmd1} or else {cmd2}",
        ],
        "cmd": "{cmd1} || {cmd2}",
        "slots": {
            "cmd1": ["ping -c1 google.com", "which python3", "test -f config.yaml"],
            "cmd2": ["echo 'no network'", "which python", "echo 'config missing'"],
        },
    },
    {
        "nl": [
            "run {cmd} in the background",
            "execute {cmd} as a background job",
            "start {cmd} in background",
        ],
        "cmd": "{cmd} &",
        "slots": {
            "cmd": ["python server.py", "node app.js", "tail -f /var/log/syslog", "./long_task.sh"],
        },
    },
    {
        "nl": [
            "run {cmd} in the background and keep it running after logout",
            "start {cmd} with nohup",
            "run {cmd} persistently in background",
            "execute {cmd} so it survives logout",
        ],
        "cmd": "nohup {cmd} &",
        "slots": {
            "cmd": ["python server.py", "node app.js", "./long_task.sh", "java -jar app.jar"],
        },
    },
    {
        "nl": [
            "get the current date and save it to {file}",
            "write today's date to {file}",
            "store the date in {file}",
        ],
        "cmd": "date > {file}",
        "slots": {"file": ["date.txt", "timestamp.log", "now.txt"]},
    },
    {
        "nl": [
            "count how many files are in the current directory",
            "how many files in current dir",
            "number of files here",
        ],
        "cmd": "ls | wc -l",
        "slots": {},
    },
    {
        "nl": [
            "list running processes and search for {proc}",
            "check if {proc} is running using ps and grep",
            "find {proc} in process list",
        ],
        "cmd": "ps aux | grep {proc}",
        "slots": {"proc": PROC_NAMES},
    },
    {
        "nl": [
            "pipe dmesg output through less",
            "view dmesg output page by page",
            "page through kernel messages",
        ],
        "cmd": "dmesg | less",
        "slots": {},
    },
    {
        "nl": [
            "show unique sorted entries from {file}",
            "sort {file} and remove duplicates",
            "get sorted unique lines from {file}",
        ],
        "cmd": "sort -u {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "count how many processes are running",
            "number of running processes",
            "how many processes are active",
        ],
        "cmd": "ps aux | wc -l",
        "slots": {},
    },
    {
        "nl": [
            "list environment variables and search for {pattern}",
            "find environment variable matching {pattern}",
            "search env vars for {pattern}",
        ],
        "cmd": "env | grep {pattern}",
        "slots": {"pattern": ["PATH", "HOME", "LANG", "USER", "SHELL", "TERM"]},
    },
    {
        "nl": [
            "show disk usage sorted by size",
            "list directories by size in human readable format",
            "sort disk usage output by size",
        ],
        "cmd": "du -sh * | sort -rh",
        "slots": {},
    },
    {
        "nl": [
            "follow {file} in real time",
            "watch {file} for new lines",
            "live tail of {file}",
            "stream new lines from {file}",
        ],
        "cmd": "tail -f {file}",
        "slots": {"file": LOG_FILES},
    },
    {
        "nl": [
            "get the hostname and save it to a variable",
            "store hostname in a shell variable",
            "capture hostname into variable",
        ],
        "cmd": "MYHOST=$(hostname)",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 2: TEXT SEARCH & EXTRACTION PIPELINES (~40 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "count lines matching {pattern} in {file}",
            "how many lines contain {pattern} in {file}",
            "number of lines with {pattern} in {file}",
        ],
        "cmd": "grep -c {pattern} {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "count lines matching {pattern} in {file} using grep and wc",
            "grep for {pattern} in {file} and count results",
            "find {pattern} in {file} and count the matches",
        ],
        "cmd": "grep {pattern} {file} | wc -l",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "recursively search for {pattern} in {dir} and sort results",
            "find all occurrences of {pattern} under {dir} sorted",
            "grep for {pattern} recursively in {dir} and sort",
        ],
        "cmd": "grep -r {pattern} {dir} | sort",
        "slots": {"pattern": SEARCH_PATTERNS, "dir": DIRS},
    },
    {
        "nl": [
            "search for {pattern} in {file} and extract the first field",
            "grep {pattern} in {file} and print the first column",
            "find lines with {pattern} in {file} and show the first word",
        ],
        "cmd": "grep {pattern} {file} | awk '{{print $1}}'",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "search for {pattern} in {file} and extract the second field",
            "grep {pattern} in {file} and print the second column",
        ],
        "cmd": "grep {pattern} {file} | awk '{{print $2}}'",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "find lines with {pattern} in {file} and extract CSV field 2",
            "grep {pattern} in {file} and get the second comma-separated field",
        ],
        "cmd": "grep {pattern} {file} | cut -d',' -f2",
        "slots": {"pattern": SEARCH_PATTERNS, "file": ["data.csv", "output.csv", "report.csv"]},
    },
    {
        "nl": [
            "search for {pattern} in {file} and replace with {replacement}",
            "grep lines with {pattern} in {file} then substitute with {replacement}",
        ],
        "cmd": "grep {pattern} {file} | sed 's/{pattern}/{replacement}/g'",
        "slots": {
            "pattern": SED_OLD,
            "file": FILES_TEXT,
            "replacement": SED_NEW,
        },
    },
    {
        "nl": [
            "show lines NOT matching {pattern} in {file}",
            "exclude lines containing {pattern} from {file}",
            "inverse grep for {pattern} in {file}",
            "filter out {pattern} from {file}",
        ],
        "cmd": "grep -v {pattern} {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "find all files named {pattern} under {dir} and search for {search} in them",
            "search for {search} inside all {pattern} files under {dir}",
        ],
        "cmd": "find {dir} -name '{pattern}' | xargs grep {search}",
        "slots": {
            "pattern": ["*.py", "*.log", "*.conf", "*.txt", "*.yaml", "*.sh"],
            "dir": DIRS,
            "search": SEARCH_PATTERNS,
        },
    },
    {
        "nl": [
            "find files containing {pattern} under {dir}",
            "list files in {dir} that contain {pattern}",
            "which files under {dir} have {pattern} in them",
        ],
        "cmd": "find {dir} -type f -exec grep -l {pattern} {{}} +",
        "slots": {"pattern": SEARCH_PATTERNS, "dir": DIRS},
    },
    {
        "nl": [
            "search and replace {old} with {new} across all files in {dir}",
            "find and replace {old} with {new} in all files under {dir}",
            "replace every {old} with {new} recursively in {dir}",
            "bulk replace {old} with {new} in {dir}",
        ],
        "cmd": "grep -rl {old} {dir} | xargs sed -i 's/{old}/{new}/g'",
        "slots": {"old": SED_OLD, "new": SED_NEW, "dir": DIRS},
    },
    {
        "nl": [
            "convert {file} to lowercase",
            "lowercase all text in {file}",
            "change all uppercase to lowercase in {file}",
        ],
        "cmd": "cat {file} | tr 'A-Z' 'a-z'",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "convert {file} to uppercase",
            "uppercase all text in {file}",
            "change all lowercase to uppercase in {file}",
        ],
        "cmd": "cat {file} | tr 'a-z' 'A-Z'",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "strip carriage returns from {file}",
            "remove windows line endings from {file}",
            "convert {file} from dos to unix line endings",
            "remove \\r from {file}",
        ],
        "cmd": "cat {file} | tr -d '\\r'",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "squeeze multiple spaces in {file} into single spaces",
            "collapse whitespace in {file}",
            "normalize spaces in {file}",
        ],
        "cmd": "cat {file} | tr -s ' '",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "get the most frequent lines in {file}",
            "frequency count of lines in {file}",
            "show line frequency in {file} sorted by count",
            "count occurrences of each line in {file} and sort by frequency",
        ],
        "cmd": "sort {file} | uniq -c | sort -rn",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "find lines common to both {file1} and {file2}",
            "show lines that exist in both {file1} and {file2}",
            "intersection of {file1} and {file2}",
        ],
        "cmd": "sort {file1} {file2} | uniq -d",
        "slots": {
            "file1": ["file1.txt", "list1.txt", "a.txt"],
            "file2": ["file2.txt", "list2.txt", "b.txt"],
        },
    },
    {
        "nl": [
            "compare {file1} and {file2} after sorting",
            "diff sorted versions of {file1} and {file2}",
            "show differences between sorted {file1} and {file2}",
        ],
        "cmd": "diff <(sort {file1}) <(sort {file2})",
        "slots": {
            "file1": ["file1.txt", "before.txt", "old.conf"],
            "file2": ["file2.txt", "after.txt", "new.conf"],
        },
    },
    {
        "nl": [
            "merge {file1} and {file2} side by side",
            "paste {file1} and {file2} together",
            "combine {file1} and {file2} column by column",
        ],
        "cmd": "paste {file1} {file2}",
        "slots": {
            "file1": ["names.txt", "keys.txt", "col1.txt"],
            "file2": ["values.txt", "vals.txt", "col2.txt"],
        },
    },
    {
        "nl": [
            "extract usernames from /etc/passwd",
            "list all usernames from the passwd file",
            "show all user accounts from /etc/passwd",
            "get the first field of /etc/passwd",
        ],
        "cmd": "cut -d':' -f1 /etc/passwd",
        "slots": {},
    },
    {
        "nl": [
            "find the last match of {pattern} in {file}",
            "show the last line matching {pattern} in {file}",
            "get the most recent line with {pattern} in {file}",
        ],
        "cmd": "grep {pattern} {file} | tail -1",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "show context around {pattern} matches in {file}",
            "grep {pattern} in {file} with 2 lines of context",
            "find {pattern} in {file} and show surrounding lines",
        ],
        "cmd": "grep -A2 -B2 {pattern} {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "show only matching parts of {pattern} in {file}",
            "extract just the matches of {pattern} from {file}",
            "print only the matched text for {pattern} in {file}",
        ],
        "cmd": "grep -o {pattern} {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "show lines matching {pattern} in {file} with line numbers",
            "grep {pattern} in {file} and show line numbers",
            "find {pattern} in {file} and display line numbers",
        ],
        "cmd": "grep -n {pattern} {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "case insensitive search for {pattern} in {file}",
            "grep {pattern} in {file} ignoring case",
            "find {pattern} in {file} case insensitive",
        ],
        "cmd": "grep -i {pattern} {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "list files in {dir} that contain {pattern}",
            "show filenames with {pattern} in {dir}",
            "which files in {dir} match {pattern}",
        ],
        "cmd": "grep -rl {pattern} {dir}",
        "slots": {"pattern": SEARCH_PATTERNS, "dir": DIRS},
    },
    {
        "nl": [
            "count the frequency of each word in {file}",
            "word frequency count for {file}",
            "show how many times each word appears in {file}",
        ],
        "cmd": "tr -s ' ' '\\n' < {file} | sort | uniq -c | sort -rn",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "show the top {n} most frequent lines in {file}",
            "top {n} most common lines in {file}",
            "most frequent {n} lines in {file}",
        ],
        "cmd": "sort {file} | uniq -c | sort -rn | head -{n}",
        "slots": {"file": FILES_TEXT, "n": LINES_N},
    },
    {
        "nl": [
            "find lines only in {file1} but not in {file2}",
            "show lines unique to {file1} compared to {file2}",
            "lines in {file1} that are not in {file2}",
            "difference of {file1} minus {file2}",
        ],
        "cmd": "comm -23 <(sort {file1}) <(sort {file2})",
        "slots": {
            "file1": ["file1.txt", "all.txt", "full.txt"],
            "file2": ["file2.txt", "exclude.txt", "subset.txt"],
        },
    },
    {
        "nl": [
            "show line counts for multiple files {file1} {file2}",
            "count lines in {file1} and {file2}",
            "line count comparison of {file1} and {file2}",
        ],
        "cmd": "wc -l {file1} {file2}",
        "slots": {
            "file1": ["file1.txt", "data.csv", "access.log"],
            "file2": ["file2.txt", "output.csv", "error.log"],
        },
    },
    {
        "nl": [
            "search for whole word {pattern} in {file}",
            "grep for exact word {pattern} in {file}",
            "match whole word {pattern} only in {file}",
        ],
        "cmd": "grep -w {pattern} {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "find {pattern} recursively in {dir} showing only filenames",
            "list just filenames containing {pattern} under {dir}",
        ],
        "cmd": "grep -rl {pattern} {dir}",
        "slots": {"pattern": SEARCH_PATTERNS, "dir": DIRS},
    },
    {
        "nl": [
            "show unique lines that appear more than once in {file}",
            "find repeated lines in {file}",
            "show only duplicate lines in {file}",
        ],
        "cmd": "sort {file} | uniq -d",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "remove all blank lines from {file}",
            "delete empty lines from {file}",
            "strip blank lines from {file}",
        ],
        "cmd": "grep -v '^$' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "display {file} with line numbers",
            "show {file} contents with line numbers",
            "number the lines in {file}",
        ],
        "cmd": "cat -n {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "reverse the lines of {file}",
            "show {file} in reverse order",
            "print {file} lines from bottom to top",
        ],
        "cmd": "tac {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "count blank lines in {file}",
            "how many empty lines are in {file}",
            "number of blank lines in {file}",
        ],
        "cmd": "grep -c '^$' {file}",
        "slots": {"file": FILES_TEXT},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 3: LOG ANALYSIS PIPELINES (~40 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "show the top 10 IP addresses in {log}",
            "find the most frequent IPs in {log}",
            "top 10 visitors by IP in {log}",
            "which IPs hit {log} the most",
            "most active IP addresses in {log}",
        ],
        "cmd": "awk '{{print $1}}' {log} | sort | uniq -c | sort -rn | head -10",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show the top 10 requested URLs in {log}",
            "most visited pages in {log}",
            "top 10 URLs by frequency in {log}",
            "what are the most requested paths in {log}",
        ],
        "cmd": "awk '{{print $7}}' {log} | sort | uniq -c | sort -rn | head -10",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show all 404 errors in {log}",
            "find pages returning 404 in {log}",
            "list URLs with 404 status in {log}",
            "which pages are not found in {log}",
        ],
        "cmd": "awk '$9 == 404 {{print $7}}' {log} | sort | uniq -c | sort -rn",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show all 5xx server errors in {log}",
            "find server error responses in {log}",
            "list 500-level errors in {log}",
        ],
        "cmd": "awk '$9 >= 500' {log}",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show requests per day in {log}",
            "count requests by date in {log}",
            "daily request counts from {log}",
            "how many requests per day in {log}",
        ],
        "cmd": "awk '{{print $4}}' {log} | cut -d'[' -f2 | cut -d':' -f1 | sort | uniq -c",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "calculate total bytes transferred in {log}",
            "sum of all response sizes in {log}",
            "total bandwidth used in {log}",
        ],
        "cmd": "awk '{{sum += $10}} END {{print sum}}' {log}",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show slow requests taking more than 1 second in {log}",
            "find requests slower than 1s in {log}",
            "list slow responses in {log}",
        ],
        "cmd": "awk '$NF > 1.0 {{print}}' {log}",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show the top POST endpoints in {log}",
            "most frequently POSTed URLs in {log}",
            "which POST endpoints are hit most in {log}",
        ],
        "cmd": "grep \"POST \" {log} | awk '{{print $7}}' | sort | uniq -c | sort -rn",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show recent SSH activity in {log}",
            "display latest SSH events from {log}",
            "check SSH log entries in {log}",
        ],
        "cmd": 'grep "sshd" {log} | tail -20',
        "slots": {"log": AUTH_LOGS},
    },
    {
        "nl": [
            "show IP addresses with failed SSH logins in {log}",
            "find IPs with failed password attempts in {log}",
            "top IPs failing SSH login in {log}",
            "which IPs have the most failed login attempts in {log}",
        ],
        "cmd": "grep \"Failed password\" {log} | awk '{{print $11}}' | sort | uniq -c | sort -rn",
        "slots": {"log": AUTH_LOGS},
    },
    {
        "nl": [
            "count failed login attempts in {log}",
            "how many failed logins in {log}",
            "number of failed password attempts in {log}",
        ],
        "cmd": 'grep "Failed password" {log} | wc -l',
        "slots": {"log": AUTH_LOGS},
    },
    {
        "nl": [
            "show users who successfully logged in from {log}",
            "list users with accepted logins in {log}",
            "which users logged in successfully in {log}",
        ],
        "cmd": "grep \"Accepted\" {log} | awk '{{print $9}}' | sort | uniq -c",
        "slots": {"log": AUTH_LOGS},
    },
    {
        "nl": [
            "show logs for {service} from the last hour",
            "recent logs for {service} service",
            "last hour of {service} logs",
            "check what {service} did in the past hour",
        ],
        "cmd": "journalctl -u {service} --since '1 hour ago' --no-pager",
        "slots": {"service": SERVICES},
    },
    {
        "nl": [
            "show today's error messages in the journal",
            "list today's error-level journal entries",
            "what errors happened today in systemd journal",
        ],
        "cmd": "journalctl -p err --since today",
        "slots": {},
    },
    {
        "nl": [
            "show kernel errors in dmesg",
            "find error messages in kernel log",
            "check dmesg for errors",
        ],
        "cmd": "dmesg | grep -i error",
        "slots": {},
    },
    {
        "nl": [
            "follow {log} in real time filtering for {pattern}",
            "live tail {log} showing only {pattern}",
            "stream {log} and filter for {pattern}",
            "watch {log} for {pattern} in real time",
        ],
        "cmd": "tail -f {log} | grep --line-buffered {pattern}",
        "slots": {"log": LOG_FILES, "pattern": SEARCH_PATTERNS},
    },
    {
        "nl": [
            "count requests per HTTP status code in {log}",
            "breakdown of HTTP status codes in {log}",
            "how many 200s, 404s, 500s in {log}",
            "status code distribution in {log}",
        ],
        "cmd": "awk '{{print $9}}' {log} | sort | uniq -c | sort -rn",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show the top user agents in {log}",
            "most common browsers in {log}",
            "user agent frequency in {log}",
        ],
        "cmd": "awk -F'\"' '{{print $6}}' {log} | sort | uniq -c | sort -rn | head -10",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show requests from IP {host} in {log}",
            "filter {log} for requests from {host}",
            "what did {host} access in {log}",
        ],
        "cmd": "grep {host} {log}",
        "slots": {"host": HOSTS, "log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show requests with status code {code} in {log}",
            "filter {log} for HTTP {code} responses",
            "find all {code} responses in {log}",
        ],
        "cmd": "awk '$9 == {code}' {log}",
        "slots": {"code": HTTP_CODES, "log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show requests per hour in {log}",
            "hourly request breakdown in {log}",
            "count requests by hour in {log}",
        ],
        "cmd": "awk '{{print $4}}' {log} | cut -d':' -f2 | sort | uniq -c",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show the largest HTTP responses in {log}",
            "biggest responses by size in {log}",
            "top 10 largest response sizes in {log}",
        ],
        "cmd": "awk '{{print $10, $7}}' {log} | sort -rn | head -10",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "count unique IPs in {log}",
            "how many unique visitors in {log}",
            "number of distinct IP addresses in {log}",
        ],
        "cmd": "awk '{{print $1}}' {log} | sort -u | wc -l",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show the top 10 referrers in {log}",
            "most common referrers in {log}",
            "where is traffic coming from in {log}",
        ],
        "cmd": "awk -F'\"' '{{print $4}}' {log} | sort | uniq -c | sort -rn | head -10",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "count unique URLs in {log}",
            "how many different pages were requested in {log}",
            "number of distinct URLs in {log}",
        ],
        "cmd": "awk '{{print $7}}' {log} | sort -u | wc -l",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show GET requests in {log}",
            "filter {log} for GET requests only",
            "list all GET requests from {log}",
        ],
        "cmd": 'grep "GET " {log}',
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show requests between 2 and 3 AM in {log}",
            "filter {log} for requests at 02 hour",
            "find nighttime requests at 2 AM in {log}",
        ],
        "cmd": "awk '$4 ~ /02:/' {log}",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show IPs making more than 100 requests in {log}",
            "find IPs with excessive requests in {log}",
            "IPs with over 100 hits in {log}",
        ],
        "cmd": "awk '{{print $1}}' {log} | sort | uniq -c | sort -rn | awk '$1 > 100'",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "follow the journal for {service} in real time",
            "stream live logs for {service}",
            "watch {service} logs live",
        ],
        "cmd": "journalctl -u {service} -f",
        "slots": {"service": SERVICES},
    },
    {
        "nl": [
            "show kernel warnings and errors",
            "display dmesg warnings",
            "check kernel log for warnings",
        ],
        "cmd": "dmesg | grep -iE 'error|warning'",
        "slots": {},
    },
    {
        "nl": [
            "show boot messages from dmesg",
            "display kernel boot log",
            "check what happened during boot",
        ],
        "cmd": "dmesg | head -50",
        "slots": {},
    },
    {
        "nl": [
            "show unique error messages in {log}",
            "list distinct errors in {log}",
            "deduplicated errors from {log}",
        ],
        "cmd": "grep -i error {log} | sort -u",
        "slots": {"log": LOG_FILES},
    },
    {
        "nl": [
            "show the last 50 lines of {log} and search for {pattern}",
            "check recent {log} entries for {pattern}",
            "search the tail of {log} for {pattern}",
        ],
        "cmd": "tail -50 {log} | grep {pattern}",
        "slots": {"log": LOG_FILES, "pattern": SEARCH_PATTERNS},
    },
    {
        "nl": [
            "show today's entries in {log}",
            "filter {log} for today's date",
        ],
        "cmd": 'grep "$(date +%Y-%m-%d)" {log}',
        "slots": {"log": LOG_FILES},
    },
    {
        "nl": [
            "count errors per hour in {log}",
            "hourly error count from {log}",
            "how many errors each hour in {log}",
        ],
        "cmd": "grep -i error {log} | awk '{{print $3}}' | cut -d':' -f1 | sort | uniq -c",
        "slots": {"log": LOG_FILES},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 4: PROCESS & SYSTEM MONITORING PIPELINES (~25 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "find {proc} process excluding the grep itself",
            "search for {proc} in process list without grep",
            "check if {proc} is running filtering out grep",
        ],
        "cmd": "ps aux | grep {proc} | grep -v grep",
        "slots": {"proc": PROC_NAMES},
    },
    {
        "nl": [
            "show the top 10 processes by CPU usage",
            "which processes use the most CPU",
            "top 10 CPU consuming processes",
            "highest CPU usage processes",
        ],
        "cmd": "ps aux | sort -k3 -rn | head -10",
        "slots": {},
    },
    {
        "nl": [
            "show the top 10 processes by memory usage",
            "which processes use the most memory",
            "top 10 memory consuming processes",
            "highest memory usage processes",
        ],
        "cmd": "ps aux | sort -k4 -rn | head -10",
        "slots": {},
    },
    {
        "nl": [
            "show total CPU usage across all processes",
            "aggregate CPU percentage of all processes",
            "sum of all process CPU usage",
        ],
        "cmd": "ps aux | awk '{{sum+=$3}} END {{print sum\"%\"}}'",
        "slots": {},
    },
    {
        "nl": [
            "show processes using more than 50% CPU",
            "find processes with high CPU usage",
            "which processes are using over 50 percent CPU",
        ],
        "cmd": "ps aux | awk '$3 > 50'",
        "slots": {},
    },
    {
        "nl": [
            "check what process is listening on port {port}",
            "find what's running on port {port}",
            "show the process using port {port}",
            "what is listening on port {port}",
        ],
        "cmd": "ss -tulnp | grep :{port}",
        "slots": {"port": PORTS},
    },
    {
        "nl": [
            "show what process is using port {port}",
            "which process has port {port} open",
            "find process on port {port} with lsof",
        ],
        "cmd": "lsof -i :{port}",
        "slots": {"port": PORTS},
    },
    {
        "nl": [
            "list all files opened by process {proc}",
            "show open files for {proc}",
            "what files does {proc} have open",
        ],
        "cmd": "lsof -c {proc}",
        "slots": {"proc": PROC_NAMES},
    },
    {
        "nl": [
            "show the 10 largest files and directories in current dir",
            "biggest items in current directory",
            "top 10 largest items by disk usage here",
        ],
        "cmd": "du -sh * | sort -rh | head -10",
        "slots": {},
    },
    {
        "nl": [
            "show the 10 largest log files",
            "biggest log files in /var/log",
            "which logs are taking the most space",
        ],
        "cmd": "du -sh /var/log/* | sort -rh | head -10",
        "slots": {},
    },
    {
        "nl": [
            "show filesystems that are over 80% full",
            "find nearly full disk partitions",
            "which filesystems are running low on space",
            "check for disk partitions above 80 percent usage",
        ],
        "cmd": "df -h | awk '$5+0 > 80'",
        "slots": {},
    },
    {
        "nl": [
            "show current memory usage as a percentage",
            "what percentage of memory is used",
            "display memory utilization percentage",
        ],
        "cmd": "free -m | awk 'NR==2 {{printf \"%.1f%%\\n\", $3/$2*100}}'",
        "slots": {},
    },
    {
        "nl": [
            "find files larger than {size} on the system",
            "search for files bigger than {size}",
            "locate files over {size} in size",
        ],
        "cmd": "find / -type f -size +{size} 2>/dev/null",
        "slots": {"size": ["100M", "500M", "1G", "5G"]},
    },
    {
        "nl": [
            "find files modified today in {dir}",
            "show files changed today in {dir}",
            "list files modified in the last 24 hours under {dir}",
        ],
        "cmd": "find {dir} -mtime -1 -type f",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "find files modified in the last hour in {dir}",
            "show files changed in the past 60 minutes under {dir}",
            "recently modified files in {dir}",
        ],
        "cmd": "find {dir} -mmin -60 -type f",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "show all listening ports",
            "list all services listening on ports",
            "what ports are open and listening",
            "display listening network services",
        ],
        "cmd": "ss -tulnp",
        "slots": {},
    },
    {
        "nl": [
            "count how many users are logged in",
            "number of logged-in users",
            "how many users are currently logged in",
        ],
        "cmd": "who | wc -l",
        "slots": {},
    },
    {
        "nl": [
            "find process {proc} by name",
            "search for {proc} process",
            "get PID and command line for {proc}",
        ],
        "cmd": "pgrep -a {proc}",
        "slots": {"proc": PROC_NAMES},
    },
    {
        "nl": [
            "show disk I/O statistics",
            "display disk read/write stats",
            "check disk throughput",
        ],
        "cmd": "iostat -x 1 3",
        "slots": {},
    },
    {
        "nl": [
            "show the top 10 largest files in {dir}",
            "find the biggest files in {dir}",
            "list the largest files under {dir}",
        ],
        "cmd": "find {dir} -type f -exec du -sh {{}} + 2>/dev/null | sort -rh | head -10",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "show swap usage per process",
            "which processes are using swap",
            "check process swap usage",
        ],
        "cmd": "for f in /proc/*/status; do awk '/VmSwap/ && $2 > 0 {{print FILENAME, $0}}' $f; done 2>/dev/null | sort -k3 -rn | head -10",
        "slots": {},
    },
    {
        "nl": [
            "show CPU load averages",
            "check system load",
            "display current load average",
        ],
        "cmd": "uptime",
        "slots": {},
    },
    {
        "nl": [
            "show number of open files system-wide",
            "count total open file descriptors",
            "how many files are open on the system",
        ],
        "cmd": "cat /proc/sys/fs/file-nr",
        "slots": {},
    },
    {
        "nl": [
            "show number of established network connections",
            "count active TCP connections",
            "how many connections are established",
        ],
        "cmd": "ss -t state established | wc -l",
        "slots": {},
    },
    {
        "nl": [
            "show zombie processes",
            "find zombie processes",
            "list any zombie processes on the system",
        ],
        "cmd": "ps aux | awk '$8 ~ /Z/'",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 5: REGEX CONSTRUCTION FROM NL (~50 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "find all lines containing IP addresses in {file}",
            "extract IP addresses from {file}",
            "grep for IP addresses in {file}",
            "match IP addresses in {file}",
            "search for IP addresses in {file}",
            "show lines with IP addresses in {file}",
            "find IPs in {file}",
        ],
        "cmd": "grep -E '([0-9]{{1,3}}\\.){3}[0-9]{{1,3}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "extract only IP addresses from {file}",
            "print just the IP addresses in {file}",
            "pull out IP addresses from {file}",
            "get only the IPs from {file}",
        ],
        "cmd": "grep -oE '([0-9]{{1,3}}\\.){3}[0-9]{{1,3}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find email addresses in {file}",
            "extract email addresses from {file}",
            "grep for emails in {file}",
            "match email addresses in {file}",
            "search for email addresses in {file}",
            "show lines with email addresses in {file}",
        ],
        "cmd": "grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find URLs in {file}",
            "extract URLs from {file}",
            "grep for URLs in {file}",
            "match HTTP URLs in {file}",
            "search for web addresses in {file}",
            "show lines with URLs in {file}",
        ],
        "cmd": "grep -oE 'https?://[^[:space:]]+' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find dates in YYYY-MM-DD format in {file}",
            "extract dates from {file}",
            "grep for dates in {file}",
            "match YYYY-MM-DD dates in {file}",
            "search for date patterns in {file}",
        ],
        "cmd": "grep -E '[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find phone numbers in {file}",
            "extract phone numbers from {file}",
            "grep for phone numbers in {file}",
            "match phone numbers in {file}",
            "search for US phone numbers in {file}",
        ],
        "cmd": "grep -E '\\(?[0-9]{{3}}\\)?[-. ]?[0-9]{{3}}[-. ]?[0-9]{{4}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find MAC addresses in {file}",
            "extract MAC addresses from {file}",
            "grep for MAC addresses in {file}",
            "match MAC addresses in {file}",
        ],
        "cmd": "grep -E '([0-9A-Fa-f]{{2}}:){5}[0-9A-Fa-f]{{2}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find hex color codes in {file}",
            "extract HTML color codes from {file}",
            "grep for hex colors in {file}",
            "match color hex values in {file}",
        ],
        "cmd": "grep -E '#[0-9A-Fa-f]{{6}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find blank lines in {file}",
            "show empty lines in {file}",
            "match blank lines in {file}",
            "count empty lines in {file}",
        ],
        "cmd": "grep -c '^$' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines starting with {pattern} in {file}",
            "show lines that begin with {pattern} in {file}",
            "grep for lines starting with {pattern} in {file}",
        ],
        "cmd": "grep -E '^{pattern}' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines ending with {pattern} in {file}",
            "show lines that end with {pattern} in {file}",
            "grep for lines ending with {pattern} in {file}",
        ],
        "cmd": "grep -E '{pattern}$' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines containing only numbers in {file}",
            "show lines that are all digits in {file}",
            "match lines with only numbers in {file}",
            "extract numeric-only lines from {file}",
        ],
        "cmd": "grep -E '^[0-9]+$' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines containing only letters in {file}",
            "show lines that are all alphabetic in {file}",
            "match lines with only letters in {file}",
        ],
        "cmd": "grep -E '^[a-zA-Z]+$' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "extract all numbers from {file}",
            "pull out numbers from {file}",
            "get all numeric values from {file}",
            "find all numbers in {file}",
        ],
        "cmd": "grep -oE '[0-9]+' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "extract words in all caps from {file}",
            "find uppercase words in {file}",
            "show ALLCAPS words in {file}",
            "match uppercase-only words in {file}",
        ],
        "cmd": "grep -oE '\\b[A-Z]{{2,}}\\b' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find UUIDs in {file}",
            "extract UUIDs from {file}",
            "grep for UUID patterns in {file}",
            "match UUIDs in {file}",
        ],
        "cmd": "grep -E '[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find semantic version numbers in {file}",
            "extract version strings from {file}",
            "grep for semver patterns in {file}",
            "match version numbers like X.Y.Z in {file}",
        ],
        "cmd": "grep -E '[0-9]+\\.[0-9]+\\.[0-9]+' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "remove ANSI color codes from {file}",
            "strip terminal color escape sequences from {file}",
            "clean ANSI escape codes from {file}",
        ],
        "cmd": "sed 's/\\x1b\\[[0-9;]*m//g' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find timestamps in HH:MM:SS format in {file}",
            "extract time strings from {file}",
            "grep for time patterns in {file}",
            "match HH:MM:SS timestamps in {file}",
        ],
        "cmd": "grep -E '[0-9]{{2}}:[0-9]{{2}}:[0-9]{{2}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find IPv6 addresses in {file}",
            "extract IPv6 addresses from {file}",
            "grep for IPv6 in {file}",
        ],
        "cmd": "grep -E '([0-9a-fA-F]{{0,4}}:){{2,7}}[0-9a-fA-F]{{0,4}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines with exactly {n} words in {file}",
            "show lines that have {n} words in {file}",
        ],
        "cmd": "awk 'NF == {n}' {file}",
        "slots": {"n": ["3", "5", "7", "10"], "file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines longer than 80 characters in {file}",
            "show lines exceeding 80 chars in {file}",
            "which lines in {file} are longer than 80 characters",
        ],
        "cmd": "awk 'length > 80' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "extract domain names from URLs in {file}",
            "get domains from URLs in {file}",
            "pull out hostnames from URLs in {file}",
        ],
        "cmd": "grep -oE 'https?://[^/]+' {file} | sed 's|https\\?://||'",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines matching both {p1} and {p2} in {file}",
            "grep for lines containing {p1} and {p2} in {file}",
            "show lines with both {p1} and {p2} in {file}",
        ],
        "cmd": "grep {p1} {file} | grep {p2}",
        "slots": {
            "p1": ["error", "warning", "failed"],
            "p2": ["timeout", "connection", "denied"],
            "file": REGEX_FILES,
        },
    },
    {
        "nl": [
            "find lines matching {p1} or {p2} in {file}",
            "grep for {p1} or {p2} in {file}",
            "show lines containing either {p1} or {p2} in {file}",
        ],
        "cmd": "grep -E '{p1}|{p2}' {file}",
        "slots": {
            "p1": ["error", "warning", "failed", "critical"],
            "p2": ["timeout", "connection", "denied", "fatal"],
            "file": REGEX_FILES,
        },
    },
    {
        "nl": [
            "find lines with 3 or more consecutive digits in {file}",
            "match sequences of 3+ digits in {file}",
            "grep for long number sequences in {file}",
        ],
        "cmd": "grep -E '[0-9]{{3,}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "extract file paths from {file}",
            "find absolute paths in {file}",
            "grep for file paths in {file}",
        ],
        "cmd": "grep -oE '/[a-zA-Z0-9_./-]+' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines that are comments starting with # in {file}",
            "show comment lines in {file}",
            "extract hash-prefixed comments from {file}",
        ],
        "cmd": "grep -E '^\\s*#' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines that are NOT comments in {file}",
            "show non-comment lines in {file}",
            "filter out comments from {file}",
        ],
        "cmd": "grep -vE '^\\s*#|^\\s*$' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "extract key=value pairs from {file}",
            "find variable assignments in {file}",
            "grep for key-value pairs in {file}",
        ],
        "cmd": "grep -oE '[a-zA-Z_][a-zA-Z0-9_]*=[^ ]+' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines with repeated words in {file}",
            "detect duplicate words on same line in {file}",
            "show lines with word repetition in {file}",
        ],
        "cmd": "grep -E '\\b(\\w+)\\s+\\1\\b' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find strings in single or double quotes in {file}",
            "extract quoted strings from {file}",
            "grep for quoted text in {file}",
        ],
        "cmd": "grep -oE '\"[^\"]*\"|'\"'\"'[^'\"'\"']*'\"'\"'' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "count how many IP addresses are in {file}",
            "number of IPs in {file}",
            "how many IP addresses does {file} contain",
        ],
        "cmd": "grep -oE '([0-9]{{1,3}}\\.){3}[0-9]{{1,3}}' {file} | wc -l",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "show unique IP addresses in {file}",
            "list distinct IPs in {file}",
            "deduplicated IP addresses from {file}",
        ],
        "cmd": "grep -oE '([0-9]{{1,3}}\\.){3}[0-9]{{1,3}}' {file} | sort -u",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "count unique IP addresses in {file}",
            "how many distinct IPs in {file}",
            "number of unique IP addresses in {file}",
        ],
        "cmd": "grep -oE '([0-9]{{1,3}}\\.){3}[0-9]{{1,3}}' {file} | sort -u | wc -l",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines with tabs in {file}",
            "show lines containing tab characters in {file}",
            "grep for tab characters in {file}",
        ],
        "cmd": "grep -P '\\t' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines with trailing whitespace in {file}",
            "show lines with spaces at end in {file}",
            "detect trailing whitespace in {file}",
        ],
        "cmd": "grep -E '\\s+$' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "extract dates in MM/DD/YYYY format from {file}",
            "find US-format dates in {file}",
            "grep for MM/DD/YYYY in {file}",
        ],
        "cmd": "grep -oE '[0-9]{{2}}/[0-9]{{2}}/[0-9]{{4}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find credit card number patterns in {file}",
            "detect potential card numbers in {file}",
            "grep for 16-digit card patterns in {file}",
        ],
        "cmd": "grep -E '[0-9]{{4}}[- ]?[0-9]{{4}}[- ]?[0-9]{{4}}[- ]?[0-9]{{4}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "top 10 most frequent IP addresses in {file}",
            "IP frequency ranking in {file}",
            "most common IPs by count in {file}",
        ],
        "cmd": "grep -oE '([0-9]{{1,3}}\\.){3}[0-9]{{1,3}}' {file} | sort | uniq -c | sort -rn | head -10",
        "slots": {"file": REGEX_FILES},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 6: ADVANCED AWK PATTERNS (~40 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "print the first and third columns of {file}",
            "extract columns 1 and 3 from {file}",
            "show fields 1 and 3 of {file}",
        ],
        "cmd": "awk '{{print $1, $3}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "extract the second field from CSV {file}",
            "get the second column of comma-separated {file}",
            "print column 2 from CSV {file}",
        ],
        "cmd": "awk -F',' '{{print $2}}' {file}",
        "slots": {"file": ["data.csv", "output.csv", "report.csv", "users.csv", "records.csv"]},
    },
    {
        "nl": [
            "extract the first field from colon-delimited {file}",
            "get the first column with colon separator in {file}",
            "print first colon-separated field in {file}",
        ],
        "cmd": "awk -F':' '{{print $1}}' {file}",
        "slots": {"file": ["/etc/passwd", "/etc/group", "config.conf", "data.txt"]},
    },
    {
        "nl": [
            "extract fields from tab-delimited {file}",
            "get the first field from tab-separated {file}",
            "print first column of TSV {file}",
        ],
        "cmd": "awk -F'\\t' '{{print $1}}' {file}",
        "slots": {"file": ["data.tsv", "output.tsv", "report.txt", "table.txt"]},
    },
    {
        "nl": [
            "show lines matching {pattern} in {file} using awk",
            "awk filter for {pattern} in {file}",
            "print lines containing {pattern} from {file} with awk",
        ],
        "cmd": "awk '/{pattern}/ {{print}}' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "extract the second field from lines matching {pattern} in {file}",
            "get field 2 from matching lines in {file}",
        ],
        "cmd": "awk '/{pattern}/ {{print $2}}' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "show lines where column 3 is greater than 50 in {file}",
            "filter {file} where the third field exceeds 50",
            "awk conditional filter on third column of {file}",
        ],
        "cmd": "awk '$3 > 50 {{print $1, $3}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "show lines where first field equals {pattern} in {file}",
            "filter {file} where column 1 is {pattern}",
            "awk exact match on first field for {pattern} in {file}",
        ],
        "cmd": "awk '$1 == \"{pattern}\" {{print}}' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "print lines 10 through 20 of {file}",
            "show lines 10 to 20 of {file}",
            "extract line range 10-20 from {file}",
        ],
        "cmd": "awk 'NR >= 10 && NR <= 20' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "sum the {col} column of {file}",
            "add up all values in column {col} of {file}",
            "total of column {col} in {file}",
            "calculate the sum of field {col} in {file}",
        ],
        "cmd": "awk '{{sum += ${col}}} END {{print sum}}' {file}",
        "slots": {"col": ["2", "3", "4", "5"], "file": FILES_TEXT},
    },
    {
        "nl": [
            "calculate the average of column {col} in {file}",
            "mean of field {col} in {file}",
            "average value of column {col} in {file}",
        ],
        "cmd": "awk '{{sum += ${col}; n++}} END {{print sum/n}}' {file}",
        "slots": {"col": ["2", "3", "4", "5"], "file": FILES_TEXT},
    },
    {
        "nl": [
            "find the maximum value in column {col} of {file}",
            "get the max of field {col} in {file}",
            "largest value in column {col} of {file}",
        ],
        "cmd": "awk '{{if (${col} > max) max=${col}}} END {{print max}}' {file}",
        "slots": {"col": ["2", "3", "4", "5"], "file": FILES_TEXT},
    },
    {
        "nl": [
            "group by first field and count in {file}",
            "count occurrences of each value in column 1 of {file}",
            "frequency of first field in {file}",
            "count by first column in {file}",
        ],
        "cmd": "awk '{{count[$1]++}} END {{for (k in count) print k, count[k]}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "remove duplicate lines by first field in {file}",
            "deduplicate {file} based on first column",
            "unique by first field in {file}",
        ],
        "cmd": "awk '!seen[$1]++' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "remove all duplicate lines in {file} preserving order",
            "deduplicate {file} keeping first occurrence",
            "unique lines in {file} without sorting",
        ],
        "cmd": "awk '!seen[$0]++' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "replace {old} with {new} in {file} using awk",
            "awk substitution of {old} to {new} in {file}",
        ],
        "cmd": "awk '{{gsub(/{old}/, \"{new}\"); print}}' {file}",
        "slots": {"old": SED_OLD, "new": SED_NEW, "file": FILES_TEXT},
    },
    {
        "nl": [
            "pass a variable to awk and print with first field of {file}",
            "use an awk variable with {file}",
        ],
        "cmd": "awk -v var=value '{{print var, $1}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "print {file} fields separated by commas using awk",
            "convert {file} to comma-separated using awk",
            "change output separator to comma for {file}",
        ],
        "cmd": "awk 'BEGIN {{OFS=\",\"}} {{print $1, $2}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "format output of {file} in columns using awk",
            "pretty print {file} with aligned columns",
            "formatted column output of {file}",
        ],
        "cmd": "awk '{{printf \"%-20s %s\\n\", $1, $2}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "count lines in {file} using awk",
            "number of lines in {file} with awk",
            "awk line count for {file}",
        ],
        "cmd": "awk 'END {{print NR}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "add line numbers to {file} using awk",
            "number each line of {file} with awk",
            "prepend line numbers to {file}",
        ],
        "cmd": "awk '{{print NR\": \"$0}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "change delimiter of {file} to comma using awk",
            "convert {file} delimiter to comma",
            "replace whitespace separator with comma in {file}",
        ],
        "cmd": "awk '{{$1=$1}}1' OFS=',' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "show lines longer than 80 characters in {file} using awk",
            "find long lines in {file}",
            "lines exceeding 80 chars in {file}",
        ],
        "cmd": "awk 'length > 80' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "show the 5 longest lines in {file}",
            "find the longest lines in {file}",
            "top 5 lines by length in {file}",
        ],
        "cmd": "awk '{{print length, $0}}' {file} | sort -rn | head -5",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "print the last field of each line in {file}",
            "extract the last column of {file}",
            "show the last word on each line of {file}",
        ],
        "cmd": "awk '{{print $NF}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "print all fields except the first in {file}",
            "skip the first column of {file}",
            "remove the first field from {file}",
        ],
        "cmd": "awk '{{$1=\"\"; print substr($0,2)}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "sum the third column of CSV {file} skipping the header",
            "total of column 3 in {file} ignoring header row",
            "add up third field in {file} excluding first line",
        ],
        "cmd": "awk -F',' 'NR>1 {{sum+=$3}} END {{print sum}}' {file}",
        "slots": {"file": ["data.csv", "output.csv", "report.csv", "sales.csv"]},
    },
    {
        "nl": [
            "select columns 1 and 3 from CSV {file}",
            "extract first and third comma-separated fields from {file}",
            "pick CSV columns 1 and 3 from {file}",
        ],
        "cmd": "awk -F',' '{{print $1\",\"$3}}' {file}",
        "slots": {"file": ["data.csv", "output.csv", "report.csv"]},
    },
    {
        "nl": [
            "print lines where the second field is not empty in {file}",
            "filter lines with non-empty second column in {file}",
        ],
        "cmd": "awk '$2 != \"\"' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "calculate the minimum value in column {col} of {file}",
            "find the smallest value in field {col} of {file}",
        ],
        "cmd": "awk 'NR==1 || ${col} < min {{min=${col}}} END {{print min}}' {file}",
        "slots": {"col": ["2", "3", "4"], "file": FILES_TEXT},
    },
    {
        "nl": [
            "print every other line of {file}",
            "show odd-numbered lines of {file}",
            "display alternating lines from {file}",
        ],
        "cmd": "awk 'NR % 2 == 1' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "sum values grouped by first column in {file}",
            "aggregate second column by first column in {file}",
            "group by field 1 and sum field 2 in {file}",
        ],
        "cmd": "awk '{{sum[$1] += $2}} END {{for (k in sum) print k, sum[k]}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "transpose rows and columns of {file}",
            "pivot {file} so rows become columns",
            "convert rows to columns in {file}",
        ],
        "cmd": 'awk \'{{for (i=1; i<=NF; i++) a[i][NR]=$i}} END {{for (i in a) {{for (j in a[i]) printf "%s ", a[i][j]; print ""}}}}\' {file}',
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "print lines between {p1} and {p2} in {file} using awk",
            "extract section from {p1} to {p2} in {file}",
        ],
        "cmd": "awk '/{p1}/,/{p2}/' {file}",
        "slots": {
            "p1": ["BEGIN", "START", "\\[section\\]", "---"],
            "p2": ["END", "STOP", "\\[/section\\]", "---"],
            "file": FILES_TEXT,
        },
    },
    {
        "nl": [
            "number of fields on each line of {file}",
            "count columns per line in {file}",
            "show field count for each line of {file}",
        ],
        "cmd": "awk '{{print NF, $0}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "print lines with more than {n} fields in {file}",
            "show lines with over {n} columns in {file}",
        ],
        "cmd": "awk 'NF > {n}' {file}",
        "slots": {"n": ["3", "5", "7", "10"], "file": FILES_TEXT},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 7: ADVANCED SED PATTERNS (~30 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "replace first occurrence of {old} with {new} in each line of {file}",
            "substitute {old} with {new} in {file}",
            "sed replace {old} to {new} in {file}",
        ],
        "cmd": "sed 's/{old}/{new}/' {file}",
        "slots": {"old": SED_OLD, "new": SED_NEW, "file": FILES_TEXT},
    },
    {
        "nl": [
            "replace all occurrences of {old} with {new} in {file}",
            "global substitution of {old} with {new} in {file}",
            "change every {old} to {new} in {file}",
        ],
        "cmd": "sed 's/{old}/{new}/g' {file}",
        "slots": {"old": SED_OLD, "new": SED_NEW, "file": FILES_TEXT},
    },
    {
        "nl": [
            "replace {old} with {new} in {file} in-place",
            "modify {file} replacing {old} with {new}",
            "edit {file} in-place changing {old} to {new}",
            "change {old} to {new} directly in {file}",
        ],
        "cmd": "sed -i 's/{old}/{new}/g' {file}",
        "slots": {"old": SED_OLD, "new": SED_NEW, "file": FILES_TEXT},
    },
    {
        "nl": [
            "replace {old} with {new} in {file} keeping a backup",
            "in-place replace with backup in {file}",
            "sed with backup replacing {old} with {new} in {file}",
        ],
        "cmd": "sed -i.bak 's/{old}/{new}/g' {file}",
        "slots": {"old": SED_OLD, "new": SED_NEW, "file": FILES_TEXT},
    },
    {
        "nl": [
            "print line {n} of {file}",
            "show only line {n} from {file}",
            "extract line number {n} from {file}",
            "display line {n} of {file}",
        ],
        "cmd": "sed -n '{n}p' {file}",
        "slots": {"n": LINES_N, "file": FILES_TEXT},
    },
    {
        "nl": [
            "delete line {n} from {file}",
            "remove line {n} of {file}",
            "drop line number {n} from {file}",
        ],
        "cmd": "sed '{n}d' {file}",
        "slots": {"n": LINES_N, "file": FILES_TEXT},
    },
    {
        "nl": [
            "delete the last line of {file}",
            "remove the final line from {file}",
            "drop the last line of {file}",
        ],
        "cmd": "sed '$d' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "delete lines matching {pattern} from {file}",
            "remove lines containing {pattern} in {file}",
            "filter out lines with {pattern} from {file}",
        ],
        "cmd": "sed '/{pattern}/d' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "print only lines matching {pattern} in {file} using sed",
            "sed show only matching lines for {pattern} in {file}",
        ],
        "cmd": "sed -n '/{pattern}/p' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "indent all lines of {file} with two spaces",
            "add two spaces at the beginning of each line in {file}",
            "prepend spaces to every line of {file}",
        ],
        "cmd": "sed 's/^/  /' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "add a semicolon at the end of each line in {file}",
            "append semicolon to every line of {file}",
            "add suffix ; to each line of {file}",
        ],
        "cmd": "sed 's/$/;/' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "join every two lines in {file}",
            "merge pairs of lines in {file}",
            "combine every two lines into one in {file}",
        ],
        "cmd": "sed 'N;s/\\n/ /' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "trim trailing whitespace from {file}",
            "remove spaces at end of lines in {file}",
            "strip trailing spaces from {file}",
        ],
        "cmd": "sed 's/[[:space:]]*$//' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "trim leading whitespace from {file}",
            "remove spaces at start of lines in {file}",
            "strip leading spaces from {file}",
        ],
        "cmd": "sed 's/^[[:space:]]*//' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "remove blank lines from {file} using sed",
            "delete empty lines from {file} with sed",
            "strip blank lines from {file}",
        ],
        "cmd": "sed '/^$/d' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "apply multiple substitutions to {file}: replace {old} with {new}",
            "multiple sed replacements on {file}",
        ],
        "cmd": "sed -e 's/{old}/{new}/g' {file}",
        "slots": {"old": SED_OLD, "new": SED_NEW, "file": FILES_TEXT},
    },
    {
        "nl": [
            "insert a header line at the beginning of {file}",
            "add a first line to {file}",
            "prepend a header to {file}",
        ],
        "cmd": "sed '1i\\header text' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "print lines between {p1} and {p2} patterns in {file}",
            "extract text between {p1} and {p2} from {file}",
            "show section from {p1} to {p2} in {file}",
        ],
        "cmd": "sed -n '/{p1}/,/{p2}/p' {file}",
        "slots": {
            "p1": ["BEGIN", "START", "\\[section\\]", "---"],
            "p2": ["END", "STOP", "\\[/section\\]", "---"],
            "file": FILES_TEXT,
        },
    },
    {
        "nl": [
            "double-space {file}",
            "add an empty line after every line in {file}",
            "insert blank line between each line of {file}",
        ],
        "cmd": "sed 'G' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "number all lines in {file} using sed",
            "add line numbers to {file} with sed",
        ],
        "cmd": "sed '=' {file} | sed 'N;s/\\n/\\t/'",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "replace only on line {n} of {file} changing {old} to {new}",
            "substitute {old} with {new} only on line {n} of {file}",
        ],
        "cmd": "sed '{n}s/{old}/{new}/g' {file}",
        "slots": {"n": LINES_N, "old": SED_OLD, "new": SED_NEW, "file": FILES_TEXT},
    },
    {
        "nl": [
            "delete lines 5 through 10 of {file}",
            "remove lines 5 to 10 from {file}",
        ],
        "cmd": "sed '5,10d' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "replace the entire line matching {pattern} with {new} in {file}",
            "change the whole line containing {pattern} to {new} in {file}",
        ],
        "cmd": "sed '/{pattern}/c\\{new}' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "new": SED_NEW, "file": FILES_TEXT},
    },
    {
        "nl": [
            "append a line after the line matching {pattern} in {file}",
            "insert text after lines with {pattern} in {file}",
            "add a line below {pattern} in {file}",
        ],
        "cmd": "sed '/{pattern}/a\\new line here' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "insert a line before the line matching {pattern} in {file}",
            "add text before lines with {pattern} in {file}",
            "put a line above {pattern} in {file}",
        ],
        "cmd": "sed '/{pattern}/i\\new line here' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "reverse the order of lines in {file} using sed",
            "print {file} in reverse line order with sed",
        ],
        "cmd": "sed -n '1!G;h;$p' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "remove HTML tags from {file}",
            "strip HTML from {file}",
            "clean HTML tags from {file}",
        ],
        "cmd": "sed 's/<[^>]*>//g' {file}",
        "slots": {"file": ["page.html", "output.html", "template.html", "index.html"]},
    },
    {
        "nl": [
            "convert tabs to 4 spaces in {file}",
            "replace tabs with spaces in {file}",
            "expand tabs to spaces in {file}",
        ],
        "cmd": "sed 's/\\t/    /g' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "remove the first column from space-separated {file}",
            "delete the first field of each line in {file}",
        ],
        "cmd": "sed 's/^[^ ]* //' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "add line numbers only to non-empty lines in {file}",
            "number non-blank lines in {file}",
        ],
        "cmd": "sed '/./=' {file} | sed '/./N; s/\\n/ /'",
        "slots": {"file": FILES_TEXT},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 8: FILE MANIPULATION IDIOMS (~30 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "append '{text}' to {file}",
            "add the line '{text}' to the end of {file}",
            "write '{text}' at the end of {file}",
            "add '{text}' to {file}",
        ],
        "cmd": "echo '{text}' >> {file}",
        "slots": {"text": TEXT_LINES, "file": FILES_TEXT},
    },
    {
        "nl": [
            "write '{text}' to {file}",
            "save '{text}' to {file}",
            "put '{text}' into {file}",
            "overwrite {file} with '{text}'",
        ],
        "cmd": "echo '{text}' > {file}",
        "slots": {"text": TEXT_LINES, "file": FILES_TEXT},
    },
    {
        "nl": [
            "truncate {file} to zero bytes",
            "empty {file}",
            "clear the contents of {file}",
            "wipe {file}",
        ],
        "cmd": "> {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "make a backup of {file}",
            "create a backup copy of {file}",
            "copy {file} to {file}.bak",
            "back up {file}",
        ],
        "cmd": "cp {file} {file}.bak",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "backup {file} using brace expansion",
            "quick backup of {file}",
        ],
        "cmd": "cp {file}{{,.bak}}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "rename all {old_ext} files to {new_ext}",
            "batch change extension from {old_ext} to {new_ext}",
            "convert all {old_ext} to {new_ext} in current directory",
        ],
        "cmd": 'for f in *{old_ext}; do mv "$f" "${{f%{old_ext}}}{new_ext}"; done',
        "slots": {"old_ext": OLD_EXTS, "new_ext": NEW_EXTS},
    },
    {
        "nl": [
            "create a temporary file",
            "make a temp file",
            "generate a temporary file",
        ],
        "cmd": "mktemp",
        "slots": {},
    },
    {
        "nl": [
            "create a temporary directory",
            "make a temp directory",
            "generate a temporary directory",
        ],
        "cmd": "mktemp -d",
        "slots": {},
    },
    {
        "nl": [
            "compare {file1} and {file2}",
            "show differences between {file1} and {file2}",
            "diff {file1} and {file2}",
        ],
        "cmd": "diff {file1} {file2}",
        "slots": {
            "file1": ["file1.txt", "old.conf", "before.txt"],
            "file2": ["file2.txt", "new.conf", "after.txt"],
        },
    },
    {
        "nl": [
            "create a unified diff between {file1} and {file2}",
            "generate a patch from {file1} to {file2}",
            "unified diff of {file1} and {file2}",
        ],
        "cmd": "diff -u {file1} {file2} > patch.diff",
        "slots": {
            "file1": ["original.txt", "old.conf", "before.py"],
            "file2": ["modified.txt", "new.conf", "after.py"],
        },
    },
    {
        "nl": [
            "apply a patch file",
            "apply patch.diff",
            "patch files from diff",
        ],
        "cmd": "patch -p1 < patch.diff",
        "slots": {},
    },
    {
        "nl": [
            "split {file} into chunks of {n} lines each",
            "break {file} into {n}-line pieces",
            "divide {file} into parts of {n} lines",
        ],
        "cmd": "split -l {n} {file} chunk_",
        "slots": {"n": ["100", "500", "1000", "5000", "10000"], "file": FILES_TEXT},
    },
    {
        "nl": [
            "split {file} into {size} chunks",
            "break {file} into {size} pieces",
            "divide {file} into {size} parts",
        ],
        "cmd": "split -b {size} {file} part_",
        "slots": {"size": ["1M", "10M", "50M", "100M"], "file": FILES},
    },
    {
        "nl": [
            "reassemble split files",
            "combine chunk files back together",
            "concatenate split parts back into one file",
        ],
        "cmd": "cat part_* > combined",
        "slots": {},
    },
    {
        "nl": [
            "sort {file} in-place and remove duplicates",
            "deduplicate {file} in-place",
            "sort and unique {file} saving back to itself",
        ],
        "cmd": "sort -u {file} -o {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "show lines only in {file1} and not in {file2}",
            "lines unique to {file1} compared with {file2}",
            "what lines are in {file1} but not {file2}",
        ],
        "cmd": "comm -23 <(sort {file1}) <(sort {file2})",
        "slots": {
            "file1": ["all_users.txt", "full.txt", "list1.txt"],
            "file2": ["active_users.txt", "subset.txt", "list2.txt"],
        },
    },
    {
        "nl": [
            "convert {file} from DOS to Unix line endings",
            "fix Windows line endings in {file}",
            "remove carriage returns from {file} in-place",
        ],
        "cmd": "sed -i 's/\\r$//' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "get the md5 checksum of {file}",
            "calculate md5 hash of {file}",
            "md5sum of {file}",
        ],
        "cmd": "md5sum {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "get the sha256 checksum of {file}",
            "calculate sha256 hash of {file}",
            "sha256sum of {file}",
        ],
        "cmd": "sha256sum {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "show file type of {file}",
            "what type of file is {file}",
            "identify {file} type",
        ],
        "cmd": "file {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "show detailed file info for {file}",
            "get file statistics for {file}",
            "stat {file}",
        ],
        "cmd": "stat {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "create a symlink from {file} to link_name",
            "make a symbolic link to {file}",
            "symlink {file}",
        ],
        "cmd": "ln -s {file} link_name",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "find broken symlinks in {dir}",
            "locate dead symbolic links in {dir}",
            "show broken links under {dir}",
        ],
        "cmd": "find {dir} -xtype l",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "show the real path of {file}",
            "resolve symlinks for {file}",
            "get the absolute path of {file}",
        ],
        "cmd": "realpath {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "count files in {dir} recursively",
            "how many files are under {dir}",
            "total number of files in {dir} tree",
        ],
        "cmd": "find {dir} -type f | wc -l",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "find empty files in {dir}",
            "list zero-byte files in {dir}",
            "show empty files under {dir}",
        ],
        "cmd": "find {dir} -type f -empty",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "find empty directories in {dir}",
            "list empty dirs under {dir}",
            "show directories with no files in {dir}",
        ],
        "cmd": "find {dir} -type d -empty",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "replace spaces with underscores in filenames in current directory",
            "rename files replacing spaces with underscores",
        ],
        "cmd": 'for f in *\\ *; do mv "$f" "${f// /_}"; done',
        "slots": {},
    },
    {
        "nl": [
            "find duplicate files in {dir} by checksum",
            "detect duplicate files under {dir}",
        ],
        "cmd": "find {dir} -type f -exec md5sum {{}} + | sort | uniq -d -w32",
        "slots": {"dir": DIRS},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 9: DATA PROCESSING PIPELINES (~30 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "pretty print JSON file {file}",
            "format {file} as readable JSON",
            "beautify JSON in {file}",
        ],
        "cmd": "cat {file} | jq '.'",
        "slots": {"file": ["data.json", "output.json", "config.json", "response.json", "api.json"]},
    },
    {
        "nl": [
            "extract the {key} key from JSON file {file}",
            "get the value of {key} from {file}",
            "read {key} from JSON {file}",
        ],
        "cmd": "cat {file} | jq '.{key}'",
        "slots": {
            "key": ["name", "id", "status", "data", "results", "version", "config"],
            "file": ["data.json", "output.json", "config.json", "response.json"],
        },
    },
    {
        "nl": [
            "extract the name field from each element in JSON array {file}",
            "get all names from JSON array in {file}",
            "list names from JSON array {file}",
        ],
        "cmd": "cat {file} | jq '.[] | .name'",
        "slots": {"file": ["data.json", "users.json", "items.json", "records.json"]},
    },
    {
        "nl": [
            "count elements in JSON array {file}",
            "how many items in JSON array {file}",
            "length of JSON array in {file}",
        ],
        "cmd": "cat {file} | jq 'length'",
        "slots": {"file": ["data.json", "users.json", "items.json", "results.json"]},
    },
    {
        "nl": [
            "filter JSON array for active items in {file}",
            "select items with status active from {file}",
            "get active records from JSON {file}",
        ],
        "cmd": "cat {file} | jq '.[] | select(.status == \"active\")'",
        "slots": {"file": ["data.json", "users.json", "services.json"]},
    },
    {
        "nl": [
            "fetch JSON from {url} and pretty print it",
            "download and format JSON from {url}",
            "curl {url} and parse as JSON",
        ],
        "cmd": "curl -s {url} | jq '.'",
        "slots": {
            "url": [
                "https://api.example.com/data",
                "https://api.example.com/users",
                "https://api.example.com/status",
                "https://httpbin.org/get",
            ],
        },
    },
    {
        "nl": [
            "calculate {expr}",
            "compute {expr}",
            "what is {expr}",
        ],
        "cmd": 'echo "{expr}" | bc',
        "slots": {"expr": ["1+2", "100*5", "2^10", "1024/8", "sqrt(144)"]},
    },
    {
        "nl": [
            "calculate {expr} with decimal precision",
            "divide with decimals: {expr}",
            "compute {expr} to 2 decimal places",
        ],
        "cmd": 'echo "scale=2; {expr}" | bc',
        "slots": {"expr": ["10/3", "100/7", "22/7", "355/113"]},
    },
    {
        "nl": [
            "select columns 1 and 3 from CSV {file}",
            "extract first and third fields from {file}",
            "pick columns 1 and 3 from comma-separated {file}",
        ],
        "cmd": "cut -d',' -f1,3 {file}",
        "slots": {"file": ["data.csv", "report.csv", "output.csv"]},
    },
    {
        "nl": [
            "sort CSV {file} by second column numerically keeping header",
            "sort {file} by column 2 with header intact",
        ],
        "cmd": "head -1 {file} && sort -t',' -k2 -n {file} | tail -n+2",
        "slots": {"file": ["data.csv", "report.csv", "output.csv"]},
    },
    {
        "nl": [
            "pretty print CSV {file} as a table",
            "display {file} as an aligned table",
            "format CSV {file} for reading",
        ],
        "cmd": "column -t -s',' {file}",
        "slots": {"file": ["data.csv", "report.csv", "output.csv", "users.csv"]},
    },
    {
        "nl": [
            "convert CSV {file} to TSV",
            "change commas to tabs in {file}",
            "replace comma delimiter with tab in {file}",
        ],
        "cmd": "tr ',' '\\t' < {file}",
        "slots": {"file": ["data.csv", "report.csv", "output.csv"]},
    },
    {
        "nl": [
            "convert file size {bytes} to human-readable format",
            "make {bytes} bytes human readable",
        ],
        "cmd": "numfmt --to=iec {bytes}",
        "slots": {"bytes": ["1048576", "1073741824", "5368709120", "104857600"]},
    },
    {
        "nl": [
            "sum numbers from 1 to 100",
            "calculate the sum of 1 through 100",
            "add up 1 to 100",
        ],
        "cmd": "seq 1 100 | paste -sd+ | bc",
        "slots": {},
    },
    {
        "nl": [
            "get unique values from column {col} of CSV {file}",
            "distinct values in CSV column {col} of {file}",
        ],
        "cmd": "awk -F',' '{{print ${col}}}' {file} | sort -u",
        "slots": {"col": ["1", "2", "3"], "file": ["data.csv", "report.csv"]},
    },
    {
        "nl": [
            "count rows in CSV {file} excluding header",
            "how many data rows in {file}",
            "number of records in CSV {file}",
        ],
        "cmd": "tail -n+2 {file} | wc -l",
        "slots": {"file": ["data.csv", "report.csv", "output.csv", "users.csv"]},
    },
    {
        "nl": [
            "show the header of CSV {file}",
            "display column names from {file}",
            "print the first line of {file}",
        ],
        "cmd": "head -1 {file}",
        "slots": {"file": ["data.csv", "report.csv", "output.csv"]},
    },
    {
        "nl": [
            "sort JSON array in {file} by name field",
            "order JSON array by name in {file}",
        ],
        "cmd": "cat {file} | jq 'sort_by(.name)'",
        "slots": {"file": ["data.json", "users.json", "items.json"]},
    },
    {
        "nl": [
            "extract keys from JSON object in {file}",
            "list JSON keys in {file}",
            "show the top-level keys in {file}",
        ],
        "cmd": "cat {file} | jq 'keys'",
        "slots": {"file": ["data.json", "config.json", "response.json"]},
    },
    {
        "nl": [
            "convert JSON {file} to CSV-like output",
            "flatten JSON to tabular format from {file}",
        ],
        "cmd": "cat {file} | jq -r '.[] | [.name, .value] | @csv'",
        "slots": {"file": ["data.json", "records.json"]},
    },
    {
        "nl": [
            "merge two JSON files {file1} and {file2}",
            "combine JSON objects from {file1} and {file2}",
        ],
        "cmd": "jq -s '.[0] * .[1]' {file1} {file2}",
        "slots": {
            "file1": ["base.json", "defaults.json"],
            "file2": ["overrides.json", "custom.json"],
        },
    },
    {
        "nl": [
            "generate a sequence of numbers from 1 to {n}",
            "print numbers 1 through {n}",
            "create a number sequence 1 to {n}",
        ],
        "cmd": "seq 1 {n}",
        "slots": {"n": ["10", "20", "50", "100"]},
    },
    {
        "nl": [
            "convert JSON lines in {file} to a JSON array",
            "wrap JSONL {file} into a proper array",
        ],
        "cmd": "cat {file} | jq -s '.'",
        "slots": {"file": ["data.jsonl", "events.jsonl", "logs.jsonl"]},
    },
    {
        "nl": [
            "count CSV {file} columns",
            "how many columns in {file}",
            "number of fields in CSV {file}",
        ],
        "cmd": "head -1 {file} | awk -F',' '{{print NF}}'",
        "slots": {"file": ["data.csv", "report.csv", "output.csv"]},
    },
    {
        "nl": [
            "sort {file} by the second column",
            "sort {file} on field 2",
        ],
        "cmd": "sort -k2 {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "encode {text} in base64",
            "base64 encode the string {text}",
        ],
        "cmd": "echo -n '{text}' | base64",
        "slots": {"text": ["hello world", "admin:password", "test123", "secret_key"]},
    },
    {
        "nl": [
            "decode base64 string {encoded}",
            "base64 decode {encoded}",
        ],
        "cmd": "echo '{encoded}' | base64 -d",
        "slots": {"encoded": ["aGVsbG8gd29ybGQ=", "dGVzdDEyMw==", "YWRtaW46cGFzc3dvcmQ="]},
    },
    {
        "nl": [
            "generate a random password of {n} characters",
            "create a random {n}-character password",
            "random string of {n} characters",
        ],
        "cmd": "tr -dc 'A-Za-z0-9!@#$%' < /dev/urandom | head -c {n}; echo",
        "slots": {"n": ["16", "20", "24", "32"]},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 10: SHELL BUILTINS & CONSTRUCTS (~30 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "set environment variable {var} to {val}",
            "export {var} as {val}",
            "define environment variable {var} with value {val}",
            "set {var} to {val} in the environment",
        ],
        "cmd": "export {var}={val}",
        "slots": {"var": VAR_NAMES, "val": VAR_VALUES},
    },
    {
        "nl": [
            "remove environment variable {var}",
            "unset {var}",
            "delete environment variable {var}",
            "clear {var} from the environment",
        ],
        "cmd": "unset {var}",
        "slots": {"var": VAR_NAMES},
    },
    {
        "nl": [
            "print the value of {var}",
            "show the value of {var}",
            "display the {var} variable",
            "echo {var}",
        ],
        "cmd": "echo ${var}",
        "slots": {"var": VAR_NAMES},
    },
    {
        "nl": [
            "find environment variable {var}",
            "search for {var} in environment",
            "check if {var} is set",
        ],
        "cmd": "env | grep {var}",
        "slots": {"var": VAR_NAMES},
    },
    {
        "nl": [
            "create an alias {name} for '{cmd}'",
            "define alias {name} as '{cmd}'",
            "set up alias {name}='{cmd}'",
        ],
        "cmd": "alias {name}='{cmd}'",
        "slots": {
            "name": ["ll", "la", "gs", "gd", "dc", "k"],
            "cmd": ["ls -la", "ls -la", "git status", "git diff", "docker-compose", "kubectl"],
        },
    },
    {
        "nl": [
            "list all defined aliases",
            "show all aliases",
            "display current aliases",
        ],
        "cmd": "alias",
        "slots": {},
    },
    {
        "nl": [
            "check what type of command {cmd} is",
            "identify if {cmd} is a builtin, alias, or binary",
            "what is {cmd}",
        ],
        "cmd": "type {cmd}",
        "slots": {"cmd": ["ls", "cd", "grep", "echo", "test", "alias", "which"]},
    },
    {
        "nl": [
            "find the path of {cmd}",
            "where is {cmd} installed",
            "which {cmd}",
            "locate the {cmd} binary",
        ],
        "cmd": "which {cmd}",
        "slots": {"cmd": ["python3", "node", "gcc", "docker", "nginx", "git", "vim"]},
    },
    {
        "nl": [
            "check if {cmd} is installed",
            "verify {cmd} exists",
            "is {cmd} available on this system",
        ],
        "cmd": "command -v {cmd}",
        "slots": {"cmd": ["python3", "node", "docker", "git", "curl", "wget", "jq"]},
    },
    {
        "nl": [
            "source {file}",
            "load {file} into current shell",
            "execute {file} in current shell context",
        ],
        "cmd": "source {file}",
        "slots": {"file": [".bashrc", ".profile", ".env", "env.sh", "setup.sh", "vars.sh"]},
    },
    {
        "nl": [
            "enable exit on error in script",
            "make script exit on first error",
            "turn on strict error handling",
        ],
        "cmd": "set -e",
        "slots": {},
    },
    {
        "nl": [
            "enable debug mode for shell script",
            "turn on script tracing",
            "print each command before executing",
        ],
        "cmd": "set -x",
        "slots": {},
    },
    {
        "nl": [
            "enable pipeline error propagation",
            "make pipe failures cause script exit",
            "set pipefail option",
        ],
        "cmd": "set -o pipefail",
        "slots": {},
    },
    {
        "nl": [
            "check if file {file} exists",
            "test if {file} exists",
            "does {file} exist",
        ],
        "cmd": "test -f {file} && echo exists || echo missing",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "check if directory {dir} exists",
            "test if {dir} exists",
            "does directory {dir} exist",
        ],
        "cmd": "test -d {dir} && echo exists || echo missing",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "loop through all .txt files and print their names",
            "iterate over text files in current directory",
            "list all txt files with a for loop",
        ],
        "cmd": 'for f in *.txt; do echo "$f"; done',
        "slots": {},
    },
    {
        "nl": [
            "loop through all {pattern} files and print names",
            "iterate over {pattern} files",
            "list all {pattern} files using a for loop",
        ],
        "cmd": 'for f in {pattern}; do echo "$f"; done',
        "slots": {"pattern": ["*.py", "*.log", "*.conf", "*.sh", "*.yaml", "*.json"]},
    },
    {
        "nl": [
            "read {file} line by line",
            "process {file} one line at a time",
            "iterate through lines of {file}",
        ],
        "cmd": 'while read line; do echo "$line"; done < {file}',
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "loop from 1 to {n}",
            "count from 1 to {n}",
            "numeric for loop 1 to {n}",
            "iterate from 1 to {n}",
        ],
        "cmd": "for i in $(seq 1 {n}); do echo $i; done",
        "slots": {"n": ["5", "10", "20", "50", "100"]},
    },
    {
        "nl": [
            "run {cmd} every {n} seconds in a loop",
            "repeat {cmd} every {n} seconds",
            "continuously run {cmd} with {n} second interval",
        ],
        "cmd": "while true; do {cmd}; sleep {n}; done",
        "slots": {
            "cmd": ["date", "free -m", "df -h", "uptime", "ss -s"],
            "n": ["1", "2", "5", "10", "30"],
        },
    },
    {
        "nl": [
            "search command history for {pattern}",
            "find {pattern} in history",
            "show history entries matching {pattern}",
        ],
        "cmd": "history | grep {pattern}",
        "slots": {"pattern": ["git", "docker", "ssh", "python", "curl", "vim"]},
    },
    {
        "nl": [
            "temporarily change to {dir} and run a command",
            "pushd to {dir}",
            "change to {dir} and remember where I was",
        ],
        "cmd": "pushd {dir}",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "set a cleanup trap on script exit",
            "run cleanup on EXIT signal",
            "ensure cleanup runs when script ends",
        ],
        "cmd": "trap 'echo cleanup; rm -f /tmp/lockfile' EXIT",
        "slots": {},
    },
    {
        "nl": [
            "redirect all script output to {file}",
            "send all output to log file {file}",
            "log everything to {file}",
        ],
        "cmd": "exec > {file} 2>&1",
        "slots": {"file": ["output.log", "script.log", "run.log", "debug.log"]},
    },
    {
        "nl": [
            "show the exit code of the last command",
            "check if the last command succeeded",
            "what was the exit status",
        ],
        "cmd": "echo $?",
        "slots": {},
    },
    {
        "nl": [
            "get the PID of the current shell",
            "show current process ID",
            "print shell PID",
        ],
        "cmd": "echo $$",
        "slots": {},
    },
    {
        "nl": [
            "count arguments passed to a script",
            "how many arguments were given",
            "number of command line arguments",
        ],
        "cmd": "echo $#",
        "slots": {},
    },
    {
        "nl": [
            "run {cmd1} then {cmd2} regardless of success",
            "execute {cmd1} followed by {cmd2} always",
            "chain {cmd1} and {cmd2} unconditionally",
        ],
        "cmd": "{cmd1}; {cmd2}",
        "slots": {
            "cmd1": ["make clean", "rm -f output.log", "echo 'step 1'"],
            "cmd2": ["make build", "echo 'done'", "echo 'step 2'"],
        },
    },
    {
        "nl": [
            "watch {cmd} output refreshing every 2 seconds",
            "monitor {cmd} output continuously",
            "live watch {cmd}",
        ],
        "cmd": "watch -n 2 {cmd}",
        "slots": {"cmd": ["df -h", "free -m", "uptime", "ss -s", "ls -la"]},
    },
    {
        "nl": [
            "run {cmd} with a timeout of {n} seconds",
            "execute {cmd} with {n} second time limit",
            "time-limit {cmd} to {n} seconds",
        ],
        "cmd": "timeout {n} {cmd}",
        "slots": {
            "cmd": ["curl -s https://example.com", "ping google.com", "sleep 100"],
            "n": ["5", "10", "30", "60"],
        },
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 11: NETWORK DIAGNOSTICS PIPELINES (~20 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "get the HTTP headers from {url}",
            "fetch only headers from {url}",
            "show HTTP response headers for {url}",
        ],
        "cmd": "curl -I {url}",
        "slots": {
            "url": [
                "https://example.com",
                "https://google.com",
                "https://github.com",
                "https://api.example.com",
            ],
        },
    },
    {
        "nl": [
            "download {url} to {file}",
            "save {url} as {file}",
            "fetch {url} and save to {file}",
        ],
        "cmd": "curl -o {file} {url}",
        "slots": {
            "url": [
                "https://example.com/file.tar.gz",
                "https://example.com/data.zip",
                "https://example.com/script.sh",
            ],
            "file": ["download.tar.gz", "data.zip", "script.sh"],
        },
    },
    {
        "nl": [
            "look up DNS for {host}",
            "resolve {host} DNS",
            "quick DNS lookup for {host}",
            "get IP address for {host}",
        ],
        "cmd": "dig {host} +short",
        "slots": {"host": ["google.com", "example.com", "github.com", "cloudflare.com"]},
    },
    {
        "nl": [
            "DNS lookup for {host} using nslookup",
            "resolve {host} with nslookup",
            "nslookup {host}",
        ],
        "cmd": "nslookup {host}",
        "slots": {"host": ["google.com", "example.com", "github.com"]},
    },
    {
        "nl": [
            "list all IP addresses on this machine",
            "show my IP addresses",
            "what are my local IPs",
        ],
        "cmd": "ip a | grep 'inet '",
        "slots": {},
    },
    {
        "nl": [
            "show the default gateway",
            "what is the default route",
            "display default gateway",
        ],
        "cmd": "ip route show default",
        "slots": {},
    },
    {
        "nl": [
            "show socket statistics summary",
            "display network socket summary",
            "quick overview of socket usage",
        ],
        "cmd": "ss -s",
        "slots": {},
    },
    {
        "nl": [
            "trace the route to {host}",
            "traceroute to {host}",
            "show network path to {host}",
        ],
        "cmd": "traceroute -n {host}",
        "slots": {"host": HOSTS},
    },
    {
        "nl": [
            "ping {host} 4 times",
            "test connectivity to {host}",
            "check if {host} is reachable",
            "ping {host}",
        ],
        "cmd": "ping -c 4 {host}",
        "slots": {"host": HOSTS},
    },
    {
        "nl": [
            "get just the HTTP status code from {url}",
            "check HTTP status of {url}",
            "what status code does {url} return",
        ],
        "cmd": 'curl -w "%{{http_code}}" -s -o /dev/null {url}',
        "slots": {
            "url": [
                "https://example.com",
                "https://google.com",
                "https://api.example.com/health",
                "https://httpbin.org/status/200",
            ],
        },
    },
    {
        "nl": [
            "show the ARP table",
            "display ARP cache",
            "list ARP entries",
        ],
        "cmd": "ip neigh",
        "slots": {},
    },
    {
        "nl": [
            "simple DNS lookup for {host}",
            "resolve {host} quickly",
            "host lookup for {host}",
        ],
        "cmd": "host {host}",
        "slots": {"host": ["google.com", "example.com", "github.com"]},
    },
    {
        "nl": [
            "test if port {port} is open on {host}",
            "check if {host} port {port} is accepting connections",
            "test connectivity to {host} on port {port}",
            "check if {host}:{port} is reachable",
        ],
        "cmd": "nc -zv {host} {port}",
        "slots": {"host": HOSTS, "port": PORTS},
    },
    {
        "nl": [
            "show all established TCP connections",
            "list active TCP connections",
            "display current TCP connections",
        ],
        "cmd": "ss -t state established",
        "slots": {},
    },
    {
        "nl": [
            "download {url} silently and search for {pattern}",
            "fetch {url} and grep for {pattern}",
        ],
        "cmd": "wget -q -O - {url} | grep {pattern}",
        "slots": {
            "url": ["https://example.com", "https://example.com/page.html"],
            "pattern": SEARCH_PATTERNS,
        },
    },
    {
        "nl": [
            "show response time for {url}",
            "measure how long {url} takes to respond",
            "benchmark {url} response time",
        ],
        "cmd": 'curl -w "\\nTime: %{{time_total}}s\\n" -s -o /dev/null {url}',
        "slots": {
            "url": [
                "https://example.com",
                "https://google.com",
                "https://api.example.com",
                "https://github.com",
            ],
        },
    },
    {
        "nl": [
            "list all open network connections",
            "show all network sockets",
            "display all connections",
        ],
        "cmd": "ss -tunapl",
        "slots": {},
    },
    {
        "nl": [
            "check the SSL certificate expiry for {host}",
            "when does the SSL cert for {host} expire",
            "SSL certificate dates for {host}",
        ],
        "cmd": "openssl s_client -connect {host}:443 2>/dev/null | openssl x509 -noout -dates",
        "slots": {"host": ["google.com", "example.com", "github.com"]},
    },
    {
        "nl": [
            "show the public IP address of this machine",
            "what is my public IP",
            "get my external IP address",
        ],
        "cmd": "curl -s https://ifconfig.me",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 12: SYSTEM ADMINISTRATION SCENARIOS (~30 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "find and kill all {proc} processes",
            "kill all {proc} processes",
            "terminate all {proc} instances",
            "stop all running {proc} processes",
        ],
        "cmd": "pkill {proc}",
        "slots": {"proc": PROC_NAMES},
    },
    {
        "nl": [
            "find {proc} process and kill it using ps and xargs",
            "kill {proc} using ps aux pipe",
        ],
        "cmd": "ps aux | grep {proc} | grep -v grep | awk '{{print $2}}' | xargs kill",
        "slots": {"proc": PROC_NAMES},
    },
    {
        "nl": [
            "find PID of {proc}",
            "get the process ID of {proc}",
            "what is the PID of {proc}",
        ],
        "cmd": "pgrep -a {proc}",
        "slots": {"proc": PROC_NAMES},
    },
    {
        "nl": [
            "delete log files older than 30 days in /var/log",
            "clean up old log files",
            "remove logs older than 30 days",
        ],
        "cmd": "find /var/log -name '*.log' -mtime +30 -delete",
        "slots": {},
    },
    {
        "nl": [
            "clean temp files older than 7 days",
            "remove old temporary files",
            "delete temp files older than a week",
        ],
        "cmd": "find /tmp -type f -mtime +7 -delete",
        "slots": {},
    },
    {
        "nl": [
            "sync {dir} to {dest} using rsync",
            "copy {dir} to {dest} preserving attributes",
            "rsync {dir} to {dest}",
        ],
        "cmd": "rsync -avz {dir}/ {dest}/",
        "slots": {
            "dir": ["/home/user/data", "/var/www/html", "/opt/app", "/srv/data"],
            "dest": ["/backup/data", "/mnt/backup", "/tmp/sync", "/media/external"],
        },
    },
    {
        "nl": [
            "sync {dir} to remote {remote} via SSH",
            "rsync {dir} to remote server {remote}",
            "remote copy {dir} to {remote} with rsync",
        ],
        "cmd": "rsync -avz -e ssh {dir}/ {remote}",
        "slots": {
            "dir": ["/home/user/data", "/var/www/html", "/opt/app"],
            "remote": ["user@server:/backup/", "admin@192.168.1.10:/opt/", "deploy@prod:/var/www/"],
        },
    },
    {
        "nl": [
            "create a compressed backup of {dir}",
            "tar and gzip {dir}",
            "make a tar.gz archive of {dir}",
            "backup {dir} to a tar.gz file",
        ],
        "cmd": "tar czf backup.tar.gz {dir}/",
        "slots": {"dir": ["/home/user", "/var/www", "/opt/app", "/etc", "/srv/data"]},
    },
    {
        "nl": [
            "create a dated backup of {dir}",
            "make a timestamped backup of {dir}",
            "backup {dir} with today's date in filename",
        ],
        "cmd": "tar czf backup-$(date +%Y%m%d).tar.gz {dir}/",
        "slots": {"dir": ["/home/user", "/var/www", "/opt/app", "/etc"]},
    },
    {
        "nl": [
            "list all cron jobs",
            "show my crontab",
            "display scheduled cron tasks",
            "view crontab entries",
        ],
        "cmd": "crontab -l",
        "slots": {},
    },
    {
        "nl": [
            "check status of {service} and restart if needed",
            "restart {service} service",
            "check and restart {service}",
        ],
        "cmd": "systemctl status {service} && systemctl restart {service}",
        "slots": {"service": SERVICES},
    },
    {
        "nl": [
            "list failed systemd services",
            "show failed services",
            "which services have failed",
        ],
        "cmd": "systemctl list-units --failed",
        "slots": {},
    },
    {
        "nl": [
            "show last 10 logins",
            "recent login history",
            "who logged in recently",
        ],
        "cmd": "last -n 10",
        "slots": {},
    },
    {
        "nl": [
            "show who is logged in and what they are doing",
            "display active users and their commands",
            "who is on the system right now",
        ],
        "cmd": "w",
        "slots": {},
    },
    {
        "nl": [
            "show full system information",
            "display OS and kernel info",
            "system information summary",
        ],
        "cmd": "uname -a",
        "slots": {},
    },
    {
        "nl": [
            "show CPU model information",
            "what CPU is in this machine",
            "display processor info",
        ],
        "cmd": "cat /proc/cpuinfo | grep 'model name' | head -1",
        "slots": {},
    },
    {
        "nl": [
            "show total system memory",
            "how much RAM does this system have",
            "display total memory",
        ],
        "cmd": "cat /proc/meminfo | grep MemTotal",
        "slots": {},
    },
    {
        "nl": [
            "list block devices with filesystem info",
            "show all disks and partitions",
            "display disk layout",
        ],
        "cmd": "lsblk -f",
        "slots": {},
    },
    {
        "nl": [
            "show mounted filesystems in a formatted table",
            "display mount points neatly",
            "list all mounts formatted",
        ],
        "cmd": "mount | column -t",
        "slots": {},
    },
    {
        "nl": [
            "find files newer than {ref} in {dir}",
            "show files modified after {ref} under {dir}",
            "files changed since {ref} in {dir}",
        ],
        "cmd": "find {dir} -name '*.py' -newer {ref}",
        "slots": {
            "ref": ["reference.txt", "marker", "timestamp.txt"],
            "dir": DIRS,
        },
    },
    {
        "nl": [
            "extract a tar.gz archive {file}",
            "unpack {file}",
            "decompress {file}",
        ],
        "cmd": "tar xzf {file}",
        "slots": {"file": ["backup.tar.gz", "archive.tar.gz", "release.tar.gz", "data.tar.gz"]},
    },
    {
        "nl": [
            "list contents of tar archive {file}",
            "show files in {file} without extracting",
            "peek inside {file}",
        ],
        "cmd": "tar tzf {file}",
        "slots": {"file": ["backup.tar.gz", "archive.tar.gz", "release.tar.gz"]},
    },
    {
        "nl": [
            "check disk usage of {dir}",
            "how much space does {dir} use",
            "disk usage summary for {dir}",
        ],
        "cmd": "du -sh {dir}",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "show disk space usage",
            "display filesystem disk usage",
            "check free disk space",
            "how much disk space is available",
        ],
        "cmd": "df -h",
        "slots": {},
    },
    {
        "nl": [
            "show memory usage",
            "display RAM usage",
            "check free memory",
            "how much memory is free",
        ],
        "cmd": "free -h",
        "slots": {},
    },
    {
        "nl": [
            "show the number of CPU cores",
            "how many CPUs does this system have",
            "count CPU cores",
        ],
        "cmd": "nproc",
        "slots": {},
    },
    {
        "nl": [
            "show kernel version",
            "what kernel is running",
            "display kernel release",
        ],
        "cmd": "uname -r",
        "slots": {},
    },
    {
        "nl": [
            "restart {service}",
            "restart the {service} service",
        ],
        "cmd": "systemctl restart {service}",
        "slots": {"service": SERVICES},
    },
    {
        "nl": [
            "enable {service} to start at boot",
            "make {service} start automatically",
            "enable {service} on boot",
        ],
        "cmd": "systemctl enable {service}",
        "slots": {"service": SERVICES},
    },
    {
        "nl": [
            "check the status of {service}",
            "is {service} running",
            "show {service} status",
        ],
        "cmd": "systemctl status {service}",
        "slots": {"service": SERVICES},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 13: SECURITY & FORENSICS PIPELINES (~20 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    {
        "nl": [
            "show top 10 IPs with failed SSH logins",
            "find the most frequent failed SSH login IPs",
            "which IPs have the most failed SSH attempts",
        ],
        "cmd": "grep 'Failed password' /var/log/auth.log | awk '{{print $(NF-3)}}' | sort | uniq -c | sort -rn | head -10",
        "slots": {},
    },
    {
        "nl": [
            "find all SUID files on the system",
            "list SUID binaries",
            "show files with SUID bit set",
            "find setuid files",
        ],
        "cmd": "find / -perm -4000 2>/dev/null",
        "slots": {},
    },
    {
        "nl": [
            "find all SGID files on the system",
            "list SGID binaries",
            "show files with SGID bit set",
        ],
        "cmd": "find / -perm -2000 2>/dev/null",
        "slots": {},
    },
    {
        "nl": [
            "find world-writable files",
            "list files writable by everyone",
            "show world-writable files on the system",
        ],
        "cmd": "find / -perm -o+w -type f 2>/dev/null",
        "slots": {},
    },
    {
        "nl": [
            "find files with no owner",
            "show orphaned files",
            "find files without user or group",
        ],
        "cmd": "find / -nouser -o -nogroup 2>/dev/null",
        "slots": {},
    },
    {
        "nl": [
            "find world-executable scripts",
            "list scripts executable by everyone",
            "show world-executable .sh files",
        ],
        "cmd": "find / -name '*.sh' -perm -o+x 2>/dev/null",
        "slots": {},
    },
    {
        "nl": [
            "show login history from wtmp",
            "display user login records",
            "recent login history",
        ],
        "cmd": "last -f /var/log/wtmp | head -20",
        "slots": {},
    },
    {
        "nl": [
            "show failed login attempts",
            "display bad login records",
            "recent failed logins",
        ],
        "cmd": "lastb | head -20",
        "slots": {},
    },
    {
        "nl": [
            "find accounts with UID 0 (root privileges)",
            "which users have UID 0",
            "check for UID 0 accounts besides root",
        ],
        "cmd": "awk -F: '$3 == 0' /etc/passwd",
        "slots": {},
    },
    {
        "nl": [
            "find accounts with no password",
            "check for empty password accounts",
            "list users with no password set",
        ],
        "cmd": "awk -F: '$2 == \"\" {{print $1}}' /etc/shadow",
        "slots": {},
    },
    {
        "nl": [
            "show all listening services",
            "list all services accepting connections",
            "what services are listening for connections",
        ],
        "cmd": "ss -tulnp | awk '$1 == \"LISTEN\"'",
        "slots": {},
    },
    {
        "nl": [
            "find SSH directories under /home",
            "locate .ssh directories",
            "show user SSH directories",
        ],
        "cmd": "find /home -name '.ssh' -type d",
        "slots": {},
    },
    {
        "nl": [
            "find hardcoded passwords in /etc",
            "search for password strings in config files",
            "grep for passwords in /etc",
        ],
        "cmd": "grep -r 'password' /etc/ 2>/dev/null",
        "slots": {},
    },
    {
        "nl": [
            "check SSL certificate expiry for {host}",
            "when does the {host} SSL certificate expire",
            "SSL cert expiration date for {host}",
        ],
        "cmd": "openssl s_client -connect {host}:443 2>/dev/null | openssl x509 -noout -dates",
        "slots": {"host": ["google.com", "example.com", "github.com"]},
    },
    {
        "nl": [
            "show failed SSH logins from {log}",
            "list failed SSH authentication attempts from {log}",
            "check for SSH brute force attempts in {log}",
        ],
        "cmd": "grep 'Failed password' {log} | tail -20",
        "slots": {"log": AUTH_LOGS},
    },
    {
        "nl": [
            "find files with permissions 777",
            "list files with full permissions for everyone",
            "show files with 777 permissions",
        ],
        "cmd": "find / -perm 777 -type f 2>/dev/null",
        "slots": {},
    },
    {
        "nl": [
            "list all users who can sudo",
            "show sudoers",
            "who has sudo access",
        ],
        "cmd": "grep -E '^[^#]' /etc/sudoers | grep -v '^$'",
        "slots": {},
    },
    {
        "nl": [
            "check open ports on {host}",
            "scan {host} for open ports",
            "port scan {host}",
        ],
        "cmd": "nmap -sT {host}",
        "slots": {"host": HOSTS},
    },
    {
        "nl": [
            "find recently modified files in /etc",
            "show config files changed in the last day",
            "what changed in /etc recently",
        ],
        "cmd": "find /etc -mtime -1 -type f 2>/dev/null",
        "slots": {},
    },
    {
        "nl": [
            "check for unauthorized cron jobs",
            "list all user crontabs",
            "show cron jobs for all users",
        ],
        "cmd": "for user in $(cut -f1 -d: /etc/passwd); do crontab -l -u $user 2>/dev/null | grep -v '^#' | grep -v '^$' && echo \"--- $user ---\"; done",
        "slots": {},
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# Category 14: ADDITIONAL PIPELINE & COMPOSITION PATTERNS (~70 templates)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES_PIPELINE += [
    # --- More regex patterns ---
    {
        "nl": [
            "extract only unique email domains from {file}",
            "list distinct email domains in {file}",
            "show unique domains from email addresses in {file}",
        ],
        "cmd": "grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}' {file} | awk -F'@' '{{print $2}}' | sort -u",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find lines with valid JSON objects in {file}",
            "grep for JSON-like patterns in {file}",
        ],
        "cmd": "grep -E '^\\s*\\{{' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find all port numbers in {file}",
            "extract port numbers from {file}",
            "grep for port patterns in {file}",
        ],
        "cmd": "grep -oE ':[0-9]{{1,5}}' {file} | sed 's/://'",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "validate IP addresses are properly formatted in {file}",
            "find malformed IPs in {file}",
        ],
        "cmd": "grep -E '([0-9]{{1,3}}\\.){3}[0-9]{{1,3}}' {file} | grep -vE '\\b(([0-9]|[1-9][0-9]|1[0-9]{{2}}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{{2}}|2[0-4][0-9]|25[0-5])\\b'",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "extract hashtags from {file}",
            "find all hashtags in {file}",
            "grep for hashtag patterns in {file}",
        ],
        "cmd": "grep -oE '#[a-zA-Z0-9_]+' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "find CIDR notation addresses in {file}",
            "extract CIDR subnets from {file}",
        ],
        "cmd": "grep -oE '([0-9]{{1,3}}\\.){3}[0-9]{{1,3}}/[0-9]{{1,2}}' {file}",
        "slots": {"file": REGEX_FILES},
    },
    {
        "nl": [
            "count lines matching each search pattern in {file}",
            "how many errors vs warnings in {file}",
        ],
        "cmd": 'echo "errors: $(grep -c error {file}), warnings: $(grep -c warning {file})"',
        "slots": {"file": LOG_FILES},
    },
    # --- More pipeline composition ---
    {
        "nl": [
            "show the 10 most common words in {file}",
            "top 10 word frequency in {file}",
            "most frequent words in {file}",
        ],
        "cmd": "tr -s ' ' '\\n' < {file} | tr 'A-Z' 'a-z' | sort | uniq -c | sort -rn | head -10",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "show processes sorted by memory usage with header",
            "display top memory consumers with column headers",
        ],
        "cmd": "ps aux --sort=-%mem | head -11",
        "slots": {},
    },
    {
        "nl": [
            "find all unique file extensions in {dir}",
            "list file types in {dir}",
            "what file extensions exist in {dir}",
        ],
        "cmd": "find {dir} -type f | sed 's/.*\\.//' | sort -u",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "count files by extension in {dir}",
            "file type distribution in {dir}",
            "how many files of each type in {dir}",
        ],
        "cmd": "find {dir} -type f | sed 's/.*\\.//' | sort | uniq -c | sort -rn",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "show the most recently modified files in {dir}",
            "latest changed files in {dir}",
            "most recent files in {dir}",
        ],
        "cmd": "find {dir} -type f -printf '%T@ %p\\n' | sort -rn | head -10 | cut -d' ' -f2-",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "get the total size of all {pattern} files in {dir}",
            "how much space do {pattern} files take in {dir}",
        ],
        "cmd": "find {dir} -name '{pattern}' -exec du -ch {{}} + | tail -1",
        "slots": {
            "pattern": ["*.log", "*.py", "*.txt", "*.json", "*.csv"],
            "dir": DIRS,
        },
    },
    # --- More log analysis ---
    {
        "nl": [
            "show the busiest minute in {log}",
            "peak traffic minute in {log}",
            "when was the highest request rate in {log}",
        ],
        "cmd": "awk '{{print $4}}' {log} | cut -d'[' -f2 | cut -d']' -f1 | cut -d':' -f1-3 | sort | uniq -c | sort -rn | head -5",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show average response size in {log}",
            "mean response bytes in {log}",
        ],
        "cmd": "awk '{{sum+=$10; n++}} END {{print sum/n}}' {log}",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show HTTP method distribution in {log}",
            "breakdown of GET vs POST vs PUT in {log}",
            "request method counts in {log}",
        ],
        "cmd": "awk '{{print $6}}' {log} | tr -d '\"' | sort | uniq -c | sort -rn",
        "slots": {"log": ACCESS_LOGS},
    },
    {
        "nl": [
            "find 404 errors for a specific path {pattern} in {log}",
            "check if {pattern} is returning 404 in {log}",
        ],
        "cmd": "grep {pattern} {log} | awk '$9 == 404'",
        "slots": {"pattern": ["/api", "/admin", "/login", "/health"], "log": ACCESS_LOGS},
    },
    {
        "nl": [
            "show error rate as percentage in {log}",
            "what percentage of requests are errors in {log}",
        ],
        "cmd": "awk '{{total++; if ($9 >= 400) errors++}} END {{printf \"%.2f%%\\n\", errors/total*100}}' {log}",
        "slots": {"log": ACCESS_LOGS},
    },
    # --- More awk patterns ---
    {
        "nl": [
            "extract specific columns {col} from {delim}-delimited {file}",
            "get column {col} using {delim} as separator from {file}",
        ],
        "cmd": "awk -F'{delim}' '{{print ${col}}}' {file}",
        "slots": {
            "delim": AWK_DELIMITERS,
            "col": ["1", "2", "3", "$NF"],
            "file": FILES_TEXT,
        },
    },
    {
        "nl": [
            "join lines of {file} with comma separator",
            "combine all lines of {file} into one line separated by commas",
            "merge lines of {file} with commas",
        ],
        "cmd": "paste -sd',' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "replace newlines with spaces in {file}",
            "join all lines of {file} into one line",
            "convert {file} to a single line",
        ],
        "cmd": "tr '\\n' ' ' < {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "show the second to last field of each line in {file}",
            "extract the penultimate column of {file}",
        ],
        "cmd": "awk '{{print $(NF-1)}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "show only lines with exactly 2 fields in {file}",
            "filter lines with 2 columns in {file}",
        ],
        "cmd": "awk 'NF == 2' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "swap first and second columns in {file}",
            "exchange columns 1 and 2 in {file}",
        ],
        "cmd": "awk '{{print $2, $1}}' {file}",
        "slots": {"file": FILES_TEXT},
    },
    # --- More sed patterns ---
    {
        "nl": [
            "comment out lines matching {pattern} in {file}",
            "add # before lines containing {pattern} in {file}",
        ],
        "cmd": "sed '/{pattern}/s/^/# /' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    {
        "nl": [
            "uncomment lines starting with # in {file}",
            "remove # prefix from commented lines in {file}",
        ],
        "cmd": "sed 's/^# //' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "extract text between quotes in {file}",
            "get quoted strings from {file} using sed",
        ],
        "cmd": 'sed -n \'s/.*"\\([^"]*\\)".*/\\1/p\' {file}',
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "add a blank line after every line matching {pattern} in {file}",
            "insert empty line after {pattern} in {file}",
        ],
        "cmd": "sed '/{pattern}/G' {file}",
        "slots": {"pattern": SEARCH_PATTERNS, "file": FILES_TEXT},
    },
    # --- More file operations ---
    {
        "nl": [
            "find the newest file in {dir}",
            "most recently modified file in {dir}",
            "latest file in {dir}",
        ],
        "cmd": "ls -t {dir} | head -1",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "find the oldest file in {dir}",
            "earliest modified file in {dir}",
        ],
        "cmd": "ls -tr {dir} | head -1",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "show disk usage of {dir} sorted by size",
            "directories in {dir} sorted by space used",
        ],
        "cmd": "du -sh {dir}/* | sort -rh",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "find files larger than {size} in {dir}",
            "big files over {size} under {dir}",
        ],
        "cmd": "find {dir} -type f -size +{size} 2>/dev/null",
        "slots": {"size": ["10M", "50M", "100M", "1G"], "dir": DIRS},
    },
    {
        "nl": [
            "count lines across all {pattern} files in {dir}",
            "total line count of {pattern} files in {dir}",
        ],
        "cmd": "find {dir} -name '{pattern}' -exec wc -l {{}} + | tail -1",
        "slots": {
            "pattern": ["*.py", "*.sh", "*.txt", "*.log", "*.conf"],
            "dir": DIRS,
        },
    },
    # --- More data processing ---
    {
        "nl": [
            "remove duplicate lines from {file} without sorting",
            "unique lines preserving order in {file}",
        ],
        "cmd": "awk '!seen[$0]++' {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "check if {file} is valid JSON",
            "validate JSON in {file}",
            "is {file} valid JSON",
        ],
        "cmd": "cat {file} | jq empty && echo 'valid' || echo 'invalid'",
        "slots": {"file": ["data.json", "config.json", "response.json"]},
    },
    {
        "nl": [
            "get the size of each JSON key in {file}",
            "show lengths of top-level JSON values in {file}",
        ],
        "cmd": "cat {file} | jq 'to_entries | .[] | {{key: .key, size: (.value | length)}}'",
        "slots": {"file": ["data.json", "config.json"]},
    },
    {
        "nl": [
            "convert TSV {file} to CSV",
            "change tabs to commas in {file}",
        ],
        "cmd": "tr '\\t' ',' < {file}",
        "slots": {"file": ["data.tsv", "report.tsv", "output.tsv"]},
    },
    {
        "nl": [
            "show byte count of {file}",
            "how many bytes is {file}",
            "size of {file} in bytes",
        ],
        "cmd": "wc -c {file}",
        "slots": {"file": FILES},
    },
    {
        "nl": [
            "show character count of {file}",
            "count characters in {file}",
        ],
        "cmd": "wc -m {file}",
        "slots": {"file": FILES_TEXT},
    },
    # --- More shell constructs ---
    {
        "nl": [
            "process each line of {file} and prefix with line number",
            "number lines while processing {file}",
        ],
        "cmd": "nl {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "run a command for each line in {file}",
            "execute a command per line of {file}",
        ],
        "cmd": 'while read line; do echo "Processing: $line"; done < {file}',
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "replace colons with newlines in {var}",
            "show {var} one entry per line",
            "split {var} by colons",
        ],
        "cmd": "echo ${var} | tr ':' '\\n'",
        "slots": {"var": ["$PATH", "$MANPATH", "$LD_LIBRARY_PATH"]},
    },
    {
        "nl": [
            "list only directories in current location",
            "show only dirs here",
            "list directories only",
        ],
        "cmd": "ls -d */",
        "slots": {},
    },
    {
        "nl": [
            "list only hidden files",
            "show dotfiles in current directory",
        ],
        "cmd": "ls -d .*",
        "slots": {},
    },
    {
        "nl": [
            "show total disk space used by {dir} including subdirectories",
            "recursive size of {dir}",
        ],
        "cmd": "du -sh {dir}",
        "slots": {"dir": DIRS},
    },
    # --- More network patterns ---
    {
        "nl": [
            "fetch and display headers and body from {url}",
            "full HTTP response from {url}",
        ],
        "cmd": "curl -v {url} 2>&1",
        "slots": {
            "url": ["https://example.com", "https://api.example.com/health"],
        },
    },
    {
        "nl": [
            "send a POST request to {url} with JSON data",
            "POST JSON to {url}",
        ],
        "cmd": "curl -s -X POST -H 'Content-Type: application/json' -d '{{\"key\":\"value\"}}' {url}",
        "slots": {
            "url": ["https://api.example.com/data", "https://httpbin.org/post"],
        },
    },
    {
        "nl": [
            "download {url} and resume if interrupted",
            "resumable download of {url}",
        ],
        "cmd": "curl -C - -O {url}",
        "slots": {
            "url": ["https://example.com/large-file.tar.gz", "https://example.com/image.iso"],
        },
    },
    {
        "nl": [
            "follow redirects and download from {url}",
            "curl {url} following redirects",
        ],
        "cmd": "curl -L -O {url}",
        "slots": {
            "url": [
                "https://example.com/download",
                "https://github.com/user/repo/archive/main.tar.gz",
            ],
        },
    },
    # --- More sysadmin patterns ---
    {
        "nl": [
            "find which package provides {cmd}",
            "what package contains {cmd}",
        ],
        "cmd": {
            "debian": "dpkg -S $(which {cmd})",
            "rhel": "rpm -qf $(which {cmd})",
            "arch": "pacman -Qo $(which {cmd})",
        },
        "slots": {"cmd": ["curl", "vim", "gcc", "git", "nginx"]},
    },
    {
        "nl": [
            "show all installed packages",
            "list installed software",
        ],
        "cmd": {
            "debian": "dpkg -l",
            "rhel": "rpm -qa",
            "arch": "pacman -Q",
            "macos": "brew list",
        },
        "slots": {},
    },
    {
        "nl": [
            "force kill process {proc}",
            "send SIGKILL to {proc}",
            "hard kill {proc}",
        ],
        "cmd": "pkill -9 {proc}",
        "slots": {"proc": PROC_NAMES},
    },
    {
        "nl": [
            "send HUP signal to {proc} to reload config",
            "reload {proc} configuration",
            "SIGHUP {proc}",
        ],
        "cmd": "pkill -HUP {proc}",
        "slots": {"proc": PROC_NAMES},
    },
    {
        "nl": [
            "find all processes owned by {user}",
            "show processes running as {user}",
            "list {user}'s processes",
        ],
        "cmd": "ps -u {user}",
        "slots": {"user": USERS},
    },
    {
        "nl": [
            "show open files by {user}",
            "list files opened by user {user}",
        ],
        "cmd": "lsof -u {user}",
        "slots": {"user": USERS},
    },
    {
        "nl": [
            "show directory tree of {dir}",
            "display directory structure of {dir}",
            "tree view of {dir}",
        ],
        "cmd": "tree {dir}",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "show directory tree of {dir} limited to depth 2",
            "tree {dir} two levels deep",
        ],
        "cmd": "tree -L 2 {dir}",
        "slots": {"dir": DIRS},
    },
    {
        "nl": [
            "check if {host} is reachable on port {port}",
            "test TCP connection to {host} on port {port}",
            "can I connect to {host} port {port}",
        ],
        "cmd": "timeout 5 bash -c 'echo > /dev/tcp/{host}/{port}' && echo open || echo closed",
        "slots": {"host": HOSTS, "port": PORTS},
    },
    {
        "nl": [
            "show process tree",
            "display process hierarchy",
            "process tree view",
        ],
        "cmd": "pstree",
        "slots": {},
    },
    {
        "nl": [
            "show process tree for {proc}",
            "display process hierarchy of {proc}",
        ],
        "cmd": "pstree -p $(pgrep {proc} | head -1)",
        "slots": {"proc": PROC_NAMES},
    },
    {
        "nl": [
            "check system uptime",
            "how long has the system been running",
            "show uptime and load average",
        ],
        "cmd": "uptime",
        "slots": {},
    },
    {
        "nl": [
            "compress {file} with gzip",
            "gzip {file}",
        ],
        "cmd": "gzip {file}",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "decompress {file}.gz",
            "gunzip {file}.gz",
            "uncompress {file}.gz",
        ],
        "cmd": "gunzip {file}.gz",
        "slots": {"file": FILES_TEXT},
    },
    {
        "nl": [
            "view compressed {file} without decompressing",
            "read gzipped {file} contents",
        ],
        "cmd": "zcat {file}",
        "slots": {"file": ["data.gz", "log.gz", "backup.gz", "access.log.gz"]},
    },
    {
        "nl": [
            "search inside compressed {file} for {pattern}",
            "grep gzipped {file} for {pattern}",
        ],
        "cmd": "zgrep {pattern} {file}",
        "slots": {
            "pattern": SEARCH_PATTERNS,
            "file": ["access.log.gz", "syslog.gz", "error.log.gz", "data.gz"],
        },
    },
]
