"""Dataset assembly: merge, deduplicate, validate, and split.

Combines data from all sources (templates, paraphrases, adversarial, forum)
into a single clean dataset with stratified train/val/test splits.
"""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# Required fields in every training example
_REQUIRED_FIELDS = frozenset({
    "id", "source", "nl_request", "expected_intent", "tags",
})

# Valid sources
_VALID_SOURCES = frozenset({
    "template", "paraphrase", "adversarial", "forum", "golden", "manual",
})


class DatasetStats(BaseModel):
    """Statistics for an assembled dataset."""

    total_examples: int = 0
    unique_intents: int = 0
    intent_distribution: dict[str, int] = Field(default_factory=dict)
    source_distribution: dict[str, int] = Field(default_factory=dict)
    tag_distribution: dict[str, int] = Field(default_factory=dict)
    duplicates_removed: int = 0
    invalid_removed: int = 0
    train_size: int = 0
    val_size: int = 0
    test_size: int = 0


class SplitResult(BaseModel):
    """Result of dataset splitting."""

    train: list[dict[str, Any]] = Field(default_factory=list)
    val: list[dict[str, Any]] = Field(default_factory=list)
    test: list[dict[str, Any]] = Field(default_factory=list)
    stats: DatasetStats = Field(default_factory=DatasetStats)


def _normalize_text(text: str) -> str:
    """Normalize text for deduplication comparison."""
    import re

    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text


def _text_similarity(a: str, b: str) -> float:
    """Compute simple character-level similarity (Jaccard on character trigrams)."""
    if not a or not b:
        return 0.0

    def trigrams(s: str) -> set[str]:
        return {s[i:i + 3] for i in range(len(s) - 2)}

    tri_a = trigrams(a)
    tri_b = trigrams(b)

    if not tri_a or not tri_b:
        return 0.0

    intersection = len(tri_a & tri_b)
    union = len(tri_a | tri_b)
    return intersection / union if union > 0 else 0.0


def validate_example(example: dict[str, Any]) -> list[str]:
    """Validate a single training example.

    Returns list of error messages (empty = valid).
    """
    errors: list[str] = []

    for field in _REQUIRED_FIELDS:
        if field not in example:
            errors.append(f"Missing required field: {field}")

    if "nl_request" in example:
        text = example["nl_request"]
        if not isinstance(text, str) or not text.strip():
            errors.append("nl_request must be a non-empty string")
        elif len(text) > 1000:
            errors.append(f"nl_request too long: {len(text)} chars (max 1000)")

    if "expected_intent" in example:
        intent = example["expected_intent"]
        if not isinstance(intent, str):
            errors.append("expected_intent must be a string")

    if "tags" in example:
        tags = example["tags"]
        if not isinstance(tags, list):
            errors.append("tags must be a list")

    if "source" in example:
        source = example["source"]
        if source and source not in _VALID_SOURCES:
            errors.append(f"Invalid source: {source}")

    return errors


def deduplicate(
    examples: list[dict[str, Any]],
    threshold: float = 0.95,
) -> tuple[list[dict[str, Any]], int]:
    """Remove near-duplicate examples by NL similarity.

    Uses a two-pass approach:
    1. Exact match on normalized text (fast)
    2. Trigram similarity for near-duplicates within same intent (slower)

    Returns (deduplicated_list, num_removed).
    """
    # Pass 1: Exact dedup
    seen_exact: dict[str, int] = {}
    unique_pass1: list[dict[str, Any]] = []
    exact_dupes = 0

    for ex in examples:
        key = _normalize_text(ex.get("nl_request", ""))
        if key in seen_exact:
            exact_dupes += 1
        else:
            seen_exact[key] = len(unique_pass1)
            unique_pass1.append(ex)

    # Pass 2: Near-duplicate dedup within same intent
    # Group by intent for efficiency
    intent_groups: dict[str, list[tuple[int, str]]] = {}
    for i, ex in enumerate(unique_pass1):
        intent = ex.get("expected_intent", "")
        normalized = _normalize_text(ex.get("nl_request", ""))
        if intent not in intent_groups:
            intent_groups[intent] = []
        intent_groups[intent].append((i, normalized))

    remove_indices: set[int] = set()
    for _intent, group in intent_groups.items():
        # Only check within groups (O(n^2) within each intent, but groups are small)
        if len(group) > 5000:
            # Skip near-dedup for very large groups to avoid O(n^2) blowup
            continue
        for i in range(len(group)):
            if group[i][0] in remove_indices:
                continue
            for j in range(i + 1, len(group)):
                if group[j][0] in remove_indices:
                    continue
                sim = _text_similarity(group[i][1], group[j][1])
                if sim >= threshold:
                    remove_indices.add(group[j][0])

    near_dupes = len(remove_indices)
    deduplicated = [
        ex for i, ex in enumerate(unique_pass1)
        if i not in remove_indices
    ]

    return deduplicated, exact_dupes + near_dupes


