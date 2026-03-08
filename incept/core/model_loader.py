"""Singleton loader for the GGUF model used in the NL → command pipeline."""

from __future__ import annotations

import atexit
import contextlib
import json
import logging
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_MODEL: Any | None = None
_MODEL_PATH: str | None = None

# Project-level models directory (repo root / models)
_MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"

# Port for the llama-server fallback
_LLAMA_SERVER_PORT = 8787
_LLAMA_SERVER_PROC: subprocess.Popen[bytes] | None = None


def _find_gguf() -> str | None:
    """Auto-detect a .gguf file in the models/ directory."""
    if not _MODELS_DIR.is_dir():
        return None
    gguf_files = sorted(_MODELS_DIR.glob("*.gguf"))
    if not gguf_files:
        return None
    if len(gguf_files) > 1:
        logger.warning("Multiple .gguf files found in %s, using %s", _MODELS_DIR, gguf_files[0])
    return str(gguf_files[0])


def _load_suppressed(load_fn: Any, path: str) -> Any:
    """Call *load_fn(path)* while silencing C-level stderr (Metal/ggml warnings)."""
    try:
        stderr_fd = sys.stderr.fileno()
    except (AttributeError, OSError):
        # stderr replaced by test runner or not a real fd
        return load_fn(path)["model"]

    saved_fd = os.dup(stderr_fd)
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, stderr_fd)
        os.close(devnull)
        return load_fn(path)["model"]
    finally:
        os.dup2(saved_fd, stderr_fd)
        os.close(saved_fd)


# ---------------------------------------------------------------------------
# llama-server fallback for unsupported architectures (e.g. Qwen3.5)
# ---------------------------------------------------------------------------


class LlamaServerProxy:
    """Callable proxy that mimics the llama-cpp-python Llama interface.

    Starts ``llama-server`` as a subprocess and sends completion requests
    over HTTP.  The return format matches ``Llama.__call__()`` so the rest
    of the codebase (``run_constrained_inference``) works unchanged.
    """

    def __init__(self, model_path: str, port: int = _LLAMA_SERVER_PORT) -> None:
        self._base_url = f"http://127.0.0.1:{port}"
        self._port = port
        self._proc = _start_llama_server(model_path, port)

    # Same signature as Llama.__call__
    def __call__(self, **kwargs: Any) -> dict[str, Any]:
        prompt = kwargs.get("prompt", "")
        max_tokens = kwargs.get("max_tokens", 128)
        temperature = kwargs.get("temperature", 0.7)
        top_p = kwargs.get("top_p", 0.8)
        top_k = kwargs.get("top_k", 20)

        payload = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "stream": False,
        }

        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{self._base_url}/completion",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())

        text = result.get("content", "")

        # Build a response dict matching Llama.__call__ format
        return {
            "choices": [
                {
                    "text": text,
                    "logprobs": {
                        "tokens": [],
                        "token_logprobs": [],
                    },
                }
            ]
        }

    def close(self) -> None:
        """Shut down the server subprocess."""
        _stop_llama_server()


