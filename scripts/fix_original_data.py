#!/usr/bin/env python3
"""
Fix quality issues in original 28,154 training examples.
Resume-safe: saves after every batch.
"""
from __future__ import annotations
import json, subprocess, random, time, re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_FILE   = PROJECT_ROOT / "data" / "v2" / "train.jsonl"
FIXED_FILE   = PROJECT_ROOT / "data" / "v2" / "train_fixed.jsonl"
PROGRESS_FILE= PROJECT_ROOT / "data" / "v2" / ".fix_progress.json"
ORIGINAL_COUNT = 28154

MACOS_TO_LINUX = [
    "ubuntu 24.04 bash non-root","ubuntu 22.04 bash non-root",
    "debian 12 bash non-root","fedora 40 bash non-root","arch latest bash non-root",
]

PKG_FIX = {
    ("debian",  r'\byum\b'):      "apt-get",
    ("debian",  r'\bpacman\b'):   "apt-get",
    ("debian",  r'\bdnf\b'):      "apt-get",
    ("rhel",    r'\bapt-get\b'):  "yum",
    ("rhel",    r'\bpacman\b'):   "yum",
    ("fedora",  r'\bapt-get\b'):  "dnf",
    ("fedora",  r'\bpacman\b'):   "dnf",
    ("arch",    r'\bapt-get\b'):  "pacman -S",
    ("arch",    r'\byum\b'):      "pacman -S",
    ("arch",    r'\bdnf\b'):      "pacman -S",
}

def distro_family(s):
    s = s.lower()
    if any(x in s for x in ["ubuntu","debian","kali","mint"]): return "debian"
    if any(x in s for x in ["centos","rhel","rocky","alma"]): return "rhel"
    if "fedora" in s: return "fedora"
    if "arch" in s: return "arch"
    if "macos" in s or "mac os" in s: return "macos"
    return "other"

def fix_mismatch(sys_ctx, cmd):
    fam = distro_family(sys_ctx)
    for (f, pat), replacement in PKG_FIX.items():
        if fam == f and re.search(pat, cmd):
            cmd = re.sub(pat, replacement, cmd)
    return cmd

def convert_macos(sys_ctx, cmd):
    new_ctx = random.choice(MACOS_TO_LINUX)
    cmd = re.sub(r'\bbrew install\b', 'apt-get install -y', cmd)
    cmd = re.sub(r'\bbrew\b', 'apt-get', cmd)
    cmd = re.sub(r'\bpfctl\b', 'iptables', cmd)
    cmd = re.sub(r'\blaunchctl\b', 'systemctl', cmd)
    cmd = re.sub(r'\bopen -a\b', 'xdg-open', cmd)
    cmd = re.sub(r'/usr/local/bin/', '/usr/bin/', cmd)
    return new_ctx, cmd

def rewrite_batch(examples):
    items = "\n".join(
        f"{i+1}. CMD={e[1]} | CURRENT_Q={e[0]}"
        for i, e in enumerate(examples)
    )
    prompt = (f"Rewrite these {len(examples)} short Linux command queries into natural human language.\n"
              f"Output ONLY numbered rewrites, one per line. 5-15 words each.\n"
              f"Vary style: imperative, question, casual. Keep same intent.\n\n"
              f"{items}\n\nOutput {len(examples)} numbered rewrites:")
    try:
        r = subprocess.run(
            ["/usr/local/bin/claude","-p",prompt,"--model","claude-sonnet-4-6"],
            capture_output=True, text=True, timeout=60
        )
        lines = [l.strip() for l in r.stdout.strip().split('\n') if l.strip()]
        rewrites = []
        for line in lines:
            m = re.match(r'^\d+[\.\)]\s*(.+)$', line)
            if m: rewrites.append(m.group(1).strip())
        if len(rewrites) == len(examples): return rewrites
    except Exception as e:
        print(f"  rewrite error: {e}", flush=True)
    return [e[0] for e in examples]  # fallback

