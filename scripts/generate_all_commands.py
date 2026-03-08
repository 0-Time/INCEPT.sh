#!/usr/bin/env python3
"""INCEPT Phase 1 — Parallel data generator (3 workers). Resume-safe."""
from __future__ import annotations
import json, subprocess, time, random, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = PROJECT_ROOT / "commands"
OUTPUT_DIR   = PROJECT_ROOT / "data" / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WORKERS = 3
DISTROS = ["ubuntu 24.04","ubuntu 22.04","fedora 39","fedora 40",
           "debian 12","centos 9","rhel 9","arch latest","opensuse 15.5","sles 15"]
SHELLS = ["bash"]*8 + ["zsh"]*2
PRIVS  = ["root"]*3 + ["non-root"]*7
_lock = threading.Lock()

def log(*a):
    with _lock:
        print(*a, flush=True)

def valid(line):
    try:
        obj = json.loads(line)
        m = obj.get("messages", [])
        return (len(m)==3 and m[0]["role"]=="system" and m[1]["role"]=="user"
                and m[2]["role"]=="assistant" and len(m[2]["content"].strip())>1)
    except: return False

def load_file(path):
    lines, pairs = [], set()
    if path.exists():
        for line in path.read_text().split('\n'):
            line = line.strip()
            if line and valid(line):
                try:
                    m = json.loads(line)["messages"]
                    k = (m[1]["content"].lower().strip(), m[2]["content"].lower().strip())
                    if k not in pairs:
                        pairs.add(k); lines.append(line)
                except: pass
    return lines, pairs

def extract(output):
    valid_lines, seen = [], set()
    for line in output.split('\n'):
        line = line.strip()
        if not line or line.startswith('`'): continue
        if line.startswith('{') and line.endswith('}') and valid(line):
            try:
                m = json.loads(line)["messages"]
                k = (m[1]["content"].lower().strip(), m[2]["content"].lower().strip())
                if k not in seen:
                    seen.add(k); valid_lines.append(line)
            except: pass
    return valid_lines

def generate(md_path, target):
    key = md_path.stem
    out = OUTPUT_DIR / f"{key}.jsonl"
    lines, pairs = load_file(out)

    if len(lines) >= target:
        log(f"  ✓ [{key}] done ({len(lines)}/{target})")
        return len(lines)

    md = md_path.read_text()
    log(f"  → [{key}] have {len(lines)}, need {target}")
    fh = open(out, 'a')
    count = len(lines)
    batch, zeros = 0, 0

    while count < target:
        needed = min(50, target - count)
        batch += 1
        ctx = "\n".join(f"  {random.choice(DISTROS)} {random.choice(SHELLS)} {random.choice(PRIVS)}"
                        for _ in range(min(needed, 10)))
        prompt = (f"Generate exactly {needed} UNIQUE Linux command training examples (batch {batch}).\n\n"
                  f"{md}\n\n"
                  f"Output ONLY valid JSONL, one object per line, NO other text.\n"
                  f'Format: {{"messages":[{{"role":"system","content":"ubuntu 24.04 bash non-root"}},'
                  f'{{"role":"user","content":"show disk usage"}},{{"role":"assistant","content":"df -h"}}]}}\n\n'
                  f"Rules:\n- assistant = shell command ONLY, never prose\n"
                  f"- No <placeholders> — use real paths/names\n"
                  f"- Diverse NL styles, cover all flags listed above\n"
                  f"- Add sudo for non-root when needed\n"
                  f"- System contexts:\n{ctx}\n\n"
                  f"Output {needed} JSONL lines:")
        try:
            r = subprocess.run(["/usr/local/bin/claude","-p",prompt,"--model","claude-sonnet-4-6"],
                               capture_output=True, text=True, timeout=90,
                               cwd=str(PROJECT_ROOT))
            added = 0
            for line in extract(r.stdout):
                try:
                    m = json.loads(line)["messages"]
                    k = (m[1]["content"].lower().strip(), m[2]["content"].lower().strip())
                    if k not in pairs:
                        pairs.add(k); fh.write(line+'\n'); fh.flush()
                        count += 1; added += 1
                        if count >= target: break
                except: pass
            log(f"    [{key}] batch {batch}: +{added} → {count}/{target}")
            if added == 0:
                zeros += 1
                if zeros >= 5: log(f"    [{key}] giving up after 5 empty batches"); break
                time.sleep(3)
            else:
                zeros = 0
        except subprocess.TimeoutExpired:
            log(f"    [{key}] timeout on batch {batch}, retrying...")
            time.sleep(5)
        except Exception as e:
            log(f"    [{key}] error: {e}")
            time.sleep(3)
        time.sleep(0.2)

    fh.close()
    log(f"  ✓ [{key}] DONE — {count} examples")
    return count

