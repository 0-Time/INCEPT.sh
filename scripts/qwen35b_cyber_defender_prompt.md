# Prompt for Qwen 35B — Cyber Defender Linux Command Training Data

Copy everything below the line into Qwen 35B. Run it multiple times with different focus areas.

---

You are a senior SOC analyst and incident responder generating training data for a small language model that translates natural language into Linux/macOS shell commands used in defensive cybersecurity operations.

## Output Format

Output ONLY valid JSONL (one JSON object per line). Each line must have exactly this structure:

```json
{"system":"<distro> <version> <shell> <privilege>","nl":"<natural language request>","cmd":"<exact command>"}
```

### Column definitions:
- **system**: Vary across these contexts:
  - `ubuntu 22.04 bash non-root`, `ubuntu 22.04 bash root`, `ubuntu 24.04 bash non-root`
  - `debian 12 bash non-root`, `debian 12 bash root`
  - `rhel 9 bash non-root`, `rhel 9 bash root`
  - `centos 9 bash root`
  - `macos 15.0 zsh non-root`
  - `kali 2024 bash root`
  - `arch latest bash non-root`
- **nl**: Natural language request as a cyber defender would ask. Vary phrasing styles: terse ("failed ssh logins"), imperative ("show all listening ports"), question ("which processes are connecting to external IPs?"), scenario-based ("hunt for lateral movement via SMB"), verbose ("I want to check if any unauthorized cron jobs were added in the last 24 hours").
- **cmd**: Exact, runnable shell command. Use realistic values: real IPs (192.168.1.0/24, 10.0.0.50, 172.16.0.0/12), real paths (/var/log/auth.log, /etc/shadow, /tmp/.hidden), real ports (22, 80, 443, 4444, 8080), real process names (nginx, sshd, apache2, python3), real usernames (root, www-data, admin, john), real domains (evil.com, c2server.net, suspicious.xyz).

## Requirements

Generate **500 entries** covering ALL flag variations for each tool. For every binary listed, generate entries with DIFFERENT flag combinations. This is critical — the model must learn every useful flag.

---

### 1. GREP — Full Flag Coverage (generate 30+ entries)

Every combination matters. Cover ALL of these:

| Flags | Purpose | Example |
|-------|---------|---------|
| `grep 'pattern' file` | Basic search | Search auth.log for "Failed" |
| `grep -i` | Case insensitive | Search case-insensitive for "error" |
| `grep -r` / `grep -R` | Recursive directory search | Search all configs for password |
| `grep -v` | Invert match (exclude lines) | Show lines NOT matching "INFO" |
| `grep -n` | Show line numbers | Show line numbers of matches |
| `grep -c` | Count matches | Count failed login attempts |
| `grep -l` | List filenames only | Which log files contain "segfault" |
| `grep -L` | List files NOT matching | Which configs don't have "ssl" |
| `grep -w` | Match whole word only | Match "root" not "chroot" |
| `grep -x` | Match entire line | Lines that are exactly "CRITICAL" |
| `grep -A N` | N lines after match | Show 5 lines after each error |
| `grep -B N` | N lines before match | Show 3 lines before each crash |
| `grep -C N` | N lines context (before+after) | Show context around matches |
| `grep -E` | Extended regex (ERE) | Use regex alternation `(ssh\|ftp)` |
| `grep -P` | Perl regex (PCRE) | Use lookahead/lookbehind |
| `grep -o` | Print only matched part | Extract IP addresses from logs |
| `grep -h` | Suppress filename in output | Merge results from multiple files |
| `grep -f file` | Patterns from file | Match against IOC list |
| `grep --include` | Filter file types | Search only .conf files |
| `grep --exclude-dir` | Skip directories | Skip .git directories |
| `grep -m N` | Stop after N matches | Get first 5 matches only |
| `grep -q` | Quiet mode (for scripts) | Check if pattern exists (exit code) |
| `grep -z` | Search compressed files | Search in gzipped logs |
| Combined flags | Multiple flags together | `grep -rin`, `grep -rnl`, `grep -Eo`, `grep -Poh`, `grep -cvw` |

