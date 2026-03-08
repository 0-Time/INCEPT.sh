#!/usr/bin/env python3
"""Surgical LoRA fine-tune on targeted fixes only.

Takes the already-merged SFT model (75/100) and does a quick LoRA
on just the 730 targeted examples. ~15 min instead of 9 hours.

Usage:
    python scripts/train_surgical.py --step train     # quick LoRA
    python scripts/train_surgical.py --step merge     # merge into base
    python scripts/train_surgical.py --step gguf      # export GGUF
    python scripts/train_surgical.py --step all       # full pipeline
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Use the ALREADY TRAINED SFT-merged model as base
MERGED_SFT = PROJECT_ROOT / "outputs" / "merged-command-v2"
FIXES_FILE = PROJECT_ROOT / "data" / "v2" / "targeted_fixes" / "all_targeted_fixes.jsonl"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "surgical-command-v2"
FINAL_MERGED = PROJECT_ROOT / "outputs" / "surgical-merged-v2"
GGUF_PATH = PROJECT_ROOT / "models" / "incept-command-v2-q8_0.gguf"


def messages_to_chatml(messages: list[dict]) -> str:
    parts = []
    for msg in messages:
        parts.append(f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>")
    return "\n".join(parts)


def run_train(args):
    import torch
    from datasets import Dataset
    from peft import LoraConfig, TaskType
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig, SFTTrainer

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    log.info("Device: %s", device)
    log.info("Base model: %s (already SFT-trained)", MERGED_SFT)
    log.info("Fixes file: %s", FIXES_FILE)

    tokenizer = AutoTokenizer.from_pretrained(
        str(MERGED_SFT), trust_remote_code=True, padding_side="right",
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        str(MERGED_SFT), trust_remote_code=True, dtype=torch.float32, device_map=device,
    )

    # Smaller LoRA for surgical correction
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "in_proj_qkv", "in_proj_a", "in_proj_b", "in_proj_z", "out_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        task_type=TaskType.CAUSAL_LM,
        bias="none",
    )

    # Load targeted fixes
    records = []
    with open(FIXES_FILE) as f:
        for line in f:
            obj = json.loads(line.strip())
            text = messages_to_chatml(obj["messages"])
            records.append({"text": text})

    dataset = Dataset.from_list(records).shuffle(seed=42)
    log.info("Loaded %d targeted fix examples", len(dataset))

    training_args = SFTConfig(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=5,         # More epochs on small dataset
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=1e-4,         # Moderate LR for corrections
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        weight_decay=0.01,
        logging_steps=5,
        save_strategy="no",
        fp16=False,
        bf16=False,
        seed=42,
        report_to="none",
        remove_unused_columns=False,
        dataset_text_field="text",
        max_length=512,
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        peft_config=lora_config,
        processing_class=tokenizer,
    )

    t0 = time.time()
    trainer.train()
    elapsed = time.time() - t0
    log.info("Surgical training complete in %.1f minutes", elapsed / 60)

    final_dir = Path(str(OUTPUT_DIR)) / "final"
    trainer.save_model(str(final_dir))
    tokenizer.save_pretrained(str(final_dir))
    log.info("Saved surgical LoRA adapter to %s", final_dir)
    return final_dir


def run_merge(args):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    adapter_path = OUTPUT_DIR / "final"
    log.info("Merging surgical adapter from %s", adapter_path)

    tokenizer = AutoTokenizer.from_pretrained(str(MERGED_SFT), trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        str(MERGED_SFT), trust_remote_code=True, dtype=torch.float32,
    )
    model = PeftModel.from_pretrained(base_model, str(adapter_path))
    merged = model.merge_and_unload()

    FINAL_MERGED.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(FINAL_MERGED))
    tokenizer.save_pretrained(str(FINAL_MERGED))

    # Patch architecture
    config_path = FINAL_MERGED / "config.json"
    if config_path.exists():
        cfg = json.loads(config_path.read_text())
        if cfg.get("architectures") == ["Qwen3_5ForCausalLM"]:
            cfg["architectures"] = ["Qwen3_5ForConditionalGeneration"]
            config_path.write_text(json.dumps(cfg, indent=2))
            log.info("Patched config.json architecture")

    log.info("Saved surgical-merged model to %s", FINAL_MERGED)
    return FINAL_MERGED


def run_gguf(args):
    f16_path = GGUF_PATH.with_name(GGUF_PATH.stem + "-f16.gguf")
    GGUF_PATH.parent.mkdir(parents=True, exist_ok=True)

    log.info("Converting to f16 GGUF...")
    subprocess.run([
        sys.executable, "/opt/homebrew/bin/convert_hf_to_gguf.py",
        str(FINAL_MERGED), "--outfile", str(f16_path), "--outtype", "f16",
    ], check=True)

    log.info("Quantizing to Q8_0...")
    subprocess.run(["llama-quantize", str(f16_path), str(GGUF_PATH), "q8_0"], check=True)

    if f16_path.exists():
        f16_path.unlink()

    log.info("GGUF: %s (%.1f MB)", GGUF_PATH, GGUF_PATH.stat().st_size / 1e6)
    return GGUF_PATH


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", choices=["train", "merge", "gguf", "all"], default="all")
    args = parser.parse_args()
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    steps = {"train": [run_train], "merge": [run_merge], "gguf": [run_gguf],
             "all": [run_train, run_merge, run_gguf]}

    t0 = time.time()
    for fn in steps[args.step]:
        log.info("=" * 60)
        log.info("Running: %s", fn.__name__)
        log.info("=" * 60)
        fn(args)

    log.info("=" * 60)
    log.info("Surgical pipeline complete in %.1f minutes", (time.time() - t0) / 60)


if __name__ == "__main__":
    main()
