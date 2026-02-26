"""Tests for DPO data pipeline and trainer — mock-based, no real ML deps."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from incept.training.config import TrainingConfig
from incept.training.data_pipeline import (
    DPORecord,
    format_for_dpo,
    load_dpo_pairs,
)


def _make_config(**overrides: object) -> TrainingConfig:
    defaults: dict[str, object] = {
        "task": "intent",
        "mode": "dpo",
        "train_file": "data/training/dpo_pairs.jsonl",
    }
    defaults.update(overrides)
    return TrainingConfig(**defaults)  # type: ignore[arg-type]


def _write_jsonl(records: list[dict[str, object]], path: Path) -> None:
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


# ========================== DPORecord ==========================


class TestDPORecord:
    def test_valid_record(self) -> None:
        rec = DPORecord(
            id="dpo_001",
            prompt="classify: find big files",
            chosen="find_files",
            rejected="copy_files",
            source_id="train_042",
        )
        assert rec.id == "dpo_001"
        assert rec.prompt == "classify: find big files"
        assert rec.chosen == "find_files"
        assert rec.rejected == "copy_files"
        assert rec.source_id == "train_042"

    def test_missing_required_field(self) -> None:
        with pytest.raises(ValueError):
            DPORecord(id="dpo_001", prompt="test", chosen="a")  # type: ignore[call-arg]

    def test_optional_source_id(self) -> None:
        rec = DPORecord(
            id="dpo_001",
            prompt="test",
            chosen="a",
            rejected="b",
        )
        assert rec.source_id is None


# ========================== load_dpo_pairs ==========================


class TestLoadDpoPairs:
    def test_load_basic(self, tmp_path: Path) -> None:
        records = [
            {
                "id": "dpo_001",
                "prompt": "classify: find files",
                "chosen": "find_files",
                "rejected": "copy_files",
                "source_id": "s1",
            },
            {
                "id": "dpo_002",
                "prompt": "classify: list dirs",
                "chosen": "list_directory",
                "rejected": "find_files",
                "source_id": "s2",
            },
        ]
        p = tmp_path / "dpo.jsonl"
        _write_jsonl(records, p)
        loaded = load_dpo_pairs(p)
        assert len(loaded) == 2
        assert isinstance(loaded[0], DPORecord)
        assert loaded[0].id == "dpo_001"
        assert loaded[1].chosen == "list_directory"

    def test_empty_file(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.jsonl"
        p.write_text("")
        assert load_dpo_pairs(p) == []

    def test_nonexistent_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_dpo_pairs("/nonexistent/dpo.jsonl")

    def test_skip_comments(self, tmp_path: Path) -> None:
        p = tmp_path / "dpo.jsonl"
        content = (
            "# comment\n"
            + json.dumps(
                {
                    "id": "dpo_001",
                    "prompt": "test",
                    "chosen": "a",
                    "rejected": "b",
                }
            )
            + "\n"
        )
        p.write_text(content)
        loaded = load_dpo_pairs(p)
        assert len(loaded) == 1


# ========================== format_for_dpo ==========================


class TestFormatForDpo:
    def test_basic_format(self) -> None:
        records = [
            DPORecord(
                id="dpo_001",
                prompt="classify: find files",
                chosen="find_files</s>",
                rejected="copy_files</s>",
            ),
        ]
        result = format_for_dpo(records)
        assert len(result) == 1
        assert result[0]["prompt"] == "classify: find files"
        assert result[0]["chosen"] == "find_files"
        assert result[0]["rejected"] == "copy_files"

    def test_strips_eos_token(self) -> None:
        records = [
            DPORecord(
                id="dpo_001",
                prompt="test",
                chosen="answer</s>",
                rejected="wrong</s>",
            ),
        ]
        result = format_for_dpo(records)
        assert "</s>" not in result[0]["chosen"]
        assert "</s>" not in result[0]["rejected"]

    def test_no_eos_token(self) -> None:
        records = [
            DPORecord(
                id="dpo_001",
                prompt="test",
                chosen="answer",
                rejected="wrong",
            ),
        ]
        result = format_for_dpo(records)
        assert result[0]["chosen"] == "answer"
        assert result[0]["rejected"] == "wrong"

    def test_empty_list(self) -> None:
        assert format_for_dpo([]) == []


# ========================== load_dpo_as_hf_dataset ==========================


class TestLoadDpoAsHfDataset:
    def test_returns_dataset(self, tmp_path: Path) -> None:
        records = [
            {
                "id": "dpo_001",
                "prompt": "test",
                "chosen": "a</s>",
                "rejected": "b</s>",
            },
        ]
        p = tmp_path / "dpo.jsonl"
        _write_jsonl(records, p)

        mock_dataset_cls = MagicMock()
        mock_dataset_instance = MagicMock()
        mock_dataset_cls.from_list.return_value = mock_dataset_instance
        mock_dataset_instance.shuffle.return_value = mock_dataset_instance

        with (
            patch("incept.training._require_ml_deps"),
            patch.dict("sys.modules", {"datasets": MagicMock(Dataset=mock_dataset_cls)}),
        ):
            from importlib import reload

            import incept.training.data_pipeline as mod

            reload(mod)
            result = mod.load_dpo_as_hf_dataset(p, seed=42)

            mock_dataset_cls.from_list.assert_called_once()
            call_data = mock_dataset_cls.from_list.call_args[0][0]
            assert len(call_data) == 1
            assert call_data[0]["prompt"] == "test"
            assert call_data[0]["chosen"] == "a"
            mock_dataset_instance.shuffle.assert_called_once_with(seed=42)
            assert result == mock_dataset_instance


# ========================== run_dpo ==========================


class TestRunDpo:
    def test_run_dpo_orchestration(self, tmp_path: Path) -> None:
        mock_trl = MagicMock()
        mock_trainer_instance = MagicMock()
        mock_trl.DPOTrainer.return_value = mock_trainer_instance

        with patch.dict("sys.modules", {"trl": mock_trl}):
            from importlib import reload

            import incept.training.dpo_trainer as mod

            reload(mod)

            mock_model = MagicMock()
            mock_tokenizer = MagicMock()
            mock_ref_model = MagicMock()
            mock_dataset = MagicMock()

            with (
                patch("incept.training._require_ml_deps"),
                patch.object(mod, "_resolve_device", return_value="cpu"),
                patch.object(
                    mod,
                    "_build_model_and_tokenizer",
                    return_value=(mock_model, mock_tokenizer),
                ),
                patch.object(
                    mod,
                    "_build_reference_model",
                    return_value=mock_ref_model,
                ),
                patch(
                    "incept.training.data_pipeline.load_dpo_as_hf_dataset",
                    return_value=mock_dataset,
                ),
            ):
                config = _make_config(output_dir=str(tmp_path / "output"))
                result = mod.run_dpo(config)

                mock_trl.DPOTrainer.assert_called_once()
                call_kwargs = mock_trl.DPOTrainer.call_args[1]
                assert call_kwargs["model"] == mock_model
                assert call_kwargs["ref_model"] == mock_ref_model
                assert call_kwargs["beta"] == 0.1
                mock_trainer_instance.train.assert_called_once()
                mock_trainer_instance.save_model.assert_called_once()
                assert result == tmp_path / "output" / "final"
