#!/usr/bin/env python3
"""Build the Zvec knowledge index from ALL INCEPT data sources.

Indexes NL->command pairs into a Zvec collection with:
  - HNSW index + INT8 quantization on dense embedding (384-dim)
  - Sparse keyword vector for hybrid search
  - Inverted index on distro field for fast filtered queries
  - Cosine distance metric

Data sources:
  1. Template EXHAUSTIVE expansion: every template × every NL variant
     × every slot combination (up to --max-combos per template).
     This is the highest-quality source — hand-written NL patterns with
     real concrete values filled in.
  2. V2 training data: train + val + test (43,881 pairs)
  3. Command training data: command_train.jsonl (36,427 pairs)

Usage:
    python scripts/build_knowledge_index.py                  # all sources
    python scripts/build_knowledge_index.py --max-combos 100 # more slot combos
    python scripts/build_knowledge_index.py --templates-only
    python scripts/build_knowledge_index.py --no-expand      # raw templates only
"""
import argparse
import hashlib
import itertools
import json
import logging
import random
import re
import shutil
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from incept.knowledge.vectorizer import DENSE_DIM, hash_vectorize, sparse_vectorize

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# Regex to extract NL from old [INST] format
_INST_RE = re.compile(r"\[REQUEST\]\s*(.+?)\s*\[/INST\]", re.DOTALL)
_COMPLETION_STRIP = re.compile(r"</s>$")
_CONTEXT_RE = re.compile(r"\[CONTEXT\]\s*(\S+)")

# Safe template formatting (from generate_v2_data.py)
_FORMAT_RE = re.compile(r"\{\{|\}\}|\{(\w+)\}")
DISTRO_FAMILIES = ["debian", "rhel", "arch", "suse", "macos"]


def _extract_placeholders(text: str) -> set[str]:
    """Extract {placeholder} names, ignoring escaped {{/}}."""
    cleaned = text.replace("{{", "").replace("}}", "")
    return set(re.findall(r"\{(\w+)\}", cleaned))


def _safe_format(template: str, values: dict[str, str]) -> str:
    """Format a template string, preserving double-brace escapes."""
    def _replacer(m: re.Match) -> str:
        text = m.group(0)
        if text == "{{":
            return "{"
        if text == "}}":
            return "}"
        return values[m.group(1)]
    return _FORMAT_RE.sub(_replacer, template)


def _is_distro_specific_slots(slots: dict) -> bool:
    if not slots:
        return False
    first_val = next(iter(slots.values()))
    return isinstance(first_val, dict) and all(
        isinstance(v, dict) for v in slots.values()
    )


def _slot_combinations(
    slot_pools: dict[str, list[str]],
    max_combos: int,
    rng: random.Random,
) -> list[dict[str, str]]:
    """Generate slot value combinations.

    If total combinations <= max_combos: return ALL (exhaustive).
    Otherwise: return max_combos random unique combinations.
    This avoids wasting fills on duplicates for small pools.
    """
    keys = list(slot_pools.keys())
    pools = [slot_pools[k] for k in keys]

    total = 1
    for pool in pools:
        total *= len(pool)
        if total > max_combos:
            break

    if total <= max_combos:
        # Exhaustive — every possible combination
        return [
            dict(zip(keys, combo)) for combo in itertools.product(*pools)
        ]
    else:
        # Random sample of unique combos
        seen: set[tuple] = set()
        combos = []
        attempts = 0
        while len(combos) < max_combos and attempts < max_combos * 5:
            combo = tuple(rng.choice(pool) for pool in pools)
            if combo not in seen:
                seen.add(combo)
                combos.append(dict(zip(keys, combo)))
            attempts += 1
        return combos


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------


def _merge_extended_pools(
    slots: dict[str, list], extended: dict[str, list]
) -> dict[str, list]:
    """Merge extended pool values into template slot pools.

    For each slot key, union the original pool with the extended pool
    (if one exists for that key name). Deduplicates values.
    """
    merged = {}
    for key, pool in slots.items():
        if key in extended:
            # Union: original values + extended values, deduped, order preserved
            seen: set[str] = set()
            combined = []
            for v in pool:
                vs = str(v)
                if vs not in seen:
                    seen.add(vs)
                    combined.append(v)
            for v in extended[key]:
                vs = str(v)
                if vs not in seen:
                    seen.add(vs)
                    combined.append(v)
            merged[key] = combined
        else:
            merged[key] = pool
    return merged


