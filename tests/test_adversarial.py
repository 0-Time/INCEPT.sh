"""Tests for adversarial training data generator (incept.data.adversarial)."""

from __future__ import annotations

from typing import Any

import pytest

from incept.data.adversarial import (
    _NEAR_MISS_PAIRS,
    generate_adversarial,
)

# ---------------------------------------------------------------------------
# Fixtures / constants
# ---------------------------------------------------------------------------

_REQUIRED_FIELDS = frozenset({"id", "source", "nl_request", "expected_intent", "tags"})


@pytest.fixture(scope="module")
def default_adversarial() -> list[dict[str, Any]]:
    """Generate a default adversarial set once for the module (cached)."""
    return generate_adversarial(seed=42)


# ===================================================================
# Total count
# ===================================================================


class TestAdversarialTotalCount:
    """Verify the overall count matches default target (2500)."""

    def test_default_total_is_2500(self, default_adversarial: list[dict[str, Any]]) -> None:
        assert len(default_adversarial) == 2500

    def test_custom_counts(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=10,
            dangerous_count=10,
            wrong_distro_count=10,
            ambiguous_count=10,
            oos_count=10,
            near_miss_count=10,
        )
        assert len(examples) == 60


# ===================================================================
# Required fields
# ===================================================================


class TestAdversarialRequiredFields:
    """Every example must have all required training fields."""

    def test_all_examples_have_required_fields(
        self, default_adversarial: list[dict[str, Any]]
    ) -> None:
        for ex in default_adversarial:
            for field in _REQUIRED_FIELDS:
                assert field in ex, f"Missing '{field}' in {ex.get('id')}"

    def test_nl_request_is_nonempty(self, default_adversarial: list[dict[str, Any]]) -> None:
        for ex in default_adversarial:
            assert isinstance(ex["nl_request"], str)
            assert len(ex["nl_request"].strip()) > 0

    def test_source_is_adversarial(self, default_adversarial: list[dict[str, Any]]) -> None:
        for ex in default_adversarial:
            assert ex["source"] == "adversarial"

    def test_license_is_mit(self, default_adversarial: list[dict[str, Any]]) -> None:
        for ex in default_adversarial:
            assert ex["license"] == "MIT"

    def test_tags_is_list(self, default_adversarial: list[dict[str, Any]]) -> None:
        for ex in default_adversarial:
            assert isinstance(ex["tags"], list)
            assert len(ex["tags"]) > 0


# ===================================================================
# Prompt injection
# ===================================================================


class TestPromptInjectionExamples:
    """Prompt injection examples should be labelled UNSAFE_REQUEST."""

    def test_injection_examples_have_correct_intent(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=50,
            dangerous_count=0,
            wrong_distro_count=0,
            ambiguous_count=0,
            oos_count=0,
            near_miss_count=0,
        )
        for ex in examples:
            assert ex["expected_intent"] == "UNSAFE_REQUEST"

    def test_injection_examples_have_safety_tag(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=50,
            dangerous_count=0,
            wrong_distro_count=0,
            ambiguous_count=0,
            oos_count=0,
            near_miss_count=0,
        )
        for ex in examples:
            assert "adversarial" in ex["tags"]
            assert "prompt_injection" in ex["tags"]
            assert "safety" in ex["tags"]


# ===================================================================
# Dangerous requests
# ===================================================================


class TestDangerousExamples:
    """Dangerous request examples should be labelled UNSAFE_REQUEST."""

    def test_dangerous_examples_have_correct_intent(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=50,
            wrong_distro_count=0,
            ambiguous_count=0,
            oos_count=0,
            near_miss_count=0,
        )
        for ex in examples:
            assert ex["expected_intent"] == "UNSAFE_REQUEST"

    def test_dangerous_examples_have_dangerous_tag(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=50,
            wrong_distro_count=0,
            ambiguous_count=0,
            oos_count=0,
            near_miss_count=0,
        )
        for ex in examples:
            assert "dangerous" in ex["tags"]


# ===================================================================
# Wrong-distro traps
# ===================================================================


class TestWrongDistroExamples:
    """Wrong-distro examples should be labelled CLARIFY."""

    def test_wrong_distro_have_clarify_intent(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=0,
            wrong_distro_count=50,
            ambiguous_count=0,
            oos_count=0,
            near_miss_count=0,
        )
        for ex in examples:
            assert ex["expected_intent"] == "CLARIFY"

    def test_wrong_distro_have_correct_tag(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=0,
            wrong_distro_count=50,
            ambiguous_count=0,
            oos_count=0,
            near_miss_count=0,
        )
        for ex in examples:
            assert "wrong_distro" in ex["tags"]

    def test_wrong_distro_have_trap_type_in_slots(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=0,
            wrong_distro_count=50,
            ambiguous_count=0,
            oos_count=0,
            near_miss_count=0,
        )
        for ex in examples:
            assert "trap_type" in ex["expected_slots"]


# ===================================================================
# Ambiguous / CLARIFY
# ===================================================================


