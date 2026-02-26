"""DPO preference tuning trainer."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from incept.training.config import TrainingConfig
from incept.training.sft_trainer import (
    _build_model_and_tokenizer,
    _resolve_device,
)


def _build_reference_model(config: TrainingConfig, device: str) -> Any:
    """Load the reference model for DPO.

    If config.dpo.reference_model is set, load from that path.
    Otherwise, load a fresh copy of the base model.
    """
    from incept.training.sft_trainer import _build_model_and_tokenizer

    if config.dpo.reference_model:
        ref_config = config.model_copy(update={"model_local_path": config.dpo.reference_model})
        model, _ = _build_model_and_tokenizer(ref_config, device)
    else:
        model, _ = _build_model_and_tokenizer(config, device)
    return model


def run_dpo(config: TrainingConfig) -> Path:
    """Run DPO preference tuning.

    Args:
        config: Full training configuration with mode="dpo".

    Returns:
        Path to the saved checkpoint directory.
    """
    from incept.training import _require_ml_deps

    _require_ml_deps()

    from trl import DPOTrainer

    from incept.training.data_pipeline import load_dpo_as_hf_dataset

    os.environ.setdefault("HF_HUB_OFFLINE", "1")

    device = _resolve_device(config)
    model, tokenizer = _build_model_and_tokenizer(config, device)
    ref_model = _build_reference_model(config, device)

    train_dataset = load_dpo_as_hf_dataset(config.train_file, seed=config.seed)

    trainer = DPOTrainer(
        model=model,
        ref_model=ref_model,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
        beta=config.dpo.beta,
        max_length=config.dpo.max_length,
        max_prompt_length=config.dpo.max_prompt_length,
    )

    trainer.train()

    output_path = Path(config.output_dir) / "final"
    trainer.save_model(str(output_path))
    tokenizer.save_pretrained(str(output_path))

    return output_path