def expand_templates(
    max_combos: int, seed: int, extend: bool = True
) -> list[dict]:
    """Expand ALL templates with exhaustive/sampled slot filling.

    For templates with slots: generates up to max_combos slot value
    combinations per template, times each NL variant. Uses exhaustive
    enumeration when possible (small pools), random sampling for large.

    When extend=True, merges extended pools from
    incept.knowledge.extended_pools into each template's slot pools,
    dramatically increasing the number of unique combinations.

    For templates without slots: emits each NL variant as-is.
    Distro-specific commands are expanded per distro family.
    """
    from incept.data.v2_commands import TEMPLATES
    from incept.data.v2_commands_extended import TEMPLATES_EXTENDED
    from incept.data.v2_pipeline_templates import TEMPLATES_PIPELINE

    ext_pools: dict[str, list] = {}
    if extend:
        from incept.knowledge.extended_pools import EXTENDED_POOLS
        ext_pools = EXTENDED_POOLS

    rng = random.Random(seed)
    all_templates = TEMPLATES + TEMPLATES_EXTENDED + TEMPLATES_PIPELINE
    examples = []

    for t in all_templates:
        cmd = t.get("cmd", "")
        nl_list = t.get("nl", [])
        slots = t.get("slots", {})
        if not nl_list:
            continue

        cmd_is_distro = isinstance(cmd, dict)
        slots_are_distro = _is_distro_specific_slots(slots)

        if not cmd_is_distro:
            if slots:
                # Validate placeholders
                all_ph = set()
                for nl in nl_list:
                    all_ph |= _extract_placeholders(nl)
                all_ph |= _extract_placeholders(cmd)
                if all_ph != set(slots.keys()):
                    continue

                merged = _merge_extended_pools(slots, ext_pools) if ext_pools else slots
                combos = _slot_combinations(merged, max_combos, rng)
                for nl in nl_list:
                    for combo in combos:
                        try:
                            filled_nl = _safe_format(nl, combo)
                            filled_cmd = _safe_format(cmd, combo)
                        except (KeyError, IndexError, ValueError):
                            continue
                        examples.append({
                            "nl": filled_nl,
                            "cmd": filled_cmd,
                            "distro": "",
                        })
            else:
                for nl in nl_list:
                    examples.append({"nl": nl, "cmd": cmd, "distro": ""})
        else:
            for family in DISTRO_FAMILIES:
                if family not in cmd:
                    continue
                cmd_str = cmd[family]
                if not cmd_str:
                    continue

                if slots_are_distro:
                    family_slots = slots.get(family, {})
                elif slots:
                    family_slots = slots
                else:
                    family_slots = {}

                if family_slots:
                    all_ph = set()
                    for nl in nl_list:
                        all_ph |= _extract_placeholders(nl)
                    all_ph |= _extract_placeholders(cmd_str)
                    if all_ph != set(family_slots.keys()):
                        continue

                    merged_fs = _merge_extended_pools(family_slots, ext_pools) if ext_pools else family_slots
                    combos = _slot_combinations(merged_fs, max_combos, rng)
                    for nl in nl_list:
                        for combo in combos:
                            try:
                                filled_nl = _safe_format(nl, combo)
                                filled_cmd = _safe_format(cmd_str, combo)
                            except (KeyError, IndexError, ValueError):
                                continue
                            examples.append({
                                "nl": filled_nl,
                                "cmd": filled_cmd,
                                "distro": family,
                            })
                else:
                    for nl in nl_list:
                        examples.append({
                            "nl": nl, "cmd": cmd_str, "distro": family,
                        })

    return examples


