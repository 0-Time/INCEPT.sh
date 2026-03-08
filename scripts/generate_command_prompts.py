#!/usr/bin/env python3
"""Generate tiered numbered .md prompt files for every command in INCEPT's vocabulary.

Tiered strategy:
  Tier 1 (500 examples): Benchmark weak/failing commands — highest priority
  Tier 2 (200 examples): Benchmark passing commands — reinforcement
  Tier 3 (100 examples): Important common commands not in benchmark
  Tier 4 (20 examples):  Niche/specialized commands

Usage:
    python scripts/generate_command_prompts.py
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = PROJECT_ROOT / "commands"
FLAG_TABLES_DIR = PROJECT_ROOT / "incept" / "compiler" / "flag_tables"

# ===========================================================================
# TIER ASSIGNMENTS
# ===========================================================================

# Tier 1 (500 examples): Commands that FAIL or are WEAK in the 100-question
# benchmark. Includes: awk-overuse victims, missing command knowledge,
# underrepresented shell builtins, identity confusion, and alternate-answer
# commands that need strengthening.
TIER_1 = {
    # Awk-overuse victims (model outputs awk instead of simple tool)
    "wc", "sort", "uniq", "cut",
    # Missing/weak command knowledge
    "whoami", "umask", "chattr", "lsattr", "lscpu", "lsusb", "lshw",
    "lsmod", "top", "htop", "getent",
    # Shell builtins (very few training examples)
    "fg", "bg", "jobs", "disown", "nohup",
    # Identity separation (model self-introduces instead of command)
    "id",
    # Weak in benchmark
    "nano", "vi", "vim", "hexdump", "strings",
    "sftp", "scp", "nmap", "ss",
    "reboot", "shutdown", "kill", "pkill",
    "find", "locate",
    # Alternate-answer commands that need strengthening
    "ifconfig", "netstat", "dmidecode", "mtr", "tracepath",
    # Permission patterns the model gets wrong
    "chmod",
}

# Tier 2 (200 examples): Commands that PASS the benchmark but need
# reinforcement to stay strong. All other benchmark-tested commands.
TIER_2 = {
    "pwd", "ls", "cd", "mkdir", "rmdir", "rm", "mv", "cp", "touch",
    "which", "file", "cat", "less", "more", "head", "tail",
    "grep", "sed", "diff",
    "chown", "chgrp", "su", "sudo",
    "uptime", "date", "uname", "lspci", "free", "df", "du",
    "ps", "lsof", "dmesg",
    "ip", "ping", "traceroute", "wget", "dig", "ssh", "hostname", "curl",
    "history", "clear", "alias", "tar", "zip", "unzip",
}

# Tier 3 (100 examples): Important widely-used commands NOT in the benchmark.
TIER_3 = {
    # Core tools
    "awk", "tr", "tee", "xargs", "ln", "dd", "rsync", "shred",
    "stat", "tree", "nl", "rev", "tac", "comm", "paste", "join",
    "column", "fold", "fmt", "expand", "unexpand", "split",
    # Text processing
    "perl", "jq", "egrep", "fgrep", "emacs", "bc", "xmllint",
    # Archive
    "gzip", "gunzip", "bzip2", "bunzip2", "xz", "zstd", "cpio", "7z",
    "pigz", "zcat", "zgrep", "zless",
    # System
    "hostnamectl", "vmstat", "sensors", "hwclock", "timedatectl", "cal",
    "nproc", "arch", "inxi", "w", "who", "finger",
    # Process
    "pgrep", "pidof", "pstree", "nice", "renice", "strace", "ltrace",
    "time", "timeout", "watch", "flock", "parallel", "ionice",
    "ldd", "pv", "ulimit", "fuser", "pmap",
    # Networking
    "nc", "ncat", "arp", "route", "whois", "nslookup", "host",
    "iperf3", "tcpdump", "ethtool", "iw", "iwconfig", "nmcli", "brctl",
    "ssh-keygen", "ssh-copy-id", "ssh-add", "ssh-keyscan", "ping6",
    # Package management
    "apt", "apt-get", "apt-cache", "apt-mark", "dpkg",
    "dnf", "yum", "rpm",
    "pacman", "zypper", "snap", "flatpak", "brew",
    "pip", "pip3", "npm", "npx", "gem", "cargo",
    # User management
    "useradd", "userdel", "usermod", "groupadd", "groupdel", "groupmod",
    "passwd", "chage", "chpasswd", "chsh", "gpasswd", "visudo",
    "groups", "newgrp", "last", "lastb", "lastlog", "loginctl",
    "setfacl", "getfacl", "wall", "mesg",
    # Service management
    "systemctl", "service", "systemd-analyze", "systemd-run",
    "launchctl", "apachectl",
    # Disk & filesystem
    "mount", "umount", "fdisk", "parted", "lsblk", "blkid", "findmnt",
    "mkfs.ext4", "mkfs.xfs", "mkfs.btrfs", "e2fsck", "fsck",
    "mkswap", "swapon", "swapoff", "fstrim", "smartctl", "hdparm",
    "tune2fs", "resize2fs", "losetup", "quota",
    "pvcreate", "vgcreate", "lvcreate", "lvextend", "mdadm", "btrfs",
    # Version control
    "git",
    # Containers
    "docker", "docker-compose", "podman", "kubectl", "helm",
    "buildah", "skopeo", "chroot", "nsenter", "unshare", "lxc", "virsh",
    # Security
    "iptables", "nft", "ufw", "firewall-cmd", "pfctl",
    "openssl", "gpg", "md5sum", "sha256sum",
    "auditctl", "ausearch", "cryptsetup",
    "fail2ban-client", "rkhunter", "aide",
    "sestatus", "getenforce", "setenforce", "getsebool", "setsebool",
    "restorecon", "chcon", "getcap", "setcap",
    "aa-status", "aa-enforce", "aa-complain",
    # Scheduling
    "crontab", "at", "atq", "atrm", "batch", "anacron",
    # Logging
    "journalctl", "logger", "logrotate", "coredumpctl",
    # Shell builtins & utilities
    "echo", "printf", "export", "env", "printenv",
    "type", "whereis", "man", "source", "declare", "shopt",
    "sleep", "seq", "yes", "base64", "numfmt",
    # Kernel
    "modprobe", "modinfo", "insmod", "rmmod", "depmod",
    "sysctl", "udevadm", "mkinitramfs", "mkinitcpio", "dracut",
    "efibootmgr",
    # Terminal multiplexers
    "tmux", "screen", "script",
    # Developer tools
    "gcc", "g++", "make", "cmake", "gdb", "valgrind",
    "readelf", "objdump", "strip", "ar", "nm",
    # macOS
    "defaults", "caffeinate", "pmset", "pbcopy", "pbpaste",
    "scutil", "csrutil", "softwareupdate", "tmutil",
    "diskutil", "hdiutil", "sips", "open", "mdfind", "ditto",
    "plutil", "sw_vers", "system_profiler", "say", "kextstat",
    "networksetup",
}

# Tier 4 (20 examples): Everything else — niche, specialized, or rare commands.
# No explicit set needed — anything not in Tier 1/2/3 is automatically Tier 4.


def get_tier(cmd: str) -> tuple[int, int]:
    """Return (tier_number, example_count) for a command."""
    if cmd in TIER_1:
        return 1, 500
    elif cmd in TIER_2:
        return 2, 200
    elif cmd in TIER_3:
        return 3, 100
    else:
        return 4, 20


# ===========================================================================
# COMPLETE COMMAND INVENTORY: 587 unique commands grouped by category
# Format: (command_name, description, key_flags_or_subcommands)
# ===========================================================================

COMMANDS_BY_CATEGORY = {
    # ===== 1. FILE OPERATIONS =====
    "File Operations": [
        ("ls", "List directory contents", "-l -a -h -R -S -t -r -1 -d -i --color --sort --group-directories-first -F"),
        ("cp", "Copy files and directories", "-r -R -i -f -n -v -p -a --preserve -u -l -s --backup"),
        ("mv", "Move or rename files", "-i -f -n -v -u --backup -t"),
        ("rm", "Remove files and directories", "-r -R -f -i -I -v -d --preserve-root --no-preserve-root"),
        ("mkdir", "Create directories", "-p -v -m --parents"),
        ("rmdir", "Remove empty directories", "-p -v --ignore-fail-on-non-empty"),
        ("touch", "Create empty files or update timestamps", "-a -m -c -t -d -r --no-create"),
        ("cat", "Concatenate and display files", "-n -b -s -A -E -T -v --number --squeeze-blank"),
        ("head", "Output first part of files", "-n -c -q -v --lines --bytes"),
        ("tail", "Output last part of files", "-n -c -f -F --follow --retry --pid -q -v -s"),
        ("less", "View file with paging", "-N -S -R -X -F -i -J --line-numbers"),
        ("more", "View file page by page", "-d -l -f -p -c -s -u"),
        ("ln", "Create links between files", "-s -f -v -i -r --symbolic --force --relative"),
        ("find", "Search for files in directory hierarchy", "-name -iname -type -size -mtime -atime -ctime -newer -user -group -perm -exec -print0 -maxdepth -mindepth -empty -delete -regex -path -not -or -and"),
        ("locate", "Find files by name quickly", "-i -c -l -S --count --limit --existing --regex"),
        ("file", "Determine file type", "-b -i -L -z --mime-type --mime-encoding --brief"),
        ("stat", "Display file status", "-c --format -f -L -t --printf"),
        ("readlink", "Print resolved symbolic links", "-f -e -m -n --canonicalize"),
        ("realpath", "Print resolved absolute pathname", "-e -m -s --relative-to --relative-base"),
        ("basename", "Strip directory and suffix from filenames", "-a -s --suffix --multiple"),
        ("dirname", "Strip last component from filename", "-z --zero"),
        ("tree", "List directory contents in tree format", "-L -d -a -f -i -p -s -h --dirsfirst -I -P --prune -o --charset"),
        ("pwd", "Print working directory", "-L -P --logical --physical"),
        ("cd", "Change directory", "~ - .. / absolute relative CDPATH"),
        ("split", "Split file into pieces", "-b -l -n -d -a --bytes --lines --number --suffix-length"),
        ("csplit", "Split file into context-determined pieces", "-f -n -z -b --prefix --digits --elide-empty-files"),
        ("join", "Join lines of two files on common field", "-1 -2 -t -i -a -e -o --check-order"),
        ("paste", "Merge lines of files", "-d -s -z --delimiters --serial"),
        ("tee", "Read stdin write to stdout and files", "-a -i --append --ignore-interrupts"),
        ("dd", "Convert and copy file", "if= of= bs= count= skip= seek= conv= status= iflag= oflag="),
        ("shred", "Overwrite file to hide contents", "-n -z -u -v -f --remove --zero --iterations"),
        ("truncate", "Shrink or extend file size", "-s -c -r --size --no-create --reference"),
        ("mktemp", "Create temporary file or directory", "-d -t -p -u --directory --tmpdir --suffix"),
        ("install", "Copy files and set attributes", "-d -m -o -g -v -D -t --mode --owner --group"),
        ("rsync", "Fast versatile file copying tool", "-a -v -z -r -P --progress --delete --exclude --include -e --dry-run -n --bwlimit --checksum -c -u --partial --compress --archive --human-readable"),
        ("diff", "Compare files line by line", "-u -y -r -q -s -N -i -w -B --unified --side-by-side --recursive --brief --color"),
        ("patch", "Apply diff file to original", "-p -R -d -i -o --dry-run --verbose --reverse --strip"),
        ("wc", "Print newline word and byte counts", "-l -w -c -m -L --lines --words --chars --bytes --max-line-length"),
        ("sort", "Sort lines of text files", "-n -r -k -t -u -f -h -R -o -s --numeric --reverse --key --field-separator --unique --human-numeric --random --stable --output"),
        ("uniq", "Report or omit repeated lines", "-c -d -u -i -f -s -w --count --repeated --unique --ignore-case"),
        ("cut", "Remove sections from lines", "-d -f -c -b --delimiter --fields --characters --bytes --complement --output-delimiter"),
        ("tr", "Translate or delete characters", "-d -s -c --delete --squeeze-repeats --complement [:upper:] [:lower:] [:digit:] [:alpha:] [:space:]"),
        ("rev", "Reverse lines characterwise", ""),
        ("tac", "Concatenate and print files in reverse", "-s -r -b --separator --regex --before"),
        ("nl", "Number lines of files", "-b -i -n -s -w --body-numbering --line-increment --number-format --number-separator --number-width"),
        ("expand", "Convert tabs to spaces", "-t -i --tabs --initial"),
        ("unexpand", "Convert spaces to tabs", "-a -t --all --tabs --first-only"),
        ("fold", "Wrap each input line to fit width", "-w -s --width --spaces"),
        ("fmt", "Simple optimal text formatter", "-w -s -u --width --split-only --uniform-spacing"),
        ("pr", "Convert text files for printing", "-d -h -l -n -o -w --double-space --header --length --number-lines --indent --width --columns"),
        ("colrm", "Remove columns from a file", "start_col end_col"),
        ("column", "Columnate lists", "-t -s -n -c -o --table --separator --output-separator"),
        ("od", "Dump files in octal and other formats", "-A -t -j -N -w --address-radix --format --skip-bytes --read-bytes --width"),
        ("xxd", "Make hex dump or reverse", "-r -p -i -l -c -s -u --reverse --plain --include --len --cols --seek"),
        ("hexdump", "ASCII octal decimal hex dump", "-C -b -c -d -o -x -n -s -v --canonical"),
        ("strings", "Print printable strings from binary files", "-a -n -t -e --all --bytes --radix --encoding"),
        ("lsattr", "List file attributes on ext filesystem", "-R -a -d -v --recursive --all --directory"),
        ("chattr", "Change file attributes on ext filesystem", "+i -i +a -a +d -d +e -e +s -s -R -V --recursive --verbose"),
        ("namei", "Follow pathname to terminal point", "-l -m -x --long --modes --mountpoints"),
        ("shuf", "Generate random permutations", "-n -i -e -o -r --head-count --input-range --echo --output --repeat"),
        ("fallocate", "Preallocate or deallocate file space", "-l -n -p -o --length --keep-size --punch-hole --offset"),
        ("xargs", "Build and execute command lines from stdin", "-0 -I -n -P -d -t -r --null --replace --max-args --max-procs --delimiter --verbose --no-run-if-empty"),
        ("iconv", "Convert text encoding", "-f -t -l -c -o --from-code --to-code --list"),
        ("dos2unix", "Convert line endings DOS to Unix", "-k -n -q --keepdate --newfile --quiet"),
        ("unix2dos", "Convert line endings Unix to DOS", "-k -n -q --keepdate --newfile --quiet"),
        ("ditto", "Copy directory hierarchies (macOS)", "-v -V -X -k --rsrc --extattr"),
        ("mdfind", "Spotlight search (macOS)", "-name -onlyin -live -count -0"),
        ("open", "Open files/URLs with default app (macOS)", "-a -e -t -f -R --args"),
        ("plutil", "Property list utility (macOS)", "-convert -p -lint -extract -replace -remove -type"),
    ],

    # ===== 2. TEXT PROCESSING =====
    "Text Processing": [
        ("grep", "Search text using patterns", "-i -v -r -R -n -c -l -L -w -o -E -P -F -A -B -C -f -e -m -q -x -z -Z -h -H --include --exclude --exclude-dir --color --count --files-with-matches --only-matching --perl-regexp --extended-regexp --fixed-strings --word-regexp --line-regexp --context --after-context --before-context --max-count --quiet --recursive --no-filename --with-filename"),
        ("sed", "Stream editor for text transformation", "-i -e -n -r -E --in-place --expression --quiet --regexp-extended s/pattern/replacement/flags d p a i c y q w"),
        ("awk", "Pattern scanning and processing language", "-F -v -f BEGIN END NR NF $0 $1 print printf if for while split substr length gsub sub match tolower toupper getline OFS ORS RS FS FILENAME"),
        ("perl", "Perl one-liners for text processing", "-e -n -p -i -l -a -F -0 -w --regex --in-place --loop"),
        ("egrep", "Extended grep (grep -E)", "-i -v -r -n -c -l -o -w --color --include --exclude-dir"),
        ("fgrep", "Fixed-string grep (grep -F)", "-i -v -r -n -c -l -o --color"),
        ("jq", "JSON processor", ". .field .[] select map keys values length type to_entries from_entries group_by sort_by unique_by flatten -r -c -e -S --raw-output --compact-output --slurp --arg --argjson"),
        ("nano", "Simple terminal text editor", "-B -C -i -l -m -w --backup --backupdir --autoindent --linenumbers --mouse --nowrap"),
        ("vi", "Visual text editor", "-R -c -o -O -p +line +:command --readonly"),
        ("vim", "Vi improved text editor", "-R -c -o -O -p -d -u -N +line +:command --readonly --noplugin"),
        ("emacs", "Extensible text editor", "-nw -q -Q --no-window-system --no-init-file --quick --batch -f --funcall --eval"),
        ("bc", "Arbitrary precision calculator", "-l -q -s --mathlib --quiet --standard scale ibase obase"),
        ("comm", "Compare two sorted files line by line", "-1 -2 -3 -i --check-order --nocheck-order --total"),
        ("xmllint", "XML linter and formatter", "--format --noout --valid --schema --relaxng --xpath --html --c14n --encode"),
    ],

    # ===== 3. ARCHIVE & COMPRESSION =====
    "Archive and Compression": [
        ("tar", "Tape archive utility", "-c -x -t -v -f -z -j -J --zstd -C -r -u --delete --strip-components --exclude --wildcards -p --preserve-permissions --same-owner --no-same-owner --transform --create --extract --list --verbose --file --gzip --bzip2 --xz --directory --append --update"),
        ("zip", "Package and compress files", "-r -e -x -9 -0 -j -q -v -u -d --recurse-paths --encrypt --exclude --compression-method"),
        ("unzip", "Extract compressed files from ZIP archive", "-l -t -o -d -q -v -n --list --test --overwrite --directory --quiet"),
        ("gzip", "Compress files", "-d -k -r -v -1 -9 -f -c -l -n -N --decompress --keep --recursive --verbose --fast --best --force --stdout --list"),
        ("gunzip", "Decompress gzip files", "-k -v -f -r -c --keep --verbose --force --recursive --stdout"),
        ("bzip2", "Block-sorting file compressor", "-d -k -z -v -1 -9 -f -c --decompress --keep --compress --verbose --fast --best --force --stdout"),
        ("bunzip2", "Decompress bzip2 files", "-k -v -f -c --keep --verbose --force --stdout"),
        ("xz", "Compress files with LZMA", "-d -k -z -v -0 -9 -e -f -c -l -T --decompress --keep --compress --verbose --extreme --force --stdout --list --threads"),
        ("unxz", "Decompress xz files", "-k -v -f -c --keep --verbose --force --stdout"),
        ("zstd", "Zstandard compression", "-d -k -r -v -1 -19 --ultra -f -c -o -T --decompress --keep --recursive --verbose --force --stdout --threads"),
        ("unzstd", "Decompress zstd files", "-k -v -f -c -o --keep --verbose --force --stdout"),
        ("zcat", "View contents of compressed files", "-f --force"),
        ("bzcat", "View contents of bzip2 compressed files", ""),
        ("xzcat", "View contents of xz compressed files", ""),
        ("zgrep", "Search compressed files", "-i -v -c -l -n -E -h --count --files-with-matches --line-number"),
        ("zless", "View compressed files with pager", ""),
        ("compress", "Compress files (legacy)", "-f -v -c -d --force --verbose --stdout --decompress"),
        ("cpio", "Copy files to/from archives", "-i -o -p -d -v -t -F --extract --create --pass-through --make-directories --verbose --list --file"),
        ("7z", "7-Zip file archiver", "a x l t e -p -o -r -y -mx= -mmt= -v add extract list test"),
        ("pigz", "Parallel gzip compression", "-d -k -r -p -1 -9 -f -c -v --decompress --keep --recursive --processes --fast --best --force --stdout"),
    ],

    # ===== 4. SYSTEM INFORMATION =====
    "System Information": [
        ("uname", "Print system information", "-a -s -n -r -v -m -p -i -o --all --kernel-name --nodename --kernel-release --kernel-version --machine --processor --hardware-platform --operating-system"),
        ("uptime", "Show system uptime and load averages", "-p -s --pretty --since"),
        ("date", "Display or set date and time", "-u -d -s -r --utc --date --set --reference +FORMAT %Y %m %d %H %M %S %F %T %s %A %B %Z"),
        ("hostname", "Show or set system hostname", "-f -d -i -I -s --fqdn --domain --ip-address --all-ip-addresses --short"),
        ("hostnamectl", "Control system hostname", "status set-hostname set-icon-name set-chassis set-deployment --static --transient --pretty"),
        ("id", "Print user identity", "-u -g -G -n -r --user --group --groups --name --real"),
        ("whoami", "Print effective user name", ""),
        ("who", "Show who is logged on", "-a -b -d -H -l -p -q -r -s -t -T -u --all --boot --dead --heading --login --process --count --runlevel --short"),
        ("w", "Show who is logged on and what they are doing", "-h -s -f -i --no-header --short --from --ip-addr"),
        ("finger", "User information lookup", "-l -s -m -p"),
        ("free", "Display memory usage", "-h -b -k -m -g -t -s -c --human --bytes --kibi --mebi --gibi --total --seconds --count --wide"),
        ("df", "Report filesystem disk space usage", "-h -i -T -a -l --human-readable --inodes --print-type --all --local --output --total --type --exclude-type"),
        ("du", "Estimate file space usage", "-s -h -a -c -d --max-depth --summarize --human-readable --all --total --apparent-size --block-size --exclude --time -x"),
        ("lscpu", "Display CPU architecture information", "-e -p -J -a -b --extended --parse --json --all --online --offline"),
        ("lshw", "List hardware configuration", "-short -class -businfo -sanitize -json -xml -html -numeric -quiet"),
        ("lspci", "List PCI devices", "-v -vv -vvv -k -n -nn -t -s -d -mm -D --verbose --kernel --numeric --tree --slot --device"),
        ("lsusb", "List USB devices", "-v -s -d -t -D --verbose --tree"),
        ("lsmem", "List available memory ranges", "-a -b -J -n -o -P -r -S --all --bytes --json --noheadings --output --pairs --raw --split"),
        ("lsns", "List namespaces", "-J -l -n -o -p -r -t -u --json --list --noheadings --output --task --raw --type"),
        ("dmidecode", "DMI/SMBIOS hardware info", "-t -s --type --string memory processor system baseboard bios cache connector slot"),
        ("sensors", "Print hardware sensors data", "-f -A -u -j --fahrenheit --no-adapter --raw --json"),
        ("inxi", "Full featured system info script", "-F -b -c -G -A -N -i -o -p -r -S -t --full --basic --cpu --graphics --audio --network --ip --repos --partitions --sensors"),
        ("vmstat", "Virtual memory statistics", "-a -d -D -f -m -n -p -s -S -t -w --active --disk --disk-sum --forks --slabs --stats --timestamp --wide"),
        ("dmesg", "Print kernel ring buffer", "-T -H -L -l -f -k -u -w -c --human --color --level --facility --kernel --userspace --follow --clear --ctime --time-format"),
        ("hwclock", "Query and set hardware clock", "--show --set --systohc --hctosys --utc --localtime --verbose"),
        ("timedatectl", "Control system time and date settings", "status set-time set-timezone set-ntp list-timezones show-timesync --no-pager --adjust-system-clock"),
        ("cal", "Display calendar", "-y -3 -m -j -s -n --year --three --monday --julian --sunday --months"),
        ("arch", "Print machine architecture", ""),
        ("nproc", "Print number of processing units", "--all --ignore"),
        ("tty", "Print terminal name", "-s --silent --quiet"),
        ("runlevel", "Print previous and current runlevel", ""),
        ("sw_vers", "Print macOS version info (macOS)", "-productName -productVersion -buildVersion"),
        ("system_profiler", "System information (macOS)", "SPHardwareDataType SPSoftwareDataType SPNetworkDataType SPStorageDataType SPMemoryDataType SPDisplaysDataType SPUSBDataType -json -xml -detailLevel"),
    ],

    # ===== 5. PROCESS MANAGEMENT =====
    "Process Management": [
        ("ps", "Report process status", "aux -e -f -p -u -C -o --pid --ppid --user --format --sort --forest --headers -ww -l -H --no-headers"),
        ("top", "Display real-time process info", "-b -n -d -p -u -o -H -c --batch --iterations --delay --pid --user --sort --threads --command-line"),
        ("htop", "Interactive process viewer", "-d -u -p -s -t --delay --user --pid --sort-key --tree"),
        ("kill", "Send signal to process", "-9 -15 -TERM -KILL -HUP -USR1 -USR2 -CONT -STOP -INT -l --signal"),
        ("killall", "Kill processes by name", "-9 -i -v -w -s -u --signal --interactive --verbose --wait --user"),
        ("pkill", "Send signal to processes by pattern", "-f -u -t -P -g -x -n -o --full --uid --terminal --parent --pgroup --exact --newest --oldest"),
        ("pgrep", "List processes by pattern", "-l -f -u -t -P -a -c -d -n -o --list-name --full --uid --terminal --parent --list-full --count --delimiter --newest --oldest"),
        ("pidof", "Find process ID by name", "-s -x --single-shot"),
        ("pstree", "Display process tree", "-a -c -h -l -n -p -s -u -H --arguments --compact --highlight --long --numeric-sort --show-pids --show-parents --uid-changes"),
        ("nice", "Run command with modified scheduling priority", "-n --adjustment"),
        ("renice", "Alter priority of running processes", "-n -p -g -u --priority --pid --pgrp --user"),
        ("nohup", "Run command immune to hangups", ""),
        ("disown", "Remove job from shell job table", "-h -a -r %1 %2"),
        ("bg", "Resume job in background", "%1 %2 %+"),
        ("fg", "Bring job to foreground", "%1 %2 %+"),
        ("jobs", "List active jobs", "-l -n -p -r -s --long"),
        ("wait", "Wait for process to complete", "-n -f --pid"),
        ("lsof", "List open files", "-i -p -u -c -t -n -P +D -d --internet --pid --user --command --terse"),
        ("fuser", "Identify processes using files or sockets", "-v -k -m -n -i --verbose --kill --mount --namespace --interactive"),
        ("strace", "Trace system calls", "-e -p -f -c -t -T -o -s --trace --attach --follow-forks --summary --timestamps --syscall-times --output"),
        ("ltrace", "Trace library calls", "-e -p -f -c -t -T -o -s --attach --follow --summary --timestamps"),
        ("time", "Time command execution", "-v -p --verbose --portability"),
        ("timeout", "Run command with time limit", "-k -s --kill-after --signal --foreground --preserve-status"),
        ("watch", "Execute program periodically", "-n -d -g -t -p -e -c --interval --differences --chgexit --no-title --precise --errexit --color"),
        ("flock", "Manage file locks from shell scripts", "-s -x -u -n -w -o --shared --exclusive --unlock --nonblock --wait --close"),
        ("parallel", "Execute jobs in parallel", "-j -k --jobs --keep-order --dry-run --progress --bar --eta --colsep --header"),
        ("ionice", "Set or get I/O scheduling class and priority", "-c -n -p -t --class --classdata --pid --ignore"),
        ("taskset", "Set or get CPU affinity", "-p -c --pid --cpu-list"),
        ("cpupower", "CPU power management", "frequency-info frequency-set idle-info idle-set monitor --governor --min --max"),
        ("numactl", "Control NUMA policy", "--hardware --show --membind --cpunodebind --interleave --physcpubind --preferred"),
        ("pmap", "Report memory map of a process", "-x -d -q -A --extended --device --quiet --range"),
        ("pidstat", "Report statistics for Linux tasks", "-u -r -d -t -p -C --cpu --memory --disk --task --pid --command"),
        ("mpstat", "Report CPU statistics", "-P -u -A -I -o --processor --cpu --all --interrupts --json"),
        ("iostat", "Report CPU and I/O statistics", "-c -d -k -m -x -t -z -p -N --cpu --disk --kilobytes --megabytes --extended --timestamp --omit"),
        ("sar", "Collect and report system activity", "-u -r -b -d -n -q -A -o -f --cpu --memory --io --disk --network --queue --all --output --file"),
        ("iotop", "Display I/O usage by processes", "-o -b -n -d -p -u -a --only --batch --iter --delay --pid --user --accumulated"),
        ("atop", "Advanced system and process monitor", "-a -d -m -s -c -g -l -w -r --all --disk --memory --scheduling --various --generic --logging --write --read"),
        ("perf", "Performance analysis tools", "stat record report top list annotate script probe sched --event --call-graph --frequency --output"),
        ("pv", "Monitor data through a pipe", "-p -t -e -r -b -n -q -L --progress --timer --eta --rate --bytes --numeric --quiet --rate-limit"),
        ("prlimit", "Get and set process resource limits", "--pid --nofile --nproc --memlock --as --stack --core --fsize"),
        ("ulimit", "Get and set user limits", "-a -c -d -f -l -m -n -s -t -u -v -H -S --all --core --data --fsize --locks --memlock --nofile --nproc --stack --cpu"),
    ],

    # ===== 6. NETWORKING =====
    "Networking": [
        ("ping", "Send ICMP echo to network hosts", "-c -i -s -t -W -w -4 -6 -q -f -n -I --count --interval --packetsize --ttl --timeout --deadline --quiet --flood --numeric --interface"),
        ("ping6", "Send ICMPv6 echo requests", "-c -i -s -W -q -n -I --count --interval"),
        ("curl", "Transfer data from or to server", "-o -O -L -s -S -v -k -X -H -d -F -u -T -b -c -e -A -x --output --remote-name --location --silent --show-error --verbose --insecure --request --header --data --form --user --upload-file --cookie --cookie-jar --referer --user-agent --proxy --retry --max-time --connect-timeout -w --write-out -I --head --compressed --cert --key"),
        ("wget", "Non-interactive network downloader", "-O -o -q -c -r -l -p -k -np -N -P -b -i -t -T --output-document --output-file --quiet --continue --recursive --level --page-requisites --convert-links --no-parent --timestamping --directory-prefix --background --input-file --tries --timeout --user-agent --header --limit-rate --no-check-certificate --mirror --spider"),
        ("ssh", "OpenSSH remote login client", "-p -i -l -v -N -f -L -R -D -X -C -o -t -J --port --identity --login_name --verbose --no-execute --background --local-forward --remote-forward --dynamic --x11 --compress --option --force-tty --jump"),
        ("scp", "Secure copy between hosts", "-r -P -i -v -C -p -q -l --recursive --port --identity --verbose --compress --preserve --quiet --limit"),
        ("sftp", "Secure file transfer program", "-P -i -b -r -v --port --identity --batchfile --recursive --verbose get put ls cd mkdir rm rmdir"),
        ("ssh-keygen", "Generate SSH key pairs", "-t -b -f -C -N -p -l -R -y --type --bits --filename --comment --new-passphrase --change-passphrase --fingerprint --remove --pubkey rsa ed25519 ecdsa"),
        ("ssh-copy-id", "Install SSH key on remote server", "-i -p -f --identity --port --force"),
        ("ssh-keyscan", "Gather SSH public keys", "-t -p -T -H --type --port --timeout --hash"),
        ("ssh-add", "Add SSH keys to agent", "-l -L -d -D -t -K --list --delete --delete-all --lifetime"),
        ("ip", "Show/manipulate routing network devices interfaces", "addr link route neigh netns rule tunnel tuntap maddr monitor a l r n show add del set flush up down"),
        ("ifconfig", "Configure network interfaces", "up down inet netmask broadcast mtu promisc -a"),
        ("ss", "Socket statistics", "-t -u -l -n -p -a -4 -6 -s -e -o -i --tcp --udp --listening --numeric --processes --all --ipv4 --ipv6 --summary --extended --options --info state sport dport"),
        ("netstat", "Network statistics", "-t -u -l -n -p -a -r -i -s -c --tcp --udp --listening --numeric --programs --all --route --interfaces --statistics --continuous"),
        ("dig", "DNS lookup utility", "+short +trace +noall +answer +stats -t -x -p @server ANY A AAAA MX NS SOA CNAME TXT PTR SRV"),
        ("nslookup", "Query DNS interactively", "-type= -debug -timeout= -retry= server set type= A AAAA MX NS SOA CNAME TXT PTR"),
        ("host", "DNS lookup utility", "-t -a -l -v -T -4 -6 --type --all --list --verbose"),
        ("whois", "Domain registration lookup", "-h -p --host --port"),
        ("traceroute", "Print route packets trace to host", "-n -m -w -q -I -T -U -p -4 -6 --numeric --max-hops --wait --queries --icmp --tcp --udp --port"),
        ("tracepath", "Trace path to network host discovering MTU", "-n -b -l -m -p --no-dns --both --pktlen --max-hops --port"),
        ("mtr", "Network diagnostic tool combining traceroute and ping", "-r -c -n -w -b -o -s --report --report-cycles --no-dns --report-wide --show-ips --order --psize --json --xml --csv"),
        ("nmap", "Network exploration and security scanner", "-sS -sT -sU -sP -sn -sV -O -A -p -T0-5 -v -oN -oX -oG --top-ports --open --script --min-rate --max-retries --host-timeout"),
        ("nc", "Netcat networking utility", "-l -p -u -v -z -w -k -n --listen --port --udp --verbose --zero --wait --keep-open --numeric"),
        ("ncat", "Nmap's netcat replacement", "-l -p -u -v -k -e -c --listen --port --udp --verbose --keep-open --exec --sh-exec --ssl"),
        ("arp", "Address resolution protocol manipulation", "-a -d -s -n -v --all --delete --set --numeric --verbose"),
        ("route", "Show/manipulate routing table", "-n -v add del default gw metric dev"),
        ("iperf3", "Network bandwidth measurement", "-s -c -t -p -P -R -u -b -n -J --server --client --time --port --parallel --reverse --udp --bandwidth --bytes --json"),
        ("tcpdump", "Dump traffic on network", "-i -n -c -w -r -v -vv -vvv -A -X -s -e --interface --numeric --count --write --read --verbose --ascii --hex --snaplen --show-link port host src dst and or not tcp udp icmp"),
        ("ethtool", "Query or control network driver settings", "-i -a -A -c -C -g -G -k -K -s -S --driver --show-pause --pause --show-coalesce --coalesce --show-ring --ring --show-offload --offload --change --statistics"),
        ("iw", "Show/manipulate wireless devices", "dev phy list info link scan connect disconnect reg set"),
        ("iwconfig", "Configure wireless network interfaces", "essid mode channel freq key rate power txpower retry"),
        ("nmcli", "NetworkManager CLI", "general networking radio connection device agent monitor status show add modify delete up down reload"),
        ("brctl", "Ethernet bridge administration", "addbr delbr addif delif show setageing setbridgeprio setfd sethello setmaxage setpathcost setportprio stp"),
        ("networksetup", "Network configuration (macOS)", "-listallhardwareports -getairportnetwork -setairportnetwork -getinfo -setmanual -setdhcp -setdnsservers -getdnsservers -setwebproxy -setsocksfirewallproxy -setairportpower -ordernetworkservices"),
    ],

    # ===== 7. PACKAGE MANAGEMENT =====
    "Package Management": [
        ("apt", "APT package manager (Debian/Ubuntu)", "install remove purge update upgrade full-upgrade autoremove search show list edit-sources --fix-broken -y -d --download-only --no-install-recommends --reinstall"),
        ("apt-get", "APT package handling utility", "install remove purge update upgrade dist-upgrade autoremove autoclean clean download source build-dep -y -f -d --reinstall --no-install-recommends"),
        ("apt-cache", "APT package cache query", "search show showpkg depends rdepends policy pkgnames stats unmet --names-only --full"),
        ("apt-mark", "Mark/unmark packages as manually installed", "auto manual hold unhold showmanual showauto showhold"),
        ("dpkg", "Debian package manager", "-i -r -P -l -L -s -S -c --install --remove --purge --list --listfiles --status --search --contents --configure --audit"),
        ("dnf", "Fedora/RHEL package manager", "install remove update upgrade search info list provides repolist clean history group autoremove makecache --enablerepo --disablerepo -y --best --allowerasing --skip-broken --downloadonly"),
        ("yum", "RPM package manager (legacy)", "install remove update search info list provides repolist clean history groupinstall groupremove -y --enablerepo --disablerepo --skip-broken --downloadonly"),
        ("rpm", "RPM package manager", "-i -U -e -q -V -K -qa -qi -ql -qf -qR --install --upgrade --erase --query --verify --checksig --all --info --list --file --requires --whatprovides --import"),
        ("pacman", "Arch Linux package manager", "-S -R -Q -U -Ss -Si -Qi -Ql -Qo -Sc -Scc -Syu -Rs -Rns --sync --remove --query --upgrade --search --info --list --owns --clean --sysupgrade --refresh --noconfirm --needed"),
        ("yay", "AUR helper for Arch Linux", "-S -R -Q -Ss -Si -Sua --sync --remove --query --search --info --sysupgrade"),
        ("makepkg", "Make Arch Linux packages", "-s -i -c -f -d --syncdeps --install --clean --force --nodeps --noextract --nocheck"),
        ("zypper", "SUSE package manager", "install remove update search info list-updates patch dup repos addrepo removerepo refresh clean --non-interactive --no-confirm -y"),
        ("snap", "Snap package manager", "install remove refresh list find info run connect disconnect alias services start stop restart logs set get"),
        ("flatpak", "Flatpak application manager", "install uninstall update list search info run remote-add remote-delete remote-list --system --user"),
        ("brew", "Homebrew package manager (macOS/Linux)", "install uninstall upgrade update list search info outdated cleanup doctor deps autoremove services tap untap --cask --formula --verbose --force"),
        ("pip", "Python package installer", "install uninstall list show freeze search download check -r --requirement -U --upgrade --user --target --index-url --no-deps --force-reinstall --no-cache-dir -e --editable"),
        ("pip3", "Python 3 package installer", "install uninstall list show freeze download -r --requirement -U --upgrade --user --no-deps --force-reinstall"),
        ("npm", "Node.js package manager", "install uninstall update list search init run test build start audit fix pack publish --save --save-dev --global -g --production --legacy-peer-deps ci"),
        ("npx", "Execute npm package binaries", "-p -c --package --call --yes --no"),
        ("gem", "Ruby package manager", "install uninstall update list search info environment cleanup build -v --version --no-document --user-install --pre"),
        ("cargo", "Rust package manager and build tool", "build run test bench check clean doc new init add remove update publish install clippy fmt --release --features --all-features --target --jobs -p --package"),
    ],

    # ===== 8. USER & PERMISSION MANAGEMENT =====
    "User and Permission Management": [
        ("chmod", "Change file mode bits", "777 755 700 644 600 400 +x -x +r -r +w -w u+x g+w o-r a+rx u=rwx -R --recursive --verbose --changes --reference"),
        ("chown", "Change file owner and group", "user:group user: :group -R -v -c -f -h --recursive --verbose --changes --silent --no-dereference --reference --from"),
        ("chgrp", "Change group ownership", "-R -v -c -f -h --recursive --verbose --changes --silent --no-dereference --reference"),
        ("umask", "Set file mode creation mask", "022 077 027 002 000 -S --symbolic"),
        ("useradd", "Create new user", "-m -d -s -g -G -u -c -e -r -M -k --create-home --home-dir --shell --gid --groups --uid --comment --expiredate --system --no-create-home --skel"),
        ("userdel", "Delete user account", "-r -f --remove --force"),
        ("usermod", "Modify user account", "-l -d -m -s -g -G -a -L -U -e -c --login --home --move-home --shell --gid --groups --append --lock --unlock --expiredate --comment"),
        ("groupadd", "Create new group", "-g -r -f --gid --system --force"),
        ("groupdel", "Delete a group", "-f --force"),
        ("groupmod", "Modify group", "-n -g --new-name --gid"),
        ("groups", "Print group memberships", ""),
        ("passwd", "Change user password", "-l -u -d -e -n -x -w -i -S --lock --unlock --delete --expire --mindays --maxdays --warndays --inactive --status"),
        ("chpasswd", "Update passwords in batch mode", "-e -c --encrypted --crypt-method"),
        ("chage", "Change user password expiry info", "-l -d -E -I -m -M -W --list --lastday --expiredate --inactive --mindays --maxdays --warndays"),
        ("chsh", "Change login shell", "-s --shell --list-shells"),
        ("su", "Switch user", "- -l -c -s --login --command --shell"),
        ("sudo", "Execute command as another user", "-u -i -s -l -k -v -H -E -n --user --login --shell --list --reset-timestamp --validate --set-home --preserve-env --non-interactive"),
        ("visudo", "Safely edit sudoers file", "-c -f -s --check --file --strict"),
        ("whoami", "Print effective username", ""),
        ("getent", "Get entries from NSS databases", "passwd group hosts services protocols networks shadow"),
        ("newgrp", "Log in to a new group", ""),
        ("gpasswd", "Administer group passwords", "-a -d -r -R -A -M --add --delete --remove-password --restrict --administrators --members"),
        ("last", "Show listing of last logged in users", "-n -f -a -d -F -i -R -w -x --num --file --hostlast --dns --fullnames --ip --nohostname"),
        ("lastb", "Show bad login attempts", "-n -f -a --num --file --hostlast"),
        ("lastlog", "Report most recent login of users", "-b -t -u --before --time --user"),
        ("loginctl", "Control systemd login manager", "list-sessions show-session list-users show-user terminate-session terminate-user enable-linger disable-linger"),
        ("setfacl", "Set file access control lists", "-m -x -b -k -R -d -n --modify --remove --remove-all --remove-default --recursive --default --no-mask --set"),
        ("getfacl", "Get file access control lists", "-a -d -R -c -e -p --access --default --recursive --omit-header --all-effective --absolute-names"),
        ("wall", "Write a message to all users", "-n -t --nobanner --timeout"),
        ("mesg", "Control write access to terminal", "y n"),
    ],

    # ===== 9. SERVICE MANAGEMENT =====
    "Service Management": [
        ("systemctl", "Control systemd system and service manager", "start stop restart reload enable disable status is-active is-enabled list-units list-unit-files daemon-reload mask unmask show set-property edit cat reset-failed isolate --type --state --all --now --no-pager -l --failed --user"),
        ("service", "Run System V init script", "start stop restart reload status --status-all"),
        ("init", "System V init process", "0 1 2 3 4 5 6"),
        ("telinit", "Change System V runlevel", "0 1 2 3 4 5 6 q Q"),
        ("systemd-analyze", "Analyze system boot-up performance", "time blame critical-chain plot dot log-level log-target calendar timestamp security verify"),
        ("systemd-run", "Run programs in transient scoped units", "--scope --unit --slice --property --on-active --on-boot --on-calendar --timer-property -t --pty -P --pipe"),
        ("launchctl", "Control macOS launchd", "load unload start stop list print enable disable bootstrap bootout kickstart blame"),
        ("apachectl", "Apache HTTP server control", "start stop restart graceful graceful-stop configtest status fullstatus"),
    ],

    # ===== 10. DISK & FILESYSTEM =====
    "Disk and Filesystem": [
        ("mount", "Mount a filesystem", "-t -o -a -r -w -v -n --type --options --all --read-only --read-write --verbose --no-mtab remount bind loop noexec nosuid nodev"),
        ("umount", "Unmount filesystem", "-f -l -a -r -v --force --lazy --all --read-only --verbose"),
        ("fdisk", "Manipulate disk partition table", "-l -u -b -c -n -d -p -t -w --list --units --sector-size --cylinders"),
        ("parted", "Partition manipulation program", "print mklabel mkpart rm resizepart name set align-check unit --script --list --align"),
        ("lsblk", "List block devices", "-a -f -l -o -p -r -t -J -n --all --fs --list --output --paths --raw --topology --json --noheadings"),
        ("blkid", "Locate/print block device attributes", "-o -s -t -p -L -U --output --match-tag --match-token --probe --label --uuid"),
        ("findmnt", "Find a filesystem", "-t -o -n -l -r -J -T --type --output --noheadings --list --raw --json --target --source"),
        ("mkfs.ext4", "Create ext4 filesystem", "-L -b -i -j -m -O -T --label --block-size --bytes-per-inode --journal --reserved-blocks-percentage"),
        ("mkfs.ext3", "Create ext3 filesystem", "-L -b -i -j -m --label --block-size --bytes-per-inode --journal"),
        ("mkfs.ext2", "Create ext2 filesystem", "-L -b -i -m --label --block-size --bytes-per-inode"),
        ("mkfs.xfs", "Create XFS filesystem", "-L -b -d -f -l -r --label --block-size --force"),
        ("mkfs.btrfs", "Create Btrfs filesystem", "-L -d -m -f --label --data --metadata --force"),
        ("mkfs.vfat", "Create FAT filesystem", "-F -n -s --fat --name --sectors-per-cluster"),
        ("mkfs.ntfs", "Create NTFS filesystem", "-L -f -Q --label --force --quick"),
        ("mkfs.exfat", "Create exFAT filesystem", "-n -i --volume-label --volume-serial"),
        ("e2fsck", "Check ext2/3/4 filesystem", "-f -y -n -p -v -c --force --yes --no --preen --verbose --check-blocks"),
        ("fsck", "Check and repair filesystem", "-t -A -a -y -n -r -v --type --all --automatic --yes --no --repair --verbose"),
        ("xfs_repair", "Repair XFS filesystem", "-n -v -L --no-modify --verbose --zero-log"),
        ("xfs_info", "Display XFS filesystem geometry", ""),
        ("xfs_growfs", "Expand XFS filesystem", "-d -D -L -l --data --data-size --log --log-size"),
        ("resize2fs", "Resize ext2/3/4 filesystem", "-f -p -M --force --progress --minimum"),
        ("tune2fs", "Adjust ext2/3/4 filesystem parameters", "-l -c -i -m -L -O -e -U --list --max-mount-counts --interval --reserved-blocks-percentage --label --feature --error-behavior --uuid"),
        ("e2label", "Change ext2/3/4 filesystem label", ""),
        ("mkswap", "Set up a Linux swap area", "-L -U -f --label --uuid --force"),
        ("swapon", "Enable swap space", "-a -s -p --all --summary --priority --show"),
        ("swapoff", "Disable swap space", "-a -v --all --verbose"),
        ("fstrim", "Discard unused filesystem blocks", "-a -v --all --verbose --minimum --offset --length"),
        ("smartctl", "Control SMART-enabled drives", "-a -i -H -t -l -A --all --info --health --test --log --attributes short long conveyance offline"),
        ("hdparm", "Get/set SATA/IDE parameters", "-i -I -t -T -g -v -C -S -B -M --identify --Istdout --read-timing --cache-read --geometry --verbose --check-power --standby --apm --acoustic"),
        ("badblocks", "Search for bad blocks on device", "-b -c -f -n -s -v -w --blocksize --test-count --force --non-destructive --show-progress --verbose --write-mode"),
        ("blockdev", "Call block device ioctls", "--getsize64 --getss --getbsz --setbsz --getro --setro --setrw --rereadpt --flushbufs"),
        ("losetup", "Set up and control loop devices", "-a -d -f -j -l -o -P -r --all --detach --find --associated --list --offset --partscan --read-only --sizelimit --show"),
        ("quota", "Display disk usage and limits", "-u -g -v -s --user --group --verbose --human-readable"),
        ("pvcreate", "Initialize physical volume for LVM", "-f -y -v --force --yes --verbose"),
        ("vgcreate", "Create volume group", "-s --physicalextentsize"),
        ("lvcreate", "Create logical volume", "-L -l -n -s -T --size --extents --name --snapshot --thin"),
        ("lvextend", "Extend logical volume", "-L -l -r --size --extents --resizefs"),
        ("lvs", "Display LV information", "-a -o --all --options"),
        ("vgs", "Display VG information", "-a -o --all --options"),
        ("mdadm", "Manage MD/software RAID", "--create --assemble --manage --detail --examine --monitor --grow --stop --add --remove --fail -l --level -n --raid-devices -x --spare-devices"),
        ("btrfs", "Btrfs filesystem management", "subvolume filesystem balance device scrub quota check rescue inspect-internal property send receive snapshot create delete list show start stop"),
        ("diskutil", "Disk utility (macOS)", "list info mount unmount eject partitionDisk eraseDisk eraseVolume verifyDisk repairDisk apfs addVolume deleteVolume"),
        ("hdiutil", "Disk image utility (macOS)", "create mount unmount attach detach info compact convert verify burn"),
        ("sips", "Scriptable image processing (macOS)", "-s -g -z -Z --setProperty --getProperty --resampleWidth --resampleHeight --resampleHeightWidthMax --out"),
    ],

    # ===== 11. VERSION CONTROL =====
    "Version Control": [
        ("git", "Distributed version control system", "init clone add commit push pull fetch merge rebase branch checkout switch restore status log diff show stash tag remote reset revert cherry-pick bisect blame reflog clean gc config am format-patch apply archive bundle submodule worktree -m -a -b -d -f -v -p --amend --no-edit --squash --abort --continue --stat --oneline --graph --all --force --set-upstream -u --hard --soft --mixed --cached"),
    ],

    # ===== 12. CONTAINER & VIRTUALIZATION =====
    "Container and Virtualization": [
        ("docker", "Container platform", "run exec build pull push images ps logs stop start restart rm rmi inspect network volume compose create cp tag save load export import system prune login logout -d -it -p -v -e --name --rm --network --volume --env --restart -f --force --all --quiet"),
        ("docker-compose", "Multi-container Docker applications", "up down build start stop restart logs ps exec pull push config rm --build -d --force-recreate --no-deps --scale --remove-orphans -f --file"),
        ("podman", "Daemonless container engine", "run exec build pull push images ps logs stop start restart rm rmi inspect network volume pod create cp tag save load -d -it -p -v -e --name --rm"),
        ("buildah", "Build OCI container images", "from run copy add commit config push pull inspect rm bud --format --layers --squash"),
        ("skopeo", "Container image registry tool", "copy inspect delete list-tags sync login logout --src-tls-verify --dest-tls-verify --override-os --override-arch"),
        ("kubectl", "Kubernetes CLI", "get describe create apply delete patch edit logs exec port-forward top scale rollout expose run label annotate config auth api-resources explain -n --namespace -o --output -f --filename -l --selector --all-namespaces -A --context --kubeconfig -w --watch --dry-run -it"),
        ("helm", "Kubernetes package manager", "install uninstall upgrade rollback list repo search show create package template lint status history dependency env -n --namespace --values -f --set --version --create-namespace --wait --timeout --dry-run"),
        ("chroot", "Run command with different root directory", "--userspec --groups --skip-chdir"),
        ("nsenter", "Enter namespaces of another process", "-t -m -u -i -n -p -U --target --mount --uts --ipc --net --pid --user"),
        ("unshare", "Run program with unshared namespaces", "-m -u -i -n -p -U -f --mount --uts --ipc --net --pid --user --fork --map-root-user"),
        ("lxc", "Linux containers", "launch start stop delete list info exec file image network storage profile config publish remote"),
        ("virsh", "Virtualization management CLI", "list start shutdown reboot destroy create define undefine suspend resume migrate snapshot-create snapshot-revert dominfo domstate dumpxml pool-list vol-list net-list --all"),
    ],

    # ===== 13. SECURITY & AUDIT =====
    "Security and Audit": [
        ("iptables", "IPv4 packet filter administration", "-A -D -I -L -F -P -N -X -Z -t -p -s -d --dport --sport -j -i -o -m --append --delete --insert --list --flush --policy --new-chain --delete-chain --zero --table --protocol --source --destination --jump --in-interface --out-interface --match nat filter mangle raw ACCEPT DROP REJECT LOG SNAT DNAT MASQUERADE"),
        ("nft", "Nftables packet filtering framework", "add delete list flush create rename table chain rule set map counter quota limit monitor export import"),
        ("ufw", "Uncomplicated firewall", "enable disable status allow deny reject limit delete route reset default logging app --dry-run --force"),
        ("firewall-cmd", "Firewalld control tool", "--add-port --remove-port --add-service --remove-service --add-rich-rule --list-all --list-ports --list-services --reload --permanent --zone --get-zones --get-active-zones --get-default-zone --set-default-zone --query-port --query-service --info-zone"),
        ("pfctl", "PF packet filter control (macOS/BSD)", "-e -d -f -F -s -t -T -v --enable --disable --flush --show --table"),
        ("openssl", "OpenSSL command line tool", "genrsa genpkey req x509 s_client s_server enc dgst rand verify pkcs12 rsa ec pkey crl ca passwd prime -in -out -key -cert -CAfile -CApath -subj -days -nodes -newkey -new -sha256 -aes256 -text -noout -connect"),
        ("gpg", "GNU Privacy Guard encryption", "--gen-key --list-keys --list-secret-keys --encrypt --decrypt --sign --verify --export --import --delete-key --edit-key --keyserver --recv-keys --send-keys --armor --recipient --output --symmetric --detach-sign --clearsign --fingerprint -c -d -e -s -k -r -o -a"),
        ("md5sum", "Compute MD5 message digest", "-c -b -t --check --binary --text --quiet --status --warn"),
        ("sha1sum", "Compute SHA-1 message digest", "-c -b --check --binary --text"),
        ("sha256sum", "Compute SHA-256 message digest", "-c -b --check --binary --text"),
        ("auditctl", "Control Linux audit system", "-a -d -l -D -w -W -p -k -e -f -b --add --delete --list --deleteall --watch --remove --permission --key --enabled --failure --backlog"),
        ("ausearch", "Search audit daemon logs", "-a -c -f -ga -gi -gu -k -m -p -sc -sv -ts -te -i --event --comm --file --gid-all --group-id --user-id --key --message --pid --syscall --success --start --end --interpret"),
        ("sestatus", "SELinux status tool", "-v -b --verbose --booleans"),
        ("getenforce", "Get SELinux enforcement mode", ""),
        ("setenforce", "Set SELinux enforcement mode", "0 1 Enforcing Permissive"),
        ("getsebool", "Get SELinux boolean values", "-a --all"),
        ("setsebool", "Set SELinux booleans", "-P --permanent on off 1 0"),
        ("restorecon", "Restore SELinux security contexts", "-R -v -n -F --recursive --verbose --no-change --force"),
        ("chcon", "Change SELinux security context", "-t -u -r -R -v --type --user --role --recursive --verbose"),
        ("aa-status", "AppArmor status", "--enabled --profiled --enforced --complaining"),
        ("aa-enforce", "Set AppArmor profile to enforce mode", ""),
        ("aa-complain", "Set AppArmor profile to complain mode", ""),
        ("getcap", "Get file capabilities", "-r -v --recursive --verbose"),
        ("setcap", "Set file capabilities", "-r -v --remove --verbose cap_net_bind_service cap_sys_admin cap_net_raw cap_dac_override"),
        ("aide", "Advanced intrusion detection", "--init --check --update --compare --config"),
        ("rkhunter", "Rootkit hunter", "--check --update --propupd --list --versioncheck --skip-keypress -c"),
        ("cryptsetup", "Manage encrypted volumes", "luksFormat luksOpen luksClose luksAddKey luksRemoveKey luksDump luksHeaderBackup luksHeaderRestore status isLuks open close --type --cipher --key-size --hash --verify-passphrase --key-file"),
        ("fail2ban-client", "Fail2ban control interface", "status start stop reload restart set get banned unban --loglevel --logtarget -i"),
    ],

    # ===== 14. SCHEDULING =====
    "Scheduling": [
        ("crontab", "Maintain crontab files", "-e -l -r -u -i --edit --list --remove --user --interactive"),
        ("at", "Execute commands at scheduled time", "-f -l -d -c -m -q -v --file --list --delete --cat --mail --queue --verbose now noon midnight tomorrow teatime"),
        ("atq", "List pending at jobs", ""),
        ("atrm", "Remove at jobs", ""),
        ("batch", "Execute commands when system load permits", "-f --file"),
        ("anacron", "Run commands periodically", "-f -u -s -n -d -q --force --update --serial --now --debug --quiet"),
    ],

    # ===== 15. LOGGING =====
    "Logging": [
        ("journalctl", "Query the systemd journal", "-u -f -b -p -n --since --until -o -k -r --unit --follow --boot --priority --lines --output --kernel --reverse --no-pager --disk-usage --vacuum-size --vacuum-time --vacuum-files -e --pager-end --catalog -x"),
        ("logger", "Enter messages into system log", "-p -t -i -s --priority --tag --id --stderr"),
        ("logrotate", "Rotate log files", "-f -d -v -s --force --debug --verbose --state"),
        ("dmesg", "Print kernel ring buffer messages", "-T -H -L -l -f -k -u -w -c --human --color --level --facility --kernel --userspace --follow --clear"),
        ("coredumpctl", "Retrieve and process saved core dumps", "list info dump debug gdb --no-pager --since --until -o --output -1"),
        ("log", "macOS unified logging", "show stream --predicate --info --debug --style --source --process --start --end --last"),
    ],

    # ===== 16. SHELL BUILTINS & UTILITIES =====
    "Shell Builtins and Utilities": [
        ("echo", "Display a line of text", "-n -e -E --no-newline --escape --no-escape \\n \\t \\\\"),
        ("printf", "Format and print data", "%s %d %f %x %o %e %g %% \\n \\t --"),
        ("export", "Set environment variables", "-n -p --name --print"),
        ("env", "Run in modified environment", "-i -u -0 --ignore-environment --unset --null"),
        ("printenv", "Print environment variables", ""),
        ("alias", "Create command aliases", "-p"),
        ("unalias", "Remove aliases", "-a --all"),
        ("history", "Command history", "-c -d -a -r -w -n -p -s --clear --delete"),
        ("clear", "Clear terminal screen", "-x --keep"),
        ("reset", "Reset terminal", ""),
        ("type", "Describe command type", "-a -t -p --all --type --path"),
        ("which", "Locate a command", "-a --all"),
        ("whereis", "Locate binary source and man pages", "-b -m -s --binary --manual --source"),
        ("man", "Manual page viewer", "-k -f -a -w --apropos --whatis --all --path"),
        ("source", "Execute commands from file in current shell", ". filename"),
        ("declare", "Declare variables and attributes", "-a -A -f -i -l -r -u -x -p --array --assoc --function --integer --lower --readonly --upper --export --print"),
        ("shopt", "Set and unset shell options", "-s -u -p -q --set --unset --print --quiet"),
        ("builtin", "Execute shell builtin", ""),
        ("command", "Execute command bypassing functions", "-v -V -p --verbose --path"),
        ("hash", "Remember command locations", "-r -d -l -t --remove --delete --list"),
        ("sleep", "Delay for specified time", "s m h d"),
        ("seq", "Print sequence of numbers", "-w -f -s --equal-width --format --separator"),
        ("yes", "Output a string repeatedly", ""),
        ("expr", "Evaluate expressions", "match substr index length + - \\* / % = \\> \\< \\| \\&"),
        ("factor", "Print prime factors", ""),
        ("numfmt", "Convert numbers to/from human-readable", "--from --to --padding --round --suffix --format iec si auto"),
        ("base64", "Base64 encode/decode", "-d -w --decode --wrap"),
        ("ldd", "Print shared library dependencies", "-v -u -r --verbose --unused --function-relocs"),
        ("nm", "List symbols from object files", "-g -u -D -C -A -n --extern-only --undefined-only --dynamic --demangle --print-file-name --numeric-sort"),
        ("say", "Text to speech (macOS)", "-v -r -o --voice --rate --output-file"),
        ("lolcat", "Rainbow colored cat", "-a -d -s -f --animate --duration --speed --freq"),
        ("bash", "Bourne Again Shell", "-c -l -i -r -s -x -v -n --login --interactive --restricted --verbose --norc --noprofile"),
        ("sh", "POSIX shell", "-c -l -i -r -s -x -v -n"),
    ],

    # ===== 17. KERNEL & HARDWARE =====
    "Kernel and Hardware": [
        ("lsmod", "Show loaded kernel modules", ""),
        ("modprobe", "Add/remove kernel modules", "-r -v -n -f -a --remove --verbose --dry-run --force --all"),
        ("modinfo", "Show kernel module information", "-a -d -l -n -p --author --description --license --filename --parm"),
        ("insmod", "Insert kernel module", ""),
        ("rmmod", "Remove kernel module", "-f -v --force --verbose"),
        ("depmod", "Generate modules dependency list", "-a -b -n -v --all --basedir --dry-run --verbose"),
        ("sysctl", "Configure kernel parameters at runtime", "-a -p -w -n --all --load --write --values"),
        ("udevadm", "Udev management tool", "info trigger settle monitor control test-builtin hwdb --query --path --name --attribute-walk --action --subsystem-match"),
        ("mkinitramfs", "Generate initramfs image", "-o -v --output --verbose"),
        ("mkinitcpio", "Create initial ramdisk (Arch)", "-p -g -k -A --preset --generate --kernel --addhooks"),
        ("dracut", "Create initial ramdisk", "-f -v -k --force --verbose --kver --add --omit --install"),
        ("efibootmgr", "Manage UEFI boot entries", "-v -c -d -p -L -l -b -B -o --verbose --create --disk --part --label --loader --bootnum --delete-bootnum --bootorder"),
        ("kextstat", "Show loaded kernel extensions (macOS)", "-l -b --list --bundle-id"),
    ],

    # ===== 18. TERMINAL MULTIPLEXERS & SESSION =====
    "Terminal Multiplexers and Session": [
        ("tmux", "Terminal multiplexer", "new-session attach-session detach-client list-sessions kill-session new-window split-window select-pane select-window rename-window rename-session send-keys resize-pane list-windows kill-window swap-pane swap-window copy-mode set-option -t -s -n -d -h -v -p -x -y"),
        ("screen", "Screen manager with terminal emulation", "-S -r -d -ls -X -L -h -wipe -R -DR attach detach quit split focus select title caption"),
        ("script", "Make typescript of terminal session", "-a -c -f -q -t --append --command --flush --quiet --timing"),
    ],

    # ===== 19. DEVELOPER TOOLS =====
    "Developer Tools": [
        ("gcc", "GNU C compiler", "-o -c -S -E -g -O -O2 -O3 -Os -Wall -Wextra -Werror -pedantic -std= -I -L -l -D -U -shared -fPIC -static -march= -mtune= -pipe --version"),
        ("g++", "GNU C++ compiler", "-o -c -S -E -g -O -O2 -O3 -Os -Wall -Wextra -Werror -pedantic -std= -I -L -l -D -U -shared -fPIC -static"),
        ("make", "Build automation tool", "-f -j -k -n -B -C -d -s --file --jobs --keep-going --dry-run --always-make --directory --debug --silent clean all install"),
        ("cmake", "Cross-platform build system generator", "-B -S -G -D -DCMAKE_BUILD_TYPE= -DCMAKE_INSTALL_PREFIX= --build --install --target --config --preset --list-presets"),
        ("gdb", "GNU debugger", "run break continue step next print backtrace info list watch set quit attach detach frame thread catch display undisplay source x/"),
        ("valgrind", "Memory debugging and profiling", "--leak-check=full --show-reachable --track-origins --tool= --log-file= --gen-suppressions= memcheck callgrind cachegrind massif helgrind"),
        ("readelf", "Display ELF file information", "-a -h -l -S -s -d -r -n -V -A --all --file-header --program-headers --section-headers --symbols --dynamic --relocs --notes --version-info --arch-specific"),
        ("objdump", "Display object file information", "-d -D -h -t -T -r -R -s -x -f --disassemble --disassemble-all --headers --syms --dynamic-syms --reloc --dynamic-reloc --full-contents --all-headers --file-headers"),
        ("strip", "Discard symbols from object files", "-s -g -x --strip-all --strip-debug --strip-unneeded"),
        ("ar", "Archive utility", "r c s d t x q --create --extract --list --delete --replace --quick-append"),
    ],

    # ===== 20. macOS-SPECIFIC =====
    "macOS Specific": [
        ("defaults", "Access macOS user defaults", "read write delete read-type domains find -g -currentHost -app"),
        ("caffeinate", "Prevent macOS from sleeping", "-d -i -m -s -u -t --display --idle --disk --system --user --timeout"),
        ("pmset", "Power management settings (macOS)", "-g -a -b -c -u displaysleep disksleep sleep womp ring autorestart lidwake acwake lessbright halfdim sms hibernatemode standby standbydelay autopoweroff ttyskeepawake"),
        ("pbcopy", "Copy to macOS clipboard", ""),
        ("pbpaste", "Paste from macOS clipboard", ""),
        ("scutil", "System configuration utility (macOS)", "--dns --proxy --nwi --get --set ComputerName LocalHostName HostName"),
        ("csrutil", "System Integrity Protection (macOS)", "status enable disable"),
        ("softwareupdate", "Software update tool (macOS)", "-l -i -a -d -r --list --install --all --download --restart --recommended --verbose --agree-to-license"),
        ("tmutil", "Time Machine utility (macOS)", "enable disable startbackup stopbackup status destinationinfo setdestination removedestination listbackups latestbackup deletelocalsnapshots thinlocalsnapshots"),
    ],

    # ===== 21. OTHER / APPLICATION-SPECIFIC =====
    "Databases": [
        ("mysql", "MySQL client", "-u -p -h -P -D -e --user --password --host --port --database --execute --batch --table --xml --json --ssl-mode"),
        ("mysqladmin", "MySQL admin tool", "create drop status processlist flush-hosts flush-logs flush-privileges ping shutdown variables version -u -p"),
        ("psql", "PostgreSQL client", "-U -d -h -p -c -f -l --username --dbname --host --port --command --file --list --html --csv --quiet --no-align --tuples-only"),
        ("pg_dump", "PostgreSQL backup", "-U -d -h -f -F -t -T -n -N --username --dbname --host --file --format --table --exclude-table --schema --exclude-schema --data-only --schema-only --clean --create --insert"),
        ("pg_ctl", "PostgreSQL control", "start stop restart reload status promote init -D -l -o --pgdata --log --options"),
        ("redis-cli", "Redis client", "-h -p -a -n -u --host --port --auth --db --uri ping set get del keys scan monitor info config client cluster pubsub subscribe"),
        ("mongo", "MongoDB shell", "--host --port --username --password --authenticationDatabase --eval --quiet --shell"),
        ("mongod", "MongoDB server", "--dbpath --port --bind_ip --logpath --fork --auth --replSet --configsvr --shardsvr"),
        ("sqlite3", "SQLite client", "-header -column -csv -json -html -line -separator -cmd .tables .schema .dump .import .mode .headers .output .quit .read"),
        ("influx", "InfluxDB CLI", "-host -port -username -password -database -execute -format -precision write query"),
        ("influxd", "InfluxDB daemon", "run backup restore config"),
    ],

    "Web Servers and Proxies": [
        ("nginx", "Nginx web server", "-t -T -c -s -p -g --test --dump-config --config --signal --prefix stop quit reload reopen"),
        ("caddy", "Caddy web server", "run start stop reload adapt environ file-server reverse-proxy --config --adapter"),
        ("lighttpd", "Lightweight web server", "-f -t -D --config --test --no-daemonize"),
        ("squid", "Squid proxy server", "-N -d -f -k -z --no-daemon --debug --config --reconfigure --shutdown"),
    ],

    "Programming Languages and Runtimes": [
        ("python3", "Python 3 interpreter", "-c -m -i -u -v -B -O -W --command --module --interactive --unbuffered --verbose"),
        ("python", "Python interpreter", "-c -m -i -u -v -B -O --command --module --interactive --unbuffered --verbose"),
        ("node", "Node.js runtime", "-e -p -r -v --eval --print --require --version --inspect --inspect-brk"),
        ("ruby", "Ruby interpreter", "-e -n -p -i -l -a -w --eval --in-place --line --autosplit --warnings"),
        ("java", "Java runtime", "-jar -cp -classpath -Xmx -Xms -Xss -D -ea -da --module --module-path --add-modules --version"),
        ("go", "Go programming language", "build run test get mod fmt vet install clean doc env version"),
        ("dotnet", "NET runtime and CLI", "new build run test publish restore add remove clean pack nuget tool sln --configuration --framework --runtime --output"),
        ("scala", "Scala compiler and runner", "-cp -classpath -e -deprecation -feature -Xfatal-warnings"),
        ("clojure", "Clojure programming language", "-M -A -X -T -P --main --aliases --exec --tool --prepare"),
        ("elixir", "Elixir programming language", "-e -r -S -pa --eval --require --script"),
        ("julia", "Julia programming language", "-e -p -t --eval --procs --threads --project --startup-file"),
        ("erl", "Erlang runtime", "-sname -name -setcookie -pa -pz -eval -noshell -detached"),
        ("groovy", "Groovy programming language", "-e -c -d -i --eval --compile --debug --indy"),
        ("octave", "GNU Octave numerical computing", "--eval --persist --no-gui --silent --verbose"),
        ("php", "PHP interpreter", "-r -f -S -i -m -v --run --file --server --info --modules --version"),
        ("pwsh", "PowerShell Core", "-Command -File -NoProfile -NonInteractive -ExecutionPolicy"),
    ],

    "Build Tools and Task Runners": [
        ("gradle", "Build automation tool", "build clean test run assemble check dependencies -x --info --debug --stacktrace --parallel --daemon"),
        ("mvn", "Maven build tool", "clean compile test package install deploy site -DskipTests -pl -am -P --batch-mode --offline --update-snapshots"),
        ("sbt", "Scala build tool", "compile test run clean package publish console assembly ~compile"),
        ("grunt", "JavaScript task runner", "init build test clean deploy --force --verbose --no-color"),
        ("gulp", "JavaScript streaming build", "default build test clean watch --tasks --depth --silent"),
        ("webpack", "JavaScript module bundler", "--mode --config --env --progress --watch --devtool --output-path --entry development production"),
        ("vite", "Frontend build tool", "dev build preview optimize --host --port --open --config --mode"),
        ("rollup", "JavaScript module bundler", "-c -i -o -f -w -p --config --input --output --format --watch --plugin"),
        ("parcel", "Web application bundler", "build serve watch --port --host --dist-dir --no-cache --no-source-maps"),
        ("tsc", "TypeScript compiler", "--init --watch --build --project --target --module --outDir --strict --noEmit --declaration --sourceMap"),
        ("babel", "JavaScript compiler", "--presets --plugins --config-file --out-dir --out-file --watch --source-maps"),
        ("eslint", "JavaScript linter", "--fix --config --ext --ignore-path --max-warnings --format --rule --debug"),
        ("sass", "Sass CSS preprocessor", "--watch --style --source-map --no-source-map --load-path compressed expanded"),
        ("lessc", "Less CSS compiler", "--source-map --clean-css --include-path --global-var --modify-var"),
        ("postcss", "CSS post-processor", "--config --dir --output --watch --use --map"),
        ("svgo", "SVG optimizer", "-i -o -f -r -p --input --output --folder --recursive --precision --config"),
    ],

    "JavaScript Package Managers": [
        ("yarn", "Yarn package manager", "add remove upgrade install init run test build --dev --peer --optional --exact --tilde --global --frozen-lockfile --production"),
        ("pnpm", "Fast node package manager", "add remove install update run test build --save-dev --global --filter --recursive --frozen-lockfile --shamefully-hoist"),
        ("ng", "Angular CLI", "new generate serve build test lint e2e add update deploy --routing --style --skip-tests --standalone --project"),
    ],

    "CI/CD and Infrastructure": [
        ("terraform", "Infrastructure as code", "init plan apply destroy validate fmt state output import refresh workspace show -var -var-file --auto-approve --target --lock --parallelism"),
    ],

    "Monitoring and Observability": [
        ("prometheus", "Monitoring system", "--config.file --web.listen-address --storage.tsdb.path --storage.tsdb.retention.time --web.enable-lifecycle"),
        ("nagios", "Network monitoring", "-v -d -s --verify-config --daemon --show-scheduling"),
        ("datadog-agent", "Datadog monitoring agent", "run start status check config flare health diagnose"),
        ("splunk", "Splunk enterprise", "start stop restart status search add edit remove list enable disable"),
        ("zabbix_server", "Zabbix monitoring server", "-c -R --config --runtime-control config_cache_reload diaginfo"),
    ],

    "Message Queues": [
        ("rabbitmqctl", "RabbitMQ management", "status list_queues list_exchanges list_bindings list_connections list_channels add_user delete_user set_permissions clear_permissions set_policy cluster_status join_cluster"),
    ],

    "Media and Document Processing": [
        ("ffmpeg", "Multimedia processing", "-i -c -vcodec -acodec -r -s -b -f -ss -t -to -y -n -v -vf -af -map -preset -crf -an -vn copy libx264 libx265 aac mp3 --duration --overwrite"),
        ("convert", "ImageMagick convert", "-resize -crop -rotate -flip -flop -quality -colorspace -depth -format -filter -composite -draw -annotate -gravity"),
        ("pandoc", "Universal document converter", "-f -t -o -s --from --to --output --standalone --template --toc --number-sections --bibliography --csl --filter --lua-filter --metadata --variable"),
        ("pdflatex", "LaTeX PDF compiler", "-interaction= -output-directory= -jobname= -synctex= nonstopmode batchmode"),
        ("ebook-convert", "Calibre ebook converter", "--output-profile --input-profile --cover --title --authors --language --series --series-index"),
    ],

    "System Configuration": [
        ("localectl", "Control system locale", "status set-locale list-locales set-keymap list-keymaps set-x11-keymap"),
        ("locale-gen", "Generate locales", ""),
        ("grub-mkconfig", "Generate GRUB config", "-o --output"),
        ("grub2-mkconfig", "Generate GRUB2 config", "-o --output"),
        ("update-grub", "Update GRUB config", ""),
        ("dpkg-reconfigure", "Reconfigure installed packages", "-f --frontend --priority --all"),
        ("dpkg-query", "Query dpkg database", "-l -L -s -S -W --list --listfiles --status --search --show --showformat"),
    ],

    "Wireless and Bluetooth": [
        ("bluetoothctl", "Bluetooth control", "power scan discoverable agent connect disconnect pair trust untrust remove devices info"),
    ],

    "Miscellaneous CLI Tools": [
        ("help", "Display shell help", ""),
        ("exit", "Exit shell", ""),
        ("trap", "Trap signals and events", "EXIT INT TERM HUP ERR DEBUG RETURN"),
        ("pushd", "Push directory on stack", "+N -N"),
        ("print", "Print arguments (zsh/ksh)", "-n -l -r -f"),
        ("unset", "Unset variables or functions", "-v -f --variable --function"),
        ("fc", "Fix command from history", "-l -s -n -r -e --list --redo"),
        ("pass", "Password store", "init insert generate show ls find grep cp mv rm edit git push pull"),
        ("ftp", "File transfer protocol client", "open close get put mget mput ls cd lcd binary ascii prompt hash passive"),
        ("sshfs", "Mount remote filesystem via SSH", "-o -p -C --port --compress reconnect follow_symlinks allow_other"),
        ("showmount", "Show NFS mount info", "-a -d -e --all --directories --exports"),
        ("ipcs", "IPC status", "-m -q -s -a -l --shmems --queues --semaphores --all --limits"),
        ("inotifywait", "Wait for filesystem events", "-m -r -e -t -o --monitor --recursive --event --timeout --outfile create modify delete move access"),
        ("sync", "Synchronize cached writes to storage", "-f -d --file --data"),
        ("halt", "Halt the system", "-f -p --force --poweroff"),
        ("poweroff", "Power off the system", "-f --force"),
        ("reboot", "Reboot the system", "-f --force"),
        ("shutdown", "Halt power-off or reboot", "-h -r -c -k now +minutes HH:MM --halt --reboot --cancel"),
        ("xclip", "X clipboard tool", "-i -o -selection clipboard primary secondary -target"),
        ("xrandr", "X display configuration", "--output --mode --rate --pos --rotate --left-of --right-of --above --below --auto --off --primary --scale"),
        ("xinput", "X input device configuration", "list set-prop --list-props --disable --enable"),
        ("pactl", "PulseAudio control", "list info set-sink-volume set-source-volume set-sink-mute set-source-mute get-sink-volume set-default-sink set-default-source"),
        ("wg", "WireGuard management", "show showconf genkey genpsk pubkey set setconf addconf syncconf"),
        ("ykman", "YubiKey manager", "info list fido oath openpgp otp piv"),
        ("sqlmap", "SQL injection testing", "-u -r --dbs --tables --columns --dump --batch --level --risk --threads --proxy --tor --os-shell"),
        ("torsocks", "Route traffic through Tor", ""),
        ("vncviewer", "VNC client", "-geometry -passwd -fullscreen -viewonly -encoding"),
        ("code", "VS Code editor", "-r -g -d -n --reuse-window --goto --diff --new-window --install-extension --uninstall-extension --list-extensions"),
        ("jupyter", "Jupyter notebooks", "notebook lab console kernelspec nbconvert --ip --port --no-browser --generate-config"),
        ("ollama", "Local LLM runner", "run pull push list show create cp rm serve"),
        ("uv", "Fast Python package installer", "pip venv run sync lock add remove init --python --no-cache"),
        ("uvicorn", "ASGI server", "--host --port --reload --workers --log-level --ssl-keyfile --ssl-certfile --factory"),
        ("uwsgi", "Application server", "--http --socket --wsgi-file --module --processes --threads --master --virtualenv --chdir --logto"),
        ("flask", "Flask web framework CLI", "run shell db routes --host --port --debug --reload"),
        ("rails", "Ruby on Rails CLI", "new server console generate db routes test --api --database --skip-bundle"),
        ("pytest", "Python testing framework", "-v -x -s -k -m --verbose --exitfirst --capture --keyword --marker --cov --tb --maxfail --durations"),
    ],

    "Graph and Time-Series Databases": [
        ("neo4j", "Neo4j graph database", "start stop status console dump load --verbose --force"),
        ("dgraph", "Dgraph database", "alpha zero bulk live tool --lru_mb --raft --my --peer"),
        ("cockroach", "CockroachDB", "start start-single-node init cert sql dump node quit --insecure --listen-addr --join --store --certs-dir"),
        ("arangodb", "ArangoDB", "--starter.mode --starter.join --server.endpoint --database.directory cluster single"),
    ],

    "Big Data and Streaming": [
        ("kafka-server-start.sh", "Start Kafka broker", "config/server.properties --override"),
        ("kafka-topics.sh", "Kafka topic management", "--create --delete --list --describe --alter --bootstrap-server --topic --partitions --replication-factor"),
        ("storm", "Apache Storm", "jar list nimbus supervisor ui drpc logviewer kill rebalance activate deactivate"),
        ("hbase-daemon.sh", "HBase daemon", "start stop status master regionserver"),
        ("zeppelin-daemon.sh", "Zeppelin notebook", "start stop restart status"),
    ],

    "Kubernetes Ecosystem": [
        ("spark-submit", "Submit Spark jobs", "--master --deploy-mode --class --driver-memory --executor-memory --num-executors --conf --packages --jars --py-files"),
    ],

    "Security Testing": [
        ("clamscan", "ClamAV virus scanner", "-r -i -l -v --recursive --infected --log --verbose --remove --move --exclude --include"),
        ("chkrootkit", "Rootkit checker", "-q -x -n --quiet --expert"),
    ],

    "Filesystem Tools": [
        ("zfs", "ZFS filesystem", "create destroy list set get snapshot rollback clone promote send receive mount unmount share unshare -r -R -o"),
        ("zpool", "ZFS pool management", "create destroy list status add remove online offline clear scrub replace history -f -n"),
    ],

    "Miscellaneous Servers": [
        ("sshd", "OpenSSH server daemon", "-d -D -e -f -p --debug --no-daemon --log-stderr --config --port"),
        ("chronyc", "Chrony NTP client", "tracking sources sourcestats activity makestep burst online offline"),
        ("ntpdate", "Set date via NTP", "-b -d -q -s -u -v --debug --query"),
        ("cron", "Cron daemon", ""),
        ("iftop", "Display bandwidth usage", "-i -n -N -B -P -b -f --interface --no-dns --no-port-resolution --bytes-per-second --port-display"),
        ("conntrack", "Connection tracking tool", "-L -D -I -E -C -S --list --delete --create --event --count --stats"),
        ("iscsiadm", "iSCSI administration", "-m --mode node session discovery interface host --type --targetname --portal --login --logout --rescan"),
        ("nvme", "NVMe device management", "list id-ctrl id-ns smart-log fw-log error-log format fw-download fw-activate"),
        ("filebeat", "Log file shipper", "-e -c --modules --once --strict.perms --path.home --path.config --path.data --path.logs"),
        ("fluent-bit", "Log processor", "-c -i -o -f -R --config --input --output --flush --parser"),
    ],

    "Ruby and Web Frameworks": [
        ("bundle", "Ruby Bundler", "install update exec add remove outdated clean config show --path --without --deployment --jobs"),
        ("rackup", "Rack web server launcher", "-p -o -E -D --port --host --env --daemonize"),
    ],

    "Haskell and Clojure": [
        ("stack", "Haskell tool", "build run test bench exec setup new init install --resolver --ghc-options --no-test --fast"),
        ("lein", "Leiningen Clojure build", "new run test repl uberjar deploy clean deps compile"),
    ],

    "Arch Linux Specific": [
        ("paru", "AUR helper", "-S -R -Q -Ss -Sua --sync --remove --query --search --sysupgrade"),
        ("paccache", "Pacman cache cleanup", "-r -d -u -v --remove --dryrun --uninstalled --verbose"),
        ("pacgraph", "Pacman dependency graph", "-c -n --console --no-version"),
        ("pacman-conf", "Query pacman configuration", "--repo-list --config"),
        ("pacman-key", "Pacman keyring management", "--init --populate --refresh-keys --add --recv-keys --verify --lsign-key"),
        ("pacstrap", "Install packages to new root", "-c -d -G -M --cache --dir --config"),
        ("pactree", "Package dependency tree", "-r -d -s -u --reverse --depth --sync --unique"),
        ("reflector", "Pacman mirror list updater", "--country --protocol --latest --sort --save --age --fastest"),
    ],

    "Miscellaneous Utilities": [
        ("updatedb", "Update locate database", "--localpaths --prunepaths --output --verbose"),
        ("mlocate", "Locate files using database", "-i -c -l --ignore-case --count --limit"),
        ("getfattr", "Get extended file attributes", "-d -m -n --dump --match --name"),
        ("pivot_root", "Change root filesystem", ""),
        ("firefox", "Firefox browser", "-P -private --new-window --new-tab --safe-mode --headless"),
        ("google-chrome", "Chrome browser", "--headless --disable-gpu --remote-debugging-port --screenshot --print-to-pdf --no-sandbox --user-data-dir"),
        ("ipconfig", "IP configuration (macOS/Windows)", "getifaddr getpacket getsummary set waitall"),
        ("dscacheutil", "Directory Service cache (macOS)", "-q -flushcache --query --cachedump"),
        ("vm_stat", "Virtual memory statistics (macOS)", ""),
    ],
}

# Commands that typically need sudo
SUDO_COMMANDS = {
    "mount", "umount", "fdisk", "parted", "mkfs.ext4", "mkfs.ext3", "mkfs.ext2",
    "mkfs.xfs", "mkfs.btrfs", "mkfs.vfat", "mkfs.ntfs", "mkfs.exfat",
    "e2fsck", "fsck", "iptables", "nft", "ufw", "firewall-cmd",
    "useradd", "userdel", "usermod", "groupadd", "groupdel", "groupmod",
    "chown", "modprobe", "insmod", "rmmod", "systemctl", "dmidecode",
    "lshw", "hdparm", "smartctl", "cryptsetup", "mdadm", "pvcreate",
    "vgcreate", "lvcreate", "lvextend", "auditctl", "ausearch",
    "setenforce", "setsebool", "restorecon", "chcon", "setcap",
    "aa-enforce", "aa-complain", "efibootmgr", "grub-mkconfig",
    "update-grub", "dpkg", "rpm", "apt", "apt-get", "dnf", "yum",
    "pacman", "zypper", "chattr", "shutdown", "reboot", "halt",
    "poweroff", "init", "telinit", "hwclock", "timedatectl",
    "sysctl", "visudo", "fail2ban-client", "nmap", "tcpdump",
}


def load_flag_table(cmd: str) -> str | None:
    """Load flag table JSON for a command if it exists."""
    path = FLAG_TABLES_DIR / f"{cmd}.json"
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    lines = []
    for key, info in data.items():
        flag = info.get("flag", "")
        desc = info.get("description", "")
        lines.append(f"- `{flag}`: {desc}")
    return "\n".join(lines)


TIER_LABELS = {
    1: "TIER 1 — BENCHMARK CRITICAL",
    2: "TIER 2 — BENCHMARK REINFORCEMENT",
    3: "TIER 3 — IMPORTANT COMMON COMMAND",
    4: "TIER 4 — NICHE/SPECIALIZED",
}

TIER_RATIONALE = {
    1: "This command is FAILING or WEAK in the 100-question benchmark. Maximum training examples needed.",
    2: "This command PASSES the benchmark but needs reinforcement to maintain accuracy.",
    3: "This command is widely used in practice but not directly tested in the benchmark.",
    4: "This command is specialized/niche. Minimal coverage to establish basic competence.",
}


def generate_prompt(cmd: str, desc: str, flags: str, category: str, idx: int) -> str:
    """Generate a tiered prompt for one command."""
    tier, count = get_tier(cmd)
    tier_label = TIER_LABELS[tier]
    tier_rationale = TIER_RATIONALE[tier]

    flag_table = load_flag_table(cmd)

    if flag_table:
        flag_section = f"""## Detailed Flag Reference (from project flag table)

