# 384 — `dos2unix` — TIER 4 — NICHE/SPECIALIZED

> **20 examples** | This command is specialized/niche. Minimal coverage to establish basic competence.

## Task

Generate exactly **20** training examples for the **`dos2unix`** command in ChatML JSONL format.

## Command Overview

`dos2unix` — Convert line endings DOS to Unix
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

1. **20 unique examples** — NO duplicate (user, assistant) pairs
2. **Cover EVERY flag/argument** listed below — each in at least 3 examples
3. **Diverse natural language phrasing:**
   - Imperative: "List all files in /tmp"
   - Question: "How do I see hidden files?"
   - Casual: "show me whats in this folder"
   - Formal: "Display the contents of the /etc directory with detailed permissions"
   - Terse: "files in /var"
   - Verbose: "I need to list all files including hidden ones with human-readable sizes"
4. **Difficulty distribution:** 40% basic, 35% intermediate, 25% advanced
5. **Include a few piped commands** where natural
6. **Real-world scenarios** with realistic file paths, usernames, hostnames, IPs
7. **Vary argument values** — don't reuse the same filenames/paths/patterns

## Key Flags and Arguments to Cover

-k -n -q --keepdate --newfile --quiet

Cover ALL documented flags and options for `dos2unix`. Think through the full man page.

## Example Output Lines

```jsonl
{"messages": [{"role": "system", "content": "ubuntu 24.04 bash non-root"}, {"role": "user", "content": "<natural language request for dos2unix>"}, {"role": "assistant", "content": "<correct dos2unix command>"}]}
{"messages": [{"role": "system", "content": "fedora 39 zsh non-root"}, {"role": "user", "content": "<different phrasing>"}, {"role": "assistant", "content": "<dos2unix with different flags>"}]}
```

## Quality Checklist

- [ ] Exactly 20 lines of valid JSONL
- [ ] Every flag/subcommand appears at least 3 times
- [ ] No duplicate user+assistant pairs
- [ ] Mix of simple, intermediate, and advanced examples
- [ ] Realistic file paths, users, hosts, IPs (not placeholder junk)
- [ ] System contexts distributed across distros/shells/privileges
- [ ] Natural language is diverse (not just "use dos2unix to...")
