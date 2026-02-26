"""Tests for template-based training data generator (incept.data.generator)."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from incept.data.generator import (
    _extract_slots,
    _fill_template,
    _make_id,
    _pick_context,
    dataset_statistics,
    generate_examples,
    generate_to_jsonl,
)
from incept.data.templates import NL_TEMPLATES

# ---------------------------------------------------------------------------
# Fixtures / factories
# ---------------------------------------------------------------------------

_REQUIRED_FIELDS = frozenset({"id", "source", "nl_request", "expected_intent", "tags"})

# A small, controlled template set for isolated tests
_MINI_TEMPLATES: dict[str, list[str]] = {
    "find_files": ["find {name_pattern} in {path}"],
    "copy_files": ["copy {source} to {destination}"],
    "install_package": ["install {package}"],
}


def _small_templates(n_intents: int = 3) -> dict[str, list[str]]:
    """Return the first *n_intents* from the real template map."""
    items = list(NL_TEMPLATES.items())[:n_intents]
    return dict(items)


# ===================================================================
# _extract_slots
# ===================================================================


class TestExtractSlots:
    """Tests for _extract_slots helper."""

    def test_single_slot(self) -> None:
        assert _extract_slots("find {name_pattern} files") == ["name_pattern"]

    def test_multiple_slots(self) -> None:
        result = _extract_slots("copy {source} to {destination}")
        assert result == ["source", "destination"]

    def test_no_slots(self) -> None:
        assert _extract_slots("list all cron jobs") == []

    def test_repeated_slot(self) -> None:
        result = _extract_slots("{path} and {path}")
        assert result == ["path", "path"]

    def test_empty_string(self) -> None:
        assert _extract_slots("") == []

    def test_curly_without_content(self) -> None:
        # {} doesn't match \w+ so it returns nothing
        assert _extract_slots("empty {} braces") == []


# ===================================================================
# _fill_template
# ===================================================================


class TestFillTemplate:
    """Tests for _fill_template helper."""

    def test_returns_tuple_of_text_and_slots(self) -> None:
        import random

        rng = random.Random(42)
        text, slots = _fill_template("install {package}", "install_package", rng)
        assert isinstance(text, str)
        assert isinstance(slots, dict)
        assert "package" in slots

    def test_fills_all_placeholders(self) -> None:
        import random

        rng = random.Random(42)
        text, slots = _fill_template("copy {source} to {destination}", "copy_files", rng)
        assert "{source}" not in text
        assert "{destination}" not in text

    def test_unknown_slot_gets_angle_bracket_fallback(self) -> None:
        import random

        rng = random.Random(42)
        text, slots = _fill_template("do {unknown_slot_xyz}", "find_files", rng)
        assert "<unknown_slot_xyz>" in text
        assert slots["unknown_slot_xyz"] == "<unknown_slot_xyz>"

    def test_distro_rhel_uses_rhel_packages(self) -> None:
        import random

        rng = random.Random(42)
        _text, slots = _fill_template("install {package}", "install_package", rng, distro="rhel")
        from incept.data.slot_pools import PACKAGES_RHEL

        assert slots["package"] in PACKAGES_RHEL

    def test_distro_debian_uses_debian_packages(self) -> None:
        import random

        rng = random.Random(42)
        _text, slots = _fill_template(
            "install {package}", "install_package", rng, distro="debian"
        )
        from incept.data.slot_pools import PACKAGES_DEBIAN

        assert slots["package"] in PACKAGES_DEBIAN

    def test_deterministic_with_same_seed(self) -> None:
        import random

        text1, slots1 = _fill_template(
            "find {name_pattern} in {path}", "find_files", random.Random(99)
        )
        text2, slots2 = _fill_template(
            "find {name_pattern} in {path}", "find_files", random.Random(99)
        )
        assert text1 == text2
        assert slots1 == slots2


# ===================================================================
# _make_id / _pick_context
# ===================================================================


class TestHelperFunctions:
    """Tests for _make_id and _pick_context."""

    def test_make_id_format(self) -> None:
        assert _make_id("find_files", 0) == "TG-find_files-0000"
        assert _make_id("install_package", 42) == "TG-install_package-0042"

    def test_pick_context_debian(self) -> None:
        import random

        ctx = _pick_context(random.Random(42), "debian")
        assert "debian" in ctx or "ubuntu" in ctx

    def test_pick_context_rhel(self) -> None:
        import random

        ctx = _pick_context(random.Random(42), "rhel")
        assert "rhel" in ctx


# ===================================================================
# generate_examples
# ===================================================================


class TestGenerateExamples:
    """Tests for generate_examples()."""

    def test_produces_correct_count_mini(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=30, seed=42)
        assert len(examples) == 30

    def test_produces_correct_count_large(self) -> None:
        examples = generate_examples(NL_TEMPLATES, target_count=100, seed=42)
        assert len(examples) == 100

    def test_all_examples_have_required_fields(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=30, seed=42)
        for ex in examples:
            for field in _REQUIRED_FIELDS:
                assert field in ex, f"Missing field '{field}' in example {ex.get('id')}"

    def test_all_intents_represented(self) -> None:
        """When target_count is large enough, all template intents appear."""
        examples = generate_examples(NL_TEMPLATES, target_count=500, seed=42)
        present_intents = {ex["expected_intent"] for ex in examples}
        template_intents = set(NL_TEMPLATES.keys())
        assert template_intents == present_intents

    def test_all_49_non_special_intents_in_full_generation(self) -> None:
        examples = generate_examples(NL_TEMPLATES, target_count=2000, seed=42)
        present_intents = {ex["expected_intent"] for ex in examples}
        # NL_TEMPLATES covers 49 non-special intents
        assert len(present_intents) == len(NL_TEMPLATES)

    def test_distro_mix_approximately_correct(self) -> None:
        examples = generate_examples(NL_TEMPLATES, target_count=2000, seed=42)
        distro_counts: Counter[str] = Counter()
        for ex in examples:
            for tag in ex["tags"]:
                if tag in ("debian", "rhel"):
                    distro_counts[tag] += 1
        total = sum(distro_counts.values())
        debian_ratio = distro_counts["debian"] / total
        # 70% default +/- tolerance
        assert 0.60 < debian_ratio < 0.80

    def test_custom_distro_mix(self) -> None:
        examples = generate_examples(
            _MINI_TEMPLATES,
            target_count=300,
            seed=42,
            distro_mix={"debian": 0.5, "rhel": 0.5},
        )
        distro_counts: Counter[str] = Counter()
        for ex in examples:
            for tag in ex["tags"]:
                if tag in ("debian", "rhel"):
                    distro_counts[tag] += 1
        total = sum(distro_counts.values())
        debian_ratio = distro_counts["debian"] / total
        assert 0.35 < debian_ratio < 0.65

    def test_deterministic_with_same_seed(self) -> None:
        a = generate_examples(_MINI_TEMPLATES, target_count=50, seed=123)
        b = generate_examples(_MINI_TEMPLATES, target_count=50, seed=123)
        assert a == b

    def test_different_seeds_produce_different_results(self) -> None:
        a = generate_examples(_MINI_TEMPLATES, target_count=50, seed=1)
        b = generate_examples(_MINI_TEMPLATES, target_count=50, seed=2)
        texts_a = [ex["nl_request"] for ex in a]
        texts_b = [ex["nl_request"] for ex in b]
        assert texts_a != texts_b

    def test_empty_templates_return_empty(self) -> None:
        assert generate_examples({}, target_count=100, seed=42) == []

    def test_ids_are_sequential_after_shuffle(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=30, seed=42)
        ids = [ex["id"] for ex in examples]
        expected = [f"TG-{i:05d}" for i in range(30)]
        assert ids == expected

    def test_source_field_is_template(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=10, seed=42)
        for ex in examples:
            assert ex["source"] == "template"

    def test_license_field_is_mit(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=10, seed=42)
        for ex in examples:
            assert ex["license"] == "MIT"

    def test_tags_include_category_and_distro(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=10, seed=42)
        for ex in examples:
            tags = ex["tags"]
            assert "template" in tags
            assert any(t in ("debian", "rhel") for t in tags)

    def test_expected_slots_is_dict(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=10, seed=42)
        for ex in examples:
            assert isinstance(ex["expected_slots"], dict)

    def test_nl_request_is_nonempty_string(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=30, seed=42)
        for ex in examples:
            assert isinstance(ex["nl_request"], str)
            assert len(ex["nl_request"].strip()) > 0


# ===================================================================
# dataset_statistics
# ===================================================================


class TestDatasetStatistics:
    """Tests for dataset_statistics()."""

    def test_total_examples_count(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=30, seed=42)
        stats = dataset_statistics(examples)
        assert stats["total_examples"] == 30

    def test_unique_intents_count(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=30, seed=42)
        stats = dataset_statistics(examples)
        assert stats["unique_intents"] == 3

    def test_intent_distribution_sums_to_total(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=30, seed=42)
        stats = dataset_statistics(examples)
        total_from_dist = sum(stats["intent_distribution"].values())
        assert total_from_dist == 30

    def test_min_max_per_intent(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=30, seed=42)
        stats = dataset_statistics(examples)
        assert stats["min_per_intent"] >= 1
        assert stats["max_per_intent"] >= stats["min_per_intent"]

    def test_empty_dataset(self) -> None:
        stats = dataset_statistics([])
        assert stats["total_examples"] == 0
        assert stats["unique_intents"] == 0
        assert stats["min_per_intent"] == 0

    def test_distro_distribution_present(self) -> None:
        examples = generate_examples(_MINI_TEMPLATES, target_count=100, seed=42)
        stats = dataset_statistics(examples)
        assert "distro_distribution" in stats
        assert len(stats["distro_distribution"]) > 0


# ===================================================================
# generate_to_jsonl
# ===================================================================


class TestGenerateToJsonl:
    """Tests for generate_to_jsonl()."""

    def test_writes_valid_jsonl_file(self, tmp_path: Path) -> None:
        out = tmp_path / "output.jsonl"
        count = generate_to_jsonl(_MINI_TEMPLATES, out, target_count=20, seed=42)
        assert count == 20
        assert out.exists()

        lines = out.read_text().strip().split("\n")
        assert len(lines) == 20
        for line in lines:
            obj = json.loads(line)
            assert "id" in obj
            assert "nl_request" in obj

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        out = tmp_path / "deep" / "nested" / "output.jsonl"
        count = generate_to_jsonl(_MINI_TEMPLATES, out, target_count=5, seed=42)
        assert count == 5
        assert out.exists()

    def test_returns_count(self, tmp_path: Path) -> None:
        out = tmp_path / "data.jsonl"
        count = generate_to_jsonl(_MINI_TEMPLATES, out, target_count=15, seed=42)
        assert count == 15

    def test_jsonl_lines_are_valid_json(self, tmp_path: Path) -> None:
        out = tmp_path / "data.jsonl"
        generate_to_jsonl(_MINI_TEMPLATES, out, target_count=10, seed=42)
        with open(out) as f:
            for line in f:
                record = json.loads(line.strip())
                assert isinstance(record, dict)