def main():
    print("="*60, flush=True)
    print("INCEPT Data Quality Fixer (resume-safe)", flush=True)
    print("="*60, flush=True)

    # Load progress
    progress = json.loads(PROGRESS_FILE.read_text()) if PROGRESS_FILE.exists() else {}
    rewrites_done = progress.get("rewrites_done", 0)
    phase = progress.get("phase", "fix")  # fix or rewrite

    # Load all lines
    all_lines = [l.strip() for l in open(TRAIN_FILE) if l.strip()]
    original_lines = all_lines[:ORIGINAL_COUNT]
    generated_lines = all_lines[ORIGINAL_COUNT:]

    # Phase 1: Apply rule-based fixes (instant, idempotent)
    if phase == "fix":
        print("Phase 1: Applying rule-based fixes...", flush=True)
        macos_n = mismatch_n = terse_n = 0
        fixed = []
        terse_indices = []

        for i, line in enumerate(original_lines):
            obj = json.loads(line)
            m = obj["messages"]
            sys_ctx, user, cmd = m[0]["content"], m[1]["content"], m[2]["content"]

            if "macos" in sys_ctx.lower() or "mac os" in sys_ctx.lower():
                sys_ctx, cmd = convert_macos(sys_ctx, cmd)
                macos_n += 1

            cmd = fix_mismatch(sys_ctx, cmd)
            if cmd != m[2]["content"]: mismatch_n += 1

            if len(user.split()) <= 2:
                terse_indices.append(i)
                terse_n += 1

            fixed.append({"messages":[
                {"role":"system","content":sys_ctx},
                {"role":"user","content":user},
                {"role":"assistant","content":cmd}
            ]})

        print(f"  macOS fixed:      {macos_n:,}", flush=True)
        print(f"  Mismatches fixed: {mismatch_n:,}", flush=True)
        print(f"  Terse NL found:   {terse_n:,}", flush=True)

        # Save intermediate fixed file
        with open(FIXED_FILE, 'w') as f:
            for obj in fixed:
                f.write(json.dumps(obj) + '\n')
            for line in generated_lines:
                f.write(line + '\n')

        progress = {"phase":"rewrite","terse_indices":terse_indices,"rewrites_done":0}
        PROGRESS_FILE.write_text(json.dumps(progress))
        print("Phase 1 done. Starting Phase 2: AI rewrites...", flush=True)

    else:
        terse_indices = progress["terse_indices"]
        rewrites_done = progress["rewrites_done"]
        print(f"Resuming Phase 2: rewrites ({rewrites_done}/{len(terse_indices)} done)", flush=True)

    # Phase 2: AI rewrites for terse NL
    terse_indices = progress["terse_indices"]
    rewrites_done = progress.get("rewrites_done", 0)
    total_terse = len(terse_indices)
    batch_size = 30

    # Load current fixed file
    fixed_lines = [l.strip() for l in open(FIXED_FILE) if l.strip()]

    # Process remaining batches
    remaining_indices = terse_indices[rewrites_done:]
    batches = [remaining_indices[i:i+batch_size] for i in range(0, len(remaining_indices), batch_size)]
    total_batches = len(batches)

    for b_idx, batch in enumerate(batches):
        examples = []
        for idx in batch:
            obj = json.loads(fixed_lines[idx])
            m = obj["messages"]
            examples.append((m[1]["content"], m[2]["content"]))

        rewrites = rewrite_batch(examples)

        for j, idx in enumerate(batch):
            obj = json.loads(fixed_lines[idx])
            if j < len(rewrites):
                obj["messages"][1]["content"] = rewrites[j]
            fixed_lines[idx] = json.dumps(obj)

        rewrites_done += len(batch)
        done_total = progress.get("rewrites_done", 0) + rewrites_done - (rewrites_done - len(batch))

        # Save after every batch
        with open(FIXED_FILE, 'w') as f:
            for line in fixed_lines:
                f.write(line + '\n')

        progress["rewrites_done"] = rewrites_done
        PROGRESS_FILE.write_text(json.dumps(progress))

        current_batch = b_idx + 1
        print(f"  Batch {current_batch}/{total_batches}: +{len(batch)} rewrites ({rewrites_done}/{total_terse} done)", flush=True)
        time.sleep(0.2)

    # Cleanup progress file
    PROGRESS_FILE.unlink(missing_ok=True)
    total = sum(1 for l in open(FIXED_FILE) if l.strip())
    print(f"\n✓ Done! {total:,} examples in train_fixed.jsonl", flush=True)
    print("Run: cp data/v2/train_fixed.jsonl data/v2/train.jsonl", flush=True)

if __name__ == "__main__":
    main()
