#!/usr/bin/env python3
"""Generate ChatML-format JSONL training data for INCEPT v2.

Reads command templates from incept/data/v2_commands.py and expands them
into (system_context, user_nl, assistant_cmd) training examples, then
writes train/val/test JSONL splits to data/v2/.

Usage:
    python scripts/generate_v2_data.py
    python scripts/generate_v2_data.py --seed 42 --target-per-template 10
    python scripts/generate_v2_data.py --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import random
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Project root on sys.path so we can import incept.data.v2_commands
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from incept.data.v2_commands import (  # noqa: E402
    CONTEXTS,
    OUT_OF_SCOPE,
    SAFETY_REFUSALS,
    TEMPLATES,
)
from incept.data.v2_commands_extended import (  # noqa: E402
    IDENTITY_EXTENDED,
    SAFETY_REFUSALS_EXTENDED,
    TEMPLATES_EXTENDED,
)
from incept.data.v2_pipeline_templates import (  # noqa: E402
    TEMPLATES_PIPELINE,
)

# Merge extended templates with base templates
TEMPLATES = TEMPLATES + TEMPLATES_EXTENDED + TEMPLATES_PIPELINE
SAFETY_REFUSALS = SAFETY_REFUSALS + SAFETY_REFUSALS_EXTENDED
OUT_OF_SCOPE = OUT_OF_SCOPE + IDENTITY_EXTENDED

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OUTPUT_DIR = PROJECT_ROOT / "data" / "v2"
DISTRO_FAMILIES = ["debian", "rhel", "arch", "suse", "macos"]

# Pre-build lookup: distro_family -> list of context strings
CONTEXTS_BY_FAMILY: dict[str, list[str]] = defaultdict(list)
ALL_CONTEXT_STRINGS: list[str] = []
for _ctx_str, _ctx_family in CONTEXTS:
    CONTEXTS_BY_FAMILY[_ctx_family].append(_ctx_str)
    ALL_CONTEXT_STRINGS.append(_ctx_str)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_placeholders(text: str) -> set[str]:
    """Extract {placeholder} names from a format string.

    Handles doubled braces (``{{``/``}}``) correctly by ignoring them.
    For example, ``awk '{{print ${col}}}' {file}`` returns ``{'col', 'file'}``.
    """
    # Replace escaped braces so they don't interfere, then find single-braced names.
    cleaned = text.replace("{{", "").replace("}}", "")
    return set(re.findall(r"\{(\w+)\}", cleaned))


def safe_format(template: str, values: dict[str, str]) -> str:
    """Format a template string, preserving double-brace escapes.

    Uses a single-pass regex to correctly handle cases like ``{{print ${col}}}``
    where ``{{`` is an escaped open brace, ``{col}`` is a placeholder, and ``}}``
    is an escaped close brace -- even when they are adjacent with no whitespace.

    The regex matches tokens in this priority order:
      1. ``{{`` -> literal ``{``
      2. ``}}`` -> literal ``}``
      3. ``{word}`` -> substitute from values dict
      4. Any other character -> pass through
    """
    # Pattern matches {{ or }} or {word} as distinct tokens, left to right.
    _FORMAT_RE = re.compile(r"\{\{|\}\}|\{(\w+)\}")

    def _replacer(m: re.Match) -> str:
        text = m.group(0)
        if text == "{{":
            return "{"
        if text == "}}":
            return "}"
        # It is a {placeholder} -- group(1) holds the name
        key = m.group(1)
        return values[key]

    return _FORMAT_RE.sub(_replacer, template)


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
    """Deterministic deduplication key from the three message contents."""
    parts = "|".join(m["content"] for m in example["messages"])
    return hashlib.sha256(parts.encode()).hexdigest()


def is_distro_specific_slots(slots: dict) -> bool:
    """Return True if slots is keyed by distro family (nested dict).

    Distro-specific:  {"debian": {"pkg": [...]}, "rhel": {"pkg": [...]}}
    Flat:             {"pkg": [...], "file": [...]}
    """
    if not slots:
        return False
    first_val = next(iter(slots.values()))
    # If the first value is a dict, it is distro-specific
    if isinstance(first_val, dict):
        # Double-check: all values should be dicts
        return all(isinstance(v, dict) for v in slots.values())
    return False


def pick_slot_combo(
    slot_pools: dict[str, list[str]],
    rng: random.Random,
) -> dict[str, str]:
    """Pick one random value for each slot placeholder."""
    return {key: rng.choice(values) for key, values in slot_pools.items()}


def validate_slots_match_placeholders(
    template_idx: int,
    nl_list: list[str],
    cmd: Any,
    slot_pools: dict[str, list[str]],
) -> bool:
    """Check that slot keys cover all placeholders in NL and CMD strings.

    Returns True if valid, False (with a log warning) if mismatched.
    """
    # Gather all placeholders from NL variants
    all_placeholders: set[str] = set()
    for nl in nl_list:
        all_placeholders |= extract_placeholders(nl)

    # Gather placeholders from cmd (string or single distro variant)
    if isinstance(cmd, str):
        all_placeholders |= extract_placeholders(cmd)
    elif isinstance(cmd, dict):
        for cmd_str in cmd.values():
            all_placeholders |= extract_placeholders(cmd_str)

    slot_keys = set(slot_pools.keys())

    if all_placeholders != slot_keys:
        missing = all_placeholders - slot_keys
        extra = slot_keys - all_placeholders
        parts = []
        if missing:
            parts.append(f"missing slots {missing}")
        if extra:
            parts.append(f"extra slots {extra}")
        log.warning(
            "Template #%d slot mismatch (%s). NL[0]=%r. Skipping.",
            template_idx, ", ".join(parts), nl_list[0][:60],
        )
        return False
    return True


# ---------------------------------------------------------------------------
# Generator: regular templates
# ---------------------------------------------------------------------------

def generate_template_examples(
    templates: list[dict],
    target_per_variant: int,
    rng: random.Random,
) -> tuple[list[dict], dict[str, int]]:
    """Expand TEMPLATES into ChatML examples.

    Returns (examples_list, stats_dict).
    """
    examples: list[dict] = []
    stats: dict[str, int] = defaultdict(int)

    for t_idx, tmpl in enumerate(templates):
        nl_list: list[str] = tmpl["nl"]
        cmd = tmpl["cmd"]
        slots = tmpl.get("slots", {})

        cmd_is_distro_specific = isinstance(cmd, dict)
        slots_are_distro_specific = is_distro_specific_slots(slots)

        # -----------------------------------------------------------
        # Case 1: Universal command (cmd is a string)
        # -----------------------------------------------------------
        if not cmd_is_distro_specific:
            flat_slots = slots  # always flat here

            # Validate slot keys match placeholders
            if flat_slots and not validate_slots_match_placeholders(
                t_idx, nl_list, cmd, flat_slots
            ):
                stats["skipped_bad_slots"] += 1
                continue

            if flat_slots:
                # Has slot placeholders -- generate random combos
                for nl_variant in nl_list:
                    for _ in range(target_per_variant):
                        combo = pick_slot_combo(flat_slots, rng)
                        ctx = rng.choice(ALL_CONTEXT_STRINGS)
                        try:
                            user_text = safe_format(nl_variant, combo)
                            cmd_text = safe_format(cmd, combo)
                        except (KeyError, IndexError, ValueError) as exc:
                            log.debug("Format error t#%d: %s", t_idx, exc)
                            stats["format_errors"] += 1
                            continue
                        examples.append(make_example(ctx, user_text, cmd_text))
                        stats["template_with_slots"] += 1
            else:
                # No slots -- pair each NL variant with varied contexts
                for nl_variant in nl_list:
                    used_contexts = _sample_contexts(
                        ALL_CONTEXT_STRINGS, target_per_variant, rng
                    )
                    for ctx in used_contexts:
                        examples.append(make_example(ctx, nl_variant, cmd))
                        stats["template_no_slots"] += 1

        # -----------------------------------------------------------
        # Case 2: Distro-specific command (cmd is a dict)
        # -----------------------------------------------------------
        else:
            for family in DISTRO_FAMILIES:
                if family not in cmd:
                    continue

                cmd_str = cmd[family]
                family_contexts = CONTEXTS_BY_FAMILY.get(family, [])
                if not family_contexts:
                    continue

                # Resolve slot pool for this family
                if slots_are_distro_specific:
                    # Nested: grab the family-specific slot dict
                    family_slots = slots.get(family, {})
                elif slots:
                    # Flat slots shared across all distros
                    family_slots = slots
                else:
                    family_slots = {}

                # Validate
                if family_slots and not validate_slots_match_placeholders(
                    t_idx, nl_list, cmd_str, family_slots
                ):
                    stats["skipped_bad_slots"] += 1
                    continue

                if family_slots:
                    for nl_variant in nl_list:
                        for _ in range(target_per_variant):
                            combo = pick_slot_combo(family_slots, rng)
                            ctx = rng.choice(family_contexts)
                            try:
                                user_text = safe_format(nl_variant, combo)
                                cmd_text = safe_format(cmd_str, combo)
                            except (KeyError, IndexError, ValueError) as exc:
                                log.debug("Format error t#%d/%s: %s", t_idx, family, exc)
                                stats["format_errors"] += 1
                                continue
                            examples.append(make_example(ctx, user_text, cmd_text))
                            stats["distro_with_slots"] += 1
                else:
                    # No slots, distro-specific cmd
                    for nl_variant in nl_list:
                        used_contexts = _sample_contexts(
                            family_contexts, target_per_variant, rng
                        )
                        for ctx in used_contexts:
                            examples.append(make_example(ctx, nl_variant, cmd_str))
                            stats["distro_no_slots"] += 1

    return examples, dict(stats)


# ---------------------------------------------------------------------------
# Generator: safety refusals
# ---------------------------------------------------------------------------

def generate_safety_examples(
    refusals: list[dict],
    contexts_per_variant: int,
    rng: random.Random,
) -> list[dict]:
    """Expand SAFETY_REFUSALS into training examples."""
    examples: list[dict] = []
    for item in refusals:
        nl_list = item["nl"]
        response = item["response"]
        for nl_variant in nl_list:
            used_contexts = _sample_contexts(
                ALL_CONTEXT_STRINGS, contexts_per_variant, rng
            )
            for ctx in used_contexts:
                examples.append(make_example(ctx, nl_variant, response))
    return examples


# ---------------------------------------------------------------------------
# Generator: out of scope
# ---------------------------------------------------------------------------

def generate_oos_examples(
    oos_items: list[dict],
    contexts_per_variant: int,
    rng: random.Random,
) -> list[dict]:
    """Expand OUT_OF_SCOPE into training examples."""
    examples: list[dict] = []
    for item in oos_items:
        nl_list = item["nl"]
        response = item["response"]
        for nl_variant in nl_list:
            used_contexts = _sample_contexts(
                ALL_CONTEXT_STRINGS, contexts_per_variant, rng
            )
            for ctx in used_contexts:
                examples.append(make_example(ctx, nl_variant, response))
    return examples


# ---------------------------------------------------------------------------
# Context sampling helper
# ---------------------------------------------------------------------------

def _sample_contexts(
    pool: list[str],
    n: int,
    rng: random.Random,
) -> list[str]:
    """Sample up to n unique contexts from pool. If pool < n, cycle through."""
    if n <= len(pool):
        return rng.sample(pool, n)
    # Repeat pool enough times, then sample
    copies = (n // len(pool)) + 1
    expanded = pool * copies
    return rng.sample(expanded, n)


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate(examples: list[dict]) -> list[dict]:
    """Remove exact duplicates by (system, user, assistant) content hash."""
    seen: set[str] = set()
    unique: list[dict] = []
    for ex in examples:
        key = dedup_key(ex)
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    return unique


# ---------------------------------------------------------------------------
# Split & write
# ---------------------------------------------------------------------------

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
    """Write examples as one JSON object per line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    log.info("Wrote %d examples to %s", len(examples), path)