Also generate piped grep patterns:
- `cat file | grep -v '^#' | grep -v '^$'` (strip comments and blanks)
- `grep -rn 'pattern' | grep -v 'false_positive'` (chain greps)
- `zgrep 'pattern' /var/log/*.gz` (search rotated logs)
- `grep -oP '\d{1,3}(\.\d{1,3}){3}' file` (extract IPs with PCRE)
- `grep -f ioc_list.txt /var/log/syslog` (bulk IOC matching)

---

### 2. FIND — Full Flag Coverage (generate 30+ entries)

| Flags | Purpose |
|-------|---------|
| `-name '*.log'` | Match by filename pattern |
| `-iname` | Case-insensitive name match |
| `-type f` / `-type d` / `-type l` | File type (file/dir/symlink) |
| `-size +100M` / `-size -1k` | Size filters |
| `-mtime -1` / `-mtime +30` | Modified time (days) |
| `-mmin -60` | Modified time (minutes) |
| `-atime` / `-ctime` | Access time / change time |
| `-newer file` | Modified after reference file |
| `-user root` / `-group www-data` | Owner/group filter |
| `-perm 777` / `-perm -4000` | Permission filter (SUID!) |
| `-perm /u+s` / `-perm /g+s` | SUID/SGID bits |
| `-writable` / `-readable` / `-executable` | Permission checks |
| `-empty` | Empty files/dirs |
| `-maxdepth N` / `-mindepth N` | Depth control |
| `-exec cmd {} \;` | Execute per file |
| `-exec cmd {} +` | Execute batched |
| `-execdir` | Execute in file's directory |
| `-delete` | Delete matched files |
| `-print0` | Null-delimited output (for xargs -0) |
| `-printf '%p %u %m\n'` | Custom output format |
| `-ls` | ls-style output |
| `-not` / `!` | Negate condition |
| `-o` | OR conditions |
| `-regex` | Path regex match |
| `-samefile` | Find hardlinks |
| `-inum` | Find by inode |
| `-links +1` | Files with multiple hardlinks |
| `-xdev` | Don't cross filesystem boundaries |
| Combined | `find / -perm -4000 -type f -ls` (SUID audit) |

---

### 3. NETWORK FORENSICS TOOLS — Full Flag Coverage

**ss** (generate 15+ entries):
`-t` (TCP), `-u` (UDP), `-l` (listening), `-n` (numeric), `-p` (process), `-a` (all), `-4`/`-6` (IPv4/6), `-o` (timer info), `-e` (extended), `-i` (internal info), `state established`, `state time-wait`, `sport = :22`, `dport = :443`, `dst 10.0.0.0/8`
Combinations: `ss -tunap`, `ss -tlnp`, `ss -tan state established`, `ss -tunap | grep ESTAB`, `ss -o state time-wait`

**netstat** (generate 10+ entries):
`-t`, `-u`, `-l`, `-n`, `-p`, `-a`, `-r` (routing), `-s` (statistics), `-i` (interfaces), `-g` (multicast)
Combinations: `netstat -tulnp`, `netstat -an | grep ESTABLISHED`, `netstat -s | grep -i error`

**tcpdump** (generate 15+ entries):
`-i eth0`, `-i any`, `-n` (no DNS), `-nn` (no DNS/port resolve), `-v`/`-vv`/`-vvv`, `-c N` (count), `-w file.pcap`, `-r file.pcap`, `-X` (hex+ASCII), `-A` (ASCII), `-s 0` (full packet), `-e` (link layer), `-q` (quiet), `-tttt` (timestamps)
Filters: `host 10.0.0.5`, `port 443`, `src net 192.168.1.0/24`, `dst port 22`, `tcp[tcpflags] & tcp-syn != 0`, `not port 22`, `icmp`, `arp`
Combinations: `tcpdump -i eth0 -nn -w capture.pcap 'port 443 and host 10.0.0.5'`, `tcpdump -r capture.pcap -nn 'tcp[tcpflags] & (tcp-syn) != 0'`

**curl** (generate 15+ entries):
`-I` (headers only), `-v` (verbose), `-k` (insecure), `-L` (follow redirects), `-o file`, `-O`, `-s` (silent), `-S`, `-x proxy`, `-H 'header'`, `-d 'data'`, `-X POST/GET/PUT/DELETE`, `-u user:pass`, `--connect-timeout`, `-w '%{http_code}'`, `--resolve`, `-b cookie`, `-c cookie_jar`, `--cert`, `--key`

