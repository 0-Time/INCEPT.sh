#!/usr/bin/env python3
"""Download external HuggingFace Linux command datasets and merge with v2 data.

Downloads, converts to ChatML, deduplicates, and merges:
  1. missvector/linux-commands        (5.2K rows: eng → completion)
  2. mecha-org/linux-command-dataset  (8.7K rows: input → output)
  3. hrsvrn/linux-commands-dataset    (1M rows: input → output, sampled)
  4. chowmean/linux-commands          (6.5K rows: eng → completion)

Usage:
    python scripts/download_external_data.py
    python scripts/download_external_data.py --hrsvrn-sample 100000
    python scripts/download_external_data.py --skip-download   # reuse cached
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import random
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Our v2 context strings for assigning to external data
CONTEXTS = [
    "ubuntu 22.04 bash non-root",
    "ubuntu 24.04 bash non-root",
    "ubuntu 22.04 zsh non-root",
    "ubuntu 22.04 bash root",
    "debian 12 bash non-root",
    "debian 12 bash root",
    "centos 7 bash non-root",
    "centos 7 bash root",
    "rhel 9 bash non-root",
    "rhel 9 bash root",
    "fedora 39 zsh non-root",
    "fedora 39 bash non-root",
    "arch rolling bash non-root",
    "arch rolling zsh non-root",
    "arch rolling bash root",
    "manjaro 23 bash non-root",
    "opensuse 15.5 bash non-root",
    "opensuse 15.5 bash root",
    "sles 15 bash non-root",
    "macos 14 zsh non-root",
    "macos 13 zsh non-root",
]

OUTPUT_DIR = PROJECT_ROOT / "data" / "v2"


def make_example(system: str, user: str, assistant: str) -> dict:
    """Build a single ChatML training example."""
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


def dedup_key(example: dict) -> str:
    """Deterministic deduplication key."""
    parts = "|".join(m["content"] for m in example["messages"])
    return hashlib.sha256(parts.encode()).hexdigest()


def is_valid_pair(nl: str, cmd: str) -> bool:
    """Basic quality check for a NL→command pair."""
    if not nl or not cmd:
        return False
    nl = nl.strip()
    cmd = cmd.strip()
    if len(nl) < 3 or len(cmd) < 2:
        return False
    if len(nl) > 500 or len(cmd) > 500:
        return False
    # Skip if command is just a description (no actual command)
    if cmd.startswith("This ") or cmd.startswith("The "):
        return False
    return True


# ---------------------------------------------------------------------------
# Dataset loaders
# ---------------------------------------------------------------------------

def load_missvector(rng: random.Random) -> list[dict]:
    """missvector/linux-commands: eng → completion."""
    from datasets import load_dataset

    log.info("Downloading missvector/linux-commands...")
    ds = load_dataset("missvector/linux-commands", "eng", split="train")
    examples = []
    for row in ds:
        nl = (row.get("eng") or "").strip()
        cmd = (row.get("completion") or "").strip()
        if is_valid_pair(nl, cmd):
            ctx = rng.choice(CONTEXTS)
            examples.append(make_example(ctx, nl, cmd))
    log.info("  missvector: %d valid examples", len(examples))
    return examples


def load_mecha(rng: random.Random) -> list[dict]:
    """mecha-org/linux-command-dataset: input → output."""
    from datasets import load_dataset

    log.info("Downloading mecha-org/linux-command-dataset...")
    ds = load_dataset("mecha-org/linux-command-dataset", split="train")
    examples = []
    for row in ds:
        nl = (row.get("input") or "").strip()
        cmd = (row.get("output") or "").strip()
        if is_valid_pair(nl, cmd):
            ctx = rng.choice(CONTEXTS)
            examples.append(make_example(ctx, nl, cmd))
    log.info("  mecha-org: %d valid examples", len(examples))
    return examples


def load_hrsvrn(rng: random.Random, sample_size: int = 50000) -> list[dict]:
    """hrsvrn/linux-commands-dataset: input → output (sampled from 1M)."""
    from datasets import load_dataset

    log.info("Downloading hrsvrn/linux-commands-dataset (1M rows, sampling %d)...", sample_size)
    ds = load_dataset("hrsvrn/linux-commands-dataset", split="train")

    # Sample indices
    total = len(ds)
    if sample_size < total:
        indices = sorted(rng.sample(range(total), sample_size))
        ds = ds.select(indices)
        log.info("  Sampled %d from %d total rows", sample_size, total)

    examples = []
    for row in ds:
        nl = (row.get("input") or "").strip()
        cmd = (row.get("output") or "").strip()
        if is_valid_pair(nl, cmd):
            ctx = rng.choice(CONTEXTS)
            examples.append(make_example(ctx, nl, cmd))
    log.info("  hrsvrn: %d valid examples", len(examples))
    return examples


def load_chowmean(rng: random.Random) -> list[dict]:
    """chowmean/linux-commands: eng → completion."""
    from datasets import load_dataset

    log.info("Downloading chowmean/linux-commands...")
    ds = load_dataset("chowmean/linux-commands", "eng", split="train")
    examples = []
    for row in ds:
        nl = (row.get("eng") or "").strip()
        cmd = (row.get("completion") or "").strip()
        if is_valid_pair(nl, cmd):
            ctx = rng.choice(CONTEXTS)
            examples.append(make_example(ctx, nl, cmd))
    log.info("  chowmean: %d valid examples", len(examples))
    return examples


# ---------------------------------------------------------------------------
# Merge with existing v2 data
# ---------------------------------------------------------------------------

def load_existing_v2() -> list[dict]:
    """Load our existing v2 training data."""
    examples = []
    for split_name in ["train", "val", "test"]:
        path = OUTPUT_DIR / f"{split_name}.jsonl"
        if path.exists():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        examples.append(json.loads(line))
    log.info("Loaded %d existing v2 examples", len(examples))
    return examples


def deduplicate(examples: list[dict]) -> list[dict]:
    """Remove exact duplicates by content hash."""
    seen: set[str] = set()
    unique: list[dict] = []
    for ex in examples:
        key = dedup_key(ex)
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    return unique


def split_data(
    examples: list[dict],
    rng: random.Random,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Shuffle and split into train/val/test."""
    shuffled = list(examples)
    rng.shuffle(shuffled)
    n = len(shuffled)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    return shuffled[:train_end], shuffled[train_end:val_end], shuffled[val_end:]