def load_raw_templates() -> list[dict]:
    """Load ALL NL variants from templates WITHOUT slot expansion."""
    from incept.data.v2_commands import TEMPLATES
    from incept.data.v2_commands_extended import TEMPLATES_EXTENDED
    from incept.data.v2_pipeline_templates import TEMPLATES_PIPELINE

    examples = []
    all_templates = TEMPLATES + TEMPLATES_EXTENDED + TEMPLATES_PIPELINE

    for t in all_templates:
        cmd = t.get("cmd", "")
        nl_list = t.get("nl", [])
        if not nl_list:
            continue

        if isinstance(cmd, dict):
            for distro, distro_cmd in cmd.items():
                if not distro_cmd:
                    continue
                for nl in nl_list:
                    examples.append({
                        "nl": nl, "cmd": distro_cmd, "distro": distro,
                    })
        else:
            if not cmd:
                continue
            for nl in nl_list:
                examples.append({"nl": nl, "cmd": cmd, "distro": ""})

    return examples


def load_v2_training(root: Path) -> list[dict]:
    """Load NL->cmd pairs from all v2 ChatML JSONL files."""
    examples = []
    for name in ["train.jsonl", "val.jsonl", "test.jsonl"]:
        path = root / "data" / "v2" / name
        if not path.exists():
            continue
        with open(path) as f:
            for line in f:
                row = json.loads(line)
                msgs = row.get("messages", [])
                if len(msgs) < 3:
                    continue
                user = msgs[1].get("content", "").strip()
                assistant = msgs[2].get("content", "").strip()
                if not user or not assistant:
                    continue
                system = msgs[0].get("content", "")
                distro = system.split()[0] if system else ""
                examples.append({
                    "nl": user, "cmd": assistant, "distro": distro,
                })
    return examples


def load_command_train(root: Path) -> list[dict]:
    """Load NL->cmd from the older [INST] format command_train.jsonl."""
    path = root / "data" / "training" / "command_train.jsonl"
    if not path.exists():
        return []
    examples = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            prompt = row.get("prompt", "")
            completion = row.get("completion", "").strip()
            completion = _COMPLETION_STRIP.sub("", completion).strip()
            m = _INST_RE.search(prompt)
            if not m or not completion:
                continue
            nl = m.group(1).strip()
            cm = _CONTEXT_RE.search(prompt)
            distro = cm.group(1) if cm else ""
            examples.append({"nl": nl, "cmd": completion, "distro": distro})
    return examples


def dedup(examples: list[dict]) -> list[dict]:
    """Deduplicate by (nl_lower, cmd) keeping first occurrence."""
    seen: set[str] = set()
    unique = []
    for ex in examples:
        key = f"{ex['nl'].lower().strip()}||{ex['cmd'].strip()}"
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    return unique