**nmap** (generate 15+ entries):
`-sT` (TCP connect), `-sS` (SYN scan), `-sU` (UDP), `-sV` (version), `-sC` (scripts), `-O` (OS detect), `-A` (aggressive), `-p-` (all ports), `-p 1-1024`, `--top-ports 100`, `-Pn` (no ping), `-n` (no DNS), `-oN`/`-oX`/`-oG`/`-oA` (output formats), `--script vuln`, `--script ssl-*`, `-sn` (ping sweep), `-PR` (ARP scan), `--open`, `-T4` (speed), `-6` (IPv6)

**ip** (generate 10+ entries):
`ip addr show`, `ip addr add`, `ip link show`, `ip link set up/down`, `ip route show`, `ip route add`, `ip neigh show` (ARP table), `ip -s link` (stats), `ip netns`, `ip -br a` (brief)

---

### 4. LOG ANALYSIS (generate 40+ entries)

**journalctl**:
`-u nginx` (unit), `-f` (follow), `-n 50` (last N), `--since '1 hour ago'`, `--until '2024-01-01'`, `-p err` (priority), `-p warning`, `-k` (kernel), `-b` (current boot), `-b -1` (previous boot), `--no-pager`, `-o json`, `-o verbose`, `-o short-iso`, `--disk-usage`, `--vacuum-size=500M`, `_PID=1234`, `_UID=0`, `_COMM=sshd`, `SYSLOG_IDENTIFIER=sudo`

**tail/head**:
`tail -f`, `tail -F` (follow rotation), `tail -n 100`, `tail -c 1000`, `head -n 1`, `tail -f | grep --line-buffered`

**awk** for log parsing (generate 15+ entries):
`awk '{print $1}'`, `awk -F: '{print $1}'`, `awk '/pattern/'`, `awk '$9 >= 400'` (HTTP errors), `awk '{count[$1]++} END {for(ip in count) print count[ip], ip}'` (IP frequency), `awk -v OFS='\t'`, `awk 'NR>=100 && NR<=200'`, `awk '!seen[$0]++'` (dedup)

**sed** for log processing:
`sed -n '100,200p'`, `sed '/pattern/d'`, `sed 's/password=.*/password=REDACTED/g'`, `sed -i.bak`, `sed -n '/START/,/END/p'` (range extraction)

**sort/uniq** for analysis:
`sort | uniq -c | sort -rn` (frequency count), `sort -t: -k3 -n`, `sort -u`, `uniq -d` (dupes only), `uniq -u` (unique only)

**cut/paste**:
`cut -d' ' -f1`, `cut -d: -f1,3`, `cut -c1-15`, `paste -d, file1 file2`

**wc**:
`wc -l`, `wc -w`, `wc -c`, `wc -L` (longest line)

---

### 5. PROCESS FORENSICS (generate 30+ entries)

**ps**:
`ps aux`, `ps -ef`, `ps -eo pid,ppid,user,args`, `ps -eo pid,rss,vsz,comm --sort=-rss`, `ps auxf` (forest), `ps -p 1234`, `ps -u root`, `ps -C sshd`, `ps axjf`, `ps -eo pid,lstart,cmd`

**lsof**:
`lsof -i`, `lsof -i :443`, `lsof -iTCP`, `lsof -iUDP`, `lsof -i @10.0.0.5`, `lsof -i TCP:LISTEN`, `lsof -u www-data`, `lsof -p 1234`, `lsof -c nginx`, `lsof +D /tmp`, `lsof /var/log/syslog`, `lsof -nP` (no resolve), `lsof +L1` (deleted but open), `lsof -d txt` (text segments), `lsof -R` (PPID)

**strace**:
`strace -p 1234`, `strace -e trace=network`, `strace -e trace=file`, `strace -e trace=open,read,write`, `strace -f` (follow forks), `strace -c` (summary), `strace -t` (timestamps), `strace -o output.txt`, `strace -e trace=connect`

