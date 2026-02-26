"""LoRA merge, GGUF export, and constrained inference."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def merge_lora_adapter(
    base_path: str | Path,
    adapter_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Merge LoRA adapter weights back into the base model.

    Args:
        base_path: Path to the base model (or HF model ID).
        adapter_path: Path to the LoRA adapter checkpoint.
        output_path: Where to save the merged model.

    Returns:
        Path to the merged model directory.
    """
    from incept.training import _require_ml_deps

    _require_ml_deps()

    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(str(base_path), trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        str(base_path), trust_remote_code=True
    )
    model = PeftModel.from_pretrained(base_model, str(adapter_path))
    merged = model.merge_and_unload()

    merged.save_pretrained(str(output_path))
    tokenizer.save_pretrained(str(output_path))

    return output_path


def convert_to_gguf(
    model_path: str | Path,
    output_path: str | Path,
    quantization: str = "q4_k_m",
) -> Path:
    """Convert a HuggingFace model to GGUF format via llama.cpp.

    Requires llama.cpp's convert script to be available on PATH
    or at a known location.

    Args:
        model_path: Path to the merged HF model.
        output_path: Path for the output GGUF file.
        quantization: Quantization level (e.g., q4_k_m, q5_k_m, q8_0).

    Returns:
        Path to the GGUF file.
    """
    model_path = Path(model_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Step 1: Convert to f16 GGUF
    f16_path = output_path.with_suffix(".f16.gguf")
    subprocess.run(
        [
            "python", "-m", "llama_cpp.convert",
            "--model", str(model_path),
            "--outfile", str(f16_path),
            "--outtype", "f16",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    # Step 2: Quantize
    subprocess.run(
        [
            "llama-quantize",
            str(f16_path),
            str(output_path),
            quantization,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    # Clean up f16 intermediate
    if f16_path.exists() and f16_path != output_path:
        f16_path.unlink()

    return output_path


def load_gguf_model(
    gguf_path: str | Path,
    grammar_path: str | Path | None = None,
    n_ctx: int = 512,
    n_gpu_layers: int = 0,
) -> Any:
    """Load a GGUF model via llama-cpp-python.

    Args:
        gguf_path: Path to the GGUF model file.
        grammar_path: Optional path to a GBNF grammar file.
        n_ctx: Context window size.
        n_gpu_layers: Number of layers to offload to GPU.

    Returns:
        A dict with 'model' and optionally 'grammar' keys.
    """
    from llama_cpp import Llama, LlamaGrammar

    model = Llama(
        model_path=str(gguf_path),
        n_ctx=n_ctx,
        n_gpu_layers=n_gpu_layers,
        logits_all=True,
        verbose=False,
    )

    grammar = None
    if grammar_path:
        with open(grammar_path) as f:
            grammar_text = f.read()
        grammar = LlamaGrammar.from_string(grammar_text)

    return {"model": model, "grammar": grammar}


def run_constrained_inference(
    model: Any,
    prompt: str,
    grammar: Any | None = None,
    max_tokens: int = 128,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """Run a single constrained inference pass.

    Args:
        model: A llama-cpp-python Llama model instance.
        prompt: The input prompt string.
        grammar: Optional LlamaGrammar for constrained decoding.
        max_tokens: Maximum tokens to generate.
        temperature: Sampling temperature (0.0 = greedy).

    Returns:
        Dict with 'text', 'tokens', 'logprobs' keys.
    """
    kwargs: dict[str, Any] = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "logprobs": True,
    }
    if grammar is not None:
        kwargs["grammar"] = grammar

    output = model(** kwargs)

    choice = output["choices"][0]
    text = choice["text"]
    logprobs_data = choice.get("logprobs", {})

    token_logprobs: list[float] = []
    if logprobs_data and "token_logprobs" in logprobs_data:
        token_logprobs = [
            lp for lp in logprobs_data["token_logprobs"] if lp is not None
        ]

    return {
        "text": text,
        "tokens": logprobs_data.get("tokens", []),
        "logprobs": token_logprobs,
    }