def merge():
    log("\n" + "="*60)
    log("Merging into train.jsonl...")
    train = PROJECT_ROOT / "data" / "v2" / "train.jsonl"
    existing = set()
    if train.exists():
        for line in train.read_text().split('\n'):
            line = line.strip()
            if not line: continue
            try:
                m = json.loads(line)["messages"]
                existing.add((m[1]["content"].lower().strip(), m[2]["content"].lower().strip()))
            except: pass
    log(f"Existing: {len(existing)}")
    new, dupes = [], 0
    for f in sorted(OUTPUT_DIR.glob("[0-9]*.jsonl")):
        for line in f.read_text().split('\n'):
            line = line.strip()
            if not line: continue
            try:
                m = json.loads(line)["messages"]
                k = (m[1]["content"].lower().strip(), m[2]["content"].lower().strip())
                if k in existing: dupes += 1
                else: new.append(line); existing.add(k)
            except: pass
    with open(train, 'a') as f:
        for line in new: f.write(line+'\n')
    total = sum(1 for l in train.read_text().split('\n') if l.strip())
    log(f"Added {len(new)}, skipped {dupes} dupes. Total: {total}")
    return total

def main():
    log("="*60)
    log(f"INCEPT Phase 1 — {WORKERS} parallel workers")
    log("="*60)

    all_files = sorted(COMMANDS_DIR.glob("*.md"), key=lambda p: int(p.stem.split('_')[0]))

    def target(p):
        n = int(p.stem.split('_')[0])
        return 500 if n<=42 else 200 if n<=89 else 100 if n<=366 else 20

    ordered = sorted(all_files, key=lambda p: (
        0 if int(p.stem.split('_')[0])<=42 else
        1 if int(p.stem.split('_')[0])<=89 else
        2 if int(p.stem.split('_')[0])<=366 else 3
    ))

    todo = []
    skipped = 0
    for f in ordered:
        out = OUTPUT_DIR / f"{f.stem}.jsonl"
        t = target(f)
        if out.exists():
            lines, _ = load_file(out)
            if len(lines) >= t:
                skipped += 1
                continue
        todo.append(f)

    log(f"Done: {skipped} | Remaining: {len(todo)}\n")
    log(f"Starting {WORKERS} parallel workers...\n")

    done, failed = 0, []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(generate, f, target(f)): f for f in todo}
        for fut in as_completed(futures):
            f = futures[fut]
            try:
                count = fut.result()
                done += 1
                log(f"\n  ★ [{f.stem}] complete ({count}) | {done}/{len(todo)} done | {len(todo)-done} left\n")
            except Exception as e:
                failed.append(f.stem)
                log(f"\n  ✗ [{f.stem}] EXCEPTION: {e}\n")

    log(f"\nAll done. Failed: {failed or 'none'}")
    total = merge()
    try:
        subprocess.run(["openclaw","system","event",
                        "--text",f"INCEPT Phase 1 DONE: {total} examples ready!",
                        "--mode","now"], timeout=10)
    except: pass
    log(f"\n✓ {total} examples in train.jsonl. Ready for SFT!")

if __name__ == "__main__":
    main()