**kill/pkill/pgrep**:
`kill 1234`, `kill -9 1234`, `kill -TERM 1234`, `kill -HUP 1234` (reload), `kill -USR1 1234` (signal), `killall python3`, `pkill -f 'python.*server'`, `pkill -u john`, `pkill -9 -f 'crypto'`, `pgrep -la nginx`, `pgrep -u root sshd`, `pgrep -c sshd` (count)

**top/htop**:
`top`, `top -b -n 1` (batch), `top -b -n 1 -o %MEM`, `top -p 1234`, `top -u www-data`, `htop -t` (tree), `htop -p 1234`

**nice/renice/ionice**:
`nice -n 19 command`, `renice -n 10 -p 1234`, `ionice -c 3 -p 1234`

---

### 6. FILE INTEGRITY & FORENSICS (generate 25+ entries)

**md5sum/sha256sum/sha1sum**:
`md5sum file`, `sha256sum file`, `sha256sum -c checksums.txt`, `find /usr/bin -exec sha256sum {} \;`, `sha256sum /etc/passwd`

**stat**:
`stat file`, `stat -c '%a %U %G %n' file`, `stat -c '%Y' file` (mtime epoch), `stat --format='%A %h %U %G %s %y %n'`

**file**:
`file binary`, `file -b`, `file -i` (MIME), `file -z` (compressed), `file /proc/1234/exe`

**strings**:
`strings binary`, `strings -n 10 binary`, `strings -a binary`, `strings -e l` (16-bit), `strings /proc/1234/exe | grep -i password`

**xxd/hexdump/od**:
`xxd file | head`, `xxd -l 64 file`, `hexdump -C file | head`, `od -A x -t x1z file | head`

**diff/comm**:
`diff file1 file2`, `diff -u`, `diff -r dir1 dir2`, `diff <(ls /usr/bin) <(cat known_good_bins.txt)`, `comm -23 file1 file2` (only in file1)

**chattr/lsattr**:
`chattr +i /etc/resolv.conf`, `chattr -i file`, `chattr +a /var/log/auth.log` (append only), `lsattr /etc/`, `lsattr -R /etc/ | grep -v '----'`

---

### 7. INCIDENT RESPONSE & HUNTING (generate 40+ entries)

**Lateral movement detection:**
- Failed SSH: `grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -20`
- Successful SSH from unusual IP: `grep 'Accepted' /var/log/auth.log | grep -v '10.0.0.'`
- RDP/SMB connections: `ss -tan | grep -E ':445|:3389'`
- Unusual outbound connections: `ss -tanp | grep ESTAB | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn`

**Persistence hunting:**
- New cron jobs: `find /etc/cron* /var/spool/cron -mtime -1 -ls`
- Suspicious crontab: `for u in $(cut -d: -f1 /etc/passwd); do echo "=== $u ==="; crontab -l -u $u 2>/dev/null; done`
- Modified systemd services: `find /etc/systemd /lib/systemd -mtime -7 -name '*.service' -ls`
- Startup scripts: `ls -la /etc/init.d/ /etc/rc*.d/`
- Bashrc backdoors: `grep -rn 'curl\|wget\|nc\|/dev/tcp' /home/*/.bashrc /root/.bashrc 2>/dev/null`
- SSH authorized_keys: `find / -name authorized_keys -ls 2>/dev/null`
- SUID/SGID binaries: `find / -perm -4000 -type f -ls 2>/dev/null`
- World-writable files: `find / -perm -o+w -type f -not -path '/proc/*' -not -path '/sys/*' -ls 2>/dev/null`

**Malware hunting:**
- Hidden files in /tmp: `find /tmp /var/tmp /dev/shm -name '.*' -ls 2>/dev/null`
- Files with no owner: `find / -nouser -o -nogroup 2>/dev/null`
- Recently modified binaries: `find /usr/bin /usr/sbin /bin /sbin -mtime -3 -ls`
- Deleted but running: `lsof +L1`
- Processes with deleted binary: `ls -la /proc/*/exe 2>/dev/null | grep deleted`
- Suspicious /proc entries: `ls -la /proc/1234/exe /proc/1234/cwd /proc/1234/fd/`
- Process memory strings: `strings /proc/1234/maps`
- Check for rootkits: `find / -name '*.ko' -mtime -7 2>/dev/null`

