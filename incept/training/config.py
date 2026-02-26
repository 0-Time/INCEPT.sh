"""Training configuration: Pydantic models + YAML loader."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class TaskType(StrEnum):
    """SFT training task type."""

    INTENT = "intent"
    SLOT = "slot"


class LoraConfig(BaseModel):
    """LoRA adapter configuration."""

    r: int = Field(default=16, ge=1, le=256)
    alpha: int = Field(default=32, ge=1)
    dropout: float = Field(default=0.05, ge=0.0, le=1.0)
    target_modules: list[str] = Field(
        default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj"]
    )


class QuantizationConfig(BaseModel):
    """QLoRA quantization configuration."""

    load_in_4bit: bool = True
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_quant_type: str = "nf4"


class TrainingConfig(BaseModel):
    """Full SFT training configuration."""

    task: TaskType
    base_model: str = "Qwen/Qwen2.5-0.5B-Instruct"
    model_local_path: str | None = None
    max_seq_length: int = Field(default=512, ge=32, le=4096)

    # LoRA
    lora: LoraConfig = Field(default_factory=LoraConfig)

    # Quantization
    quantization: QuantizationConfig = Field(default_factory=QuantizationConfig)
    use_quantization: bool = True

    # Training hyperparameters
    learning_rate: float = Field(default=2e-4, gt=0.0)
    lr_scheduler: str = "cosine"
    warmup_ratio: float = Field(default=0.05, ge=0.0, le=1.0)
    num_epochs: int = Field(default=5, ge=1)
    per_device_batch_size: int = Field(default=16, ge=1)
    gradient_accumulation_steps: int = Field(default=2, ge=1)
    weight_decay: float = Field(default=0.01, ge=0.0)

    # Data
    train_file: str
    val_file: str | None = None

    # Output
    output_dir: str = "outputs/sft"
    save_strategy: str = "epoch"
    logging_steps: int = Field(default=10, ge=1)

    # Misc
    seed: int = 42
    device: str = "auto"

    @field_validator("lr_scheduler")
    @classmethod
    def _validate_scheduler(cls, v: str) -> str:
        allowed = {"cosine", "linear", "constant", "constant_with_warmup"}
        if v not in allowed:
            msg = f"lr_scheduler must be one of {allowed}, got '{v}'"
            raise ValueError(msg)
        return v

    @field_validator("save_strategy")
    @classmethod
    def _validate_save_strategy(cls, v: str) -> str:
        allowed = {"epoch", "steps", "no"}
        if v not in allowed:
            msg = f"save_strategy must be one of {allowed}, got '{v}'"
            raise ValueError(msg)
        return v


def load_config(path: str | Path) -> TrainingConfig:
    """Load a TrainingConfig from a YAML file."""
    path = Path(path)
    with open(path) as f:
        data: dict[str, Any] = yaml.safe_load(f)
    return TrainingConfig(**data)
