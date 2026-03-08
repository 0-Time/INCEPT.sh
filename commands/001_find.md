# 001 — `find` — TIER 1 — BENCHMARK CRITICAL

> **500 examples** | This command is FAILING or WEAK in the 100-question benchmark. Maximum training examples needed.

## Task

Generate exactly **500** training examples for the **`find`** command in ChatML JSONL format.

## Command Overview

`find` — Search for files in directory hierarchy
**Category:** File Operations

## Output Format

Each line must be a valid JSON object:

```json
{"messages": [{"role": "system", "content": "<distro> <version> <shell> <privilege>"}, {"role": "user", "content": "<natural language request>"}, {"role": "assistant", "content": "<correct shell command>"}]}
```

### System Context Values

Distribute across these contexts:
- **Distros:** ubuntu 24.04, ubuntu 22.04, fedora 39, fedora 40, debian 12, centos 9, rhel 9, arch latest, opensuse 15.5, sles 15
- **Shells:** bash (80%), zsh (20%)
- **Privilege:** root (30%), non-root (70%)

## Requirements

1. **500 unique examples** — NO duplicate (user, assistant) pairs
2. **Cover EVERY flag/argument** listed below — each in at least 5 examples
3. **Diverse natural language phrasing:**
   - Imperative: "List all files in /tmp"
   - Question: "How do I see hidden files?"
   - Casual: "show me whats in this folder"
   - Formal: "Display the contents of the /etc directory with detailed permissions"
   - Terse: "files in /var"
   - Verbose: "I need to list all files including hidden ones with human-readable sizes"
4. **Difficulty distribution:** 40% basic, 35% intermediate, 25% advanced
5. **Include piped commands** where natural (at least 50 examples):
   - `find ... | grep ...`
   - `find ... | sort | uniq`
   - `find ... | head/tail/wc -l`
   - `find ... | awk ...`
   - Other realistic pipelines
6. **Real-world scenarios** with realistic file paths, usernames, hostnames, IPs
7. **Vary argument values** — don't reuse the same filenames/paths/patterns

## Detailed Flag Reference (from project flag table)

- `-maxdepth`: Descend at most N levels of directories below the starting-points
- `-name`: Match filename against shell glob pattern
- `-type`: Match by file type (f=file, d=directory, l=symlink, etc.)
- `-size`: Match by file size with optional suffix (c=bytes, k=KiB, M=MiB, G=GiB)
- `-user`: Match files owned by specified user name or UID
- `-perm`: Match files with specified permission bits
- `-mtime`: Match by modification time in days (+N=more than, -N=less than, N=exactly)
- `-newer`: Match files modified more recently than the given reference file
- `-exec`: Execute a command on each matched file; terminated by ';' or '+' for batch
- `-print0`: Print full filename followed by NUL character instead of newline
- `-regextype`: Set regex dialect for -regex (posix-basic, posix-extended, emacs, etc.)

## Additional Flags to Cover

-name -iname -type -size -mtime -atime -ctime -newer -user -group -perm -exec -print0 -maxdepth -mindepth -empty -delete -regex -path -not -or -and

## Example Output Lines

```jsonl
{"messages": [{"role": "system", "content": "ubuntu 24.04 bash non-root"}, {"role": "user", "content": "<natural language request for find>"}, {"role": "assistant", "content": "<correct find command>"}]}
{"messages": [{"role": "system", "content": "fedora 39 zsh non-root"}, {"role": "user", "content": "<different phrasing>"}, {"role": "assistant", "content": "<find with different flags>"}]}
```

## Quality Checklist

- [ ] Exactly 500 lines of valid JSONL
- [ ] Every flag/subcommand appears at least 5 times
- [ ] No duplicate user+assistant pairs
- [ ] Mix of simple, intermediate, and advanced examples
- [ ] Realistic file paths, users, hosts, IPs (not placeholder junk)
- [ ] System contexts distributed across distros/shells/privileges
- [ ] Natural language is diverse (not just "use find to...")
