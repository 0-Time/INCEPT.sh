"""Tests for forum mining infrastructure (incept.data.forum_miner)."""

from __future__ import annotations

from incept.data.forum_miner import ForumExample, ForumMiner

# ---------------------------------------------------------------------------
# Fixtures / factories
# ---------------------------------------------------------------------------


def _forum_example(
    question_id: int = 12345,
    title: str = "How to find large files in Linux",
    body: str = "I need to find files larger than 100MB on my server.",
    answer_body: str = "You can use: <code>find / -size +100M</code>",
    score: int = 10,
    tags: list[str] | None = None,
    command: str | None = "find / -size +100M",
) -> ForumExample:
    """Factory for a ForumExample."""
    return ForumExample(
        question_id=question_id,
        question_title=title,
        question_body=body,
        answer_body=answer_body,
        answer_score=score,
        tags=tags or ["bash", "find", "linux"],
        extracted_command=command,
        attribution=f"Stack Exchange post #{question_id} (CC-BY-SA 4.0)",
    )


# ===================================================================
# ForumExample model
# ===================================================================


class TestForumExampleModel:
    """Tests for ForumExample Pydantic model."""

    def test_valid_construction(self) -> None:
        ex = _forum_example()
        assert ex.question_id == 12345
        assert ex.question_title == "How to find large files in Linux"
        assert ex.answer_score == 10

    def test_default_values(self) -> None:
        ex = ForumExample(
            question_id=1,
            question_title="test",
            question_body="body",
            answer_body="answer",
        )
        assert ex.answer_score == 0
        assert ex.tags == []
        assert ex.extracted_command is None
        assert ex.attribution == ""

    def test_tags_list_preserved(self) -> None:
        ex = _forum_example(tags=["bash", "permissions", "chmod"])
        assert ex.tags == ["bash", "permissions", "chmod"]


# ===================================================================
# ForumMiner initialization
# ===================================================================


class TestForumMinerInit:
    """Tests for ForumMiner initialization."""

    def test_initializes(self) -> None:
        miner = ForumMiner()
        assert isinstance(miner, ForumMiner)
        assert miner._questions == {}
        assert miner._answers == []


# ===================================================================
# ForumMiner._extract_commands
# ===================================================================


class TestExtractCommands:
    """Tests for _extract_commands helper."""

    def test_extracts_from_pre_code_block(self) -> None:
        miner = ForumMiner()
        html = "<pre><code>sudo apt-get install nginx</code></pre>"
        commands = miner._extract_commands(html)
        assert len(commands) >= 1
        assert any("apt-get install nginx" in c for c in commands)

    def test_extracts_from_inline_code_block(self) -> None:
        miner = ForumMiner()
        html = "Use <code>sudo systemctl restart nginx</code> to restart."
        commands = miner._extract_commands(html)
        assert len(commands) >= 1

    def test_no_commands_in_non_cli_html(self) -> None:
        miner = ForumMiner()
        html = "<p>This is a paragraph about cooking pasta.</p>"
        commands = miner._extract_commands(html)
        assert commands == []

    def test_strips_shell_prompt(self) -> None:
        miner = ForumMiner()
        html = "<pre><code>$ sudo apt-get update</code></pre>"
        commands = miner._extract_commands(html)
        assert any("sudo apt-get update" in c for c in commands)
        # Should not have leading $
        for cmd in commands:
            assert not cmd.startswith("$ ")

    def test_multiline_code_block(self) -> None:
        miner = ForumMiner()
        html = "<pre><code>sudo apt-get update\nsudo apt-get install curl</code></pre>"
        commands = miner._extract_commands(html)
        assert len(commands) >= 2


# ===================================================================
# ForumMiner._clean_text
# ===================================================================


class TestCleanText:
    """Tests for _clean_text helper."""

    def test_removes_html_tags(self) -> None:
        miner = ForumMiner()
        result = miner._clean_text("<p>Hello <b>world</b></p>")
        assert "<" not in result
        assert ">" not in result
        assert "Hello" in result
        assert "world" in result

    def test_decodes_html_entities(self) -> None:
        miner = ForumMiner()
        result = miner._clean_text("&amp; &lt; &gt; &quot; &#39;")
        assert "&" in result
        assert "<" in result
        assert ">" in result
        assert '"' in result
        assert "'" in result

    def test_collapses_whitespace(self) -> None:
        miner = ForumMiner()
        result = miner._clean_text("  hello   world  ")
        assert result == "hello world"


# ===================================================================
# ForumMiner.to_training_format
# ===================================================================


class TestToTrainingFormat:
    """Tests for to_training_format()."""

    def test_produces_valid_jsonl_records(self) -> None:
        miner = ForumMiner()
        examples = [_forum_example(), _forum_example(question_id=99)]
        records = miner.to_training_format(examples)

        assert len(records) == 2
        for rec in records:
            assert "id" in rec
            assert "source" in rec
            assert "nl_request" in rec
            assert "expected_intent" in rec
            assert "tags" in rec

    def test_source_is_forum(self) -> None:
        miner = ForumMiner()
        records = miner.to_training_format([_forum_example()])
        assert records[0]["source"] == "forum"

    def test_license_is_cc_by_sa(self) -> None:
        miner = ForumMiner()
        records = miner.to_training_format([_forum_example()])
        assert records[0]["license"] == "CC-BY-SA-4.0"

    def test_ids_sequential(self) -> None:
        miner = ForumMiner()
        examples = [_forum_example(question_id=i) for i in range(5)]
        records = miner.to_training_format(examples)
        for i, rec in enumerate(records):
            assert rec["id"] == f"FM-{i:05d}"

    def test_nl_request_is_question_title(self) -> None:
        miner = ForumMiner()
        records = miner.to_training_format([_forum_example(title="How to chmod")])
        assert records[0]["nl_request"] == "How to chmod"

    def test_expected_intent_is_empty_needs_labeling(self) -> None:
        miner = ForumMiner()
        records = miner.to_training_format([_forum_example()])
        assert records[0]["expected_intent"] == ""

    def test_tags_include_forum_and_stack_exchange(self) -> None:
        miner = ForumMiner()
        records = miner.to_training_format([_forum_example()])
        assert "forum" in records[0]["tags"]
        assert "stack_exchange" in records[0]["tags"]

    def test_attribution_preserved(self) -> None:
        miner = ForumMiner()
        records = miner.to_training_format([_forum_example(question_id=42)])
        assert "42" in records[0]["attribution"]
        assert "CC-BY-SA 4.0" in records[0]["attribution"]

    def test_expected_command_present(self) -> None:
        miner = ForumMiner()
        records = miner.to_training_format([_forum_example(command="find / -size +100M")])
        assert records[0]["expected_command"] == "find / -size +100M"
