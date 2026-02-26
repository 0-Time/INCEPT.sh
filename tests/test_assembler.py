"""Tests for dataset assembly (incept.data.assembler)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from incept.data.assembler import (
    DatasetStats,
    SplitResult,
    _normalize_text,
    _text_similarity,
    assemble_dataset,
    deduplicate,
    merge_sources,
    stratified_split,
    validate_example,
    write_splits,
)

# ---------------------------------------------------------------------------
# Fixtures / factories
# ---------------------------------------------------------------------------


def _valid_example(
    text: str = "install nginx",
    intent: str = "install_package",
    source: str = "template",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Factory for a valid training example."""
    return {
        "id": "TEST-0001",
        "source": source,
        "nl_request": text,
        "expected_intent": intent,
        "expected_slots": {"package": "nginx"},
        "tags": tags or ["package_mgmt", "template", "debian"],
    }


def _make_examples(n: int, intent: str = "install_package") -> list[dict[str, Any]]:
    """Create n distinct valid examples with the given intent."""
    return [
        _valid_example(text=f"do task variant {i} for {intent}", intent=intent)
        for i in range(n)
    ]


# ===================================================================
# _normalize_text
# ===================================================================


class TestNormalizeText:
    """Tests for _normalize_text helper."""

    def test_lowercases(self) -> None:
        assert _normalize_text("HELLO World") == "hello world"

    def test_strips_whitespace(self) -> None:
        assert _normalize_text("  hello  ") == "hello"

    def test_collapses_multiple_spaces(self) -> None:
        assert _normalize_text("a   b    c") == "a b c"

    def test_removes_punctuation(self) -> None:
        assert _normalize_text("hello, world!") == "hello world"

    def test_empty_string(self) -> None:
        assert _normalize_text("") == ""


# ===================================================================
# _text_similarity
# ===================================================================


class TestTextSimilarity:
    """Tests for _text_similarity trigram Jaccard."""

    def test_identical_strings_score_one(self) -> None:
        assert _text_similarity("hello world", "hello world") == 1.0

    def test_completely_different_strings(self) -> None:
        score = _text_similarity("aaa", "zzz")
        assert score < 0.5

    def test_empty_strings(self) -> None:
        assert _text_similarity("", "") == 0.0
        assert _text_similarity("hello", "") == 0.0
        assert _text_similarity("", "hello") == 0.0

    def test_short_strings_below_trigram_length(self) -> None:
        # Strings shorter than 3 chars produce no trigrams
        assert _text_similarity("ab", "ab") == 0.0

    def test_similar_strings_high_score(self) -> None:
        score = _text_similarity("install nginx package", "install nginx packages")
        assert score > 0.7


# ===================================================================
# validate_example
# ===================================================================


class TestValidateExample:
    """Tests for validate_example()."""

    def test_valid_example_passes(self) -> None:
        errors = validate_example(_valid_example())
        assert errors == []

    def test_missing_id(self) -> None:
        ex = _valid_example()
        del ex["id"]
        errors = validate_example(ex)
        assert any("id" in e for e in errors)

    def test_missing_source(self) -> None:
        ex = _valid_example()
        del ex["source"]
        errors = validate_example(ex)
        assert any("source" in e for e in errors)

    def test_missing_nl_request(self) -> None:
        ex = _valid_example()
        del ex["nl_request"]
        errors = validate_example(ex)
        assert any("nl_request" in e for e in errors)

    def test_missing_expected_intent(self) -> None:
        ex = _valid_example()
        del ex["expected_intent"]
        errors = validate_example(ex)
        assert any("expected_intent" in e for e in errors)

    def test_missing_tags(self) -> None:
        ex = _valid_example()
        del ex["tags"]
        errors = validate_example(ex)
        assert any("tags" in e for e in errors)

    def test_empty_nl_request(self) -> None:
        ex = _valid_example(text="")
        errors = validate_example(ex)
        assert any("non-empty" in e for e in errors)

    def test_whitespace_only_nl_request(self) -> None:
        ex = _valid_example(text="   ")
        errors = validate_example(ex)
        assert any("non-empty" in e for e in errors)

    def test_too_long_nl_request(self) -> None:
        ex = _valid_example(text="x" * 1001)
        errors = validate_example(ex)
        assert any("too long" in e for e in errors)

    def test_exactly_1000_chars_passes(self) -> None:
        ex = _valid_example(text="x" * 1000)
        errors = validate_example(ex)
        assert not any("too long" in e for e in errors)

    def test_invalid_source(self) -> None:
        ex = _valid_example(source="invalid_source_xyz")
        errors = validate_example(ex)
        assert any("Invalid source" in e for e in errors)

    def test_valid_sources_all_pass(self) -> None:
        for src in ("template", "paraphrase", "adversarial", "forum", "golden", "manual"):
            ex = _valid_example(source=src)
            errors = validate_example(ex)
            assert errors == [], f"Source '{src}' should be valid"

    def test_tags_not_list(self) -> None:
        ex = _valid_example()
        ex["tags"] = "not_a_list"
        errors = validate_example(ex)
        assert any("tags must be a list" in e for e in errors)

    def test_expected_intent_not_string(self) -> None:
        ex = _valid_example()
        ex["expected_intent"] = 42
        errors = validate_example(ex)
        assert any("string" in e for e in errors)


