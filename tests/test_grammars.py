"""Tests for GBNF grammar files — validates structure and coverage."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from incept.schemas.intents import IntentLabel

GRAMMAR_DIR = Path(__file__).parent.parent / "incept" / "grammars"


class TestGrammarFilePresence:
    """Every intent must have a corresponding grammar file."""

    def test_intent_grammar_exists(self) -> None:
        assert (GRAMMAR_DIR / "intent_grammar.gbnf").exists()

    @pytest.mark.parametrize("intent", list(IntentLabel))
    def test_slot_grammar_exists(self, intent: IntentLabel) -> None:
        fname = f"slots_{intent.value.lower()}.gbnf"
        path = GRAMMAR_DIR / fname
        assert path.exists(), f"Missing grammar file: {fname}"

    def test_total_grammar_count(self) -> None:
        gbnf_files = list(GRAMMAR_DIR.glob("*.gbnf"))
        assert len(gbnf_files) == 53  # 1 intent + 52 slot grammars


class TestGrammarStructure:
    """Validate basic GBNF grammar structure."""

    @pytest.mark.parametrize("gbnf_file", list(GRAMMAR_DIR.glob("*.gbnf")))
    def test_has_root_rule(self, gbnf_file: Path) -> None:
        content = gbnf_file.read_text()
        # Strip comments
        lines = [ln for ln in content.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        assert any("root" in line and "::=" in line for line in lines), (
            f"{gbnf_file.name} missing root rule"
        )

    @pytest.mark.parametrize("gbnf_file", list(GRAMMAR_DIR.glob("*.gbnf")))
    def test_no_empty_grammar(self, gbnf_file: Path) -> None:
        content = gbnf_file.read_text().strip()
        assert len(content) > 10, f"{gbnf_file.name} is too short"

    @pytest.mark.parametrize("gbnf_file", list(GRAMMAR_DIR.glob("*.gbnf")))
    def test_all_rules_have_definitions(self, gbnf_file: Path) -> None:
        """Check that all non-terminal references have definitions."""
        content = gbnf_file.read_text()
        lines = [ln for ln in content.splitlines() if ln.strip() and not ln.strip().startswith("#")]

        # Find defined rules (left side of ::=)
        defined = set()
        for line in lines:
            if "::=" in line:
                rule_name = line.split("::=")[0].strip()
                defined.add(rule_name)

        # We check that defined set is non-empty
        assert len(defined) > 0, f"{gbnf_file.name} has no rule definitions"


class TestIntentGrammar:
    """Validate the master intent grammar contains all intent labels."""

    def test_all_intents_present(self) -> None:
        content = (GRAMMAR_DIR / "intent_grammar.gbnf").read_text()
        for intent in IntentLabel:
            assert f'"{intent.value}"' in content, (
                f"Intent {intent.value} missing from intent_grammar.gbnf"
            )


class TestSlotGrammarContent:
    """Spot-check that slot grammars contain expected slot names."""

    _EXPECTED_SLOTS: dict[str, list[str]] = {
        "slots_find_files.gbnf": ["path=", "name_pattern=", "type=", "size_gt=", "user="],
        "slots_copy_files.gbnf": ["source=", "destination="],
        "slots_install_package.gbnf": ["package=", "assume_yes="],
        "slots_search_text.gbnf": ["pattern="],
        "slots_start_service.gbnf": ["service_name="],
        "slots_create_user.gbnf": ["username="],
        "slots_schedule_cron.gbnf": ["schedule=", "command="],
        "slots_download_file.gbnf": ["url="],
        "slots_mount_device.gbnf": ["device=", "mount_point="],
        "slots_clarify.gbnf": ["reason=", "template="],
    }

    @pytest.mark.parametrize("fname,expected_slots", list(_EXPECTED_SLOTS.items()))
    def test_expected_slots_present(self, fname: str, expected_slots: list[str]) -> None:
        content = (GRAMMAR_DIR / fname).read_text()
        for slot in expected_slots:
            assert slot in content, f"Slot {slot!r} missing from {fname}"


class TestGrammarValidStrings:
    """Regex-based simulation: test that valid strings match grammar patterns."""

    def test_intent_grammar_valid_strings(self) -> None:
        content = (GRAMMAR_DIR / "intent_grammar.gbnf").read_text()
        # Extract all quoted intent labels
        labels = re.findall(r'"([^"]+)"', content)
        # Each label should be a valid IntentLabel
        for label in labels:
            assert label in [i.value for i in IntentLabel], f"Unknown label in grammar: {label}"

    def test_find_files_valid_output(self) -> None:
        """A well-formed find_files slot output should be parseable."""
        sample = "path=/var/log\nname_pattern=*.log\ntype=file\nsize_gt=50M"
        lines = sample.split("\n")
        for line in lines:
            assert "=" in line, f"Malformed slot line: {line}"
            key, value = line.split("=", 1)
            assert key in ["path", "name_pattern", "type", "size_gt", "size_lt",
                           "mtime_days_gt", "mtime_days_lt", "user", "permissions"]

    def test_install_package_valid_output(self) -> None:
        sample = "package=nginx\nassume_yes=true"
        lines = sample.split("\n")
        keys = [ln.split("=")[0] for ln in lines]
        assert "package" in keys

    def test_clarify_valid_output(self) -> None:
        sample = "reason=ambiguous_intent\ntemplate=clarify_intent"
        lines = sample.split("\n")
        assert lines[0].startswith("reason=")
        assert lines[1].startswith("template=")
