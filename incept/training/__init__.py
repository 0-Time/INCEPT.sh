"""Training infrastructure for INCEPT SFT fine-tuning."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

_ML_PACKAGES = ["transformers", "peft", "trl", "datasets", "accelerate", "torch"]


def _require_ml_deps() -> None:
    """Check that ML dependencies are available, raise ImportError if not."""
    missing: list[str] = []
    for pkg in _ML_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        raise ImportError(
            f"ML dependencies not installed: {', '.join(missing)}. "
            f"Install with: pip install 'incept[ml]'"
        )
