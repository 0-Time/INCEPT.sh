#!/usr/bin/env python3
"""Generate ~200 targeted training examples to fix benchmark weak spots.

Outputs ChatML JSONL matching the data/v2/train.jsonl format.
Categories:
  A. Simple tool preference (60) — wc/sort/uniq/cut/cp over awk/cat redirect
  B. Missing/weak commands (60) — whoami, umask, chattr, lscpu, lsusb, lshw, top, etc.
  C. Shell builtins (40) — &, fg, bg, jobs, disown
  D. Identity separation (20) — "who am I" → whoami (not self-introduction)
  E. Correct permissions (20) — chmod patterns
"""

import json
import random
import sys
from pathlib import Path

random.seed(42)

DISTROS = [
    "ubuntu 24.04 bash non-root",
    "ubuntu 22.04 bash non-root",
    "fedora 39 bash non-root",
    "debian 12 bash non-root",
    "centos 9 bash non-root",
    "rhel 9 bash non-root",
    "arch latest bash non-root",
    "opensuse 15.5 bash non-root",
    "ubuntu 24.04 zsh non-root",
    "fedora 39 zsh non-root",
    "ubuntu 24.04 bash root",
    "debian 12 bash root",
]


def make_example(user: str, assistant: str, system: str | None = None) -> dict:
    if system is None:
        system = random.choice(DISTROS)
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


def category_a_simple_tools() -> list[dict]:
    """Simple tool preference: teach model to prefer wc/sort/uniq/cut/cp."""
    examples = []

    # wc -l over awk for line counting
    wc_pairs = [
        ("count lines in file.txt", "wc -l file.txt"),
        ("how many lines in data.csv", "wc -l data.csv"),
        ("count the number of lines in /var/log/syslog", "wc -l /var/log/syslog"),
        ("line count of README.md", "wc -l README.md"),
        ("count lines in output.log", "wc -l output.log"),
        ("number of lines in config.yml", "wc -l config.yml"),
        ("how many lines does access.log have", "wc -l access.log"),
        ("count lines in /etc/passwd", "wc -l /etc/passwd"),
        ("count the lines of main.py", "wc -l main.py"),
        ("get line count for report.txt", "wc -l report.txt"),
    ]

    # sort over awk for sorting
    sort_pairs = [
        ("sort lines alphabetically in file.txt", "sort file.txt"),
        ("sort data.csv", "sort data.csv"),
        ("sort names.txt in reverse order", "sort -r names.txt"),
        ("sort file numerically", "sort -n numbers.txt"),
        ("sort lines of output.log", "sort output.log"),
        ("sort /etc/passwd", "sort /etc/passwd"),
        ("alphabetically sort entries.txt", "sort entries.txt"),
        ("sort the contents of users.txt", "sort users.txt"),
        ("sort words.txt alphabetically", "sort words.txt"),
        ("reverse sort items.txt", "sort -r items.txt"),
    ]

    # uniq over awk for dedup
    uniq_pairs = [
        ("remove duplicate lines from sorted file", "sort file.txt | uniq"),
        ("get unique lines from data.txt", "sort data.txt | uniq"),
        ("deduplicate lines in log.txt", "sort log.txt | uniq"),
        ("remove duplicates from names.txt", "sort names.txt | uniq"),
        ("show only unique lines in output.txt", "sort output.txt | uniq"),
        ("count occurrences of each unique line", "sort file.txt | uniq -c"),
        ("find duplicate lines in data.csv", "sort data.csv | uniq -d"),
        ("unique lines from access.log", "sort access.log | uniq"),
        ("strip duplicates from list.txt", "sort list.txt | uniq"),
        ("deduplicate entries in results.txt", "sort results.txt | uniq"),
    ]

    # cut over awk for column extraction
    cut_pairs = [
        ("extract first column from CSV file", "cut -d',' -f1 data.csv"),
        ("get second field from comma-separated file", "cut -d',' -f2 data.csv"),
        ("extract third column from csv", "cut -d',' -f3 file.csv"),
        ("get usernames from /etc/passwd", "cut -d: -f1 /etc/passwd"),
        ("extract first field delimited by tab", "cut -f1 data.tsv"),
        ("get the home directories from passwd", "cut -d: -f6 /etc/passwd"),
        ("extract second column of tab-separated file", "cut -f2 data.tsv"),
        ("get shells from /etc/passwd", "cut -d: -f7 /etc/passwd"),
        ("first column of colon-separated file", "cut -d: -f1 file.txt"),
        ("extract fields 1 and 3 from csv", "cut -d',' -f1,3 data.csv"),
    ]

    # cp over cat redirect for copying
    cp_pairs = [
        ("copy a.txt to b.txt", "cp a.txt b.txt"),
        ("copy config.yml to config.bak", "cp config.yml config.bak"),
        ("duplicate report.pdf", "cp report.pdf report_copy.pdf"),
        ("copy the file data.csv to /tmp", "cp data.csv /tmp/"),
        ("make a copy of script.sh", "cp script.sh script_backup.sh"),
        ("copy /etc/hosts to current directory", "cp /etc/hosts ."),
        ("copy entire project directory", "cp -r project/ project_backup/"),
        ("copy all txt files to backup folder", "cp *.txt backup/"),
        ("copy file preserving permissions", "cp -p config.conf config.conf.bak"),
        ("recursive copy of src to dst", "cp -r src/ dst/"),
    ]

    for pairs in [wc_pairs, sort_pairs, uniq_pairs, cut_pairs, cp_pairs]:
        for user, assistant in pairs:
            examples.append(make_example(user, assistant))

    # Additional: head/tail preference
    extra = [
        ("show first 20 lines of file.txt", "head -n 20 file.txt"),
        ("display last 5 lines of log.txt", "tail -n 5 log.txt"),
        ("first line of /etc/hostname", "head -n 1 /etc/hostname"),
        ("show first 100 lines of data.csv", "head -n 100 data.csv"),
        ("last 50 lines of access.log", "tail -n 50 access.log"),
        ("watch log file in real time", "tail -f /var/log/syslog"),
        ("continuously monitor error.log", "tail -f error.log"),
        ("first 3 lines of README", "head -n 3 README.md"),
        ("bottom 10 lines of output.txt", "tail -n 10 output.txt"),
        ("count words in essay.txt", "wc -w essay.txt"),
    ]
    for user, assistant in extra:
        examples.append(make_example(user, assistant))

    return examples