def write_jsonl(path: Path, examples: list[dict]) -> None:
    """Write examples as JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    log.info("Wrote %d examples to %s", len(examples), path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download external datasets and merge with v2 data"
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--hrsvrn-sample", type=int, default=50000,
        help="How many rows to sample from the 1M hrsvrn dataset (default: 50000)",
    )
    parser.add_argument(
        "--output-dir", type=str, default=str(OUTPUT_DIR),
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    output_dir = Path(args.output_dir)

    log.info("=" * 70)
    log.info("INCEPT v2 — External Dataset Download & Merge")
    log.info("=" * 70)

    t0 = time.monotonic()

    # Download all 4 datasets
    all_external: list[dict] = []

    ext1 = load_missvector(rng)
    all_external.extend(ext1)

    ext2 = load_mecha(rng)
    all_external.extend(ext2)

    ext3 = load_hrsvrn(rng, sample_size=args.hrsvrn_sample)
    all_external.extend(ext3)

    ext4 = load_chowmean(rng)
    all_external.extend(ext4)

    log.info("-" * 70)
    log.info("Total external examples: %d", len(all_external))

    # Load existing v2 data
    existing = load_existing_v2()

    # Combine
    combined = existing + all_external
    log.info("Combined (before dedup): %d", len(combined))

    # Deduplicate
    combined = deduplicate(combined)
    log.info("After dedup: %d", len(combined))

    # Split
    train, val, test = split_data(combined, rng)
    log.info("Split: train=%d, val=%d, test=%d", len(train), len(val), len(test))

    # Write
    write_jsonl(output_dir / "train.jsonl", train)
    write_jsonl(output_dir / "val.jsonl", val)
    write_jsonl(output_dir / "test.jsonl", test)

    # Stats
    stats = {
        "seed": args.seed,
        "sources": {
            "v2_existing": len(existing),
            "missvector": len(ext1),
            "mecha_org": len(ext2),
            "hrsvrn": len(ext3),
            "chowmean": len(ext4),
        },
        "total_external": len(all_external),
        "combined_raw": len(existing) + len(all_external),
        "after_dedup": len(combined),
        "train": len(train),
        "val": len(val),
        "test": len(test),
    }
    stats_path = output_dir / "stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    elapsed = time.monotonic() - t0
    log.info("=" * 70)
    log.info("Done in %.1fs", elapsed)
    log.info("=" * 70)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