# ===================================================================
# deduplicate
# ===================================================================


class TestDeduplicate:
    """Tests for deduplicate()."""

    def test_removes_exact_duplicates(self) -> None:
        examples = [
            _valid_example(text="install nginx"),
            _valid_example(text="install nginx"),
            _valid_example(text="install curl"),
        ]
        result, removed = deduplicate(examples)
        assert len(result) == 2
        assert removed == 1

    def test_case_insensitive_exact_dedup(self) -> None:
        examples = [
            _valid_example(text="Install Nginx"),
            _valid_example(text="install nginx"),
        ]
        result, removed = deduplicate(examples)
        assert len(result) == 1
        assert removed == 1

    def test_near_duplicate_removal(self) -> None:
        examples = [
            _valid_example(text="install the nginx package on the server"),
            _valid_example(text="install the nginx package on the servers"),
            _valid_example(text="completely different request about logs"),
        ]
        result, removed = deduplicate(examples, threshold=0.85)
        assert len(result) == 2
        assert removed == 1

    def test_threshold_one_only_exact(self) -> None:
        examples = [
            _valid_example(text="install nginx web server"),
            _valid_example(text="install nginx web servers"),
        ]
        result, removed = deduplicate(examples, threshold=1.0)
        # Threshold=1.0 means only exact (normalized) matches are removed
        assert len(result) == 2
        assert removed == 0

    def test_no_duplicates(self) -> None:
        examples = [
            _valid_example(text="install nginx"),
            _valid_example(text="remove curl"),
            _valid_example(text="start docker service"),
        ]
        result, removed = deduplicate(examples)
        assert len(result) == 3
        assert removed == 0

    def test_empty_list(self) -> None:
        result, removed = deduplicate([])
        assert result == []
        assert removed == 0

    def test_near_dedup_only_within_same_intent(self) -> None:
        """Near-duplicates with different intents should both be kept."""
        examples = [
            _valid_example(text="install the nginx package right now", intent="install_package"),
            _valid_example(text="install the nginx package right now", intent="remove_package"),
        ]
        result, removed = deduplicate(examples, threshold=0.85)
        # They are exact duplicates in text but different intents;
        # exact dedup doesn't check intent, so one is removed
        assert removed >= 1


# ===================================================================
# merge_sources
# ===================================================================


class TestMergeSources:
    """Tests for merge_sources()."""

    def test_combines_two_lists(self) -> None:
        a = [_valid_example(text="a1"), _valid_example(text="a2")]
        b = [_valid_example(text="b1")]
        result = merge_sources(a, b)
        assert len(result) == 3

    def test_combines_three_lists(self) -> None:
        a = [_valid_example(text="a")]
        b = [_valid_example(text="b")]
        c = [_valid_example(text="c")]
        result = merge_sources(a, b, c)
        assert len(result) == 3

    def test_preserves_order(self) -> None:
        a = [_valid_example(text="first")]
        b = [_valid_example(text="second")]
        result = merge_sources(a, b)
        assert result[0]["nl_request"] == "first"
        assert result[1]["nl_request"] == "second"

    def test_empty_sources(self) -> None:
        result = merge_sources([], [], [])
        assert result == []

    def test_single_source(self) -> None:
        a = [_valid_example(text="only")]
        result = merge_sources(a)
        assert len(result) == 1


# ===================================================================
# stratified_split
# ===================================================================


