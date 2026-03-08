#!/usr/bin/env python3
"""Full INCEPT v2 training pipeline: SFT → merge LoRA → GGUF.

Usage:
    python scripts/train_v2.py                          # full pipeline
    python scripts/train_v2.py --step train             # SFT only
    python scripts/train_v2.py --step merge             # merge LoRA only
    python scripts/train_v2.py --step gguf              # GGUF export only
    python scripts/train_v2.py --epochs 5 --batch-size 8
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
BASE_MODEL = "Qwen/Qwen3.5-0.8B"
TRAIN_FILE = PROJECT_ROOT / "data" / "v2" / "train.jsonl"
VAL_FILE = PROJECT_ROOT / "data" / "v2" / "val.jsonl"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "sft-command-v2"
MERGED_DIR = PROJECT_ROOT / "outputs" / "merged-command-v2"
GGUF_PATH = PROJECT_ROOT / "models" / "incept-command-v2-q8_0.gguf"


# ---------------------------------------------------------------------------
# Data loading: convert messages → ChatML text
# ---------------------------------------------------------------------------

def messages_to_chatml(messages: list[dict]) -> str:
    """Convert a list of role/content dicts to a ChatML string."""
    parts = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        parts.append(f"<|im_start|>{role}\n{content}<|im_end|>")
    return "\n".join(parts)


def load_chatml_dataset(path: Path, seed: int = 42):
    """Load messages JSONL and convert to HF Dataset with 'text' column."""
    from datasets import Dataset

    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            text = messages_to_chatml(obj["messages"])
            records.append({"text": text})

    dataset = Dataset.from_list(records)
    dataset = dataset.shuffle(seed=seed)
    log.info("Loaded %d examples from %s", len(dataset), path)
    return dataset


# ---------------------------------------------------------------------------
# Step 1: SFT training with LoRA
# ---------------------------------------------------------------------------

def run_train(args: argparse.Namespace) -> Path:
    """Fine-tune Qwen3.5-0.8B with LoRA on ChatML command data."""
    import torch
    from peft import LoraConfig, TaskType
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig, SFTTrainer

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    log.info("Device: %s", device)
    log.info("Base model: %s", args.base_model)
    log.info("Train file: %s", args.train_file)
    log.info("Epochs: %d, batch size: %d, lr: %s", args.epochs, args.batch_size, args.lr)

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        args.base_model, trust_remote_code=True, padding_side="right",
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load model
    log.info("Loading base model...")
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        trust_remote_code=True,
        dtype=torch.float32,  # MPS needs fp32
        device_map=device,
    )

    # LoRA config: r=32, all projection layers including linear attention
    # Qwen3.5 has 3:1 linear:full attention ratio — must target both types
    lora_config = LoraConfig(
        r=32,
        lora_alpha=64,
        lora_dropout=0.05,
        target_modules=[
            # Full attention layers (every 4th layer)
            "q_proj", "k_proj", "v_proj", "o_proj",
            # Linear attention layers (3 out of 4 layers)
            "in_proj_qkv", "in_proj_a", "in_proj_b", "in_proj_z", "out_proj",
            # MLP layers (all layers)
            "gate_proj", "up_proj", "down_proj",
        ],
        task_type=TaskType.CAUSAL_LM,
        bias="none",
    )

    # Training arguments
    output_dir = str(args.output_dir)
    training_args = SFTConfig(
        output_dir=output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        weight_decay=0.01,
        logging_steps=50,
        save_strategy="no",
        fp16=False,
        bf16=False,
        seed=42,
        report_to="none",
        remove_unused_columns=False,
        dataset_text_field="text",
        max_length=1024,
    )

    # Load datasets
    log.info("Loading training data...")
    train_dataset = load_chatml_dataset(Path(args.train_file))
    eval_dataset = None
    if args.val_file and Path(args.val_file).exists():
        eval_dataset = load_chatml_dataset(Path(args.val_file))

    # Create trainer
    log.info("Starting SFT training...")
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        peft_config=lora_config,
        processing_class=tokenizer,
    )

    t0 = time.time()
    trainer.train()
    elapsed = time.time() - t0
    log.info("Training complete in %.1f minutes", elapsed / 60)

    # Save final checkpoint
    final_dir = Path(output_dir) / "final"
    trainer.save_model(str(final_dir))
    tokenizer.save_pretrained(str(final_dir))
    log.info("Saved LoRA adapter to %s", final_dir)

    return final_dir


# ---------------------------------------------------------------------------
# Step 2: Merge LoRA into base model
# ---------------------------------------------------------------------------

def run_merge(args: argparse.Namespace) -> Path:
    """Merge LoRA adapter back into the base model."""
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    adapter_path = Path(args.output_dir) / "final"
    merged_path = Path(args.merged_dir)

    log.info("Merging LoRA adapter from %s", adapter_path)
    log.info("Base model: %s", args.base_model)

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        args.base_model, trust_remote_code=True, dtype=torch.float32,
    )

    model = PeftModel.from_pretrained(base_model, str(adapter_path))
    merged = model.merge_and_unload()

    merged_path.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(merged_path))
    tokenizer.save_pretrained(str(merged_path))

    # Fix architecture name for GGUF conversion: convert_hf_to_gguf.py
    # registers Qwen3_5ForConditionalGeneration, not Qwen3_5ForCausalLM
    config_path = merged_path / "config.json"
    if config_path.exists():
        cfg = json.loads(config_path.read_text())
        if cfg.get("architectures") == ["Qwen3_5ForCausalLM"]:
            cfg["architectures"] = ["Qwen3_5ForConditionalGeneration"]
            config_path.write_text(json.dumps(cfg, indent=2))
            log.info("Patched config.json architecture for GGUF compatibility")

    log.info("Saved merged model to %s", merged_path)

    return merged_path


# ---------------------------------------------------------------------------
# Step 3: Convert to GGUF
# ---------------------------------------------------------------------------

def run_gguf(args: argparse.Namespace) -> Path:
    """Convert merged HF model to GGUF Q4_K_M."""
    import subprocess

    merged_path = Path(args.merged_dir)
    gguf_path = Path(args.gguf_path)

    gguf_path.parent.mkdir(parents=True, exist_ok=True)

    # Step 3a: Convert HF → f16 GGUF
    f16_path = gguf_path.with_name(gguf_path.stem + "-f16.gguf")
    log.info("Converting HF model to f16 GGUF...")
    convert_script = "/opt/homebrew/bin/convert_hf_to_gguf.py"
    subprocess.run(
        [
            sys.executable, convert_script,
            str(merged_path),
            "--outfile", str(f16_path),
            "--outtype", "f16",
        ],
        check=True,
    )
    log.info("f16 GGUF: %s (%.1f MB)", f16_path, f16_path.stat().st_size / 1e6)

    # Step 3b: Quantize to Q8_0
    log.info("Quantizing to Q8_0...")
    subprocess.run(
        [
            "llama-quantize",
            str(f16_path),
            str(gguf_path),
            "q8_0",
        ],
        check=True,
    )
    log.info("Q8_0 GGUF: %s (%.1f MB)", gguf_path, gguf_path.stat().st_size / 1e6)

    # Clean up f16 intermediate
    if f16_path.exists():
        f16_path.unlink()
        log.info("Cleaned up f16 intermediate")

    return gguf_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="INCEPT v2 full training pipeline")
    parser.add_argument(
        "--step", choices=["train", "merge", "gguf", "all"], default="all",
        help="Which step to run (default: all)",
    )
    parser.add_argument("--base-model", default=BASE_MODEL)
    parser.add_argument("--train-file", default=str(TRAIN_FILE))
    parser.add_argument("--val-file", default=str(VAL_FILE))
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    parser.add_argument("--merged-dir", default=str(MERGED_DIR))
    parser.add_argument("--gguf-path", default=str(GGUF_PATH))
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--grad-accum", type=int, default=8)
    parser.add_argument("--lr", type=float, default=2e-4)
    args = parser.parse_args()

    # Suppress noisy warnings
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    steps = {
        "train": [run_train],
        "merge": [run_merge],
        "gguf": [run_gguf],
        "all": [run_train, run_merge, run_gguf],
    }

    t0 = time.time()
    for step_fn in steps[args.step]:
        log.info("=" * 70)
        log.info("Running: %s", step_fn.__name__)
        log.info("=" * 70)
        step_fn(args)

    elapsed = time.time() - t0
    log.info("=" * 70)
    log.info("Pipeline complete in %.1f minutes", elapsed / 60)
    log.info("=" * 70)


if __name__ == "__main__":
    main()
