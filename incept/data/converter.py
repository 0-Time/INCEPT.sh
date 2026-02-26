"""Training data format conversion for model fine-tuning.

Converts INCEPT JSONL examples to model-specific instruction formats:
1. Intent classification format
2. Slot filling format
3. DPO preference pairs for near-miss intents
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any


def to_intent_format(example: dict[str, Any]) -> dict[str, str]:
    """Convert a single example to intent classification training format.

    Format:
        <s>[INST] Given the context and request, classify the intent.
        [CONTEXT] {context_line}
        [REQUEST] {nl_request}
        [INTENT] [/INST]{intent_label}</s>
    """
    context = example.get("context_line", "debian bash non-root safe")
    request = example.get("nl_request", "")
    intent = example.get("expected_intent", "")

    prompt = (
        "Given the context and request, classify the intent.\n"
        f"[CONTEXT] {context}\n"
        f"[REQUEST] {request}\n"
        "[INTENT]"
    )
    completion = intent

    return {
        "prompt": f"<s>[INST] {prompt} [/INST]",
        "completion": f"{completion}</s>",
        "id": example.get("id", ""),
        "intent": intent,
    }


def to_slot_format(example: dict[str, Any]) -> dict[str, str]:
    """Convert a single example to slot filling training format.

    Format:
        <s>[INST] Given the context, request, and intent, extract parameter slots.
        [CONTEXT] {context_line}
        [REQUEST] {nl_request}
        [INTENT] {intent_label}
        [SLOTS] [/INST]{json_slots}</s>
    """
    context = example.get("context_line", "debian bash non-root safe")
    request = example.get("nl_request", "")
    intent = example.get("expected_intent", "")
    slots = example.get("expected_slots", {})

    prompt = (
        "Given the context, request, and intent, extract parameter slots.\n"
        f"[CONTEXT] {context}\n"
        f"[REQUEST] {request}\n"
        f"[INTENT] {intent}\n"
        "[SLOTS]"
    )
    completion = json.dumps(slots, ensure_ascii=False, sort_keys=True)

    return {
        "prompt": f"<s>[INST] {prompt} [/INST]",
        "completion": f"{completion}</s>",
        "id": example.get("id", ""),
        "intent": intent,
    }


def generate_dpo_pairs(
    examples: list[dict[str, Any]],
    target_count: int = 1000,
    seed: int = 44,
) -> list[dict[str, Any]]:
    """Generate DPO preference pairs from near-miss intent examples.

    For each near-miss example, creates a pair where:
    - chosen: correct intent classification
    - rejected: distractor intent classification

    Returns list of DPO pair dicts.
    """
    rng = random.Random(seed)

    # Find examples with near_miss or distractor tags
    near_miss_examples = [
        ex for ex in examples
        if any("distractor" in t or "near_miss" in t for t in ex.get("tags", []))
    ]

    # Also find examples where we can create synthetic distractors
    # Group by intent for cross-intent pairing
    intent_groups: dict[str, list[dict[str, Any]]] = {}
    for ex in examples:
        intent = ex.get("expected_intent", "")
        if intent and intent not in ("CLARIFY", "OUT_OF_SCOPE", "UNSAFE_REQUEST"):
            if intent not in intent_groups:
                intent_groups[intent] = []
            intent_groups[intent].append(ex)

    pairs: list[dict[str, Any]] = []
    intents = sorted(intent_groups.keys())

    # Phase 1: DPO pairs from near-miss examples
    for ex in near_miss_examples:
        if len(pairs) >= target_count:
            break

        correct_intent = ex["expected_intent"]
        # Find distractor intent from tags
        distractor = None
        for tag in ex.get("tags", []):
            if tag.startswith("distractor_"):
                distractor = tag.replace("distractor_", "")
                break

        if not distractor:
            # Pick a similar intent as distractor
            if correct_intent in intents:
                idx = intents.index(correct_intent)
                distractor_idx = (idx + 1) % len(intents)
                distractor = intents[distractor_idx]
            else:
                continue

        context = ex.get("context_line", "debian bash non-root safe")
        request = ex.get("nl_request", "")

        prompt = (
            "Given the context and request, classify the intent.\n"
            f"[CONTEXT] {context}\n"
            f"[REQUEST] {request}\n"
            "[INTENT]"
        )

        pair = {
            "id": f"DPO-{len(pairs):05d}",
            "prompt": f"<s>[INST] {prompt} [/INST]",
            "chosen": f"{correct_intent}</s>",
            "rejected": f"{distractor}</s>",
            "source_id": ex.get("id", ""),
        }
        pairs.append(pair)

    # Phase 2: Synthetic pairs from cross-intent examples
    while len(pairs) < target_count and intents:
        # Pick a random example
        intent = rng.choice(intents)
        group = intent_groups.get(intent, [])
        if not group:
            continue

        ex = rng.choice(group)
        # Pick a different intent as distractor
        other_intents = [i for i in intents if i != intent]
        if not other_intents:
            break
        distractor = rng.choice(other_intents)

        context = ex.get("context_line", "debian bash non-root safe")
        request = ex.get("nl_request", "")

        prompt = (
            "Given the context and request, classify the intent.\n"
            f"[CONTEXT] {context}\n"
            f"[REQUEST] {request}\n"
            "[INTENT]"
        )

        pair = {
            "id": f"DPO-{len(pairs):05d}",
            "prompt": f"<s>[INST] {prompt} [/INST]",
            "chosen": f"{intent}</s>",
            "rejected": f"{distractor}</s>",
            "source_id": ex.get("id", ""),
        }
        pairs.append(pair)

    return pairs[:target_count]


def convert_dataset(
    examples: list[dict[str, Any]],
    output_dir: str | Path,
    generate_dpo: bool = True,
    dpo_count: int = 1000,
) -> dict[str, Path]:
    """Convert full dataset to training formats and write to files.

    Creates:
    - intent_train.jsonl: Intent classification format
    - slot_train.jsonl: Slot filling format
    - dpo_pairs.jsonl: DPO preference pairs (if enabled)

    Returns dict of output name -> file path.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    paths: dict[str, Path] = {}

    # Intent classification format
    intent_path = out / "intent_train.jsonl"
    with open(intent_path, "w") as f:
        for ex in examples:
            record = to_intent_format(ex)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    paths["intent"] = intent_path

    # Slot filling format (skip special intents without meaningful slots)
    slot_path = out / "slot_train.jsonl"
    with open(slot_path, "w") as f:
        for ex in examples:
            if ex.get("expected_intent") in ("CLARIFY", "OUT_OF_SCOPE", "UNSAFE_REQUEST"):
                continue
            if not ex.get("expected_slots"):
                continue
            record = to_slot_format(ex)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    paths["slots"] = slot_path

    # DPO pairs
    if generate_dpo:
        dpo_path = out / "dpo_pairs.jsonl"
        pairs = generate_dpo_pairs(examples, target_count=dpo_count)
        with open(dpo_path, "w") as f:
            for pair in pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        paths["dpo"] = dpo_path

    return paths
