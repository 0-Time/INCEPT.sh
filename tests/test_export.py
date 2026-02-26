"""Tests for incept.training.export — mock-based, no real ML deps."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestMergeLoraAdapter:
    @patch("incept.training._require_ml_deps")
    def test_merge_calls_peft(self, mock_deps: MagicMock, tmp_path: Path) -> None:
        mock_peft = MagicMock()
        mock_transformers = MagicMock()

        mock_base_model = MagicMock()
        mock_transformers.AutoModelForCausalLM.from_pretrained.return_value = mock_base_model

        mock_merged = MagicMock()
        mock_peft_model = MagicMock()
        mock_peft_model.merge_and_unload.return_value = mock_merged
        mock_peft.PeftModel.from_pretrained.return_value = mock_peft_model

        with patch.dict(
            "sys.modules",
            {"peft": mock_peft, "transformers": mock_transformers},
        ):
            from importlib import reload

            import incept.training.export as mod

            reload(mod)

            output = tmp_path / "merged"
            result = mod.merge_lora_adapter(
                base_path="Qwen/Qwen2.5-0.5B",
                adapter_path=str(tmp_path / "adapter"),
                output_path=str(output),
            )

            mock_transformers.AutoModelForCausalLM.from_pretrained.assert_called_once()
            mock_peft.PeftModel.from_pretrained.assert_called_once()
            mock_peft_model.merge_and_unload.assert_called_once()
            mock_merged.save_pretrained.assert_called_once()
            assert result == output


class TestConvertToGguf:
    @patch("subprocess.run")
    def test_convert_calls_subprocess(self, mock_run: MagicMock, tmp_path: Path) -> None:
        from incept.training.export import convert_to_gguf

        model_path = tmp_path / "model"
        model_path.mkdir()
        output_path = tmp_path / "output.gguf"

        result = convert_to_gguf(model_path, output_path, quantization="q4_k_m")

        assert mock_run.call_count == 2
        # First call: convert to f16
        first_call = mock_run.call_args_list[0]
        assert "f16" in str(first_call)
        # Second call: quantize
        second_call = mock_run.call_args_list[1]
        assert "q4_k_m" in str(second_call)
        assert result == output_path

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "cmd"))
    def test_convert_raises_on_failure(self, mock_run: MagicMock, tmp_path: Path) -> None:
        from incept.training.export import convert_to_gguf

        with pytest.raises(subprocess.CalledProcessError):
            convert_to_gguf(tmp_path / "model", tmp_path / "out.gguf")


class TestLoadGgufModel:
    def test_load_without_grammar(self) -> None:
        mock_llama_mod = MagicMock()
        mock_model_instance = MagicMock()
        mock_llama_mod.Llama.return_value = mock_model_instance

        with patch.dict("sys.modules", {"llama_cpp": mock_llama_mod}):
            from importlib import reload

            import incept.training.export as mod

            reload(mod)
            result = mod.load_gguf_model("/path/to/model.gguf", n_ctx=256)

            assert result["model"] == mock_model_instance
            assert result["grammar"] is None
            mock_llama_mod.Llama.assert_called_once()

    def test_load_with_grammar(self, tmp_path: Path) -> None:
        mock_llama_mod = MagicMock()
        mock_model_instance = MagicMock()
        mock_grammar_instance = MagicMock()
        mock_llama_mod.Llama.return_value = mock_model_instance
        mock_llama_mod.LlamaGrammar.from_string.return_value = mock_grammar_instance

        grammar_file = tmp_path / "test.gbnf"
        grammar_file.write_text('root ::= "hello"')

        with patch.dict("sys.modules", {"llama_cpp": mock_llama_mod}):
            from importlib import reload

            import incept.training.export as mod

            reload(mod)
            result = mod.load_gguf_model(
                "/path/to/model.gguf",
                grammar_path=str(grammar_file),
            )

            assert result["model"] == mock_model_instance
            assert result["grammar"] == mock_grammar_instance


class TestRunConstrainedInference:
    def test_basic_inference(self) -> None:
        from incept.training.export import run_constrained_inference

        mock_model = MagicMock()
        mock_model.return_value = {
            "choices": [
                {
                    "text": "find_files",
                    "logprobs": {
                        "tokens": ["find", "_", "files"],
                        "token_logprobs": [-0.1, -0.05, -0.02],
                    },
                }
            ]
        }

        result = run_constrained_inference(mock_model, "classify this")
        assert result["text"] == "find_files"
        assert len(result["logprobs"]) == 3
        assert result["tokens"] == ["find", "_", "files"]

    def test_inference_with_grammar(self) -> None:
        from incept.training.export import run_constrained_inference

        mock_model = MagicMock()
        mock_grammar = MagicMock()
        mock_model.return_value = {
            "choices": [
                {
                    "text": "find_files",
                    "logprobs": {
                        "tokens": ["find_files"],
                        "token_logprobs": [-0.1],
                    },
                }
            ]
        }

        run_constrained_inference(mock_model, "classify", grammar=mock_grammar)
        # Verify grammar was passed to model
        call_kwargs = mock_model.call_args[1]
        assert call_kwargs["grammar"] == mock_grammar

    def test_inference_no_logprobs(self) -> None:
        from incept.training.export import run_constrained_inference

        mock_model = MagicMock()
        mock_model.return_value = {
            "choices": [{"text": "find_files", "logprobs": {}}]
        }

        result = run_constrained_inference(mock_model, "test")
        assert result["text"] == "find_files"
        assert result["logprobs"] == []

    def test_greedy_decoding(self) -> None:
        from incept.training.export import run_constrained_inference

        mock_model = MagicMock()
        mock_model.return_value = {
            "choices": [{"text": "ok", "logprobs": {"tokens": [], "token_logprobs": []}}]
        }

        run_constrained_inference(mock_model, "test", temperature=0.0)
        call_kwargs = mock_model.call_args[1]
        assert call_kwargs["temperature"] == 0.0
