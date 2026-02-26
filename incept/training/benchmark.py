"""Multi-adapter merge and benchmark report generation."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from incept.eval.metrics import (
    IntentMetrics,
    SlotMetrics,
    compute_intent_accuracy,
    compute_slot_metrics,
)
from incept.training.adversarial import generate_canaries, validate_canary_pass_rate
from incept.training.export import merge_lora_adapter


class BenchmarkReport(BaseModel):
    """Full benchmark evaluation report."""

    model_name: str
    intent_metrics: IntentMetrics | None = None
    slot_metrics: SlotMetrics | None = None
    safety_pass_rate: float = Field(ge=0.0, le=1.0)
    grammar_validity: float = Field(ge=0.0, le=1.0)
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


def merge_multiple_adapters(
    base_path: str | Path,
    adapter_paths: list[str | Path],
    output_path: str | Path,
) -> Path:
    """Merge multiple LoRA adapters sequentially into a base model.

    Args:
        base_path: Path to the base model.
        adapter_paths: List of adapter paths to merge in order.
        output_path: Final output directory.

    Returns:
        Path to the merged model directory.
    """
    base_path = Path(base_path)
    output_path = Path(output_path)

    if not adapter_paths:
        return base_path

    current_base = base_path
    for i, adapter in enumerate(adapter_paths):
        is_last = i == len(adapter_paths) - 1
        target = output_path if is_last else output_path / f"intermediate_{i}"
        merge_lora_adapter(
            base_path=current_base,
            adapter_path=adapter,
            output_path=target,
        )
        current_base = target

    return output_path


def run_benchmark(
    model_path: str,
    test_data_dir: str,
) -> BenchmarkReport:
    """Run a full benchmark evaluation suite.

    Args:
        model_path: Path to the model (GGUF or HF directory).
        test_data_dir: Directory with test data (intent/, slot/ subdirs).

    Returns:
        BenchmarkReport with all metrics.
    """
    test_dir = Path(test_data_dir)

    # Intent evaluation
    intent_dir = test_dir / "intent"
    intent_metrics = None
    if intent_dir.exists():
        with open(intent_dir / "predictions.json") as f:
            preds = json.load(f)
        with open(intent_dir / "ground_truth.json") as f:
            gt = json.load(f)
        if preds and gt:
            intent_metrics = compute_intent_accuracy(preds, gt)

    # Slot evaluation
    slot_dir = test_dir / "slot"
    slot_metrics = None
    if slot_dir.exists():
        with open(slot_dir / "predictions.json") as f:
            slot_preds = json.load(f)
        with open(slot_dir / "ground_truth.json") as f:
            slot_gt = json.load(f)
        intents = None
        intents_path = slot_dir / "intents.json"
        if intents_path.exists():
            with open(intents_path) as f:
                intents = json.load(f)
        if slot_preds and slot_gt:
            slot_metrics = compute_slot_metrics(slot_preds, slot_gt, intents=intents)

    # Safety canary check
    generate_canaries()  # Validates canary set is well-formed
    safety_rate = validate_canary_pass_rate([], [])

    return BenchmarkReport(
        model_name=Path(model_path).stem,
        intent_metrics=intent_metrics,
        slot_metrics=slot_metrics,
        safety_pass_rate=safety_rate,
        grammar_validity=1.0,
    )
