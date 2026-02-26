"""Paraphrase generator for training data augmentation.

Generates diverse NL variants from seed examples using rule-based
transformations: colloquial, formal, terse, verbose, and question styles.
"""

from __future__ import annotations

import random
import re
from typing import Any

# fmt: off

# ── Transformation patterns ───────────────────────────────────────────────────

# Imperative → question transformations
_QUESTION_PREFIXES: list[str] = [
    "how do I {verb_phrase}",
    "how can I {verb_phrase}",
    "what's the command to {verb_phrase}",
    "what command do I use to {verb_phrase}",
    "can you {verb_phrase}",
    "could you {verb_phrase}",
    "I need to {verb_phrase}",
    "I want to {verb_phrase}",
    "help me {verb_phrase}",
    "I'm trying to {verb_phrase}",
]

# Casual/colloquial variants
_CASUAL_PREFIXES: list[str] = [
    "hey, {rest}",
    "yo, {rest}",
    "quick question: {rest}",
    "so I need to {rest}",
    "can ya {rest}",
    "gimme a command to {rest}",
    "show me how to {rest}",
    "just {rest}",
    "{rest} please",
    "{rest}, thanks",
]

# Formal variants
_FORMAL_PREFIXES: list[str] = [
    "please {rest}",
    "kindly {rest}",
    "I would like to {rest}",
    "could you please {rest}",
    "I need assistance to {rest}",
    "please provide a command to {rest}",
    "I require a command that will {rest}",
    "would you be so kind as to {rest}",
]

# Terse/abbreviated variants
_TERSE_TRANSFORMS: list[tuple[str, str]] = [
    (r"\ball files\b", "all"),
    (r"\bthe file\b", "file"),
    (r"\bthe directory\b", "dir"),
    (r"\bdirectory\b", "dir"),
    (r"\brecursively\b", "recursively"),
    (r"\bplease\b", ""),
    (r"\bcould you\b", ""),
    (r"\bI want to\b", ""),
    (r"\bI need to\b", ""),
    (r"\bshow me\b", "show"),
    (r"\bunder the\b", "under"),
    (r"\bin the\b", "in"),
]

# Verbose expansions
_VERBOSE_INSERTS: list[str] = [
    "I need you to ",
    "what I want is to ",
    "the task is to ",
    "I'm looking for a way to ",
    "my goal is to ",
    "I'd appreciate if you could ",
]

# Synonym mappings for common verbs/nouns
_SYNONYMS: dict[str, list[str]] = {
    "find": ["search for", "locate", "look for", "discover", "hunt for"],
    "delete": ["remove", "erase", "get rid of", "wipe", "clean up"],
    "copy": ["duplicate", "replicate", "make a copy of", "clone"],
    "move": ["relocate", "transfer", "put", "shift", "bring"],
    "show": ["display", "print", "output", "reveal", "view"],
    "list": ["show", "display", "enumerate", "print out"],
    "install": ["set up", "add", "get", "put in"],
    "remove": ["uninstall", "delete", "get rid of", "take out"],
    "start": ["launch", "begin", "fire up", "bring up", "activate", "turn on"],
    "stop": ["halt", "shut down", "terminate", "bring down", "turn off", "kill"],
    "restart": ["reboot", "bounce", "cycle", "reload"],
    "create": ["make", "set up", "generate", "add"],
    "check": ["verify", "inspect", "examine", "look at", "see"],
    "search": ["look for", "find", "grep for", "scan for"],
    "change": ["modify", "update", "alter", "set", "adjust"],
    "download": ["fetch", "grab", "pull", "get", "retrieve"],
    "upload": ["push", "send", "transfer", "put"],
    "compress": ["zip", "archive", "pack", "bundle"],
    "extract": ["unzip", "unpack", "decompress", "untar"],
    "connect": ["log in to", "access", "ssh into", "reach"],
    "kill": ["terminate", "end", "stop", "force quit"],
    "monitor": ["watch", "track", "follow", "observe"],
    "files": ["documents", "items"],
    "directory": ["folder", "dir", "path"],
    "server": ["machine", "host", "box", "system"],
    "big": ["large", "huge", "massive"],
    "all": ["every", "each", "the entire set of"],
    "permissions": ["access rights", "file mode", "privileges"],
}

# fmt: on


def _apply_synonym(text: str, rng: random.Random) -> str:
    """Replace one random word with a synonym."""
    words_in_text = text.lower().split()
    replaceable = [w for w in _SYNONYMS if w in words_in_text]
    if not replaceable:
        return text

    word = rng.choice(replaceable)
    synonym = rng.choice(_SYNONYMS[word])
    # Replace first occurrence, case-insensitive
    return re.sub(r"\b" + re.escape(word) + r"\b", synonym, text, count=1, flags=re.IGNORECASE)


def _make_question(text: str, rng: random.Random) -> str:
    """Transform imperative to question form."""
    # Strip leading verbs to get the verb phrase
    verb_phrase = text.strip().rstrip("?.")
    template = rng.choice(_QUESTION_PREFIXES)
    result = template.format(verb_phrase=verb_phrase)
    if not result.endswith("?"):
        result += "?"
    return result


def _make_casual(text: str, rng: random.Random) -> str:
    """Make text more casual/colloquial."""
    rest = text.strip().rstrip(".")
    # Lowercase first letter if it's a sentence start
    if rest and rest[0].isupper():
        rest = rest[0].lower() + rest[1:]
    template = rng.choice(_CASUAL_PREFIXES)
    return template.format(rest=rest)