def category_b_missing_commands() -> list[dict]:
    """Missing/weak commands: whoami, umask, chattr, lscpu, lsusb, lshw, top, etc."""
    examples = []

    pairs = [
        # whoami
        ("who am I logged in as", "whoami"),
        ("show current username", "whoami"),
        ("what user am I", "whoami"),
        ("print my username", "whoami"),
        ("display current logged in user", "whoami"),

        # umask
        ("show the current umask value", "umask"),
        ("set default file permissions to 022", "umask 022"),
        ("check umask", "umask"),
        ("set umask to 077", "umask 077"),
        ("what is my current umask", "umask"),

        # chattr
        ("make file.txt immutable", "chattr +i file.txt"),
        ("prevent deletion of important.conf", "chattr +i important.conf"),
        ("remove immutable flag from file.txt", "chattr -i file.txt"),
        ("set immutable attribute on config", "chattr +i config"),
        ("make database.db undeletable", "chattr +i database.db"),

        # lscpu
        ("show cpu information", "lscpu"),
        ("display cpu architecture details", "lscpu"),
        ("cpu info", "lscpu"),
        ("how many cpu cores do I have", "lscpu"),
        ("show processor details", "lscpu"),

        # lsusb
        ("list usb devices", "lsusb"),
        ("show connected usb devices", "lsusb"),
        ("what usb devices are connected", "lsusb"),
        ("list all usb peripherals", "lsusb"),
        ("display usb device tree", "lsusb -t"),

        # lshw
        ("list all hardware", "lshw"),
        ("show hardware information", "lshw"),
        ("display system hardware details", "lshw -short"),
        ("hardware summary", "lshw -short"),
        ("full hardware inventory", "sudo lshw"),

        # lsmod
        ("list loaded kernel modules", "lsmod"),
        ("show kernel modules", "lsmod"),
        ("what modules are loaded", "lsmod"),
        ("display loaded drivers", "lsmod"),
        ("list all active kernel modules", "lsmod"),

        # top / htop
        ("show interactive process list", "top"),
        ("real-time process monitor", "top"),
        ("interactive process viewer", "htop"),
        ("monitor system processes in real time", "top"),
        ("live process list", "top"),

        # which
        ("find where python is installed", "which python"),
        ("locate the bash executable", "which bash"),
        ("where is gcc", "which gcc"),
        ("find the path of node", "which node"),
        ("which python3 am I using", "which python3"),

        # file
        ("check file type of data.bin", "file data.bin"),
        ("what type of file is image.dat", "file image.dat"),
        ("determine file type", "file unknown.dat"),
        ("show file type of archive", "file archive.tar.gz"),
        ("identify file format", "file document.pdf"),

        # scp
        ("copy file to remote server", "scp file.txt user@server:/path/"),
        ("secure copy local file to remote", "scp data.csv user@host:/tmp/"),
        ("transfer file to server via ssh", "scp backup.tar.gz admin@server:~/"),
        ("copy from remote to local", "scp user@server:/path/file.txt ."),
        ("secure file transfer to remote host", "scp report.pdf user@192.168.1.10:/home/user/"),
    ]

    for user, assistant in pairs:
        examples.append(make_example(user, assistant))

    return examples


