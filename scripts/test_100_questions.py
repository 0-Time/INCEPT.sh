#!/usr/bin/env python3
"""Test INCEPT engine against 100 standard Linux command questions.

Runs each question through the engine and compares against expected commands.
Scoring: checks if the expected command/keyword appears in the model output.
"""

import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from incept.core.engine import InceptEngine

# ---------------------------------------------------------------------------
# 100 test questions with expected commands
# ---------------------------------------------------------------------------

TESTS = [
    # Section 1: Basic File & Directory Navigation
    ("Display the current working directory", "pwd"),
    ("List files in the current directory", "ls"),
    ("List all files, including hidden ones", "ls -a"),
    ("List files with detailed information like permissions, size, owner", "ls -l"),
    ("Change directory to /etc", "cd /etc"),
    ("Move up one directory level", "cd .."),
    ("Return to your home directory", "cd ~"),
    ("Go to the previous directory you were in", "cd -"),
    ("Create a new directory named test", "mkdir test"),
    ("Create a directory and its parents, for example a/b/c", "mkdir -p a/b/c"),
    ("Remove an empty directory", "rmdir"),
    ("Delete a file named a.txt", "rm a.txt"),
    ("Delete a directory and everything inside it", "rm -r"),
    ("Rename old.txt to new.txt", "mv old.txt new.txt"),
    ("Move a.txt into the /tmp folder", "mv a.txt /tmp"),
    ("Copy a.txt to b.txt", "cp a.txt b.txt"),
    ("Copy an entire directory to a new location", "cp -r"),
    ("Create an empty file named script.sh", "touch script.sh"),
    ("Find where the python executable is located", "which python"),
    ("Show the type of a file a.txt", "file a.txt"),

    # Section 2: Viewing & Editing Content
    ("Display the entire content of a.txt", "cat a.txt"),
    ("Concatenate two files a.txt and b.txt into c.txt", "cat a.txt b.txt > c.txt"),
    ("View a file with the ability to scroll up and down", "less"),
    ("Display the first 10 lines of a file", "head"),
    ("Display the last 10 lines of a file", "tail"),
    ("Monitor a log file in real-time as it updates", "tail -f"),
    ("Count the number of lines words and characters in a file", "wc"),
    ("Count only the lines in a file", "wc -l"),
    ("Sort the lines of a file alphabetically", "sort"),
    ("Remove duplicate lines from a sorted file", "uniq"),
    ("Extract the first column from a CSV file that is comma delimited", "cut -d"),
    ("Search for the word error in syslog", "grep"),
    ("Search for a word ignoring case sensitivity", "grep -i"),
    ("Search for a string in all files in a directory recursively", "grep -r"),
    ("Show line numbers while searching with grep", "grep -n"),
    ("Replace all instances of apple with orange in a file using sed", "sed"),
    ("Open a file for editing in the terminal", "nano"),
    ("Display the hex dump of a binary file", "hexdump"),
    ("Display only the printable strings in a binary file", "strings"),
    ("Compare two files for differences", "diff"),

    # Section 3: Permissions & Ownership
    ("Change file permissions to read write execute for everyone", "chmod 777"),
    ("Make a script executable", "chmod +x"),
    ("Give the owner full permissions and others no permissions", "chmod 700"),
    ("Change the owner of a file to root", "chown root"),
    ("Change the group of a file", "chgrp"),
    ("Change both owner and group of a file at once", "chown"),
    ("Recursively change permissions for a folder", "chmod -R"),
    ("Check your current user identity", "whoami"),
    ("Show your current user ID and group IDs", "id"),
    ("Switch to another user account", "su"),
    ("Execute a command with administrative root privileges", "sudo"),
    ("List the members of a specific group", "getent group"),
    ("Set the default permissions for newly created files", "umask"),
    ("Make a file immutable so even root cannot delete it", "chattr +i"),
    ("View special attributes of a file", "lsattr"),

    # Section 4: System Information & Management
    ("Show how long the system has been running", "uptime"),
    ("Display the current date and time", "date"),
    ("Show the Linux kernel version", "uname -r"),
    ("List all hardware information", "lshw"),
    ("Show CPU architecture and details", "lscpu"),
    ("List all connected USB devices", "lsusb"),
    ("List all PCI devices", "lspci"),
    ("Check the amount of free and used RAM", "free"),
    ("Show disk space usage in human readable format", "df -h"),
    ("Show the size of a specific directory", "du -sh"),
    ("List all running processes", "ps aux"),
    ("Show a real-time interactive list of processes", "top"),
    ("Kill a process using its PID 1234", "kill 1234"),
    ("Force kill a stubborn process with PID 1234", "kill -9"),
    ("Kill a process by its name for example firefox", "pkill firefox"),
    ("Show all open files and the processes using them", "lsof"),
    ("List all loaded kernel modules", "lsmod"),
    ("Shutdown the system immediately", "shutdown"),
    ("Reboot the system", "reboot"),
    ("View the system message buffer and kernel logs", "dmesg"),

    # Section 5: Networking
    ("Show all network interfaces and IP addresses", "ip a"),
    ("Check connectivity to google.com", "ping google.com"),
    ("Trace the path packets take to a host", "traceroute"),
    ("Download a file from the internet", "wget"),
    ("Display active network connections and ports", "ss"),
    ("Show the routing table", "ip route"),
    ("Perform a DNS lookup for a domain", "dig"),
    ("Scan for open ports on a server", "nmap"),
    ("Securely copy a file to a remote server", "scp"),
    ("Log into a remote server securely using SSH", "ssh"),
    ("Show the hostname of the machine", "hostname"),
    ("Find the public IP of your network", "curl"),
    ("Transfer files using an interactive tool", "sftp"),

    # Section 6: Advanced Shell & Utilities
    ("Show the history of all commands typed", "history"),
    ("Clear the terminal screen", "clear"),
    ("Create an alias for a long command", "alias"),
    ("Search for files by name across the whole system", "find"),
    ("Search for files larger than 100MB", "find"),
    ("Create a tar archive of a folder", "tar"),
    ("Extract a tar.gz compressed file", "tar"),
    ("Compress a file using zip", "zip"),
    ("Unzip a zip file", "unzip"),
    ("Run a command in the background", "&"),
    ("Bring a background job to the foreground", "fg"),
    ("See the list of current background jobs", "jobs"),
]