class TestAmbiguousExamples:
    """Ambiguous examples should be labelled CLARIFY."""

    def test_ambiguous_have_clarify_intent(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=0,
            wrong_distro_count=0,
            ambiguous_count=50,
            oos_count=0,
            near_miss_count=0,
        )
        for ex in examples:
            assert ex["expected_intent"] == "CLARIFY"

    def test_ambiguous_have_correct_tags(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=0,
            wrong_distro_count=0,
            ambiguous_count=50,
            oos_count=0,
            near_miss_count=0,
        )
        for ex in examples:
            assert "ambiguous" in ex["tags"]
            assert "clarify" in ex["tags"]


# ===================================================================
# Out-of-scope
# ===================================================================


class TestOutOfScopeExamples:
    """OOS examples should be labelled OUT_OF_SCOPE."""

    def test_oos_have_correct_intent(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=0,
            wrong_distro_count=0,
            ambiguous_count=0,
            oos_count=50,
            near_miss_count=0,
        )
        for ex in examples:
            assert ex["expected_intent"] == "OUT_OF_SCOPE"

    def test_oos_have_correct_tag(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=0,
            wrong_distro_count=0,
            ambiguous_count=0,
            oos_count=50,
            near_miss_count=0,
        )
        for ex in examples:
            assert "out_of_scope" in ex["tags"]


# ===================================================================
# Near-miss intents
# ===================================================================


class TestNearMissExamples:
    """Near-miss examples should have correct intent labels and distractor tags."""

    def test_near_miss_have_valid_intents(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=0,
            wrong_distro_count=0,
            ambiguous_count=0,
            oos_count=0,
            near_miss_count=50,
        )
        valid_intents = {p["correct"] for p in _NEAR_MISS_PAIRS}
        for ex in examples:
            assert ex["expected_intent"] in valid_intents

    def test_near_miss_have_near_miss_tag(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=0,
            wrong_distro_count=0,
            ambiguous_count=0,
            oos_count=0,
            near_miss_count=50,
        )
        for ex in examples:
            assert "near_miss" in ex["tags"]

    def test_near_miss_have_distractor_tag(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=0,
            dangerous_count=0,
            wrong_distro_count=0,
            ambiguous_count=0,
            oos_count=0,
            near_miss_count=50,
        )
        for ex in examples:
            distractor_tags = [t for t in ex["tags"] if t.startswith("distractor_")]
            assert len(distractor_tags) == 1


# ===================================================================
# Determinism
# ===================================================================


class TestAdversarialDeterminism:
    """Same seed should produce identical output."""

    def test_deterministic_with_same_seed(self) -> None:
        a = generate_adversarial(seed=99, injection_count=10, dangerous_count=10,
                                 wrong_distro_count=10, ambiguous_count=10,
                                 oos_count=10, near_miss_count=10)
        b = generate_adversarial(seed=99, injection_count=10, dangerous_count=10,
                                 wrong_distro_count=10, ambiguous_count=10,
                                 oos_count=10, near_miss_count=10)
        assert a == b

    def test_different_seeds_differ(self) -> None:
        a = generate_adversarial(seed=1, injection_count=10, dangerous_count=10,
                                 wrong_distro_count=10, ambiguous_count=10,
                                 oos_count=10, near_miss_count=10)
        b = generate_adversarial(seed=2, injection_count=10, dangerous_count=10,
                                 wrong_distro_count=10, ambiguous_count=10,
                                 oos_count=10, near_miss_count=10)
        texts_a = [ex["nl_request"] for ex in a]
        texts_b = [ex["nl_request"] for ex in b]
        assert texts_a != texts_b


# ===================================================================
# IDs are sequential after shuffle
# ===================================================================


class TestAdversarialIDs:
    """IDs should be sequential ADV-NNNNN after shuffle."""

    def test_ids_sequential(self) -> None:
        examples = generate_adversarial(
            seed=42,
            injection_count=5,
            dangerous_count=5,
            wrong_distro_count=5,
            ambiguous_count=5,
            oos_count=5,
            near_miss_count=5,
        )
        ids = [ex["id"] for ex in examples]
        expected = [f"ADV-{i:05d}" for i in range(30)]
        assert ids == expected


# ===================================================================
# Tags include appropriate categories
# ===================================================================


class TestAdversarialTagCategories:
    """Each category should have its appropriate tags."""

    def test_all_examples_tagged_adversarial(
        self, default_adversarial: list[dict[str, Any]]
    ) -> None:
        for ex in default_adversarial:
            assert "adversarial" in ex["tags"]

    def test_tag_variety(self, default_adversarial: list[dict[str, Any]]) -> None:
        all_tags: set[str] = set()
        for ex in default_adversarial:
            all_tags.update(ex["tags"])
        # All category tags should be present in the full default set
        expected_tags = {
            "prompt_injection", "dangerous", "wrong_distro",
            "ambiguous", "out_of_scope", "near_miss",
        }
        assert expected_tags.issubset(all_tags)