{flag_table}

## Additional Flags to Cover

{flags}
"""
    else:
        flag_section = f"""## Key Flags and Arguments to Cover

{flags}

Cover ALL documented flags and options for `{cmd}`. Think through the full man page.
"""

    sudo_note = ""
    if cmd in SUDO_COMMANDS:
        sudo_note = """
**Privilege Note:** This command often requires root privileges. For non-root
system contexts, prefix with `sudo`. For root contexts, omit sudo. Mix both.
"""

    # Adjust pipe requirement based on tier
    pipe_note = ""
    if count >= 200:
        pipe_count = max(count // 10, 20)
        pipe_note = f"5. **Include piped commands** where natural (at least {pipe_count} examples):\n"
        pipe_note += f"   - `{cmd} ... | grep ...`\n"
        pipe_note += f"   - `{cmd} ... | sort | uniq`\n"
        pipe_note += f"   - `{cmd} ... | head/tail/wc -l`\n"
        pipe_note += f"   - `{cmd} ... | awk ...`\n"
        pipe_note += "   - Other realistic pipelines\n"
    elif count >= 100:
        pipe_note = f"5. **Include piped commands** where natural (at least 10 examples)\n"
    else:
        pipe_note = "5. **Include a few piped commands** where natural\n"

    return f"""# {idx:03d} — `{cmd}` — {tier_label}