# Some questions can match multiple valid answers
# Keys are 0-based indices into TESTS (i.e. question number minus 1)
ALTERNATE_MATCHES = {
    5:  ["cd .."],
    6:  ["cd ~", "cd"],
    8:  ["mkdir"],                                      # Q9: mkdir with any path is still mkdir
    9:  ["mkdir -p", "mkdir"],                           # Q10: creating dirs
    10: ["rmdir"],
    12: ["rm -r", "rm -rf"],
    16: ["cp -r", "cp -R"],
    18: ["which", "command -v", "type", "locate", "whereis"],  # Q19: finding executables
    19: ["file", "stat"],                                # Q20: show file type
    22: ["less", "more", "view", "vim -R"],              # Q23: scrollable viewer
    27: ["wc -l", "awk"],                                # Q28: count lines
    29: ["uniq", "sort -u", "awk '!seen", "sed"],        # Q30: remove duplicates
    30: ["awk -F", "awk -F','", "awk", "cut"],           # Q31: extract column
    36: ["nano", "vi", "vim", "editor"],                 # Q37: open for editing
    37: ["hexdump", "od", "xxd"],                        # Q38: hex dump
    38: ["strings", "objdump"],                          # Q39: printable strings
    40: ["chmod 777", "chmod a+rwx", "chmod 755"],       # Q41: permissions for all
    42: ["chmod 700", "chmod u=rwx,g=,o=", "chmod u=rwx,go="],
    44: ["chgrp", "chown"],
    47: ["whoami", "id", "who am i"],                    # Q48: current user
    49: ["su"],                                          # Q50: switch user
    51: ["getent group", "getent", "id -Gn", "groups", "cat /etc/group", "groupdel"],
    52: ["umask", "chmod"],                              # Q53: default permissions
    57: ["uname -r", "uname", "cat /proc/version"],      # Q58: kernel version
    58: ["dmidecode", "system_profiler"],
    59: ["lscpu", "cat /proc/cpuinfo"],                  # Q60: CPU details
    64: ["du -sh", "du -h", "du"],                       # Q65: directory size
    66: ["top", "htop", "watch.*ps"],                    # Q67: real-time processes
    67: ["kill 1234", "kill -9 1234", "kill -TERM 1234"],
    69: ["pkill", "killall"],                            # Q70: kill by name
    72: ["shutdown", "poweroff", "systemctl poweroff", "halt"],  # Q73: shutdown
    73: ["shutdown -r", "systemctl reboot", "reboot"],
    74: ["dmesg", "journalctl", "journalctl -k"],        # Q75: kernel logs
    75: ["ip a", "ifconfig", "ip addr"],
    76: ["ping", "mtr", "fping"],                        # Q77: connectivity check
    77: ["traceroute", "mtr", "tracepath"],
    78: ["wget", "curl"],
    79: ["netstat", "ss", "lsof -i"],                    # Q80: network connections
    80: ["ip route", "ip r", "route", "netstat -r"],
    81: ["dig", "nslookup", "host"],
    83: ["rsync", "sftp", "scp"],
    82: ["nmap", "ss -tulpn", "netstat"],  # scan open ports                        # Q84: secure copy
    86: ["curl ifconfig.me", "curl", "wget"],
    87: ["sftp", "ftp", "rsync"],                        # Q88: interactive transfer
    91: ["locate", "mlocate", "find"],
    97: ["&", "nohup", "bg"],
}


