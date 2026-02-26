"""Tests for golden test case loading and validation."""

from pathlib import Path

import pytest

from incept.eval.loader import GoldenTestCase, load_golden_tests
from incept.schemas import validate_params
from incept.schemas.intents import IntentLabel

GOLDEN_FILE = Path(__file__).parent.parent / "golden_tests" / "golden_v1.jsonl"


class TestGoldenLoader:
    def test_loads_all_tests(self) -> None:
        tests = load_golden_tests(GOLDEN_FILE)
        assert len(tests) >= 100, f"Expected 100+ tests, got {len(tests)}"

    def test_all_have_required_fields(self) -> None:
        tests = load_golden_tests(GOLDEN_FILE)
        for t in tests:
            assert t.id, "Test missing id"
            assert t.nl_request, f"Test {t.id} missing nl_request"
            assert t.expected_intent is not None, f"Test {t.id} missing expected_intent"

    def test_unique_ids(self) -> None:
        tests = load_golden_tests(GOLDEN_FILE)
        ids = [t.id for t in tests]
        assert len(ids) == len(set(ids)), "Duplicate test IDs found"

    def test_all_intents_valid(self) -> None:
        tests = load_golden_tests(GOLDEN_FILE)
        for t in tests:
            assert isinstance(t.expected_intent, IntentLabel), (
                f"Test {t.id}: invalid intent {t.expected_intent}"
            )


class TestGoldenDistribution:
    """Verify test distribution meets requirements."""

    @pytest.fixture()
    def tests(self) -> list[GoldenTestCase]:
        return load_golden_tests(GOLDEN_FILE)

    def test_safety_canaries(self, tests: list[GoldenTestCase]) -> None:
        safety = [t for t in tests if "safety" in t.tags or "canary" in t.tags]
        assert len(safety) >= 10, f"Need 10+ safety canaries, got {len(safety)}"

    def test_oos_examples(self, tests: list[GoldenTestCase]) -> None:
        oos = [t for t in tests if t.expected_intent == IntentLabel.OUT_OF_SCOPE]
        assert len(oos) >= 5, f"Need 5+ OOS examples, got {len(oos)}"

    def test_clarify_examples(self, tests: list[GoldenTestCase]) -> None:
        clarify = [t for t in tests if t.expected_intent == IntentLabel.CLARIFY]
        assert len(clarify) >= 5, f"Need 5+ CLARIFY examples, got {len(clarify)}"

    def test_unsafe_examples(self, tests: list[GoldenTestCase]) -> None:
        unsafe = [t for t in tests if t.expected_intent == IntentLabel.UNSAFE_REQUEST]
        assert len(unsafe) >= 10, f"Need 10+ UNSAFE examples, got {len(unsafe)}"


class TestGoldenSlotsValidation:
    """Verify expected_slots in golden tests validate against param schemas."""

    def test_slots_validate(self) -> None:
        tests = load_golden_tests(GOLDEN_FILE)
        for t in tests:
            if t.expected_slots and t.expected_intent not in (
                IntentLabel.CLARIFY,
                IntentLabel.OUT_OF_SCOPE,
                IntentLabel.UNSAFE_REQUEST,
            ):
                try:
                    validate_params(t.expected_intent, t.expected_slots)
                except Exception as e:
                    pytest.fail(
                        f"Test {t.id} ({t.expected_intent.value}): "
                        f"slots validation failed: {e}"
                    )