def _make_formal(text: str, rng: random.Random) -> str:
    """Make text more formal."""
    rest = text.strip().rstrip(".")
    if rest and rest[0].isupper():
        rest = rest[0].lower() + rest[1:]
    template = rng.choice(_FORMAL_PREFIXES)
    return template.format(rest=rest)


def _make_terse(text: str, rng: random.Random) -> str:
    """Make text shorter/more terse."""
    result = text
    for pattern, replacement in _TERSE_TRANSFORMS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    # Remove double spaces
    result = re.sub(r"\s+", " ", result).strip()
    return result


def _make_verbose(text: str, rng: random.Random) -> str:
    """Make text more verbose/detailed."""
    insert = rng.choice(_VERBOSE_INSERTS)
    rest = text.strip()
    if rest and rest[0].isupper():
        rest = rest[0].lower() + rest[1:]
    return f"{insert}{rest}"


# Style functions with their weights (probability of being selected)
_STYLES: list[tuple[str, Any, float]] = [
    ("synonym", _apply_synonym, 0.25),
    ("question", _make_question, 0.20),
    ("casual", _make_casual, 0.15),
    ("formal", _make_formal, 0.15),
    ("terse", _make_terse, 0.10),
    ("verbose", _make_verbose, 0.15),
]


def paraphrase_one(
    text: str,
    rng: random.Random,
    style: str | None = None,
) -> tuple[str, str]:
    """Generate one paraphrase of the given text.

    Returns (paraphrased_text, style_name).
    """
    if style is None:
        names = [s[0] for s in _STYLES]
        weights = [s[2] for s in _STYLES]
        style = rng.choices(names, weights=weights, k=1)[0]

    style_func = next(s[1] for s in _STYLES if s[0] == style)
    result = style_func(text, rng)

    # Ensure non-empty
    if not result.strip():
        result = text

    return result, style


def paraphrase_example(
    example: dict[str, Any],
    rng: random.Random,
    n_variants: int = 5,
) -> list[dict[str, Any]]:
    """Generate n paraphrase variants of a single training example.

    Returns list of new examples with modified nl_request and updated tags.
    """
    variants: list[dict[str, Any]] = []
    seen: set[str] = {example["nl_request"].lower().strip()}

    # Ensure we try each style at least once if n_variants >= len(_STYLES)
    styles_to_try: list[str | None] = []
    if n_variants >= len(_STYLES):
        styles_to_try = [s[0] for s in _STYLES]
        styles_to_try.extend([None] * (n_variants - len(_STYLES)))
    else:
        styles_to_try = [None] * n_variants

    rng.shuffle(styles_to_try)

    attempts = 0
    max_attempts = n_variants * 3  # Prevent infinite loops

    for style in styles_to_try:
        if len(variants) >= n_variants:
            break
        if attempts >= max_attempts:
            break
        attempts += 1

        text, style_name = paraphrase_one(example["nl_request"], rng, style=style)
        normalized = text.lower().strip()

        if normalized in seen:
            continue
        seen.add(normalized)

        variant = {
            "id": "",  # Will be assigned later
            "source": "paraphrase",
            "license": "MIT",
            "nl_request": text,
            "context_line": example.get("context_line", "debian bash non-root safe"),
            "expected_intent": example["expected_intent"],
            "expected_slots": example.get("expected_slots", {}),
            "tags": list(set(example.get("tags", []) + ["paraphrase", style_name])),
        }
        variants.append(variant)

    return variants


def generate_paraphrases(
    seed_examples: list[dict[str, Any]],
    variants_per_example: int = 5,
    target_count: int = 4000,
    seed: int = 43,
) -> list[dict[str, Any]]:
    """Generate paraphrase variants from seed examples.

    Args:
        seed_examples: Original training examples to paraphrase.
        variants_per_example: Max variants per seed example.
        target_count: Target total number of paraphrases.
        seed: Random seed.

    Returns:
        List of paraphrased examples.
    """
    rng = random.Random(seed)
    all_paraphrases: list[dict[str, Any]] = []

    # Calculate how many seeds to use
    if not seed_examples:
        return []

    seeds_needed = min(len(seed_examples), target_count // variants_per_example + 1)

    # Sample seeds (prefer diverse intents)
    intent_groups: dict[str, list[dict[str, Any]]] = {}
    for ex in seed_examples:
        intent = ex.get("expected_intent", "unknown")
        if intent not in intent_groups:
            intent_groups[intent] = []
        intent_groups[intent].append(ex)

    # Round-robin sampling across intents
    selected_seeds: list[dict[str, Any]] = []
    intent_list = sorted(intent_groups.keys())
    idx = 0
    while len(selected_seeds) < seeds_needed:
        intent = intent_list[idx % len(intent_list)]
        group = intent_groups[intent]
        if group:
            selected_seeds.append(rng.choice(group))
        idx += 1
        if idx >= len(intent_list) * 100:  # Safety limit
            break

    # Generate paraphrases
    for seed_ex in selected_seeds:
        variants = paraphrase_example(seed_ex, rng, n_variants=variants_per_example)
        all_paraphrases.extend(variants)
        if len(all_paraphrases) >= target_count:
            break

    # Truncate to target
    all_paraphrases = all_paraphrases[:target_count]

    # Shuffle and re-ID
    rng.shuffle(all_paraphrases)
    for i, ex in enumerate(all_paraphrases):
        ex["id"] = f"PP-{i:05d}"

    return all_paraphrases
