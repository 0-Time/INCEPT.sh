"""Tests for training data format conversion (incept.data.converter)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from incept.data.converter import (
    convert_dataset,
    generate_dpo_pairs,
    to_intent_format,
    to_slot_format,
)

# ---------------------------------------------------------------------------
# Fixtures / factories
# ---------------------------------------------------------------------------


def _example(
    text: str = "install nginx",
    intent: str = "install_package",
    slots: dict[str, Any] | None = None,
    context: str = "debian bash non-root safe",
    tags: list[str] | None = None,
    example_id: str = "TEST-0001",
) -> dict[str, Any]:
    """Factory for a minimal training example."""
    return {
        "id": example_id,
        "source": "template",
        "license": "MIT",
        "nl_request": text,
        "context_line": context,
        "expected_intent": intent,
        "expected_slots": slots if slots is not None else {"package": "nginx"},
        "tags": tags or ["package_mgmt", "template", "debian"],
    }


def _near_miss_example(
    text: str = "remove nginx from the system",
    correct: str = "remove_package",
    distractor: str = "delete_files",
) -> dict[str, Any]:
    """Factory for a near-miss adversarial example."""
    return {
        "id": "NM-0001",
        "source": "adversarial",
        "license": "MIT",
        "nl_request": text,
        "context_line": "debian bash non-root safe",
        "expected_intent": correct,
        "expected_slots": {},
        "tags": ["adversarial", "near_miss", f"distractor_{distractor}"],
    }


# ===================================================================
# to_intent_format
# ===================================================================


class TestToIntentFormat:
    """Tests for to_intent_format()."""

    def test_returns_dict_with_required_keys(self) -> None:
        result = to_intent_format(_example())
        assert "prompt" in result
        assert "completion" in result
        assert "id" in result
        assert "intent" in result

    def test_prompt_contains_context_marker(self) -> None:
        result = to_intent_format(_example(context="rhel bash root safe"))
        assert "[CONTEXT]" in result["prompt"]
        assert "rhel bash root safe" in result["prompt"]

    def test_prompt_contains_request_marker(self) -> None:
        result = to_intent_format(_example(text="find all log files"))
        assert "[REQUEST]" in result["prompt"]
        assert "find all log files" in result["prompt"]

    def test_prompt_contains_intent_marker(self) -> None:
        result = to_intent_format(_example())
        assert "[INTENT]" in result["prompt"]

    def test_prompt_wrapped_in_inst_tags(self) -> None:
        result = to_intent_format(_example())
        assert result["prompt"].startswith("<s>[INST]")
        assert result["prompt"].endswith("[/INST]")

    def test_completion_contains_intent_label(self) -> None:
        result = to_intent_format(_example(intent="find_files"))
        assert result["completion"] == "find_files</s>"

    def test_completion_ends_with_eos(self) -> None:
        result = to_intent_format(_example())
        assert result["completion"].endswith("</s>")

    def test_id_preserved(self) -> None:
        result = to_intent_format(_example(example_id="MY-ID"))
        assert result["id"] == "MY-ID"

    def test_intent_field_preserved(self) -> None:
        result = to_intent_format(_example(intent="disk_usage"))
        assert result["intent"] == "disk_usage"

    def test_default_context_when_missing(self) -> None:
        ex = _example()
        del ex["context_line"]
        result = to_intent_format(ex)
        assert "debian bash non-root safe" in result["prompt"]


# ===================================================================
# to_slot_format
# ===================================================================


class TestToSlotFormat:
    """Tests for to_slot_format()."""

    def test_returns_dict_with_required_keys(self) -> None:
        result = to_slot_format(_example())
        assert "prompt" in result
        assert "completion" in result

    def test_prompt_contains_slots_marker(self) -> None:
        result = to_slot_format(_example())
        assert "[SLOTS]" in result["prompt"]

    def test_prompt_contains_intent_value(self) -> None:
        result = to_slot_format(_example(intent="find_files"))
        assert "[INTENT] find_files" in result["prompt"]

    def test_completion_is_json_slots(self) -> None:
        slots = {"package": "nginx", "version": "latest"}
        result = to_slot_format(_example(slots=slots))
        # Completion is JSON + </s>
        json_part = result["completion"].replace("</s>", "")
        parsed = json.loads(json_part)
        assert parsed == slots

    def test_completion_has_sorted_keys(self) -> None:
        slots = {"z_param": "z", "a_param": "a"}
        result = to_slot_format(_example(slots=slots))
        json_part = result["completion"].replace("</s>", "")
        # Keys should be sorted in JSON output
        assert list(json.loads(json_part).keys()) == ["a_param", "z_param"]

    def test_empty_slots(self) -> None:
        result = to_slot_format(_example(slots={}))
        json_part = result["completion"].replace("</s>", "")
        assert json.loads(json_part) == {}

    def test_prompt_wrapped_in_inst_tags(self) -> None:
        result = to_slot_format(_example())
        assert result["prompt"].startswith("<s>[INST]")
        assert result["prompt"].endswith("[/INST]")


# ===================================================================
# generate_dpo_pairs
# ===================================================================


class TestGenerateDpoPairs:
    """Tests for generate_dpo_pairs()."""

    def test_produces_target_count(self) -> None:
        examples = [
            _near_miss_example(text=f"task {i}", correct="find_files", distractor="search_text")
            for i in range(50)
        ] + [
            _example(text=f"install thing {i}", intent="install_package")
            for i in range(100)
        ]
        pairs = generate_dpo_pairs(examples, target_count=80)
        assert len(pairs) == 80

    def test_chosen_differs_from_rejected(self) -> None:
        examples = [
            _near_miss_example(text=f"task {i}", correct="find_files", distractor="search_text")
            for i in range(20)
        ] + [
            _example(text=f"install {i}", intent="install_package")
            for i in range(50)
        ]
        pairs = generate_dpo_pairs(examples, target_count=30)
        for pair in pairs:
            assert pair["chosen"] != pair["rejected"]

    def test_pair_has_required_fields(self) -> None:
        examples = [
            _near_miss_example(text=f"example {i}")
            for i in range(20)
        ] + [_example(text=f"normal {i}") for i in range(50)]
        pairs = generate_dpo_pairs(examples, target_count=20)
        for pair in pairs:
            assert "id" in pair
            assert "prompt" in pair
            assert "chosen" in pair
            assert "rejected" in pair
            assert "source_id" in pair

    def test_ids_sequential(self) -> None:
        examples = [_example(text=f"ex {i}", intent="install_package") for i in range(50)]
        pairs = generate_dpo_pairs(examples, target_count=20)
        for i, pair in enumerate(pairs):
            assert pair["id"] == f"DPO-{i:05d}"

    def test_prompt_contains_intent_marker(self) -> None:
        examples = [
            _near_miss_example(text=f"near miss {i}")
            for i in range(20)
        ] + [_example(text=f"ex {i}") for i in range(50)]
        pairs = generate_dpo_pairs(examples, target_count=10)
        for pair in pairs:
            assert "[INTENT]" in pair["prompt"]

    def test_chosen_ends_with_eos(self) -> None:
        examples = [_example(text=f"ex {i}") for i in range(50)]
        pairs = generate_dpo_pairs(examples, target_count=10)
        for pair in pairs:
            assert pair["chosen"].endswith("</s>")
            assert pair["rejected"].endswith("</s>")

    def test_near_miss_pairs_use_distractor_from_tags(self) -> None:
        examples = [
            _near_miss_example(
                text="remove nginx from system",
                correct="remove_package",
                distractor="delete_files",
            )
        ] + [_example(text=f"extra {i}") for i in range(20)]
        pairs = generate_dpo_pairs(examples, target_count=1)
        # First pair should come from the near-miss
        assert pairs[0]["chosen"] == "remove_package</s>"
        assert pairs[0]["rejected"] == "delete_files</s>"

    def test_excludes_special_intents_from_synthetic_pairs(self) -> None:
        # CLARIFY, OUT_OF_SCOPE, UNSAFE_REQUEST should not be used as source for synthetic pairs
        examples = [_example(text="ambiguous request", intent="CLARIFY")]
        examples += [
            _example(text=f"install something {i}", intent="install_package")
            for i in range(30)
        ]
        pairs = generate_dpo_pairs(examples, target_count=10)
        for pair in pairs:
            chosen_intent = pair["chosen"].replace("</s>", "")
            assert chosen_intent not in ("CLARIFY", "OUT_OF_SCOPE", "UNSAFE_REQUEST")

    def test_deterministic(self) -> None:
        examples = [_example(text=f"ex {i}", intent="install_package") for i in range(30)]
        a = generate_dpo_pairs(examples, target_count=10, seed=42)
        b = generate_dpo_pairs(examples, target_count=10, seed=42)
        assert a == b


# ===================================================================
# convert_dataset
# ===================================================================


class TestConvertDataset:
    """Tests for convert_dataset()."""

    def test_writes_all_output_files(self, tmp_path: Path) -> None:
        examples = [_example(text=f"install {i}", intent="install_package") for i in range(30)]
        paths = convert_dataset(examples, tmp_path)

        assert "intent" in paths
        assert "slots" in paths
        assert "dpo" in paths
        assert paths["intent"].exists()
        assert paths["slots"].exists()
        assert paths["dpo"].exists()

    def test_intent_file_has_correct_line_count(self, tmp_path: Path) -> None:
        examples = [_example(text=f"task {i}") for i in range(20)]
        paths = convert_dataset(examples, tmp_path)

        lines = paths["intent"].read_text().strip().split("\n")
        assert len(lines) == 20

    def test_intent_file_lines_are_valid_json(self, tmp_path: Path) -> None:
        examples = [_example(text=f"task {i}") for i in range(10)]
        paths = convert_dataset(examples, tmp_path)

        for line in paths["intent"].read_text().strip().split("\n"):
            obj = json.loads(line)
            assert "prompt" in obj
            assert "completion" in obj

    def test_slot_file_skips_special_intents(self, tmp_path: Path) -> None:
        examples = [
            _example(text="install nginx", intent="install_package", slots={"package": "nginx"}),
            _example(text="ambiguous", intent="CLARIFY", slots={}),
            _example(text="weather", intent="OUT_OF_SCOPE", slots={}),
        ]
        paths = convert_dataset(examples, tmp_path, generate_dpo=False)

        lines = paths["slots"].read_text().strip().split("\n")
        # Only the install_package example has non-empty slots and non-special intent
        assert len(lines) == 1

    def test_slot_file_skips_empty_slots(self, tmp_path: Path) -> None:
        examples = [
            _example(text="install nginx", intent="install_package", slots={"package": "nginx"}),
            _example(text="update all", intent="update_packages", slots={}),
        ]
        paths = convert_dataset(examples, tmp_path, generate_dpo=False)

        lines = paths["slots"].read_text().strip().split("\n")
        assert len(lines) == 1

    def test_no_dpo_when_disabled(self, tmp_path: Path) -> None:
        examples = [_example(text=f"ex {i}") for i in range(10)]
        paths = convert_dataset(examples, tmp_path, generate_dpo=False)

        assert "dpo" not in paths

    def test_creates_output_directory(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "deep" / "output"
        examples = [_example(text="test")]
        paths = convert_dataset(examples, out_dir, generate_dpo=False)

        assert out_dir.exists()
        assert paths["intent"].exists()
