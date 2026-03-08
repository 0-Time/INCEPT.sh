# Prompt for Qwen 35B — Linux Command Training Data Generation

Copy everything below the line into Qwen 35B. Run it multiple times with different categories each time.

---

You are a Linux command-line expert generating training data for a small language model that translates natural language into Linux/macOS shell commands.

## Output Format

Output ONLY valid JSONL (one JSON object per line). Each line must have exactly this structure:

```json
{"system":"<distro> <version> <shell> <privilege>","nl":"<natural language request>","cmd":"<exact command>"}
```

### Column definitions:
- **system**: One of these system contexts (vary them across entries):
  - `ubuntu 22.04 bash non-root`
  - `ubuntu 24.04 bash non-root`
  - `debian 12 bash non-root`
  - `rhel 9 bash non-root`
  - `arch latest bash non-root`
  - `macos 15.0 zsh non-root`
  - `ubuntu 22.04 bash root`
  - `debian 12 bash root`
- **nl**: A natural language request describing what the user wants to do. Vary phrasing: imperative ("show disk usage"), question-style ("how to find large files"), casual ("list all running services"), terse ("cpu info"), verbose ("I want to see which ports are currently open and listening on my server").
- **cmd**: The exact, correct, runnable shell command. Use realistic placeholder values (actual paths like /var/log, /etc/nginx, real filenames, real package names, real usernames like "john", "deploy", real IPs like 192.168.1.100). NEVER use generic placeholders like <file>, <user>, PATH, FILENAME.

## Requirements

1. Generate **500 entries** covering ALL of the following built-in Linux binaries/commands. Generate multiple entries per binary with DIFFERENT flag combinations and DIFFERENT natural language phrasings:

### Core File Operations
`ls`, `cp`, `mv`, `rm`, `mkdir`, `rmdir`, `touch`, `ln`, `stat`, `file`, `basename`, `dirname`, `realpath`, `readlink`, `install`, `shred`, `truncate`, `mktemp`, `sync`

### File Viewing & Editing
`cat`, `head`, `tail`, `less`, `more`, `tac`, `rev`, `nl`, `fold`, `fmt`, `pr`, `expand`, `unexpand`, `colrm`, `column`

### Text Processing
`grep`, `egrep`, `fgrep`, `sed`, `awk`, `cut`, `paste`, `sort`, `uniq`, `tr`, `wc`, `diff`, `comm`, `join`, `csplit`, `split`, `strings`, `od`, `hexdump`, `xxd`

### File Search
`find`, `locate`, `updatedb`, `which`, `whereis`, `type`, `command`

### Archives & Compression
`tar`, `gzip`, `gunzip`, `bzip2`, `bunzip2`, `xz`, `unxz`, `zip`, `unzip`, `zcat`, `zless`, `zgrep`, `cpio`, `ar`

### Permissions & Ownership
`chmod`, `chown`, `chgrp`, `chattr`, `lsattr`, `umask`, `setfacl`, `getfacl`, `namei`

### User & Group Management
`useradd`, `userdel`, `usermod`, `groupadd`, `groupdel`, `groupmod`, `passwd`, `chpasswd`, `newgrp`, `groups`, `id`, `whoami`, `who`, `w`, `last`, `lastb`, `lastlog`, `finger`, `su`, `sudo`, `visudo`, `chage`, `getent`

### Process Management
`ps`, `top`, `htop`, `kill`, `killall`, `pkill`, `pgrep`, `nice`, `renice`, `nohup`, `bg`, `fg`, `jobs`, `disown`, `wait`, `timeout`, `watch`, `strace`, `ltrace`, `lsof`, `fuser`

### System Information
`uname`, `hostname`, `hostnamectl`, `uptime`, `date`, `cal`, `timedatectl`, `hwclock`, `lscpu`, `lsblk`, `lshw`, `lspci`, `lsusb`, `lsmod`, `modprobe`, `modinfo`, `dmesg`, `free`, `vmstat`, `iostat`, `mpstat`, `sar`, `nproc`, `arch`

### Disk & Filesystem
`df`, `du`, `mount`, `umount`, `fdisk`, `parted`, `mkfs`, `fsck`, `blkid`, `lsblk`, `tune2fs`, `e2label`, `xfs_info`, `findmnt`, `fstrim`, `dd`, `sync`, `blockdev`

### Networking
`ip`, `ifconfig`, `ping`, `ping6`, `traceroute`, `tracepath`, `mtr`, `ss`, `netstat`, `nmap`, `nc`, `ncat`, `curl`, `wget`, `dig`, `nslookup`, `host`, `whois`, `arp`, `route`, `ethtool`, `nmcli`, `iwconfig`, `tcpdump`, `iptables`, `nft`, `firewall-cmd`, `scp`, `sftp`, `ssh`, `ssh-keygen`, `ssh-copy-id`, `rsync`

### Package Management
`apt`, `apt-get`, `apt-cache`, `dpkg`, `yum`, `dnf`, `rpm`, `pacman`, `snap`, `flatpak`, `pip`, `pip3`, `gem`, `npm`, `cargo`

