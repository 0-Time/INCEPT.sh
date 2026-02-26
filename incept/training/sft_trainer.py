"""Unified SFT trainer for intent classification and slot filling."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from incept.training.config import TrainingConfig


def _resolve_device(config: TrainingConfig) -> str:
    """Resolve the training device: cuda > mps > cpu."""
    if config.device != "auto":
        return config.device

    try:
        import torch
    except ImportError:
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _can_use_bnb() -> bool:
    """Check if bitsandbytes is available (for QLoRA quantization)."""
    try:
        import bitsandbytes  # noqa: F401

        return True
    except ImportError:
        return False


def _build_model_and_tokenizer(
    config: TrainingConfig, device: str
) -> tuple[Any, Any]:
    """Load base model and tokenizer with optional QLoRA quantization.

    Returns:
        (model, tokenizer) tuple.
    """
    from incept.training import _require_ml_deps

    _require_ml_deps()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_path = config.model_local_path or config.base_model

    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True,
        padding_side="right",
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_kwargs: dict[str, Any] = {
        "trust_remote_code": True,
    }

    # QLoRA quantization: only on CUDA with bitsandbytes
    if config.use_quantization and device == "cuda" and _can_use_bnb():
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=config.quantization.load_in_4bit,
            bnb_4bit_compute_dtype=config.quantization.bnb_4bit_compute_dtype,
            bnb_4bit_quant_type=config.quantization.bnb_4bit_quant_type,
        )
        model_kwargs["quantization_config"] = bnb_config
    else:
        model_kwargs["device_map"] = device if device != "cpu" else None

    model = AutoModelForCausalLM.from_pretrained(model_path, **model_kwargs)

    return model, tokenizer


def _build_lora_config(config: TrainingConfig) -> Any:
    """Build PEFT LoRA configuration."""
    from peft import LoraConfig as PeftLoraConfig
    from peft import TaskType
    return PeftLoraConfig(
        r=config.lora.r,
        lora_alpha=config.lora.alpha,
        lora_dropout=config.lora.dropout,
        target_modules=config.lora.target_modules,
        task_type=TaskType.CAUSAL_LM,
        bias="none",
    )


def _build_training_args(config: TrainingConfig, device: str) -> Any:
    """Build HuggingFace TrainingArguments."""
    from transformers import TrainingArguments
    fp16 = device == "cuda"
    bf16 = False

    return TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.per_device_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        lr_scheduler_type=config.lr_scheduler,
        warmup_ratio=config.warmup_ratio,
        weight_decay=config.weight_decay,
        logging_steps=config.logging_steps,
        save_strategy=config.save_strategy,
        fp16=fp16,
        bf16=bf16,
        seed=config.seed,
        report_to="tensorboard",
        remove_unused_columns=False,
    )


def run_sft(config: TrainingConfig) -> Path:
    """Run SFT training.

    Main entry point: loads data, builds model, runs SFTTrainer, saves checkpoint.

    Args:
        config: Full training configuration.

    Returns:
        Path to the best checkpoint directory.
    """
    from incept.training import _require_ml_deps

    _require_ml_deps()

    from trl import SFTTrainer

    from incept.training.data_pipeline import load_as_hf_dataset

    # Set offline mode
    os.environ.setdefault("HF_HUB_OFFLINE", "1")

    device = _resolve_device(config)
    model, tokenizer = _build_model_and_tokenizer(config, device)
    lora_config = _build_lora_config(config)
    training_args = _build_training_args(config, device)

    train_dataset = load_as_hf_dataset(config.train_file, seed=config.seed)
    eval_dataset = None
    if config.val_file:
        eval_dataset = load_as_hf_dataset(config.val_file, seed=config.seed)

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        peft_config=lora_config,
        tokenizer=tokenizer,
        max_seq_length=config.max_seq_length,
        dataset_text_field="text",
    )

    trainer.train()

    output_path = Path(config.output_dir) / "final"
    trainer.save_model(str(output_path))
    tokenizer.save_pretrained(str(output_path))

    return output_path
