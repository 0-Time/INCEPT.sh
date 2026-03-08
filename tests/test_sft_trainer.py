"""Tests for incept.training.sft_trainer — mock-based, no real ML deps."""

from __future__ import annotations

from importlib import reload
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from incept.training.config import TrainingConfig

_trl_available = True
try:
    import trl  # noqa: F401
except ImportError:
    _trl_available = False


def _make_config(**overrides: object) -> TrainingConfig:
    defaults: dict[str, object] = {
        "task": "intent",
        "train_file": "data/training/intent_train.jsonl",
    }
    defaults.update(overrides)
    return TrainingConfig(**defaults)  # type: ignore[arg-type]


class TestResolveDevice:
    def test_explicit_device(self) -> None:
        from incept.training.sft_trainer import _resolve_device

        config = _make_config(device="cpu")
        assert _resolve_device(config) == "cpu"

    def test_explicit_cuda(self) -> None:
        from incept.training.sft_trainer import _resolve_device

        config = _make_config(device="cuda")
        assert _resolve_device(config) == "cuda"

    def test_auto_cpu_fallback(self) -> None:
        from incept.training.sft_trainer import _resolve_device

        config = _make_config(device="auto")
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False
        with patch.dict("sys.modules", {"torch": mock_torch}):
            assert _resolve_device(config) == "cpu"

    def test_auto_mps_detection(self) -> None:
        from incept.training.sft_trainer import _resolve_device

        config = _make_config(device="auto")
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = True
        with patch.dict("sys.modules", {"torch": mock_torch}):
            assert _resolve_device(config) == "mps"

    def test_auto_cuda_detection(self) -> None:
        from incept.training.sft_trainer import _resolve_device

        config = _make_config(device="auto")
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        with patch.dict("sys.modules", {"torch": mock_torch}):
            assert _resolve_device(config) == "cuda"


class TestCanUseBnb:
    def test_bnb_available(self) -> None:
        from incept.training.sft_trainer import _can_use_bnb

        with patch.dict("sys.modules", {"bitsandbytes": MagicMock()}):
            assert _can_use_bnb() is True

    def test_bnb_not_available(self) -> None:
        from incept.training.sft_trainer import _can_use_bnb

        with (
            patch.dict("sys.modules", {"bitsandbytes": None}),
            patch("builtins.__import__", side_effect=ImportError),
        ):
            assert _can_use_bnb() is False


@pytest.mark.skipif(not _trl_available, reason="trl not installed")
class TestBuildTrainingArgs:
    def test_cuda_enables_fp16(self) -> None:
        mock_sft_config = MagicMock()
        with patch("incept.training.sft_trainer.SFTConfig", mock_sft_config, create=True):
            import incept.training.sft_trainer as mod

            # Patch SFTConfig at module level after reload
            with (
                patch.object(mod, "_build_training_args", wraps=mod._build_training_args),
                patch("trl.SFTConfig", mock_sft_config),
            ):
                config = _make_config()
                mod._build_training_args(config, "cuda")
                call_kwargs = mock_sft_config.call_args[1]
                assert call_kwargs["fp16"] is True
                assert call_kwargs["bf16"] is False

    def test_cpu_disables_fp16(self) -> None:
        mock_sft_config = MagicMock()
        with patch("incept.training.sft_trainer.SFTConfig", mock_sft_config, create=True):
            import incept.training.sft_trainer as mod

            with (
                patch.object(mod, "_build_training_args", wraps=mod._build_training_args),
                patch("trl.SFTConfig", mock_sft_config),
            ):
                config = _make_config()
                mod._build_training_args(config, "cpu")
                call_kwargs = mock_sft_config.call_args[1]
                assert call_kwargs["fp16"] is False


class TestBuildLoraConfig:
    def test_builds_lora_config(self) -> None:
        mock_peft = MagicMock()
        with patch.dict("sys.modules", {"peft": mock_peft}):
            import incept.training.sft_trainer as mod

            reload(mod)
            config = _make_config()
            mod._build_lora_config(config)
            mock_peft.LoraConfig.assert_called_once()
            call_kwargs = mock_peft.LoraConfig.call_args[1]
            assert call_kwargs["r"] == 16
            assert call_kwargs["lora_alpha"] == 32
            assert call_kwargs["lora_dropout"] == 0.05


class TestRunSft:
    def test_run_sft_orchestration(self, tmp_path: Path) -> None:
        mock_trl = MagicMock()
        mock_trainer_instance = MagicMock()
        mock_trl.SFTTrainer.return_value = mock_trainer_instance

        with patch.dict("sys.modules", {"trl": mock_trl}):
            import incept.training.sft_trainer as mod

            reload(mod)

            mock_model_tokenizer = (MagicMock(), MagicMock())
            with (
                patch("incept.training._require_ml_deps"),
                patch.object(mod, "_resolve_device", return_value="cpu") as mock_device,
                patch.object(
                    mod, "_build_model_and_tokenizer", return_value=mock_model_tokenizer
                ) as mock_model,
                patch.object(mod, "_build_lora_config") as mock_lora,
                patch.object(mod, "_build_training_args") as mock_args,
                patch(
                    "incept.training.data_pipeline.load_as_hf_dataset",
                    return_value=MagicMock(),
                ) as mock_data,
            ):
                config = _make_config(output_dir=str(tmp_path / "output"))
                mod.run_sft(config)

                mock_device.assert_called_once_with(config)
                mock_model.assert_called_once()
                mock_lora.assert_called_once()
                mock_args.assert_called_once()
                mock_data.assert_called()
                mock_trainer_instance.train.assert_called_once()
                mock_trainer_instance.save_model.assert_called_once()