def _start_llama_server(model_path: str, port: int) -> subprocess.Popen[bytes]:
    """Start llama-server as a background process and wait until ready."""
    global _LLAMA_SERVER_PROC

    llama_server = shutil.which("llama-server")
    if llama_server is None:
        raise RuntimeError(
            "llama-server not found on PATH. Install via: brew install llama.cpp"
        )

    logger.info("Starting llama-server on port %d (Qwen3.5 fallback)...", port)
    proc = subprocess.Popen(
        [
            llama_server,
            "-m", model_path,
            "--port", str(port),
            "-ngl", "99",
            "-c", "2048",
            "--log-disable",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _LLAMA_SERVER_PROC = proc
    atexit.register(_stop_llama_server)

    # Wait for server to be ready (poll /health)
    deadline = time.time() + 60
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(
                f"llama-server exited with code {proc.returncode} during startup"
            )
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/health")
            with urllib.request.urlopen(req, timeout=2) as resp:
                body = json.loads(resp.read())
                if body.get("status") == "ok":
                    logger.info("llama-server ready on port %d", port)
                    return proc
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            pass
        time.sleep(0.5)

    proc.terminate()
    raise RuntimeError("llama-server failed to become ready within 60 seconds")


def _stop_llama_server() -> None:
    """Terminate the llama-server subprocess if running."""
    global _LLAMA_SERVER_PROC
    if _LLAMA_SERVER_PROC is not None:
        try:
            _LLAMA_SERVER_PROC.terminate()
            _LLAMA_SERVER_PROC.wait(timeout=5)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            with contextlib.suppress(ProcessLookupError):
                _LLAMA_SERVER_PROC.kill()
        _LLAMA_SERVER_PROC = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_model(model_path: str | None = None) -> Any | None:
    """Load and cache the GGUF model singleton.

    Resolution order for model path:
    1. Explicit ``model_path`` argument
    2. ``INCEPT_MODEL_PATH`` environment variable
    3. Auto-detect first ``*.gguf`` in ``models/``

    If llama-cpp-python cannot load the model (e.g. unsupported architecture
    like Qwen3.5), falls back to starting ``llama-server`` as a subprocess
    and proxying requests over HTTP.

    Returns a callable model instance, or ``None`` when no model file is
    found (graceful degradation).
    """
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    path = model_path or os.environ.get("INCEPT_MODEL_PATH") or _find_gguf()
    if path is None:
        logger.info("No GGUF model found — model-based slot filling disabled")
        return None

    if not Path(path).is_file():
        logger.warning("GGUF model path does not exist: %s", path)
        return None

    from incept.training.export import load_gguf_model

    global _MODEL_PATH
    logger.info("Loading GGUF model from %s", path)

    # Try llama-cpp-python first (fastest, in-process).
    # On failure the Llama __del__ destructor prints noisy tracebacks to
    # stderr, so we suppress stderr at the fd level around the whole
    # attempt including GC of the failed object.
    llama_failed = False
    try:
        stderr_fd = sys.stderr.fileno()
    except (AttributeError, OSError):
        stderr_fd = -1

    saved_fd = os.dup(stderr_fd) if stderr_fd >= 0 else -1
    try:
        if stderr_fd >= 0:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, stderr_fd)
            os.close(devnull)
        try:
            result = load_gguf_model(path)
            _MODEL = result["model"]
            _MODEL_PATH = path
            return _MODEL
        except (ValueError, RuntimeError):
            # Force GC so __del__ fires while stderr is still suppressed
            import gc
            gc.collect()
            llama_failed = True
    finally:
        if saved_fd >= 0:
            os.dup2(saved_fd, stderr_fd)
            os.close(saved_fd)

    if llama_failed:
        logger.info("Falling back to llama-server (llama-cpp-python does not support this model)...")

    # Fallback: use llama-server (supports newer architectures)
    try:
        _MODEL = LlamaServerProxy(path)
        _MODEL_PATH = path
        return _MODEL
    except RuntimeError as exc:
        logger.error("llama-server fallback also failed: %s", exc)
        return None


def get_model_path() -> str | None:
    """Return the path of the currently loaded model, or None."""
    return _MODEL_PATH


def is_command_model() -> bool:
    """Return True if the loaded model was trained for direct command generation.

    Checks whether the model filename contains 'command'. The old intent/slot
    model is named ``incept-unified-*.gguf``; a command-trained model would
    be named ``incept-command-*.gguf``.
    """
    if _MODEL_PATH is None:
        return False
    from pathlib import Path as _Path
    return "command" in _Path(_MODEL_PATH).stem.lower()


def reset_model() -> None:
    """Reset the cached model (useful for testing)."""
    global _MODEL, _MODEL_PATH
    _stop_llama_server()
    _MODEL = None
    _MODEL_PATH = None
