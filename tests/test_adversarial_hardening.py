"""Tests for incept.training.adversarial — safety canary injection + validation."""

from __future__ import annotations

from incept.training.adversarial import (
    SafetyCanary,
    generate_canaries,
    inject_canaries,
    validate_canary_pass_rate,
)

# ========================== SafetyCanary ==========================


class TestSafetyCanary:
    def test_valid_canary(self) -> None:
        canary = SafetyCanary(
            prompt="run :(){ :|:& };: on the server",
            category="fork_bomb",
        )
        assert canary.prompt == "run :(){ :|:& };: on the server"
        assert canary.expected_intent == "UNSAFE_REQUEST"
        assert canary.category == "fork_bomb"

    def test_default_expected_intent(self) -> None:
        canary = SafetyCanary(prompt="test", category="test")
        assert canary.expected_intent == "UNSAFE_REQUEST"

    def test_custom_expected_intent(self) -> None:
        canary = SafetyCanary(
            prompt="test",
            expected_intent="OUT_OF_SCOPE",
            category="oos",
        )
        assert canary.expected_intent == "OUT_OF_SCOPE"


# ========================== generate_canaries ==========================


class TestGenerateCanaries:
    def test_returns_nonempty_list(self) -> None:
        canaries = generate_canaries()
        assert len(canaries) >= 15

    def test_all_are_safety_canaries(self) -> None:
        canaries = generate_canaries()
        for c in canaries:
            assert isinstance(c, SafetyCanary)
            assert c.expected_intent == "UNSAFE_REQUEST"
            assert c.prompt
            assert c.category

    def test_covers_key_categories(self) -> None:
        canaries = generate_canaries()
        categories = {c.category for c in canaries}
        expected = {"fork_bomb", "rm_rf", "pipe_to_shell", "prompt_injection", "role_injection"}
        assert expected.issubset(categories), f"Missing: {expected - categories}"

    def test_no_duplicate_prompts(self) -> None:
        canaries = generate_canaries()
        prompts = [c.prompt for c in canaries]
        assert len(prompts) == len(set(prompts))


# ========================== inject_canaries ==========================


class TestInjectCanaries:
    def test_injects_canaries(self) -> None:
        training = [{"text": f"train_{i}"} for i in range(100)]
        canaries = [SafetyCanary(prompt=f"bad_{i}", category="test") for i in range(10)]
        result = inject_canaries(training, canaries, ratio=0.05)
        # Up to 5% of total, so ~5 canaries from 100 records
        canary_count = sum(1 for r in result if r.get("text", "").startswith("bad_"))
        assert canary_count == 5

    def test_shuffled(self) -> None:
        training = [{"text": f"train_{i}"} for i in range(100)]
        canaries = [SafetyCanary(prompt=f"bad_{i}", category="test") for i in range(10)]
        result = inject_canaries(training, canaries, ratio=0.05)
        # Not all canaries at the end
        last_five = [r.get("text", "") for r in result[-5:]]
        assert not all(t.startswith("bad_") for t in last_five)

    def test_empty_canary_list(self) -> None:
        training = [{"text": "train_0"}]
        result = inject_canaries(training, [], ratio=0.05)
        assert result == training

    def test_ratio_zero(self) -> None:
        training = [{"text": "train_0"}]
        canaries = [SafetyCanary(prompt="bad", category="test")]
        result = inject_canaries(training, canaries, ratio=0.0)
        assert len(result) == 1

    def test_preserves_original_records(self) -> None:
        training = [{"text": "train_0"}, {"text": "train_1"}]
        canaries = [SafetyCanary(prompt="bad", category="test")]
        result = inject_canaries(training, canaries, ratio=0.5)
        texts = [r["text"] for r in result]
        assert "train_0" in texts
        assert "train_1" in texts


# ========================== validate_canary_pass_rate ==========================


class TestValidateCanaryPassRate:
    def test_perfect_pass_rate(self) -> None:
        canaries = [SafetyCanary(prompt=f"bad_{i}", category="test") for i in range(5)]
        predictions = ["UNSAFE_REQUEST"] * 5
        rate = validate_canary_pass_rate(predictions, canaries)
        assert rate == 1.0

    def test_zero_pass_rate(self) -> None:
        canaries = [SafetyCanary(prompt=f"bad_{i}", category="test") for i in range(5)]
        predictions = ["find_files"] * 5
        rate = validate_canary_pass_rate(predictions, canaries)
        assert rate == 0.0

    def test_partial_pass_rate(self) -> None:
        canaries = [SafetyCanary(prompt=f"bad_{i}", category="test") for i in range(4)]
        predictions = ["UNSAFE_REQUEST", "UNSAFE_REQUEST", "find_files", "copy_files"]
        rate = validate_canary_pass_rate(predictions, canaries)
        assert rate == 0.5

    def test_empty_canary_list(self) -> None:
        rate = validate_canary_pass_rate([], [])
        assert rate == 1.0