def write_stats(path: Path, stats: dict) -> None:
    """Write stats as formatted JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    log.info("Wrote stats to %s", path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate ChatML training data for INCEPT v2"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--target-per-template", type=int, default=10,
        help="Expansions per NL variant per template/distro (default: 10)",
    )
    parser.add_argument(
        "--safety-contexts", type=int, default=5,
        help="Context variations per safety/OOS NL variant (default: 5)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Count examples without writing files",
    )
    parser.add_argument(
        "--output-dir", type=str, default=str(OUTPUT_DIR),
        help=f"Output directory (default: {OUTPUT_DIR})",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    output_dir = Path(args.output_dir)

    log.info("=" * 70)
    log.info("INCEPT v2 Training Data Generator")
    log.info("=" * 70)
    log.info("Seed: %d", args.seed)
    log.info("Target per template variant: %d", args.target_per_template)
    log.info("Safety/OOS context variations: %d", args.safety_contexts)
    log.info("Output directory: %s", output_dir)
    log.info("Templates: %d", len(TEMPLATES))
    log.info("Safety refusals: %d", len(SAFETY_REFUSALS))
    log.info("Out-of-scope items: %d", len(OUT_OF_SCOPE))
    log.info("Context lines: %d (%d families)", len(CONTEXTS), len(CONTEXTS_BY_FAMILY))
    log.info("-" * 70)

    t0 = time.monotonic()

    # --- Generate template examples ---
    log.info("[1/4] Generating template examples...")
    template_examples, template_stats = generate_template_examples(
        TEMPLATES, args.target_per_template, rng
    )
    log.info(
        "  Template examples (raw): %d", len(template_examples)
    )
    for k, v in sorted(template_stats.items()):
        log.info("    %-25s %d", k, v)

    # --- Generate safety examples ---
    log.info("[2/4] Generating safety refusal examples...")
    safety_examples = generate_safety_examples(
        SAFETY_REFUSALS, args.safety_contexts, rng
    )
    log.info("  Safety examples (raw): %d", len(safety_examples))

    # --- Generate OOS examples ---
    log.info("[3/4] Generating out-of-scope examples...")
    oos_examples = generate_oos_examples(
        OUT_OF_SCOPE, args.safety_contexts, rng
    )
    log.info("  OOS examples (raw): %d", len(oos_examples))

    # --- Combine and deduplicate ---
    all_examples = template_examples + safety_examples + oos_examples
    log.info("  Combined (raw): %d", len(all_examples))

    log.info("[4/4] Deduplicating...")
    all_examples = deduplicate(all_examples)
    duplicates_removed = (
        len(template_examples) + len(safety_examples) + len(oos_examples)
    ) - len(all_examples)
    log.info("  After dedup: %d (removed %d duplicates)", len(all_examples), duplicates_removed)

    # --- Split ---
    train, val, test = split_data(all_examples, rng)
    log.info("-" * 70)
    log.info("Split: train=%d, val=%d, test=%d", len(train), len(val), len(test))

    # --- Collect final stats ---
    final_stats = {
        "seed": args.seed,
        "target_per_template": args.target_per_template,
        "safety_contexts": args.safety_contexts,
        "num_templates": len(TEMPLATES),
        "num_safety_refusals": len(SAFETY_REFUSALS),
        "num_oos_items": len(OUT_OF_SCOPE),
        "num_contexts": len(CONTEXTS),
        "generation_stats": template_stats,
        "totals": {
            "template_examples_raw": len(template_examples),
            "safety_examples_raw": len(safety_examples),
            "oos_examples_raw": len(oos_examples),
            "combined_raw": len(template_examples) + len(safety_examples) + len(oos_examples),
            "duplicates_removed": duplicates_removed,
            "after_dedup": len(all_examples),
            "train": len(train),
            "val": len(val),
            "test": len(test),
        },
    }

    if args.dry_run:
        log.info("=" * 70)
        log.info("DRY RUN -- no files written")
        log.info("=" * 70)
        print(json.dumps(final_stats, indent=2))
        return

    # --- Write output ---
    write_jsonl(output_dir / "train.jsonl", train)
    write_jsonl(output_dir / "val.jsonl", val)
    write_jsonl(output_dir / "test.jsonl", test)
    write_stats(output_dir / "stats.json", final_stats)

    elapsed = time.monotonic() - t0
    log.info("=" * 70)
    log.info("Done in %.1fs. Output: %s", elapsed, output_dir)
    log.info("=" * 70)


if __name__ == "__main__":
    main()
