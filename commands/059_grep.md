# 059 — `grep` — TIER 2 — BENCHMARK REINFORCEMENT

> **200 examples** | This command PASSES the benchmark but needs reinforcement to maintain accuracy.

## Task

Generate exactly **200** training examples for the **`grep`** command in ChatML JSONL format.

## Command Overview

`grep` — Search text using patterns
**Category:** Text Processing

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

1. **200 unique examples** — NO duplicate (user, assistant) pairs
2. **Cover EVERY flag/argument** listed below — each in at least 3 examples
3. **Diverse natural language phrasing:**
   - Imperative: "List all files in /tmp"
   - Question: "How do I see hidden files?"
   - Casual: "show me whats in this folder"
   - Formal: "Display the contents of the /etc directory with detailed permissions"
   - Terse: "files in /var"
   - Verbose: "I need to list all files including hidden ones with human-readable sizes"
4. **Difficulty distribution:** 40% basic, 35% intermediate, 25% advanced
5. **Include piped commands** where natural (at least 20 examples):
   - `grep ... | grep ...`
   - `grep ... | sort | uniq`
   - `grep ... | head/tail/wc -l`
   - `grep ... | awk ...`
   - Other realistic pipelines
6. **Real-world scenarios** with realistic file paths, usernames, hostnames, IPs
7. **Vary argument values** — don't reuse the same filenames/paths/patterns

## Detailed Flag Reference (from project flag table)

- `-P`: Interpret pattern as a Perl-compatible regular expression (PCRE)
- `-E`: Interpret pattern as an extended regular expression (ERE)
- `-r`: Read all files under each directory recursively
- `-n`: Prefix each line of output with the 1-based line number within its file
- `-i`: Perform case-insensitive matching
- `-c`: Print only the count of matching lines per file
- `-l`: Print only the names of files containing matches
- `-Z`: Output NUL byte after each filename instead of newline
- `--include`: Search only files matching the given glob pattern
- `--exclude-dir`: Skip directories matching the given glob pattern during recursive search
- `--color`: Surround matching strings with ANSI color escape sequences (auto/always/never)

## Additional Flags to Cover

-i -v -r -R -n -c -l -L -w -o -E -P -F -A -B -C -f -e -m -q -x -z -Z -h -H --include --exclude --exclude-dir --color --count --files-with-matches --only-matching --perl-regexp --extended-regexp --fixed-strings --word-regexp --line-regexp --context --after-context --before-context --max-count --quiet --recursive --no-filename --with-filename

## Example Output Lines

```jsonl
{"messages": [{"role": "system", "content": "ubuntu 24.04 bash non-root"}, {"role": "user", "content": "<natural language request for grep>"}, {"role": "assistant", "content": "<correct grep command>"}]}
{"messages": [{"role": "system", "content": "fedora 39 zsh non-root"}, {"role": "user", "content": "<different phrasing>"}, {"role": "assistant", "content": "<grep with different flags>"}]}
```

## Quality Checklist

- [ ] Exactly 200 lines of valid JSONL
- [ ] Every flag/subcommand appears at least 3 times
- [ ] No duplicate user+assistant pairs
- [ ] Mix of simple, intermediate, and advanced examples
- [ ] Realistic file paths, users, hosts, IPs (not placeholder junk)
- [ ] System contexts distributed across distros/shells/privileges
- [ ] Natural language is diverse (not just "use grep to...")