**Network IOC hunting:**
- DNS queries for suspicious domains: `tcpdump -i any -nn 'port 53' | grep -E 'evil\.com|c2server\.net'`
- Connections to known bad IPs: `ss -tanp | grep -f bad_ips.txt`
- Unusual listening ports: `ss -tlnp | grep -v -E ':22|:80|:443'`
- Beaconing detection (regular intervals): `tcpdump -i eth0 -nn dst host 10.0.0.50 -c 100 -tttt`
- Data exfiltration (large DNS): `tcpdump -i any -nn 'port 53 and udp[10] > 50'`
- Reverse shells: `ss -tanp | grep -E ':4444|:5555|:1337|:9001'`

**User activity forensics:**
- Last logins: `last -aiF`, `lastb -aiF` (failed), `lastlog`
- Currently logged in: `w`, `who -a`
- Sudo history: `grep 'sudo' /var/log/auth.log | tail -50`
- User command history: `cat /home/john/.bash_history`
- Password changes: `grep 'password changed' /var/log/auth.log`
- Account modifications: `grep -E 'useradd|usermod|userdel|groupadd' /var/log/auth.log`
- PAM authentication: `grep 'pam_unix' /var/log/auth.log`

**Filesystem timeline:**
- Files modified today: `find / -mtime 0 -ls 2>/dev/null | head -50`
- Files accessed in last hour: `find / -amin -60 -type f 2>/dev/null | head -50`
- Files changed (metadata) recently: `find /etc -ctime -1 -ls`
- Timeline sorted by mtime: `find /var/log -type f -printf '%T+ %p\n' | sort -r | head -50`

---

### 8. HARDENING & COMPLIANCE (generate 20+ entries)

- Check open ports: `ss -tlnp`
- Check SUID bits: `find / -perm -4000 -type f -exec ls -la {} \;`
- Check world-writable dirs: `find / -perm -0002 -type d 2>/dev/null`
- Check password policy: `chage -l john`
- Check PAM config: `cat /etc/pam.d/common-password`
- List all users with shell: `grep -v '/nologin\|/false' /etc/passwd`
- Check shadow file permissions: `ls -la /etc/shadow`
- List all sudoers: `grep -v '^#' /etc/sudoers | grep -v '^$'`
- Firewall rules: `iptables -L -n -v`, `nft list ruleset`, `ufw status verbose`
- Check SSH config: `sshd -T | grep -E 'permitrootlogin|passwordauthentication|port'`
- Check kernel parameters: `sysctl -a | grep -E 'ip_forward|accept_redirects|syncookies'`
- Audit running services: `systemctl list-units --type=service --state=running`
- Check file capabilities: `getcap -r / 2>/dev/null`
- Check AppArmor/SELinux: `aa-status`, `sestatus`, `getenforce`

---

### 9. MEMORY & VOLATILE DATA (generate 15+ entries)

- Process maps: `cat /proc/1234/maps`
- Process environment: `cat /proc/1234/environ | tr '\0' '\n'`
- Process file descriptors: `ls -la /proc/1234/fd/`
- Process network: `cat /proc/1234/net/tcp`
- System memory: `free -h`, `cat /proc/meminfo`, `vmstat 1 5`
- Swap usage: `swapon --show`, `cat /proc/swaps`
- Kernel ring buffer: `dmesg -T | tail -50`, `dmesg --level=err,warn`
- Loaded modules: `lsmod`, `cat /proc/modules`
- Mount points: `mount | column -t`, `findmnt`, `cat /proc/mounts`
- System uptime and load: `uptime`, `cat /proc/loadavg`

---

### 10. PERMISSIONS — Complete chmod/chown/chattr Coverage (generate 20+ entries)

**chmod numeric:**
`chmod 777`, `chmod 755`, `chmod 700`, `chmod 644`, `chmod 600`, `chmod 400`, `chmod 4755` (SUID), `chmod 2755` (SGID), `chmod 1777` (sticky)

**chmod symbolic:**
`chmod +x`, `chmod u+rwx`, `chmod go-rwx`, `chmod a+r`, `chmod u+s` (SUID), `chmod g+s` (SGID), `chmod o+t` (sticky)

**chmod recursive:**
`chmod -R 755 /var/www`, `chmod -R go-rwx /root`

**chown:**
`chown root:root`, `chown www-data:www-data`, `chown -R`, `chown --reference=file1 file2`

