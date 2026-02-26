"""Comprehensive tests for incept.core.decomposer — ~25 tests.

Covers: simple vs. compound requests, split patterns (then, and-then, pipe,
semicolon, sentence boundary, and+verb), pronoun/reference detection,
before/after reordering, complexity limits, and edge cases.
"""

from __future__ import annotations

from incept.core.decomposer import (
    MAX_SUBSTEPS,
    DecompositionResult,
    SubRequest,
    decompose,
)

# ===========================================================================
# Simple (non-compound) requests
# ===========================================================================


class TestSimpleRequests:
    """Single-action requests should not be decomposed."""

    def test_simple_request_not_compound(self) -> None:
        result = decompose("find all log files in /var/log")

        assert result.is_compound is False
        assert len(result.sub_requests) == 1
        assert result.sub_requests[0].text == "find all log files in /var/log"
        assert result.sub_requests[0].index == 0

    def test_simple_request_preserves_original_text(self) -> None:
        text = "list running processes"
        result = decompose(text)

        assert result.original_text == text
        assert result.is_compound is False

    def test_and_without_verb_not_split(self) -> None:
        """'large and small files' has 'and' but no second action verb."""
        result = decompose("find large and small files in /tmp")

        assert result.is_compound is False
        assert len(result.sub_requests) == 1

    def test_single_word_request(self) -> None:
        result = decompose("ls")

        assert result.is_compound is False
        assert len(result.sub_requests) == 1
        assert result.sub_requests[0].text == "ls"


# ===========================================================================
# Compound: ", then" and "and then" splitting
# ===========================================================================


class TestThenSplitting:
    """Requests with ', then' or 'and then' connectors."""

    def test_comma_then_splits_into_two(self) -> None:
        result = decompose("find files, then compress them")

        assert result.is_compound is True
        assert len(result.sub_requests) == 2
        assert result.composition == "sequential"

    def test_and_then_splits_into_two(self) -> None:
        result = decompose("find files and then delete them")

        assert result.is_compound is True
        assert len(result.sub_requests) == 2
        assert result.composition == "sequential"

    def test_then_splits_content_correctly(self) -> None:
        result = decompose("find the log files, then compress them")

        assert result.sub_requests[0].text == "find the log files"
        # Second part should be the compression request
        assert "compress" in result.sub_requests[1].text.lower()


# ===========================================================================
# Compound: pipe composition
# ===========================================================================


class TestPipeSplitting:
    """Requests with pipe indicators."""

    def test_pipe_char_detected(self) -> None:
        result = decompose("search logs | grep error")

        assert result.is_compound is True
        assert result.composition == "pipe"

    def test_pipe_keyword_detected(self) -> None:
        result = decompose("list processes pipe to grep nginx")

        assert result.is_compound is True
        assert result.composition == "pipe"


# ===========================================================================
# Compound: independent (semicolon) composition
# ===========================================================================


class TestIndependentSplitting:
    """Requests with semicolons indicate independent composition."""

    def test_semicolon_splits_independent(self) -> None:
        result = decompose("install nginx; restart nginx")

        assert result.is_compound is True
        assert len(result.sub_requests) == 2
        assert result.composition == "independent"


# ===========================================================================
# Compound: "and" + verb splitting
# ===========================================================================


class TestAndVerbSplitting:
    """'and' followed by an action verb triggers splitting."""

    def test_and_verb_splits(self) -> None:
        result = decompose("copy files, and move the backups")

        assert result.is_compound is True
        assert len(result.sub_requests) == 2

    def test_and_without_action_verb_no_split(self) -> None:
        """'and' not followed by an action verb should not split."""
        result = decompose("find large and important files")

        assert result.is_compound is False
        assert len(result.sub_requests) == 1


# ===========================================================================
# Pronoun / reference detection
# ===========================================================================