### Service & Init
`systemctl`, `service`, `journalctl`, `loginctl`, `timedatectl`, `hostnamectl`, `localectl`, `coredumpctl`

### Cron & Scheduling
`crontab`, `at`, `atq`, `atrm`, `batch`, `anacron`

### Shell Built-ins & Utilities
`echo`, `printf`, `read`, `test`, `expr`, `seq`, `yes`, `true`, `false`, `sleep`, `tee`, `xargs`, `parallel`, `env`, `export`, `set`, `unset`, `source`, `alias`, `unalias`, `history`, `fc`, `hash`, `type`, `command`, `builtin`, `eval`, `exec`

### System Administration
`shutdown`, `reboot`, `halt`, `poweroff`, `init`, `telinit`, `runlevel`, `wall`, `mesg`, `logger`, `logrotate`, `ulimit`, `sysctl`, `chroot`, `pivot_root`, `nsenter`

### SELinux / AppArmor
`getenforce`, `setenforce`, `sestatus`, `chcon`, `restorecon`, `setsebool`, `getsebool`, `aa-status`, `aa-enforce`, `aa-complain`

### Kernel & Modules
`lsmod`, `modprobe`, `rmmod`, `insmod`, `modinfo`, `depmod`, `dracut`, `mkinitramfs`, `update-grub`, `grub-mkconfig`

### Performance & Debugging
`perf`, `strace`, `ltrace`, `gdb`, `valgrind`, `time`, `/usr/bin/time`, `nice`, `ionice`, `taskset`, `numactl`, `pidstat`, `perf stat`, `oom_score`

### Containers & Virtualization (commonly pre-installed tools)
`chroot`, `unshare`, `nsenter`, `mount --bind`, `ip netns`

2. For EACH binary, generate at least 3-5 entries with:
   - Different flags and options (e.g., `ls -la`, `ls -lhS`, `ls -R`, `ls --color=auto`)
   - Different natural language styles (terse, verbose, question, imperative)
   - Both simple and complex/piped commands
   - Root vs non-root contexts where relevant (use `sudo` for non-root)

3. Include piped/compound commands (20% of entries):
   - `ps aux | grep nginx | awk '{print $2}' | xargs kill`
   - `find /var/log -name '*.log' -mtime +30 -exec rm {} \;`
   - `du -sh /home/* | sort -rh | head -10`
   - `journalctl -u nginx --since '1 hour ago' | tail -50`
   - `tar czf - /etc | ssh user@backup-server 'cat > /backups/etc-backup.tar.gz'`

4. Include edge cases and advanced usage:
   - Commands with regex patterns
   - Commands with brace expansion: `mkdir -p project/{src,bin,docs,tests}`
   - Commands with process substitution: `diff <(ls dir1) <(ls dir2)`
   - Commands with here-strings and heredocs
   - One-liners with `while`, `for`, `if` constructs

5. CRITICAL RULES:
   - Every command MUST be syntactically valid and runnable
   - NO markdown, NO explanations, NO headers — ONLY JSONL lines
   - NO placeholder text like `<filename>`, `<user>`, `<ip>` — use realistic values
   - Vary the system context across entries
   - Each `nl` field should sound natural, like a real human would ask
   - Commands must match the system context (e.g., `apt` for debian/ubuntu, `dnf` for rhel, `pacman` for arch, `brew` for macos)

## Example output (first 10 lines):

```
{"system":"ubuntu 22.04 bash non-root","nl":"show all files including hidden ones","cmd":"ls -la"}
{"system":"debian 12 bash root","nl":"recursively change ownership of /var/www to www-data","cmd":"chown -R www-data:www-data /var/www"}
{"system":"macos 15.0 zsh non-root","nl":"find all .log files modified in the last 24 hours","cmd":"find /var/log -name '*.log' -mtime -1"}
{"system":"rhel 9 bash non-root","nl":"show top 10 largest directories in /home","cmd":"sudo du -sh /home/* | sort -rh | head -10"}
{"system":"ubuntu 24.04 bash non-root","nl":"kill all processes named python3","cmd":"pkill python3"}
{"system":"arch latest bash root","nl":"list all installed packages sorted by size","cmd":"pacman -Qi | awk '/^Name/{name=$3} /^Installed Size/{print $4,$5,name}' | sort -rh | head -20"}
{"system":"debian 12 bash non-root","nl":"monitor cpu and memory usage every 2 seconds","cmd":"vmstat 2"}
{"system":"ubuntu 22.04 bash non-root","nl":"compress all .log files older than 7 days","cmd":"find /var/log -name '*.log' -mtime +7 -exec gzip {} \\;"}
{"system":"macos 15.0 zsh non-root","nl":"check which ports are listening","cmd":"sudo lsof -iTCP -sTCP:LISTEN -nP"}
{"system":"rhel 9 bash root","nl":"set immutable flag on /etc/resolv.conf","cmd":"chattr +i /etc/resolv.conf"}
```

NOW GENERATE 500 ENTRIES. Output ONLY the JSONL lines, nothing else.
