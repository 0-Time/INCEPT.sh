"""Data pipeline: JSONL loading and HuggingFace Dataset conversion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load records from a JSONL file. Pure Python, no ML deps."""
    path = Path(path)
    records: list[dict[str, Any]] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            records.append(json.loads(line))
    return records


def format_for_sft(record: dict[str, Any]) -> dict[str, str]:
    """Merge prompt+completion into a single 'text' field for SFTTrainer.

    Expects record to have 'prompt' and 'completion' keys (as produced by
    the data assembler in data/training/*.jsonl).
    """
    prompt = record.get("prompt", "")
    completion = record.get("completion", "")
    return {"text": f"{prompt}{completion}"}


def load_validation_dataset(
    val_path: str | Path, task: str
) -> list[dict[str, Any]]:
    """Load raw assembled JSONL for evaluation.

    Preserves expected_intent / expected_slots fields for evaluation use.
    Filters records to only those relevant for the given task.

    Args:
        val_path: Path to assembled validation JSONL (data/assembled/val.jsonl).
        task: Either 'intent' or 'slot'.

    Returns:
        List of dicts with at minimum: nl_request, context_line,
        expected_intent, and (for slot) expected_slots.
    """
    records = load_jsonl(val_path)
    # All records have both intent and slot info; return as-is
    validated: list[dict[str, Any]] = []
    for rec in records:
        if "expected_intent" not in rec:
            continue
        if task == "slot" and "expected_slots" not in rec:
            continue
        validated.append(rec)
    return validated


def load_as_hf_dataset(path: str | Path, seed: int = 42) -> Any:
    """Load JSONL and convert to HuggingFace Dataset.

    Requires the `datasets` package (install with `pip install 'incept[ml]'`).
    Records are formatted via format_for_sft before loading.
    """
    from incept.training import _require_ml_deps

    _require_ml_deps()
    from datasets import Dataset
    records = load_jsonl(path)
    formatted = [format_for_sft(r) for r in records]
    dataset: Any = Dataset.from_list(formatted)
    dataset = dataset.shuffle(seed=seed)
    return dataset
