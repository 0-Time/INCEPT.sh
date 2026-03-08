# 076 — `curl` — TIER 2 — BENCHMARK REINFORCEMENT

> **200 examples** | This command PASSES the benchmark but needs reinforcement to maintain accuracy.

## Task

Generate exactly **200** training examples for the **`curl`** command in ChatML JSONL format.

## Command Overview

`curl` — Transfer data from or to server
**Category:** Networking

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
   - `curl ... | grep ...`
   - `curl ... | sort | uniq`
   - `curl ... | head/tail/wc -l`
   - `curl ... | awk ...`
   - Other realistic pipelines
6. **Real-world scenarios** with realistic file paths, usernames, hostnames, IPs
7. **Vary argument values** — don't reuse the same filenames/paths/patterns

## Detailed Flag Reference (from project flag table)

- `-o`: Write output to the specified file instead of stdout
- `-L`: Follow HTTP 3xx redirects automatically
- `-s`: Suppress progress meter and error messages
- `-k`: Allow connections to TLS sites without certificate validation
- `--fail-with-body`: Return error exit code on HTTP errors but still output the response body
- `--retry`: Retry the request N times on transient errors
- `-X`: Specify the HTTP method to use (GET, POST, PUT, DELETE, etc.)

## Additional Flags to Cover

-o -O -L -s -S -v -k -X -H -d -F -u -T -b -c -e -A -x --output --remote-name --location --silent --show-error --verbose --insecure --request --header --data --form --user --upload-file --cookie --cookie-jar --referer --user-agent --proxy --retry --max-time --connect-timeout -w --write-out -I --head --compressed --cert --key

## Example Output Lines

```jsonl
{"messages": [{"role": "system", "content": "ubuntu 24.04 bash non-root"}, {"role": "user", "content": "<natural language request for curl>"}, {"role": "assistant", "content": "<correct curl command>"}]}
{"messages": [{"role": "system", "content": "fedora 39 zsh non-root"}, {"role": "user", "content": "<different phrasing>"}, {"role": "assistant", "content": "<curl with different flags>"}]}
```

## Quality Checklist

- [ ] Exactly 200 lines of valid JSONL
- [ ] Every flag/subcommand appears at least 3 times
- [ ] No duplicate user+assistant pairs
- [ ] Mix of simple, intermediate, and advanced examples
- [ ] Realistic file paths, users, hosts, IPs (not placeholder junk)
- [ ] System contexts distributed across distros/shells/privileges
- [ ] Natural language is diverse (not just "use curl to...")
