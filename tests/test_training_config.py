"""Tests for incept.training.config — pure Pydantic + YAML, no ML deps."""

from __future__ import annotations

from pathlib import Path

import pytest

from incept.training.config import (
    LoraConfig,
    QuantizationConfig,
    TaskType,
    TrainingConfig,
    load_config,
)

CONFIGS_DIR = Path(__file__).resolve().parent.parent / "configs"


class TestTaskType:
    def test_values(self) -> None:
        assert TaskType.INTENT == "intent"
        assert TaskType.SLOT == "slot"

    def test_from_string(self) -> None:
        assert TaskType("intent") is TaskType.INTENT
        assert TaskType("slot") is TaskType.SLOT


class TestLoraConfig:
    def test_defaults(self) -> None:
        cfg = LoraConfig()
        assert cfg.r == 16
        assert cfg.alpha == 32
        assert cfg.dropout == 0.05
        assert cfg.target_modules == ["q_proj", "k_proj", "v_proj", "o_proj"]

    def test_custom_values(self) -> None:
        cfg = LoraConfig(r=8, alpha=16, dropout=0.1, target_modules=["q_proj"])
        assert cfg.r == 8
        assert cfg.alpha == 16
        assert cfg.dropout == 0.1
        assert cfg.target_modules == ["q_proj"]

    def test_invalid_r(self) -> None:
        with pytest.raises(ValueError):
            LoraConfig(r=0)

    def test_invalid_dropout(self) -> None:
        with pytest.raises(ValueError):
            LoraConfig(dropout=1.5)


class TestQuantizationConfig:
    def test_defaults(self) -> None:
        cfg = QuantizationConfig()
        assert cfg.load_in_4bit is True
        assert cfg.bnb_4bit_compute_dtype == "float16"
        assert cfg.bnb_4bit_quant_type == "nf4"


class TestTrainingConfig:
    def _minimal(self, **overrides: object) -> TrainingConfig:
        defaults: dict[str, object] = {
            "task": "intent",
            "train_file": "data/training/intent_train.jsonl",
        }
        defaults.update(overrides)
        return TrainingConfig(**defaults)  # type: ignore[arg-type]

    def test_minimal_config(self) -> None:
        cfg = self._minimal()
        assert cfg.task == TaskType.INTENT
        assert cfg.base_model == "Qwen/Qwen2.5-0.5B-Instruct"
        assert cfg.max_seq_length == 512
        assert cfg.learning_rate == 2e-4
        assert cfg.num_epochs == 5
        assert cfg.seed == 42
        assert cfg.device == "auto"

    def test_slot_task(self) -> None:
        cfg = self._minimal(task="slot", train_file="data/training/slot_train.jsonl")
        assert cfg.task == TaskType.SLOT

    def test_lora_defaults_embedded(self) -> None:
        cfg = self._minimal()
        assert cfg.lora.r == 16
        assert cfg.lora.alpha == 32

    def test_custom_lora(self) -> None:
        cfg = self._minimal(lora={"r": 8, "alpha": 16, "dropout": 0.1})
        assert cfg.lora.r == 8

    def test_invalid_lr_scheduler(self) -> None:
        with pytest.raises(ValueError):
            self._minimal(lr_scheduler="polynomial")

    def test_valid_lr_schedulers(self) -> None:
        for sched in ("cosine", "linear", "constant", "constant_with_warmup"):
            cfg = self._minimal(lr_scheduler=sched)
            assert cfg.lr_scheduler == sched

    def test_invalid_save_strategy(self) -> None:
        with pytest.raises(ValueError):
            self._minimal(save_strategy="best")

    def test_max_seq_length_bounds(self) -> None:
        with pytest.raises(ValueError):
            self._minimal(max_seq_length=16)
        with pytest.raises(ValueError):
            self._minimal(max_seq_length=8192)

    def test_learning_rate_positive(self) -> None:
        with pytest.raises(ValueError):
            self._minimal(learning_rate=0.0)
        with pytest.raises(ValueError):
            self._minimal(learning_rate=-1e-4)

    def test_optional_val_file(self) -> None:
        cfg = self._minimal()
        assert cfg.val_file is None

    def test_val_file_set(self) -> None:
        cfg = self._minimal(val_file="data/assembled/val.jsonl")
        assert cfg.val_file == "data/assembled/val.jsonl"


class TestLoadConfig:
    def test_load_intent_yaml(self) -> None:
        cfg = load_config(CONFIGS_DIR / "training_intent.yaml")
        assert cfg.task == TaskType.INTENT
        assert cfg.train_file == "data/training/intent_train.jsonl"
        assert cfg.output_dir == "outputs/sft-intent"
        assert cfg.lora.r == 16
        assert cfg.learning_rate == 2e-4

    def test_load_slot_yaml(self) -> None:
        cfg = load_config(CONFIGS_DIR / "training_slot.yaml")
        assert cfg.task == TaskType.SLOT
        assert cfg.train_file == "data/training/slot_train.jsonl"
        assert cfg.output_dir == "outputs/sft-slot"

    def test_load_nonexistent_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.yaml")

    def test_roundtrip_all_fields(self) -> None:
        """Verify YAML configs populate all expected fields."""
        cfg = load_config(CONFIGS_DIR / "training_intent.yaml")
        assert cfg.base_model == "Qwen/Qwen2.5-0.5B-Instruct"
        assert cfg.max_seq_length == 512
        assert cfg.use_quantization is True
        assert cfg.quantization.load_in_4bit is True
        assert cfg.warmup_ratio == 0.05
        assert cfg.per_device_batch_size == 16
        assert cfg.gradient_accumulation_steps == 2
        assert cfg.weight_decay == 0.01
        assert cfg.save_strategy == "epoch"
        assert cfg.logging_steps == 10
        assert cfg.seed == 42