def main():
    parser = argparse.ArgumentParser(
        description="Build Zvec knowledge index from ALL INCEPT data"
    )
    parser.add_argument(
        "--output",
        default=str(Path.home() / ".incept"),
        help="Output directory (default: ~/.incept/)",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=500000,
        help="Max examples to index (default: 500000)",
    )
    parser.add_argument(
        "--max-combos",
        type=int,
        default=750,
        help="Max slot combinations per template (default: 750, "
             "exhaustive if total combos <= this, ~500K+ with extended pools)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=99,
        help="Random seed for slot expansion (default: 99, "
             "different from training seed=42 to minimize overlap)",
    )
    parser.add_argument(
        "--templates-only",
        action="store_true",
        help="Index only expanded templates (no training data files)",
    )
    parser.add_argument(
        "--no-expand",
        action="store_true",
        help="Don't expand template slots (raw templates only, ~4K entries)",
    )
    parser.add_argument(
        "--no-extend",
        action="store_true",
        help="Don't merge extended pools (use original small pools only)",
    )
    parser.add_argument(
        "--no-sparse",
        action="store_true",
        help="Skip sparse vectors (smaller index, no hybrid search)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Insert batch size (default: 1000)",
    )
    args = parser.parse_args()

    import zvec

    zvec.init(log_level=zvec.LogLevel.INFO)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / "examples.zvec"

    # Remove existing index
    if db_path.exists():
        shutil.rmtree(db_path, ignore_errors=True)
        log.info("Removed existing index at %s", db_path)

    # --- Schema ---
    fields = [
        zvec.FieldSchema(name="nl", data_type=zvec.DataType.STRING),
        zvec.FieldSchema(name="cmd", data_type=zvec.DataType.STRING),
        zvec.FieldSchema(
            name="distro",
            data_type=zvec.DataType.STRING,
            index_param=zvec.InvertIndexParam(),
        ),
    ]

    vectors = [
        zvec.VectorSchema(
            name="embedding",
            data_type=zvec.DataType.VECTOR_FP32,
            dimension=DENSE_DIM,
            index_param=zvec.HnswIndexParam(
                metric_type=zvec.MetricType.COSINE,
                m=32,
                ef_construction=400,
                quantize_type=zvec.QuantizeType.INT8,
            ),
        ),
    ]

    if not args.no_sparse:
        vectors.append(
            zvec.VectorSchema(
                name="sparse",
                data_type=zvec.DataType.SPARSE_VECTOR_FP32,
            )
        )

    schema = zvec.CollectionSchema(
        name="examples", fields=fields, vectors=vectors,
    )
    collection = zvec.create_and_open(path=str(db_path), schema=schema)
    log.info("Created collection at %s (sparse=%s)", db_path, not args.no_sparse)

    # --- Load data ---
    if args.no_expand:
        log.info("Loading raw templates (no slot expansion)...")
        template_examples = load_raw_templates()
        log.info("  Raw templates: %d NL->cmd pairs", len(template_examples))
    else:
        log.info(
            "Expanding templates: max %d combos/template, seed=%d...",
            args.max_combos, args.seed,
        )
        template_examples = expand_templates(
            args.max_combos, args.seed, extend=not args.no_extend
        )
        log.info("  Expanded templates: %d NL->cmd pairs", len(template_examples))

    if args.templates_only:
        all_examples = template_examples
    else:
        log.info("Loading v2 training data (train+val+test)...")
        v2 = load_v2_training(PROJECT_ROOT)
        log.info("  V2 data: %d pairs", len(v2))

        log.info("Loading command_train data...")
        cmd_train = load_command_train(PROJECT_ROOT)
        log.info("  Command train: %d pairs", len(cmd_train))

        all_examples = template_examples + v2 + cmd_train

    # Dedup
    before_dedup = len(all_examples)
    all_examples = dedup(all_examples)
    log.info(
        "After dedup: %d unique (removed %d dupes, cap %d)",
        len(all_examples),
        before_dedup - len(all_examples),
        args.max_examples,
    )
    if len(all_examples) > args.max_examples:
        all_examples = all_examples[: args.max_examples]
        log.info("  Capped at %d examples", args.max_examples)

    # --- Index ---
    t0 = time.time()
    batch = []
    use_sparse = not args.no_sparse
    total = len(all_examples)

    for i, ex in enumerate(all_examples):
        doc_id = hashlib.sha256(
            f"{ex['nl']}|{ex['cmd']}".encode()
        ).hexdigest()[:16]

        vectors_dict: dict = {"embedding": hash_vectorize(ex["nl"])}
        if use_sparse:
            vectors_dict["sparse"] = sparse_vectorize(ex["nl"])

        batch.append(zvec.Doc(
            id=doc_id,
            vectors=vectors_dict,
            fields={
                "nl": ex["nl"],
                "cmd": ex["cmd"],
                "distro": ex.get("distro", ""),
            },
        ))

        if len(batch) >= args.batch_size:
            collection.insert(batch)
            batch = []
            done = i + 1
            if done % 10000 == 0:
                elapsed = time.time() - t0
                rate = done / elapsed
                eta = (total - done) / rate if rate > 0 else 0
                log.info(
                    "  Indexed %d / %d (%.0f docs/sec, ETA %.0fs)...",
                    done, total, rate, eta,
                )

    if batch:
        collection.insert(batch)

    insert_time = time.time() - t0
    log.info("Insert complete: %d docs in %.1fs", total, insert_time)

    # Build HNSW index
    log.info("Optimizing index (building HNSW graph)...")
    t1 = time.time()
    collection.optimize()
    opt_time = time.time() - t1
    log.info("Optimization complete in %.1fs", opt_time)

    collection.flush()

    total_time = time.time() - t0
    log.info(
        "=== DONE: %d examples indexed in %.1fs "
        "(insert %.1fs + optimize %.1fs) → %s ===",
        total, total_time, insert_time, opt_time, db_path,
    )

    stats = collection.stats
    log.info("Collection stats: %s", stats)


if __name__ == "__main__":
    main()