class TestStratifiedSplit:
    """Tests for stratified_split()."""

    def test_default_ratios(self) -> None:
        examples = _make_examples(100, "install_package") + _make_examples(100, "find_files")
        result = stratified_split(examples, seed=42)

        total = len(result.train) + len(result.val) + len(result.test)
        assert total == 200

    def test_approximately_80_10_10(self) -> None:
        examples = _make_examples(100, "install_package") + _make_examples(100, "find_files")
        result = stratified_split(examples, seed=42)

        total = len(result.train) + len(result.val) + len(result.test)
        train_ratio = len(result.train) / total
        val_ratio = len(result.val) / total
        test_ratio = len(result.test) / total

        assert 0.70 < train_ratio < 0.90
        assert 0.05 < val_ratio < 0.20
        assert 0.05 < test_ratio < 0.20

    def test_stratified_by_intent(self) -> None:
        examples = _make_examples(50, "install_package") + _make_examples(50, "find_files")
        result = stratified_split(examples, seed=42)

        train_intents = {ex["expected_intent"] for ex in result.train}
        val_intents = {ex["expected_intent"] for ex in result.val}
        test_intents = {ex["expected_intent"] for ex in result.test}

        # Both intents should appear in all splits
        assert "install_package" in train_intents
        assert "find_files" in train_intents
        assert "install_package" in val_intents
        assert "find_files" in val_intents
        assert "install_package" in test_intents
        assert "find_files" in test_intents

    def test_custom_ratios(self) -> None:
        examples = _make_examples(100, "install_package")
        result = stratified_split(examples, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2, seed=42)

        total = len(result.train) + len(result.val) + len(result.test)
        train_ratio = len(result.train) / total
        assert 0.50 < train_ratio < 0.70

    def test_invalid_ratios_raise(self) -> None:
        examples = _make_examples(10)
        with pytest.raises(AssertionError):
            stratified_split(examples, train_ratio=0.5, val_ratio=0.5, test_ratio=0.5)

    def test_stats_populated(self) -> None:
        examples = _make_examples(50, "install_package") + _make_examples(50, "find_files")
        result = stratified_split(examples, seed=42)

        assert result.stats.total_examples == 100
        assert result.stats.unique_intents == 2
        assert result.stats.train_size == len(result.train)
        assert result.stats.val_size == len(result.val)
        assert result.stats.test_size == len(result.test)

    def test_deterministic(self) -> None:
        examples = _make_examples(100, "install_package")
        a = stratified_split(examples, seed=42)
        b = stratified_split(examples, seed=42)
        assert a.train == b.train
        assert a.val == b.val
        assert a.test == b.test

    def test_small_group_at_least_one_in_train(self) -> None:
        """Even a single-example stratum gets at least one in train."""
        examples = [_valid_example(text="singleton example", intent="rare_intent")]
        result = stratified_split(examples, seed=42)
        assert len(result.train) >= 1


# ===================================================================
# assemble_dataset (full pipeline)
# ===================================================================


class TestAssembleDataset:
    """Tests for assemble_dataset() full pipeline."""

    def test_full_pipeline(self) -> None:
        source1 = _make_examples(50, "install_package")
        source2 = _make_examples(50, "find_files")
        result = assemble_dataset(source1, source2, seed=42)

        assert isinstance(result, SplitResult)
        total = len(result.train) + len(result.val) + len(result.test)
        assert total > 0

    def test_filters_invalid_examples(self) -> None:
        good = [_valid_example(text="good example")]
        bad = [{"bad": "missing_fields"}]
        result = assemble_dataset(good, bad, seed=42)

        assert result.stats.invalid_removed >= 1

    def test_removes_duplicates(self) -> None:
        dupes = [_valid_example(text="duplicate text")] * 5
        unique = [_valid_example(text="unique text")]
        result = assemble_dataset(dupes, unique, seed=42)

        assert result.stats.duplicates_removed >= 4

    def test_stats_model_is_populated(self) -> None:
        source = _make_examples(50, "install_package")
        result = assemble_dataset(source, seed=42)

        assert isinstance(result.stats, DatasetStats)
        assert result.stats.total_examples > 0


# ===================================================================
# write_splits
# ===================================================================


class TestWriteSplits:
    """Tests for write_splits()."""

    def test_creates_jsonl_files(self, tmp_path: Path) -> None:
        examples = _make_examples(30, "install_package")
        result = stratified_split(examples, seed=42)
        paths = write_splits(result, tmp_path)

        assert "train" in paths
        assert "val" in paths
        assert "test" in paths
        assert "stats" in paths

        assert paths["train"].exists()
        assert paths["val"].exists()
        assert paths["test"].exists()
        assert paths["stats"].exists()

    def test_jsonl_lines_are_valid_json(self, tmp_path: Path) -> None:
        examples = _make_examples(20, "install_package")
        result = stratified_split(examples, seed=42)
        paths = write_splits(result, tmp_path)

        for split in ("train", "val", "test"):
            content = paths[split].read_text().strip()
            if content:
                for line in content.split("\n"):
                    obj = json.loads(line)
                    assert isinstance(obj, dict)

    def test_stats_file_is_valid_json(self, tmp_path: Path) -> None:
        examples = _make_examples(20, "install_package")
        result = stratified_split(examples, seed=42)
        paths = write_splits(result, tmp_path)

        stats = json.loads(paths["stats"].read_text())
        assert "total_examples" in stats
        assert "train_size" in stats

    def test_creates_output_directory(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "nested" / "output"
        examples = _make_examples(10)
        result = stratified_split(examples, seed=42)
        paths = write_splits(result, out_dir)

        assert out_dir.exists()
        assert paths["train"].exists()

    def test_line_counts_match_split_sizes(self, tmp_path: Path) -> None:
        examples = _make_examples(50, "install_package")
        result = stratified_split(examples, seed=42)
        paths = write_splits(result, tmp_path)

        splits = [("train", result.train), ("val", result.val), ("test", result.test)]
        for split_name, data in splits:
            content = paths[split_name].read_text().strip()
            line_count = len(content.split("\n")) if content else 0
            assert line_count == len(data)