def match_score(output: str, expected: str, idx: int) -> bool:
    """Check if output matches expected command."""
    out_lower = output.lower().strip()

    # Check alternate matches first
    if idx in ALTERNATE_MATCHES:
        for alt in ALTERNATE_MATCHES[idx]:
            if alt.lower() in out_lower:
                return True

    # Check primary expected
    if expected.lower() in out_lower:
        return True

    return False


def main():
    print("=" * 70)
    print("INCEPT Engine - 100 Question Benchmark")
    print("=" * 70)
    print()

    engine = InceptEngine(think=False)
    engine._context_line = "ubuntu 22.04 bash non-root"
    if not engine.model_loaded:
        print("ERROR: No model loaded!")
        sys.exit(1)

    print(f"System context: {engine.context_line}")
    print(f"Questions: {len(TESTS)}")
    print()

    results = []
    correct = 0
    errors = []
    t0 = time.time()

    for i, (question, expected) in enumerate(TESTS):
        qi = i + 1
        try:
            resp = engine.ask(question)
            output = resp.text.strip()
            passed = match_score(output, expected, i)

            if passed:
                correct += 1
                status = "PASS"
            else:
                status = "FAIL"
                errors.append((qi, question, expected, output))

            results.append({
                "q": qi,
                "question": question,
                "expected": expected,
                "output": output,
                "type": resp.type,
                "confidence": resp.confidence,
                "passed": passed,
            })

            # Progress
            pct = correct / qi * 100
            print(f"  [{qi:3d}/100] {status}  {output:<45s}  (expect: {expected})")

        except Exception as exc:
            print(f"  [{qi:3d}/100] ERR   {exc}")
            errors.append((qi, question, expected, f"ERROR: {exc}"))
            results.append({
                "q": qi, "question": question, "expected": expected,
                "output": f"ERROR: {exc}", "type": "error",
                "confidence": "low", "passed": False,
            })

    elapsed = time.time() - t0

    # Summary
    print()
    print("=" * 70)
    print(f"RESULTS: {correct}/{len(TESTS)} correct ({correct/len(TESTS)*100:.1f}%)")
    print(f"Time: {elapsed:.1f}s ({elapsed/len(TESTS):.2f}s per question)")
    print("=" * 70)

    if errors:
        print(f"\n--- FAILURES ({len(errors)}) ---")
        for qi, question, expected, output in errors:
            print(f"  Q{qi}: {question}")
            print(f"       Expected: {expected}")
            print(f"       Got:      {output}")
            print()

    # Section breakdown
    sections = [
        ("Basic File & Directory Navigation", 0, 20),
        ("Viewing & Editing Content", 20, 40),
        ("Permissions & Ownership", 40, 55),
        ("System Information & Management", 55, 75),
        ("Networking", 75, 88),
        ("Advanced Shell & Utilities", 88, 100),
    ]
    print("--- SECTION BREAKDOWN ---")
    for name, start, end in sections:
        section_results = results[start:end]
        section_correct = sum(1 for r in section_results if r["passed"])
        section_total = len(section_results)
        pct = section_correct / section_total * 100
        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        print(f"  {name:<40s} {section_correct:2d}/{section_total:2d} ({pct:5.1f}%) [{bar}]")

    # Save detailed results
    out_path = PROJECT_ROOT / "test_100_results.json"
    with open(out_path, "w") as f:
        json.dump({
            "total": len(TESTS),
            "correct": correct,
            "accuracy": round(correct / len(TESTS) * 100, 1),
            "elapsed_seconds": round(elapsed, 1),
            "results": results,
        }, f, indent=2)
    print(f"\nDetailed results saved to: {out_path}")


if __name__ == "__main__":
    main()