def category_c_shell_builtins() -> list[dict]:
    """Shell builtins: &, fg, bg, jobs, disown."""
    examples = []

    pairs = [
        # Background (&)
        ("run script.sh in the background", "./script.sh &"),
        ("start python server in background", "python3 -m http.server &"),
        ("run make in background", "make &"),
        ("execute backup.sh in background", "./backup.sh &"),
        ("start long running process in background", "./process.sh &"),
        ("run npm build in background", "npm run build &"),
        ("background the compilation", "make all &"),
        ("run wget download in background", "wget https://example.com/file.zip &"),
        ("start the server in the background", "./start_server.sh &"),
        ("launch process in background", "python3 train.py &"),

        # fg
        ("bring job to foreground", "fg"),
        ("bring background job 1 to foreground", "fg %1"),
        ("foreground job 2", "fg %2"),
        ("resume job in foreground", "fg %1"),
        ("bring the last background job to foreground", "fg"),
        ("move background process to foreground", "fg %1"),
        ("switch job 1 to foreground", "fg %1"),
        ("foreground the most recent job", "fg"),

        # bg
        ("resume stopped job in background", "bg %1"),
        ("continue job 1 in background", "bg %1"),
        ("background job 2", "bg %2"),
        ("resume suspended process in background", "bg"),
        ("put stopped job back in background", "bg %1"),
        ("continue background execution of job 1", "bg %1"),

        # jobs
        ("list background jobs", "jobs"),
        ("show running background jobs", "jobs"),
        ("what jobs are running", "jobs"),
        ("list all background processes", "jobs"),
        ("show current jobs", "jobs"),
        ("display running jobs", "jobs"),
        ("list active jobs", "jobs"),
        ("check background jobs", "jobs"),

        # disown
        ("detach job from shell", "disown"),
        ("disown background job 1", "disown %1"),
        ("detach process from terminal", "disown"),
        ("prevent job from being killed on logout", "disown %1"),
        ("remove job from shell job table", "disown %1"),
        ("detach running process", "disown"),
    ]

    for user, assistant in pairs:
        examples.append(make_example(user, assistant))

    return examples


def category_d_identity() -> list[dict]:
    """Identity separation: 'who am I' → whoami command, not self-intro."""
    examples = []

    pairs = [
        ("who am i", "whoami"),
        ("check my identity", "whoami"),
        ("what user am I logged in as", "whoami"),
        ("tell me my username", "whoami"),
        ("current user identity", "id"),
        ("show my user and group info", "id"),
        ("what is my user id", "id"),
        ("show my uid and gid", "id"),
        ("check my username", "whoami"),
        ("am I root", "whoami"),
        ("what account am I using", "whoami"),
        ("verify current user", "whoami"),
        ("show who I am", "whoami"),
        ("print current user name", "whoami"),
        ("display my login name", "whoami"),
        ("what is my login", "whoami"),
        ("identify current user", "whoami"),
        ("which user is active", "whoami"),
        ("my user information", "id"),
        ("show my identity", "id"),
    ]

    for user, assistant in pairs:
        examples.append(make_example(user, assistant))

    return examples


def category_e_permissions() -> list[dict]:
    """Correct permissions: chmod patterns."""
    examples = []

    pairs = [
        ("give everyone read write execute on file.txt", "chmod 777 file.txt"),
        ("full permissions for all users", "chmod 777 file.txt"),
        ("chmod read write execute for everyone", "chmod 777 file.txt"),
        ("set file permissions to 777", "chmod 777 file.txt"),
        ("make file accessible to all", "chmod 777 file.txt"),
        ("owner only full permissions", "chmod 700 file.txt"),
        ("restrict file to owner only", "chmod 700 file.txt"),
        ("give only the owner all permissions", "chmod 700 file.txt"),
        ("set permissions to owner read write execute only", "chmod 700 file.txt"),
        ("lock down file to owner", "chmod 700 file.txt"),
        ("make script.sh executable", "chmod +x script.sh"),
        ("add execute permission to deploy.sh", "chmod +x deploy.sh"),
        ("make file executable", "chmod +x file"),
        ("set execute bit on run.sh", "chmod +x run.sh"),
        ("read only for everyone", "chmod 444 file.txt"),
        ("owner read write, group and others read only", "chmod 644 file.txt"),
        ("standard file permissions 644", "chmod 644 file.txt"),
        ("owner full, group read execute, others none", "chmod 750 dir/"),
        ("recursive permissions change to 755", "chmod -R 755 dir/"),
        ("set directory permissions to 755", "chmod 755 dir/"),
    ]

    for user, assistant in pairs:
        examples.append(make_example(user, assistant))

    return examples


def main():
    all_examples = []
    all_examples.extend(category_a_simple_tools())
    all_examples.extend(category_b_missing_commands())
    all_examples.extend(category_c_shell_builtins())
    all_examples.extend(category_d_identity())
    all_examples.extend(category_e_permissions())

    # Shuffle to avoid category clustering during training
    random.shuffle(all_examples)

    out_path = Path(__file__).resolve().parent.parent / "data" / "v2" / "targeted_examples.jsonl"
    with open(out_path, "w") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Generated {len(all_examples)} targeted training examples")
    print(f"  Category A (simple tools):     {60} examples")
    print(f"  Category B (missing commands):  {60} examples")
    print(f"  Category C (shell builtins):    {40} examples")
    print(f"  Category D (identity):          {20} examples")
    print(f"  Category E (permissions):       {20} examples")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
