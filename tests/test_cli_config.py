"""Tests for CLI configuration loading."""

from __future__ import annotations

from pathlib import Path

from incept.cli.config import InceptConfig, load_config


class TestInceptConfig:
    """CLI config defaults and TOML loading."""

    def test_defaults(self) -> None:
        config = InceptConfig()
        assert config.safe_mode is True
        assert config.verbosity == "normal"
        assert config.auto_execute is False
        assert config.color is True
        assert config.prompt == "incept> "

    def test_load_from_toml(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "config.toml"
        toml_file.write_text(
            '[incept]\nsafe_mode = false\nverbosity = "detailed"\nprompt = ">> "\n'
        )
        config = load_config(str(toml_file))
        assert config.safe_mode is False
        assert config.verbosity == "detailed"
        assert config.prompt == ">> "

    def test_missing_file_returns_defaults(self) -> None:
        config = load_config("/nonexistent/path/config.toml")
        assert config.safe_mode is True

    def test_safe_mode_setting(self) -> None:
        config = InceptConfig(safe_mode=False)
        assert config.safe_mode is False

    def test_model_path_setting(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "config.toml"
        toml_file.write_text('[incept]\nmodel_path = "/models/v1/model.gguf"\n')
        config = load_config(str(toml_file))
        assert config.model_path == "/models/v1/model.gguf"

    def test_color_setting(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "config.toml"
        toml_file.write_text("[incept]\ncolor = false\n")
        config = load_config(str(toml_file))
        assert config.color is False

    def test_custom_prompt(self) -> None:
        config = InceptConfig(prompt="$ ")
        assert config.prompt == "$ "
