"""Tests for incept.core.model_classifier — grammar resolution, slot parsing, two-pass flow."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from incept.core.model_classifier import (
    ClassifierResult,
    ModelClassifierResult,
    SlotResult,
    classify_intent,
    fill_slots,
    model_classify,
    parse_slot_output,
    resolve_intent_grammar,
    resolve_slot_grammar,
)
from incept.schemas.intents import IntentLabel

# ========================== Grammar resolution (pure logic) ==========================


class TestResolveIntentGrammar:
    def test_returns_path(self) -> None:
        path = resolve_intent_grammar()
        assert isinstance(path, Path)
        assert path.name == "intent_grammar.gbnf"

    def test_grammar_file_exists(self) -> None:
        path = resolve_intent_grammar()
        assert path.exists(), f"Intent grammar not found at {path}"


class TestResolveSlotGrammar:
    def test_find_files(self) -> None:
        path = resolve_slot_grammar("find_files")
        assert path is not None
        assert path.name == "slots_find_files.gbnf"
        assert path.exists()

    def test_clarify(self) -> None:
        path = resolve_slot_grammar("CLARIFY")
        assert path is not None
        assert path.name == "slots_clarify.gbnf"
        assert path.exists()

    def test_out_of_scope(self) -> None:
        path = resolve_slot_grammar("OUT_OF_SCOPE")
        assert path is not None
        assert path.name == "slots_out_of_scope.gbnf"
        assert path.exists()

    def test_unsafe_request(self) -> None:
        path = resolve_slot_grammar("UNSAFE_REQUEST")
        assert path is not None
        assert path.name == "slots_unsafe_request.gbnf"
        assert path.exists()

    def test_nonexistent_returns_none(self) -> None:
        path = resolve_slot_grammar("nonexistent_intent_xyz")
        assert path is None

    def test_all_standard_intents_have_grammars(self) -> None:
        """Every intent in IntentLabel should have a corresponding slot grammar."""
        for intent in IntentLabel:
            path = resolve_slot_grammar(intent.value)
            assert path is not None, f"No slot grammar for intent: {intent.value}"
            assert path.exists(), f"Grammar file missing: {path}"


# ========================== Slot parsing (pure logic) ==========================


class TestParseSlotOutput:
    def test_basic_parsing(self) -> None:
        raw = "path=/tmp\nname_pattern=*.log"
        result = parse_slot_output(raw)
        assert result == {"path": "/tmp", "name_pattern": "*.log"}

    def test_empty_string(self) -> None:
        assert parse_slot_output("") == {}

    def test_three_slots(self) -> None:
        raw = "path=/tmp\ntype=file\nsize_gt=100M"
        result = parse_slot_output(raw)
        assert result == {"path": "/tmp", "type": "file", "size_gt": "100M"}

    def test_trailing_newlines(self) -> None:
        raw = "path=/tmp\nname_pattern=*.log\n\n"
        result = parse_slot_output(raw)
        assert result == {"path": "/tmp", "name_pattern": "*.log"}

    def test_leading_whitespace(self) -> None:
        raw = "  path=/tmp\n  name_pattern=*.log"
        result = parse_slot_output(raw)
        assert result == {"path": "/tmp", "name_pattern": "*.log"}

    def test_value_with_equals(self) -> None:
        raw = "expr=a=b"
        result = parse_slot_output(raw)
        assert result == {"expr": "a=b"}

    def test_single_slot(self) -> None:
        raw = "package=nginx"
        result = parse_slot_output(raw)
        assert result == {"package": "nginx"}

    def test_whitespace_only(self) -> None:
        assert parse_slot_output("   \n  \n") == {}


# ========================== Two-pass classification (mocked) ==========================


def _mock_llama_cpp() -> MagicMock:
    """Create a mock llama_cpp module with LlamaGrammar."""
    mock = MagicMock()
    mock.LlamaGrammar.from_string.return_value = MagicMock()
    return mock


class TestClassifyIntent:
    def test_returns_classifier_result(self) -> None:
        mock_model = MagicMock()
        mock_result = {
            "text": "find_files",
            "tokens": ["find", "_", "files"],
            "logprobs": [-0.1, -0.05, -0.02],
        }

        with (
            patch(
                "incept.core.model_classifier.run_constrained_inference", return_value=mock_result
            ),
            patch.dict("sys.modules", {"llama_cpp": _mock_llama_cpp()}),
        ):
            result = classify_intent(mock_model, "find large files in /tmp", "debian bash")

        assert isinstance(result, ClassifierResult)
        assert result.intent == IntentLabel.find_files
        assert result.raw_output == "find_files"

    def test_intent_logprob_is_mean(self) -> None:
        mock_model = MagicMock()
        mock_result = {
            "text": "copy_files",
            "tokens": ["copy_files"],
            "logprobs": [-0.3],
        }

        with (
            patch(
                "incept.core.model_classifier.run_constrained_inference", return_value=mock_result
            ),
            patch.dict("sys.modules", {"llama_cpp": _mock_llama_cpp()}),
        ):
            result = classify_intent(mock_model, "copy the file", "ubuntu zsh")

        assert result.intent_logprob == pytest.approx(-0.3)


class TestFillSlots:
    def test_returns_slot_result(self) -> None:
        mock_model = MagicMock()
        mock_result = {
            "text": "path=/var/log\nname_pattern=*.log",
            "tokens": ["path", "=", "/var/log", "\n", "name_pattern", "=", "*.log"],
            "logprobs": [-0.1, -0.05, -0.1, -0.01, -0.1, -0.05, -0.1],
        }

        with (
            patch(
                "incept.core.model_classifier.run_constrained_inference", return_value=mock_result
            ),
            patch.dict("sys.modules", {"llama_cpp": _mock_llama_cpp()}),
        ):
            result = fill_slots(mock_model, "find_files", "find log files", "debian bash")

        assert isinstance(result, SlotResult)
        assert result.slots == {"path": "/var/log", "name_pattern": "*.log"}
        assert result.raw_output == "path=/var/log\nname_pattern=*.log"

    def test_empty_slots(self) -> None:
        mock_model = MagicMock()
        mock_result = {"text": "", "tokens": [], "logprobs": []}

        with (
            patch(
                "incept.core.model_classifier.run_constrained_inference", return_value=mock_result
            ),
            patch.dict("sys.modules", {"llama_cpp": _mock_llama_cpp()}),
        ):
            result = fill_slots(mock_model, "system_info", "show system info", "")

        assert result.slots == {}


class TestModelClassify:
    def test_two_pass_flow(self) -> None:
        mock_model = MagicMock()
        intent_result = {
            "text": "find_files",
            "tokens": ["find_files"],
            "logprobs": [-0.05],
        }
        slot_result = {
            "text": "path=/tmp\nname_pattern=*.log",
            "tokens": ["path=/tmp", "\n", "name_pattern=*.log"],
            "logprobs": [-0.1, -0.01, -0.1],
        }

        with (
            patch(
                "incept.core.model_classifier.run_constrained_inference",
                side_effect=[intent_result, slot_result],
            ),
            patch.dict("sys.modules", {"llama_cpp": _mock_llama_cpp()}),
        ):
            result = model_classify(mock_model, "find log files in /tmp", "debian bash")

        assert isinstance(result, ModelClassifierResult)
        assert result.intent == IntentLabel.find_files
        assert result.slots == {"path": "/tmp", "name_pattern": "*.log"}
        assert result.used_model is True
        assert result.confidence.intent > 0.0

    def test_low_confidence_returns_clarification(self) -> None:
        mock_model = MagicMock()
        intent_result = {
            "text": "find_files",
            "tokens": ["find_files"],
            "logprobs": [-5.0],  # Very low confidence
        }

        with (
            patch(
                "incept.core.model_classifier.run_constrained_inference",
                return_value=intent_result,
            ),
            patch.dict("sys.modules", {"llama_cpp": _mock_llama_cpp()}),
        ):
            result = model_classify(
                mock_model, "do something", "debian bash", confidence_threshold=0.5
            )

        assert result.intent == IntentLabel.CLARIFY

    def test_clarify_intent_returns_clarification(self) -> None:
        mock_model = MagicMock()
        intent_result = {
            "text": "CLARIFY",
            "tokens": ["CLARIFY"],
            "logprobs": [-0.1],
        }

        with (
            patch(
                "incept.core.model_classifier.run_constrained_inference",
                return_value=intent_result,
            ),
            patch.dict("sys.modules", {"llama_cpp": _mock_llama_cpp()}),
        ):
            result = model_classify(mock_model, "huh?", "debian bash")

        assert result.intent == IntentLabel.CLARIFY
        assert result.slots == {}
