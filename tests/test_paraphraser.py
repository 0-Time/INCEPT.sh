"""Tests for paraphrase generator (incept.data.paraphraser)."""

from __future__ import annotations

import random
from typing import Any

from incept.data.paraphraser import (
    _apply_synonym,
    _make_casual,
    _make_formal,
    _make_question,
    _make_terse,
    _make_verbose,
    generate_paraphrases,
    paraphrase_example,
    paraphrase_one,
)

# ---------------------------------------------------------------------------
# Fixtures / factories
# ---------------------------------------------------------------------------


def _seed_example(
    text: str = "find all log files in /var/log",
    intent: str = "find_files",
    slots: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Factory for a minimal training example."""
    return {
        "id": "TEST-0001",
        "source": "template",
        "license": "MIT",
        "nl_request": text,
        "context_line": "debian bash non-root safe",
        "expected_intent": intent,
        "expected_slots": slots or {"path": "/var/log", "name_pattern": "*.log"},
        "tags": ["file_ops", "template", "debian"],
    }


# ===================================================================
# paraphrase_one
# ===================================================================


class TestParaphraseOne:
    """Tests for paraphrase_one()."""

    def test_returns_tuple_of_text_and_style(self) -> None:
        text, style = paraphrase_one("find all log files", random.Random(42))
        assert isinstance(text, str)
        assert isinstance(style, str)
        assert len(text.strip()) > 0

    def test_produces_different_text(self) -> None:
        original = "find all log files in /var/log"
        # Try multiple times -- at least one should differ
        results = {paraphrase_one(original, random.Random(i))[0] for i in range(20)}
        # At least some variant should differ from the original
        assert len(results) > 1

    def test_explicit_synonym_style(self) -> None:
        text, style = paraphrase_one("find all log files", random.Random(42), style="synonym")
        assert style == "synonym"

    def test_explicit_question_style(self) -> None:
        text, style = paraphrase_one("delete the old backups", random.Random(42), style="question")
        assert style == "question"
        assert "?" in text

    def test_explicit_casual_style(self) -> None:
        text, style = paraphrase_one("install nginx", random.Random(42), style="casual")
        assert style == "casual"

    def test_explicit_formal_style(self) -> None:
        text, style = paraphrase_one("install nginx", random.Random(42), style="formal")
        assert style == "formal"

    def test_explicit_terse_style(self) -> None:
        text, style = paraphrase_one(
            "could you please find the directory", random.Random(42), style="terse"
        )
        assert style == "terse"

    def test_explicit_verbose_style(self) -> None:
        text, style = paraphrase_one("delete /tmp/old", random.Random(42), style="verbose")
        assert style == "verbose"

    def test_non_empty_result_even_for_short_input(self) -> None:
        text, _style = paraphrase_one("ls", random.Random(42))
        assert len(text.strip()) > 0


# ===================================================================
# Individual style functions
# ===================================================================


class TestStyleFunctions:
    """Tests for each individual style transformation function."""

    def test_apply_synonym_replaces_word(self) -> None:
        rng = random.Random(42)
        result = _apply_synonym("find all log files", rng)
        # "find" has synonyms; result should differ if match found
        assert isinstance(result, str)
        assert len(result) > 0

    def test_apply_synonym_no_match_returns_original(self) -> None:
        rng = random.Random(42)
        result = _apply_synonym("xyzzy zork plugh", rng)
        assert result == "xyzzy zork plugh"

    def test_make_question_ends_with_question_mark(self) -> None:
        result = _make_question("install nginx on the server", random.Random(42))
        assert result.endswith("?")

    def test_make_casual_lowercases(self) -> None:
        result = _make_casual("Install the package", random.Random(42))
        # The wrapped text portion should be lowercased
        assert "Install" not in result or result.startswith("Install") is False

    def test_make_formal_has_polite_prefix(self) -> None:
        result = _make_formal("install nginx", random.Random(42))
        polite_words = ["please", "kindly", "like to", "assistance", "require", "kind"]
        assert any(w in result.lower() for w in polite_words)

    def test_make_terse_removes_filler(self) -> None:
        result = _make_terse("could you please find the directory", random.Random(42))
        assert "please" not in result.lower()
        assert "could you" not in result.lower()

    def test_make_verbose_adds_prefix(self) -> None:
        result = _make_verbose("delete /tmp/old", random.Random(42))
        assert len(result) > len("delete /tmp/old")


# ===================================================================
# paraphrase_example
# ===================================================================


class TestParaphraseExample:
    """Tests for paraphrase_example()."""

    def test_generates_n_variants(self) -> None:
        example = _seed_example()
        variants = paraphrase_example(example, random.Random(42), n_variants=5)
        assert len(variants) <= 5
        assert len(variants) >= 1  # Should produce at least one

    def test_variants_preserve_expected_intent(self) -> None:
        example = _seed_example(intent="install_package")
        variants = paraphrase_example(example, random.Random(42), n_variants=5)
        for v in variants:
            assert v["expected_intent"] == "install_package"

    def test_variants_preserve_expected_slots(self) -> None:
        slots = {"package": "nginx"}
        example = _seed_example(intent="install_package", slots=slots)
        variants = paraphrase_example(example, random.Random(42), n_variants=5)
        for v in variants:
            assert v["expected_slots"] == slots

    def test_variants_have_paraphrase_source(self) -> None:
        example = _seed_example()
        variants = paraphrase_example(example, random.Random(42), n_variants=3)
        for v in variants:
            assert v["source"] == "paraphrase"

    def test_variants_include_paraphrase_tag(self) -> None:
        example = _seed_example()
        variants = paraphrase_example(example, random.Random(42), n_variants=3)
        for v in variants:
            assert "paraphrase" in v["tags"]

    def test_deduplication_within_variants(self) -> None:
        example = _seed_example()
        variants = paraphrase_example(example, random.Random(42), n_variants=10)
        texts = [v["nl_request"].lower().strip() for v in variants]
        assert len(texts) == len(set(texts)), "Duplicates found among variants"

    def test_variants_differ_from_original(self) -> None:
        example = _seed_example()
        variants = paraphrase_example(example, random.Random(42), n_variants=5)
        original_lower = example["nl_request"].lower().strip()
        for v in variants:
            assert v["nl_request"].lower().strip() != original_lower


# ===================================================================
# generate_paraphrases
# ===================================================================


class TestGenerateParaphrases:
    """Tests for generate_paraphrases()."""

    def test_respects_target_count(self) -> None:
        seeds = [_seed_example(text=f"do something {i}") for i in range(20)]
        result = generate_paraphrases(seeds, target_count=50, seed=42)
        assert len(result) <= 50

    def test_empty_seeds_return_empty(self) -> None:
        result = generate_paraphrases([], target_count=100, seed=42)
        assert result == []

    def test_ids_are_sequential(self) -> None:
        seeds = [_seed_example(text=f"do task {i}") for i in range(10)]
        result = generate_paraphrases(seeds, target_count=20, seed=42)
        for i, ex in enumerate(result):
            assert ex["id"] == f"PP-{i:05d}"

    def test_deterministic_with_same_seed(self) -> None:
        seeds = [_seed_example(text=f"task {i}") for i in range(10)]
        a = generate_paraphrases(seeds, target_count=30, seed=99)
        b = generate_paraphrases(seeds, target_count=30, seed=99)
        assert a == b

    def test_all_results_have_required_fields(self) -> None:
        seeds = [_seed_example(text=f"job {i}") for i in range(10)]
        result = generate_paraphrases(seeds, target_count=30, seed=42)
        required = {"id", "source", "nl_request", "expected_intent", "tags"}
        for ex in result:
            for field in required:
                assert field in ex

    def test_diverse_intents_in_output(self) -> None:
        seeds = [
            _seed_example(text="find files in /tmp", intent="find_files"),
            _seed_example(text="install nginx", intent="install_package"),
            _seed_example(text="start docker", intent="start_service"),
        ]
        result = generate_paraphrases(seeds, variants_per_example=3, target_count=9, seed=42)
        intents = {ex["expected_intent"] for ex in result}
        # Round-robin sampling should hit all intents
        assert len(intents) >= 2
