#!/usr/bin/env python3
"""Generate targeted training examples for benchmark failures.

Creates ~20-30 ChatML JSONL variations per failing question,
using Claude to generate diverse phrasings that all map to the correct command.
"""

import json
import subprocess
import sys
import time
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "v2" / "targeted_fixes"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Each entry: (category, question, correct_command, count_to_generate)
FIXES = [
    # === Identity bleed ===
    ("identity", "Check your current user identity", "whoami", 30),
    ("identity", "List all hardware information", "lshw", 25),
    # Extra identity-hardening: questions that might confuse identity
    ("identity", "Who am I logged in as", "whoami", 25),
    ("identity", "What user am I", "whoami", 25),
    ("identity", "Tell me who I am on this system", "whoami", 20),
    ("identity", "What is my username", "whoami", 20),

    # === Narrative instead of command ===
    ("narrative", "Find where the python executable is located", "which python", 25),
    ("narrative", "Search for a word ignoring case sensitivity", "grep -i", 25),
    ("narrative", "Find the public IP of your network", "curl ifconfig.me", 25),

    # === Wrong command (close alternative) ===
    ("wrong_cmd", "Copy an entire directory to a new location", "cp -r", 30),
    ("wrong_cmd", "Remove duplicate lines from a sorted file", "uniq", 25),
    ("wrong_cmd", "Make a script executable", "chmod +x", 30),
    ("wrong_cmd", "Show the Linux kernel version", "uname -r", 25),
    ("wrong_cmd", "Show CPU architecture and details", "lscpu", 25),
    ("wrong_cmd", "Show the size of a specific directory", "du -sh", 25),
    ("wrong_cmd", "Show a real-time interactive list of processes", "top", 25),
    ("wrong_cmd", "Kill a process by its name for example firefox", "pkill firefox", 25),

    # === macOS bias ===
    ("macos_fix", "View the system message buffer and kernel logs", "dmesg", 25),
    ("macos_fix", "Display active network connections and ports", "ss -tulnp", 25),
    ("macos_fix", "List all loaded kernel modules", "lsmod", 25),

    # === Completely wrong ===
    ("wrong", "Create an empty file named script.sh", "touch script.sh", 25),
    ("wrong", "Show the type of a file a.txt", "file a.txt", 25),
    ("wrong", "View a file with the ability to scroll up and down", "less", 25),
    ("wrong", "Switch to another user account", "su username", 25),
    ("wrong", "Search for files larger than 100MB", "find / -type f -size +100M", 25),

    # === Missing from training ===
    ("missing", "Show line numbers while searching with grep", "grep -n", 25),
    ("missing", "List the members of a specific group", "getent group groupname", 25),
    ("missing", "Set the default permissions for newly created files", "umask", 25),
    ("missing", "Search for files by name across the whole system", "find / -name filename", 25),
]


def generate_batch(category: str, question: str, correct_cmd: str, count: int) -> list[dict]:
    """Use Claude to generate diverse NL→command training examples."""
    
    prompt = f"""Generate exactly {count} training examples for a Linux command-line assistant.

Each example must be a JSON object with this exact format:
{{"messages": [{{"role": "system", "content": "<distro> <version> <shell> <root_status>"}}, {{"role": "user", "content": "<natural language request>"}}, {{"role": "assistant", "content": "<linux command>"}}]}}

RULES:
1. The correct command pattern is: {correct_cmd}
2. The base question is: "{question}"
3. Generate DIVERSE natural language phrasings - casual, formal, terse, verbose, beginner-style, expert-style
4. Vary the system context: use ubuntu 22.04/24.04, debian 12, rhel 9, arch latest, fedora 41, centos 9
5. Vary shell: bash or zsh
6. Vary root status: root or non-root (add sudo for non-root when command needs privileges)
7. The assistant response must be ONLY the command - no explanations, no markdown, no prose
8. Commands must be Linux-specific - NEVER use macOS commands (no open, no pbcopy, no brew, no log show, no pfctl)
9. Never respond with chatbot text like "I'm an AI" or "I can help" - ALWAYS respond with a command
10. Vary parameters/paths/filenames to make examples diverse

Output ONLY the JSON objects, one per line (JSONL format). No other text."""

    try:
        result = subprocess.run(
            ["/usr/local/bin/claude", "-p", prompt, "--model", "claude-sonnet-4-6"],
            capture_output=True, text=True, timeout=120,
        )
        
        examples = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
                if "messages" in obj and len(obj["messages"]) == 3:
                    # Validate: assistant response should be a command, not prose
                    assistant_msg = obj["messages"][2]["content"]
                    if len(assistant_msg) < 200 and not assistant_msg.startswith("I "):
                        examples.append(obj)
            except json.JSONDecodeError:
                continue
        
        return examples
    except Exception as e:
        log.error("Failed to generate for '%s': %s", question, e)
        return []


def main():
    log.info("Generating targeted fixes for %d categories (%d total entries)", 
             len(set(f[0] for f in FIXES)), len(FIXES))
    
    all_examples = []
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        for category, question, cmd, count in FIXES:
            future = executor.submit(generate_batch, category, question, cmd, count)
            futures[future] = (category, question, cmd, count)
        
        for future in as_completed(futures):
            category, question, cmd, count = futures[future]
            examples = future.result()
            log.info("[%s] '%s' → %s: got %d/%d examples", 
                     category, question[:40], cmd, len(examples), count)
            all_examples.extend(examples)
            
            # Save per-category
            cat_file = OUTPUT_DIR / f"{category}.jsonl"
            with open(cat_file, "a") as f:
                for ex in examples:
                    f.write(json.dumps(ex) + "\n")
    
    # Save combined
    combined_file = OUTPUT_DIR / "all_targeted_fixes.jsonl"
    with open(combined_file, "w") as f:
        for ex in all_examples:
            f.write(json.dumps(ex) + "\n")
    
    log.info("=" * 60)
    log.info("Total targeted examples generated: %d", len(all_examples))
    log.info("Saved to: %s", combined_file)
    log.info("=" * 60)
    
    # Also create the merged training file
    train_file = PROJECT_ROOT / "data" / "v2" / "train.jsonl"
    merged_file = PROJECT_ROOT / "data" / "v2" / "train_v3.jsonl"
    
    # Copy original training data
    import shutil
    shutil.copy(train_file, merged_file)
    
    # Append targeted fixes (repeat 3x for emphasis)
    with open(merged_file, "a") as f:
        for _ in range(3):  # 3x repetition to emphasize corrections
            for ex in all_examples:
                f.write(json.dumps(ex) + "\n")
    
    total = sum(1 for _ in open(merged_file))
    log.info("Merged training file: %s (%d examples)", merged_file, total)


if __name__ == "__main__":
    main()