def merge_sources(*sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge multiple data sources into a single list."""
    merged: list[dict[str, Any]] = []
    for source in sources:
        merged.extend(source)
    return merged


def stratified_split(
    examples: list[dict[str, Any]],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> SplitResult:
    """Split examples into train/val/test with stratification by intent.

    Stratifies by:
    1. Intent label (primary)
    2. Source type (secondary)
    3. Adversarial tag (ensures adversarial examples in all splits)
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "Ratios must sum to 1.0"

    rng = random.Random(seed)

    # Group by (intent, is_adversarial) for stratification
    strata: dict[str, list[dict[str, Any]]] = {}
    for ex in examples:
        intent = ex.get("expected_intent", "unknown")
        is_adv = "adversarial" in ex.get("tags", [])
        key = f"{intent}__{'adv' if is_adv else 'std'}"
        if key not in strata:
            strata[key] = []
        strata[key].append(ex)

    train: list[dict[str, Any]] = []
    val: list[dict[str, Any]] = []
    test: list[dict[str, Any]] = []

    for _key, group in sorted(strata.items()):
        rng.shuffle(group)
        n = len(group)
        n_val = max(1, round(n * val_ratio)) if n >= 3 else 0
        n_test = max(1, round(n * test_ratio)) if n >= 3 else 0
        n_train = n - n_val - n_test

        # Ensure at least 1 in train
        if n_train <= 0 and n > 0:
            n_train = 1
            if n_val > 0:
                n_val -= 1
            elif n_test > 0:
                n_test -= 1

        train.extend(group[:n_train])
        val.extend(group[n_train:n_train + n_val])
        test.extend(group[n_train + n_val:])

    # Shuffle each split
    rng.shuffle(train)
    rng.shuffle(val)
    rng.shuffle(test)

    # Compute stats
    all_examples = train + val + test
    intent_counts = Counter(ex["expected_intent"] for ex in all_examples)
    source_counts = Counter(ex.get("source", "unknown") for ex in all_examples)
    tag_counts: Counter[str] = Counter()
    for ex in all_examples:
        for tag in ex.get("tags", []):
            tag_counts[tag] += 1

    stats = DatasetStats(
        total_examples=len(all_examples),
        unique_intents=len(intent_counts),
        intent_distribution=dict(intent_counts.most_common()),
        source_distribution=dict(source_counts.most_common()),
        tag_distribution=dict(tag_counts.most_common(30)),
        train_size=len(train),
        val_size=len(val),
        test_size=len(test),
    )

    return SplitResult(train=train, val=val, test=test, stats=stats)


def assemble_dataset(
    *sources: list[dict[str, Any]],
    dedup_threshold: float = 0.95,
    seed: int = 42,
) -> SplitResult:
    """Full assembly pipeline: merge → validate → dedup → split.

    Returns SplitResult with train/val/test splits and statistics.
    """
    # Merge
    merged = merge_sources(*sources)

    # Validate
    valid: list[dict[str, Any]] = []
    invalid_count = 0
    for ex in merged:
        errors = validate_example(ex)
        if not errors:
            valid.append(ex)
        else:
            invalid_count += 1

    # Deduplicate
    deduped, dupes_removed = deduplicate(valid, threshold=dedup_threshold)

    # Split
    result = stratified_split(deduped, seed=seed)

    # Update stats
    result.stats.duplicates_removed = dupes_removed
    result.stats.invalid_removed = invalid_count

    return result


def write_splits(
    result: SplitResult,
    output_dir: str | Path,
) -> dict[str, Path]:
    """Write train/val/test splits to JSONL files.

    Returns dict of split name -> file path.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    paths: dict[str, Path] = {}
    for split_name, data in [
        ("train", result.train),
        ("val", result.val),
        ("test", result.test),
    ]:
        path = out / f"{split_name}.jsonl"
        with open(path, "w") as f:
            for example in data:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")
        paths[split_name] = path

    # Write stats
    stats_path = out / "stats.json"
    with open(stats_path, "w") as f:
        json.dump(result.stats.model_dump(), f, indent=2)
    paths["stats"] = stats_path

    return paths
