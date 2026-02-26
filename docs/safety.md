# Safety System

INCEPT includes a multi-layered safety system that validates every generated command before it reaches the user. The system classifies risk, blocks dangerous patterns, audits sudo usage, and guards against destructive auto-retries.

## Risk Levels

Every command receives a risk classification:

| Level | Meaning | Behavior |
|---|---|---|
| **SAFE** | No destructive potential detected | Displayed normally |
| **CAUTION** | Uses sudo, writes to system paths, or involves `rm`/`dd`/`mkfs`/`kill -9` | Displayed with a warning |
| **DANGEROUS** | Writes to system-critical paths with sudo | Displayed with a strong warning |
| **BLOCKED** | Matches a banned pattern | Rejected; not shown to the user |

Risk classification logic:

1. If the command matches a banned pattern, it is `BLOCKED`.
2. If the command writes to a system-critical path (`/etc`, `/boot`, `/usr`, `/bin`, `/sbin`, `/dev`, `/lib`, `/lib64`, `/proc`, `/sys`) **and** uses `sudo`, it is `DANGEROUS`.
3. If the command uses `sudo`, writes to system paths, or uses potentially destructive operations (`rm`, `dd`, `mkfs`, `kill -9`), it is `CAUTION`.
4. Otherwise, it is `SAFE`.

## Banned Patterns (22)

These patterns are always blocked regardless of safe mode. A command matching any of these is immediately rejected.

| # | Pattern | Description |
|---|---|---|
| 1 | `:(){ ...:` | Fork bomb |
| 2 | `.(){ ...` | Fork bomb variant |
| 3 | `rm -rf /` | Recursive force-delete root |
| 4 | `rm -rf /*` | Recursive force-delete all root contents |
| 5 | `rm --no-preserve-root` | Override rm root protection |
| 6 | `dd ... of=/dev/sd*` | Write raw data to SCSI/SATA disk |
| 7 | `dd ... of=/dev/nvme*` | Write raw data to NVMe disk |
| 8 | `curl ... \| bash` | Pipe remote content to shell |
| 9 | `wget ... \| bash` | Pipe remote content to shell |
| 10 | `curl ... \| sudo bash` | Pipe remote content to root shell |
| 11 | `mkfs on /dev/sd*` | Format a SCSI/SATA disk |
| 12 | `mkfs on /dev/nvme*` | Format an NVMe disk |
| 13 | `chmod 777 /` | World-writable root |
| 14 | `chmod 777 /etc\|/usr\|...` | World-writable system directory |
| 15 | `chown ... /` | Change ownership of root |
| 16 | `shutdown\|reboot\|halt\|poweroff` | System shutdown or reboot |
| 17 | `iptables -F` | Flush all firewall rules |
| 18 | `python -c ...socket...connect` | Python reverse shell |
| 19 | `perl -e ...socket...connect` | Perl reverse shell |
| 20 | `base64 -d ... \| bash` | Decode and execute obfuscated payload |
| 21 | `ignore previous instructions` | Prompt injection attempt |
| 22 | `you are now a ...` | Role injection attempt |

## Safe Mode Restrictions (5 additional patterns)

When safe mode is enabled (default: on), these additional patterns are also blocked:

| # | Pattern | Description |
|---|---|---|
| 1 | `chmod 777` | World-writable permissions on any target |
| 2 | `chmod 666` | World-readable/writable on any target |
| 3 | `eval ...` | Shell eval command |
| 4 | `> /dev/sd*` or `> /dev/hd*` | Redirect output to raw device |
| 5 | `sudo su` | Escalate to root shell |

Safe mode is controlled via `INCEPT_SAFE_MODE` (server) or `safe_mode` in `config.toml` (CLI).

## Syntax Validation

Before pattern checking, every command is parsed with `bashlex` for syntax validation. Syntax errors are reported but do not block the command on their own.

## Sudo Audit

Commands containing `sudo` are flagged:

- If the environment context disallows sudo (`allow_sudo=false`), the command is marked invalid.
- The `requires_sudo` and `sudo_allowed` fields are included in the validation result.

## Path Safety Checks

Commands that write to system-critical paths generate warnings. The following paths are monitored:

**Linux:** `/etc`, `/boot`, `/usr`, `/bin`, `/sbin`, `/dev`, `/lib`, `/lib64`, `/proc`, `/sys`

**macOS:** `/System`, `/Library`, `/Applications` (in addition to the Linux paths above)

Write operations detected: `rm`, `mv`, `cp`, `dd`, `tee`, `install`, `chmod`, `chown`, `mkdir`, `rmdir`, `touch`, `ln`, and output redirection to these paths.

## Error Recovery System

When a command fails (reported via `POST /v1/feedback`), the recovery engine classifies the error and suggests a fix.

### Recognized Error Patterns (7)

| Error | Example stderr | Recovery Strategy |
|---|---|---|
| `apt_package_not_found` | `Unable to locate package foo` | Run `apt update` and search for similar packages |
| `dnf_package_not_found` | `No match for argument: foo` | Search with `dnf search` |
| `permission_denied` | `Permission denied` | Retry with `sudo` (if allowed) |
| `command_not_found` | `command not found: htop` | Attempt `apt install <command>` |
| `no_such_file` | `No such file or directory` | Search parent directory for similar files |
| `disk_full` | `No space left on device` | Show disk usage and largest files in `/tmp` |
| `flag_not_recognized` | `unrecognized option '--foo'` | Remove the invalid flag and retry |

### Destructive Command Guard

Commands matching `rm`, `dd`, `mkfs`, or `format` are never auto-retried, even if a recovery strategy is available. The `can_auto_retry` flag is forced to `false` for these commands.

### Retry Limits

The recovery engine allows a maximum of **3 retry attempts**. After 3 failures:

- `gave_up` is set to `true`
- `recovery_command` is empty
- The user is advised to investigate manually