**chattr/lsattr:**
`chattr +i` (immutable), `chattr -i`, `chattr +a` (append only), `chattr +s` (secure delete), `chattr +u` (undelete), `lsattr`, `lsattr -R`

**umask:**
`umask`, `umask 022`, `umask 077`, `umask -S`

**ACLs:**
`getfacl file`, `setfacl -m u:john:rwx file`, `setfacl -R -m g:devops:rx /opt/app`, `setfacl -x u:john file`, `setfacl -b file` (remove all)

---

## CRITICAL RULES:

1. **500 entries minimum** — aim for even coverage across all categories
2. **Every command MUST be syntactically valid and runnable**
3. **NO markdown, NO explanations, NO headers — ONLY JSONL lines**
4. **NO placeholders** like `<file>`, `<user>`, `<ip>` — use realistic values
5. **Vary natural language phrasing** — terse, verbose, question, imperative, scenario-based
6. **Vary system contexts** across entries
7. **Include piped/compound commands** (at least 30% of entries)
8. **Cover EVERY flag listed** for grep, find, ss, tcpdump, nmap, lsof, ps, journalctl
9. **Include both simple and expert-level commands**
10. **Use sudo where needed for non-root contexts**

## Example output (first 15 lines):

```
{"system":"ubuntu 22.04 bash root","nl":"show failed SSH logins with IP addresses","cmd":"grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -20"}
{"system":"debian 12 bash non-root","nl":"find all SUID binaries on the system","cmd":"sudo find / -perm -4000 -type f -ls 2>/dev/null"}
{"system":"rhel 9 bash root","nl":"capture network traffic on port 443 for 60 seconds","cmd":"tcpdump -i eth0 -nn -c 1000 -w /tmp/capture.pcap 'port 443'"}
{"system":"ubuntu 22.04 bash non-root","nl":"grep for IP addresses in all log files recursively","cmd":"sudo grep -rPoh '\\d{1,3}(\\.\\d{1,3}){3}' /var/log/ | sort | uniq -c | sort -rn | head -20"}
{"system":"kali 2024 bash root","nl":"scan top 1000 ports on the target with version detection","cmd":"nmap -sV --top-ports 1000 -oN scan_results.txt 192.168.1.100"}
{"system":"macos 15.0 zsh non-root","nl":"which processes are listening on which ports","cmd":"sudo lsof -iTCP -sTCP:LISTEN -nP"}
{"system":"debian 12 bash root","nl":"hunt for reverse shell connections","cmd":"ss -tanp | grep -E ':4444|:5555|:1337|:9001|:8888' | grep ESTAB"}
{"system":"ubuntu 24.04 bash non-root","nl":"check if any cron jobs were modified in the last day","cmd":"sudo find /etc/cron* /var/spool/cron -mtime -1 -ls 2>/dev/null"}
{"system":"rhel 9 bash root","nl":"make /etc/resolv.conf immutable so malware cant change it","cmd":"chattr +i /etc/resolv.conf"}
{"system":"ubuntu 22.04 bash root","nl":"list all processes with deleted executables","cmd":"ls -la /proc/*/exe 2>/dev/null | grep deleted"}
{"system":"centos 9 bash root","nl":"show kernel messages with timestamps for the last boot","cmd":"dmesg -T | tail -100"}
{"system":"debian 12 bash non-root","nl":"count how many times each IP failed SSH login","cmd":"sudo grep 'Failed password' /var/log/auth.log | grep -oP '\\d+\\.\\d+\\.\\d+\\.\\d+' | sort | uniq -c | sort -rn"}
{"system":"ubuntu 22.04 bash root","nl":"set default file creation permissions to owner-only","cmd":"umask 077"}
{"system":"kali 2024 bash root","nl":"search all .conf files for hardcoded passwords excluding comments","cmd":"grep -rn --include='*.conf' 'password' /etc/ | grep -v '^#'"}
{"system":"rhel 9 bash root","nl":"show top 10 processes by memory usage","cmd":"ps -eo pid,ppid,user,%mem,%cpu,rss,comm --sort=-%mem | head -11"}
```

NOW GENERATE 500 ENTRIES. Output ONLY the JSONL lines, nothing else.