> **{count} examples** | {tier_rationale}

## Task

Generate exactly **{count}** training examples for the **`{cmd}`** command in ChatML JSONL format.

## Command Overview

`{cmd}` — {desc}
**Category:** {category}
{sudo_note}
## Output Format

Each line must be a valid JSON object:

```json
{{"messages": [{{"role": "system", "content": "<distro> <version> <shell> <privilege>"}}, {{"role": "user", "content": "<natural language request>"}}, {{"role": "assistant", "content": "<correct shell command>"}}]}}
```

### System Context Values

Distribute across these contexts:
- **Distros:** ubuntu 24.04, ubuntu 22.04, fedora 39, fedora 40, debian 12, centos 9, rhel 9, arch latest, opensuse 15.5, sles 15
- **Shells:** bash (80%), zsh (20%)
- **Privilege:** root (30%), non-root (70%)

## Requirements

1. **{count} unique examples** — NO duplicate (user, assistant) pairs
2. **Cover EVERY flag/argument** listed below — each in at least {max(3, count // 100)} examples
3. **Diverse natural language phrasing:**
   - Imperative: "List all files in /tmp"
   - Question: "How do I see hidden files?"
   - Casual: "show me whats in this folder"
   - Formal: "Display the contents of the /etc directory with detailed permissions"
   - Terse: "files in /var"
   - Verbose: "I need to list all files including hidden ones with human-readable sizes"
4. **Difficulty distribution:** 40% basic, 35% intermediate, 25% advanced
{pipe_note}6. **Real-world scenarios** with realistic file paths, usernames, hostnames, IPs
7. **Vary argument values** — don't reuse the same filenames/paths/patterns

{flag_section}
## Example Output Lines

```jsonl
{{"messages": [{{"role": "system", "content": "ubuntu 24.04 bash non-root"}}, {{"role": "user", "content": "<natural language request for {cmd}>"}}, {{"role": "assistant", "content": "<correct {cmd} command>"}}]}}
{{"messages": [{{"role": "system", "content": "fedora 39 zsh non-root"}}, {{"role": "user", "content": "<different phrasing>"}}, {{"role": "assistant", "content": "<{cmd} with different flags>"}}]}}
```

## Quality Checklist

- [ ] Exactly {count} lines of valid JSONL
- [ ] Every flag/subcommand appears at least {max(3, count // 100)} times
- [ ] No duplicate user+assistant pairs
- [ ] Mix of simple, intermediate, and advanced examples
- [ ] Realistic file paths, users, hosts, IPs (not placeholder junk)
- [ ] System contexts distributed across distros/shells/privileges
- [ ] Natural language is diverse (not just "use {cmd} to...")
"""


def main():
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

    # Collect unique commands (skip duplicates across categories)
    seen = set()
    unique_commands = []  # (cmd, desc, flags, category)

    for category, commands in COMMANDS_BY_CATEGORY.items():
        for cmd, desc, flags in commands:
            if cmd not in seen:
                seen.add(cmd)
                unique_commands.append((cmd, desc, flags, category))

    # Sort: Tier 1 first, then Tier 2, then Tier 3, then Tier 4
    # Within each tier, maintain original order
    def sort_key(item):
        cmd = item[0]
        tier, _ = get_tier(cmd)
        return tier

    unique_commands.sort(key=sort_key)

    # Generate files
    tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    tier_examples = {1: 0, 2: 0, 3: 0, 4: 0}

    for idx, (cmd, desc, flags, category) in enumerate(unique_commands, 1):
        safe_name = cmd.replace("/", "_").replace(".", "_").replace(" ", "_")
        filename = f"{idx:03d}_{safe_name}.md"
        filepath = COMMANDS_DIR / filename

        prompt = generate_prompt(cmd, desc, flags, category, idx)
        filepath.write_text(prompt)

        tier, count = get_tier(cmd)
        tier_counts[tier] += 1
        tier_examples[tier] += count

    total_cmds = sum(tier_counts.values())
    total_examples = sum(tier_examples.values())

    print(f"Generated {total_cmds} command prompt files in {COMMANDS_DIR}/\n")
    print(f"{'Tier':<8} {'Label':<35} {'Commands':>8} {'Examples':>10}")
    print("-" * 65)
    for t in [1, 2, 3, 4]:
        print(f"Tier {t}   {TIER_LABELS[t]:<35} {tier_counts[t]:>8} {tier_examples[t]:>10,}")
    print("-" * 65)
    print(f"{'TOTAL':<44} {total_cmds:>8} {total_examples:>10,}")


if __name__ == "__main__":
    main()
