"""Automated training pipeline: monitors intent SFT, runs slot SFT, merges, converts to GGUF."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

# Ensure we're in project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

# Add project to path
sys.path.insert(0, str(PROJECT_ROOT))


def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def wait_for_intent_training(pid: int, output_dir: str) -> bool:
    """Wait for intent training (PID) to finish and produce final checkpoint."""
    final_dir = Path(output_dir) / "final"
    log(f"Waiting for intent training (PID {pid}) to complete...")
    log(f"  Watching for: {final_dir}")

    while True:
        # Check if process is still running
        try:
            os.kill(pid, 0)
            alive = True
        except OSError:
            alive = False

        if final_dir.exists():
            log(f"Intent training complete! Final checkpoint at {final_dir}")
            return True

        if not alive:
            # Process died — check if final dir was created
            if final_dir.exists():
                log(f"Intent training complete! Final checkpoint at {final_dir}")
                return True
            else:
                log("ERROR: Intent training process died without producing final checkpoint!")
                # Check for any checkpoints
                checkpoints = sorted(Path(output_dir).glob("checkpoint-*"))
                if checkpoints:
                    log(f"  Found checkpoints: {[c.name for c in checkpoints]}")
                    log(f"  Latest: {checkpoints[-1]}")
                return False

        time.sleep(30)


def run_slot_training() -> Path | None:
    """Run slot SFT training."""
    log("=" * 60)
    log("STEP 2: Starting slot SFT training...")
    log("=" * 60)

    from incept.training.config import load_config
    from incept.training.sft_trainer import run_sft

    config = load_config("configs/training_slot.yaml")
    log(f"  Train file: {config.train_file}")
    log(f"  Output dir: {config.output_dir}")
    log(f"  Epochs: {config.num_epochs}, Batch: {config.per_device_batch_size}")

    try:
        output_path = run_sft(config)
        log(f"Slot training complete! Checkpoint at {output_path}")
        return output_path
    except Exception as e:
        log(f"ERROR: Slot training failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def merge_lora_adapters(
    intent_adapter: str,
    slot_adapter: str,
    base_model: str = "Qwen/Qwen3.5-0.8B",
) -> Path | None:
    """Merge both LoRA adapters sequentially into the base model."""
    log("=" * 60)
    log("STEP 3: Merging LoRA adapters...")
    log("=" * 60)

    from incept.training.export import merge_lora_adapter

    # Step 3a: Merge intent adapter into base
    merged_intent_dir = "outputs/merged-intent"
    log(f"  Merging intent LoRA: {base_model} + {intent_adapter} -> {merged_intent_dir}")
    try:
        merge_lora_adapter(base_model, intent_adapter, merged_intent_dir)
        log(f"  Intent merge complete: {merged_intent_dir}")
    except Exception as e:
        log(f"ERROR: Intent LoRA merge failed: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Step 3b: Merge slot adapter into intent-merged model
    merged_final_dir = "outputs/merged-final"
    log(f"  Merging slot LoRA: {merged_intent_dir} + {slot_adapter} -> {merged_final_dir}")
    try:
        merge_lora_adapter(merged_intent_dir, slot_adapter, merged_final_dir)
        log(f"  Slot merge complete: {merged_final_dir}")
    except Exception as e:
        log(f"ERROR: Slot LoRA merge failed: {e}")
        import traceback
        traceback.print_exc()
        return None

    return Path(merged_final_dir)


def convert_to_gguf(merged_dir: str) -> Path | None:
    """Convert merged HF model to GGUF Q4_K_M format."""
    log("=" * 60)
    log("STEP 4: Converting to GGUF format...")
    log("=" * 60)

    output_gguf = Path("models/incept-0.5b-q4_k_m.gguf")
    f16_gguf = Path("models/incept-0.5b-f16.gguf")

    # Step 4a: Convert HF → F16 GGUF
    convert_script = "/opt/homebrew/Cellar/llama.cpp/8140/bin/convert_hf_to_gguf.py"
    if not Path(convert_script).exists():
        # Try finding it
        result = subprocess.run(
            ["find", "/opt/homebrew/Cellar/llama.cpp", "-name", "convert_hf_to_gguf.py"],
            capture_output=True, text=True,
        )
        if result.stdout.strip():
            convert_script = result.stdout.strip().split("\n")[0]
        else:
            log("ERROR: convert_hf_to_gguf.py not found!")
            return None

    log(f"  HF → F16 GGUF: {merged_dir} → {f16_gguf}")
    try:
        result = subprocess.run(
            [
                sys.executable,
                convert_script,
                str(merged_dir),
                "--outfile", str(f16_gguf),
                "--outtype", "f16",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        log(f"  F16 conversion done: {f16_gguf} ({f16_gguf.stat().st_size / 1e6:.1f} MB)")
    except subprocess.CalledProcessError as e:
        log(f"ERROR: F16 conversion failed: {e.stderr}")
        return None

    # Step 4b: Quantize F16 → Q4_K_M
    log(f"  F16 → Q4_K_M: {f16_gguf} → {output_gguf}")
    try:
        result = subprocess.run(
            ["llama-quantize", str(f16_gguf), str(output_gguf), "Q4_K_M"],
            capture_output=True,
            text=True,
            check=True,
        )
        log(f"  Quantization done: {output_gguf} ({output_gguf.stat().st_size / 1e6:.1f} MB)")
    except subprocess.CalledProcessError as e:
        log(f"ERROR: Quantization failed: {e.stderr}")
        return None

    # Clean up F16 intermediate
    if f16_gguf.exists():
        f16_gguf.unlink()
        log(f"  Cleaned up intermediate: {f16_gguf}")

    return output_gguf


def main() -> None:
    intent_pid = int(sys.argv[1]) if len(sys.argv) > 1 else None
    intent_output_dir = "outputs/sft-intent"
    intent_final = Path(intent_output_dir) / "final"
    slot_final = Path("outputs/sft-slot") / "final"

    log("=" * 60)
    log("INCEPT Training Pipeline — Automated")
    log("=" * 60)
    log(f"  Project root: {PROJECT_ROOT}")
    log(f"  Intent training PID: {intent_pid}")

    # STEP 1: Wait for intent training
    if intent_final.exists():
        log("Intent training already complete, skipping wait.")
    elif intent_pid:
        if not wait_for_intent_training(intent_pid, intent_output_dir):
            log("PIPELINE ABORTED: Intent training failed.")
            sys.exit(1)
    else:
        log("ERROR: No intent training PID and no final checkpoint found.")
        sys.exit(1)

    # STEP 2: Slot training
    if slot_final.exists():
        log("Slot training already complete, skipping.")
    else:
        slot_output = run_slot_training()
        if slot_output is None:
            log("PIPELINE ABORTED: Slot training failed.")
            sys.exit(1)

    # STEP 3: Merge LoRA adapters
    merged_final = Path("outputs/merged-final")
    if merged_final.exists() and any(merged_final.iterdir()):
        log("Merged model already exists, skipping merge.")
    else:
        result = merge_lora_adapters(
            intent_adapter=str(intent_final),
            slot_adapter=str(slot_final),
        )
        if result is None:
            log("PIPELINE ABORTED: LoRA merge failed.")
            sys.exit(1)

    # STEP 4: Convert to GGUF
    output_gguf = Path("models/incept-0.5b-q4_k_m.gguf")
    if output_gguf.exists():
        log(f"GGUF already exists: {output_gguf}")
    else:
        result = convert_to_gguf(str(merged_final))
        if result is None:
            log("PIPELINE ABORTED: GGUF conversion failed.")
            sys.exit(1)

    log("=" * 60)
    log("PIPELINE COMPLETE!")
    log(f"  Fine-tuned GGUF model: {output_gguf}")
    log(f"  Set INCEPT_MODEL_PATH={output_gguf} or it will auto-detect")
    log("  Test with: incept 'install nginx'")
    log("=" * 60)


if __name__ == "__main__":
    main()
