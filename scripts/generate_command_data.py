#!/usr/bin/env python3
"""Generate training data for the direct NL → command model.

Reads assembled records, compiles them using existing compilers as "teachers",
augments with template-generated examples, and writes train/val/test JSONL
splits to data/training/.

Usage:
    python scripts/generate_command_data.py [--augment-target 50000] [--seed 42]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_jsonl(path: Path) -> list[dict]:
    """Load records from a JSONL file."""
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                records.append(json.loads(line))
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate direct command training data")
    parser.add_argument(
        "--augment-target",
        type=int,
        default=50000,
        help="Target number of augmented examples from templates (default: 50000)",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--train-split", type=float, default=0.8, help="Training split ratio"
    )
    parser.add_argument(
        "--val-split", type=float, default=0.1, help="Validation split ratio"
    )
    args = parser.parse_args()

    data_dir = PROJECT_ROOT / "data"
    assembled_dir = data_dir / "assembled"
    output_dir = data_dir / "training"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Compile assembled records ────────────────────────────────────
    print("Step 1: Compiling assembled records using compilers as teachers...")

    from incept.data.command_generator import generate_command_pairs

    all_pairs: list[dict[str, str]] = []
    total_failures = 0

    for split_name in ("train", "val", "test"):
        path = assembled_dir / f"{split_name}.jsonl"
        if not path.exists():
            print(f"  Warning: {path} not found, skipping")
            continue
        records = load_jsonl(path)
        pairs, failures = generate_command_pairs(records)
        all_pairs.extend(pairs)
        total_failures += failures
        print(f"  {split_name}: {len(pairs)} pairs from {len(records)} records ({failures} failures)")

    print(f"  Total compiled: {len(all_pairs)} pairs, {total_failures} failures")

    # ── Step 2: Augment with template-generated examples ─────────────────────
    print(f"\nStep 2: Augmenting with template-generated examples (target: {args.augment_target})...")

    from incept.data.command_generator import compile_record
    from incept.data.generator import generate_examples
    from incept.data.templates import NL_TEMPLATES

    # Include macOS in the distro mix (20% as specified in plan)
    augmented_examples = generate_examples(
        templates=NL_TEMPLATES,
        target_count=args.augment_target,
        seed=args.seed,
        distro_mix={"debian": 0.4, "rhel": 0.2, "arch": 0.1, "suse": 0.1, "macos": 0.2},
    )

    augmented_pairs: list[dict[str, str]] = []
    aug_failures = 0
    for ex in augmented_examples:
        pair = compile_record(ex)
        if pair is not None:
            augmented_pairs.append(pair)
        else:
            aug_failures += 1

    print(f"  Augmented: {len(augmented_pairs)} pairs ({aug_failures} failures)")
    all_pairs.extend(augmented_pairs)

    # ── Step 3: Deduplicate ──────────────────────────────────────────────────
    print("\nStep 3: Deduplicating...")
    seen: set[str] = set()
    unique_pairs: list[dict[str, str]] = []
    for pair in all_pairs:
        key = pair["prompt"] + pair["completion"]
        if key not in seen:
            seen.add(key)
            unique_pairs.append(pair)

    print(f"  Before: {len(all_pairs)}, After: {len(unique_pairs)} ({len(all_pairs) - len(unique_pairs)} duplicates removed)")

    # ── Step 4: Shuffle and split ────────────────────────────────────────────
    print("\nStep 4: Shuffling and splitting...")
    rng = random.Random(args.seed)
    rng.shuffle(unique_pairs)

    n_total = len(unique_pairs)
    n_train = int(n_total * args.train_split)
    n_val = int(n_total * args.val_split)

    train_pairs = unique_pairs[:n_train]
    val_pairs = unique_pairs[n_train : n_train + n_val]
    test_pairs = unique_pairs[n_train + n_val :]

    print(f"  Train: {len(train_pairs)}, Val: {len(val_pairs)}, Test: {len(test_pairs)}")

    # ── Step 5: Write output files ───────────────────────────────────────────
    print("\nStep 5: Writing output files...")

    for name, pairs in [
        ("command_train", train_pairs),
        ("command_val", val_pairs),
        ("command_test", test_pairs),
    ]:
        path = output_dir / f"{name}.jsonl"
        with open(path, "w") as f:
            for pair in pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        print(f"  Wrote {path} ({len(pairs)} examples)")

    # ── Step 6: Write stats ──────────────────────────────────────────────────
    stats = {
        "total_unique_pairs": n_total,
        "train_count": len(train_pairs),
        "val_count": len(val_pairs),
        "test_count": len(test_pairs),
        "assembled_compiled": len(all_pairs) - len(augmented_pairs),
        "augmented_compiled": len(augmented_pairs),
        "duplicates_removed": len(all_pairs) - n_total,
        "total_failures": total_failures + aug_failures,
    }
    stats_path = output_dir / "command_stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\n  Stats written to {stats_path}")

    # ── Summary ──────────────────────────────────────────────────────────────
    failure_rate = (total_failures + aug_failures) / (
        len(all_pairs) + total_failures + aug_failures
    ) * 100 if (len(all_pairs) + total_failures + aug_failures) > 0 else 0

    print(f"\nDone! {n_total} unique training pairs generated ({failure_rate:.1f}% failure rate)")


if __name__ == "__main__":
    main()