class TestReferenceDetection:
    """Pronouns like 'them', 'it', 'the result', 'the output' detected."""

    def test_pronoun_them_detected(self) -> None:
        result = decompose("find files, then compress them")

        assert result.is_compound is True
        # The second sub-request contains "them"
        second = result.sub_requests[1]
        assert second.has_reference is True
        assert second.reference_type == "pronoun_them"

    def test_pronoun_it_detected(self) -> None:
        result = decompose("download the file, then extract it")

        assert result.is_compound is True
        second = result.sub_requests[1]
        assert second.has_reference is True
        assert second.reference_type == "pronoun_it"

    def test_the_result_detected(self) -> None:
        result = decompose("run the query, then save the result")

        assert result.is_compound is True
        second = result.sub_requests[1]
        assert second.has_reference is True
        assert second.reference_type == "the_result"

    def test_the_output_detected(self) -> None:
        result = decompose("list processes, then filter the output")

        assert result.is_compound is True
        second = result.sub_requests[1]
        assert second.has_reference is True
        assert second.reference_type == "the_output"

    def test_first_part_no_reference(self) -> None:
        result = decompose("find log files, then delete them")

        first = result.sub_requests[0]
        assert first.has_reference is False
        assert first.reference_type is None


# ===========================================================================
# Before / After reordering
# ===========================================================================


class TestReordering:
    """'After X, do Y' triggers reordering of decomposed parts."""

    def test_after_reorders_parts(self) -> None:
        # Use ", then" to ensure the decomposer splits first, then
        # the after-reordering logic reverses the two parts.
        result = decompose("After updating the system, then restart nginx")

        assert result.is_compound is True
        assert len(result.sub_requests) == 2
        # The after-reordering reverses the parts: "restart" ends up at index 0
        # and "After updating" ends up at index 1.
        texts = [sr.text.lower() for sr in result.sub_requests]
        assert "restart" in texts[0]
        assert "updating" in texts[1]


# ===========================================================================
# Sentence boundary splitting
# ===========================================================================


class TestSentenceBoundary:
    """Period followed by capital letter splits on sentence boundary."""

    def test_two_sentences_split(self) -> None:
        result = decompose("Find the files. Delete the old ones.")

        assert result.is_compound is True
        assert len(result.sub_requests) == 2
        assert "Find" in result.sub_requests[0].text
        assert "Delete" in result.sub_requests[1].text


# ===========================================================================
# Complexity limits
# ===========================================================================


class TestComplexityLimits:
    """Requests exceeding MAX_SUBSTEPS are truncated."""

    def test_max_substeps_constant(self) -> None:
        assert MAX_SUBSTEPS == 4

    def test_truncation_at_max_substeps(self) -> None:
        # Create a request with 6 steps using "; " separator
        text = "step1; step2; step3; step4; step5; step6"
        result = decompose(text)

        assert result.is_compound is True
        assert len(result.sub_requests) <= MAX_SUBSTEPS
        assert result.was_truncated is True

    def test_within_limit_not_truncated(self) -> None:
        text = "step1; step2; step3"
        result = decompose(text)

        assert result.is_compound is True
        assert len(result.sub_requests) == 3
        assert result.was_truncated is False

    def test_exactly_at_limit_not_truncated(self) -> None:
        text = "step1; step2; step3; step4"
        result = decompose(text)

        assert result.is_compound is True
        assert len(result.sub_requests) == MAX_SUBSTEPS
        assert result.was_truncated is False


# ===========================================================================
# Result model properties
# ===========================================================================


class TestDecompositionResultModel:
    """Verify the result Pydantic models are well-formed."""

    def test_result_is_pydantic_model(self) -> None:
        result = decompose("list files")
        assert isinstance(result, DecompositionResult)

    def test_sub_request_is_pydantic_model(self) -> None:
        result = decompose("list files")
        assert isinstance(result.sub_requests[0], SubRequest)

    def test_sub_request_indexes_are_sequential(self) -> None:
        result = decompose("step1; step2; step3")
        indexes = [sr.index for sr in result.sub_requests]
        assert indexes == list(range(len(indexes)))

    def test_composition_defaults_to_sequential(self) -> None:
        result = decompose("find files, then compress them")
        assert result.composition == "sequential"
