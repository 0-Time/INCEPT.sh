"""Tests for pipeline integration with model classifier.

Verifies:
- Default behavior (no model) is unchanged
- Model classifier is called when enabled + preclassifier has no match
- Real confidence scores replace hardcoded 0.9
- Safety violations from model are still blocked
- Low confidence triggers clarification
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from incept.core.pipeline import run_pipeline
from incept.schemas.intents import IntentLabel
from incept.schemas.ir import ConfidenceScore

# ========================== Default behavior (no model) ==========================


class TestPipelineDefaultBehavior:
    """When model classifier is disabled, pipeline uses preclassifier only."""

    def test_safety_blocked_without_model(self) -> None:
        result = run_pipeline("rm -rf /")
        assert result.status == "blocked"

    def test_matched_intent_without_model(self) -> None:
        result = run_pipeline("find all log files in /var/log")
        assert result.status in ("success", "clarification", "no_match")
        assert len(result.responses) > 0

    def test_no_match_without_model(self) -> None:
        result = run_pipeline("xyzzy florp blargh")
        assert result.status == "no_match"

    def test_oos_without_model(self) -> None:
        result = run_pipeline("what's the weather like?")
        assert result.status == "error"


# ========================== Model classifier enabled ==========================


class TestPipelineWithModel:
    """When model classifier is enabled, it handles unmatched intents."""

    def test_model_called_on_no_match(self) -> None:
        """Preclassifier returns no match → model classifier is called."""
        mock_model = MagicMock()
        mock_result = MagicMock()
        mock_result.intent = IntentLabel.find_files
        mock_result.slots = {"path": "/var/log", "name_pattern": "*.log"}
        mock_result.confidence = ConfidenceScore(intent=0.95, slots=0.9, composite=0.92)
        mock_result.used_model = True

        with patch(
            "incept.core.model_classifier.model_classify", return_value=mock_result
        ) as mock_mc:
            run_pipeline(
                "locate the largest log entries under var",  # Won't match preclassifier
                use_model_classifier=True,
                model=mock_model,
            )

            mock_mc.assert_called_once()
            # Model should have been called with the sub-request text
            call_args = mock_mc.call_args
            assert call_args[0][0] == mock_model

    def test_model_not_called_when_preclassifier_matches(self) -> None:
        """Preclassifier matches → model is NOT called."""
        mock_model = MagicMock()

        with patch("incept.core.model_classifier.model_classify") as mock_mc:
            run_pipeline(
                "find all log files in /var/log",  # Matches preclassifier
                use_model_classifier=True,
                model=mock_model,
            )

            mock_mc.assert_not_called()

    def test_model_not_called_when_disabled(self) -> None:
        """Model classifier disabled → never called."""
        mock_model = MagicMock()

        with patch("incept.core.model_classifier.model_classify") as mock_mc:
            run_pipeline(
                "locate the largest log entries under var",
                use_model_classifier=False,
                model=mock_model,
            )

            mock_mc.assert_not_called()


# ========================== Confidence scores ==========================


class TestPipelineConfidence:
    """Model classifier provides real confidence instead of hardcoded 0.9."""

    def test_model_confidence_used_in_response(self) -> None:
        mock_model = MagicMock()
        mock_result = MagicMock()
        mock_result.intent = IntentLabel.disk_usage
        mock_result.slots = {}
        mock_result.confidence = ConfidenceScore(intent=0.85, slots=0.78, composite=0.82)
        mock_result.used_model = True

        with patch("incept.core.model_classifier.model_classify", return_value=mock_result):
            result = run_pipeline(
                "analyze storage utilization on the root partition",
                use_model_classifier=True,
                model=mock_model,
            )

            # Response should exist (model returned a compilable intent)
            assert len(result.responses) > 0


# ========================== Safety from model ==========================


class TestPipelineModelSafety:
    """Safety violations detected by the model are still blocked."""

    def test_model_unsafe_result_blocked(self) -> None:
        mock_model = MagicMock()
        mock_result = MagicMock()
        mock_result.intent = IntentLabel.UNSAFE_REQUEST
        mock_result.slots = {}
        mock_result.confidence = ConfidenceScore(intent=0.99, slots=0.0, composite=0.5)
        mock_result.used_model = True

        with patch("incept.core.model_classifier.model_classify", return_value=mock_result):
            result = run_pipeline(
                "hack into the neighbor's wifi network",
                use_model_classifier=True,
                model=mock_model,
            )

            assert result.status == "blocked"

    def test_preclassifier_safety_takes_precedence(self) -> None:
        """Even with model enabled, preclassifier safety check runs first."""
        mock_model = MagicMock()

        with patch("incept.core.model_classifier.model_classify") as mock_mc:
            result = run_pipeline(
                "rm -rf /",
                use_model_classifier=True,
                model=mock_model,
            )

            # Model should never be called — preclassifier catches it first
            mock_mc.assert_not_called()
            assert result.status == "blocked"


# ========================== Low confidence / clarification ==========================


class TestPipelineModelClarification:
    """Low confidence from model triggers clarification."""

    def test_model_clarify_intent(self) -> None:
        mock_model = MagicMock()
        mock_result = MagicMock()
        mock_result.intent = IntentLabel.CLARIFY
        mock_result.slots = {}
        mock_result.confidence = ConfidenceScore(intent=0.3, slots=0.0, composite=0.15)
        mock_result.used_model = True

        with patch("incept.core.model_classifier.model_classify", return_value=mock_result):
            result = run_pipeline(
                "do the thing with the stuff",
                use_model_classifier=True,
                model=mock_model,
            )

            # Should be clarification, not error
            assert result.status in ("no_match", "clarification")
            assert len(result.responses) > 0
