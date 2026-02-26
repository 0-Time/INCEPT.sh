"""Tests for server configuration."""

from __future__ import annotations

import os
from unittest.mock import patch

from incept.server.config import ServerConfig


class TestServerConfig:
    """Server configuration from defaults and env vars."""

    def test_defaults(self) -> None:
        config = ServerConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 8080
        assert config.api_key is None
        assert config.rate_limit == 60
        assert config.request_timeout == 30.0

    def test_from_env_vars(self) -> None:
        env = {
            "INCEPT_HOST": "127.0.0.1",
            "INCEPT_PORT": "9090",
            "INCEPT_API_KEY": "test-key-123",
            "INCEPT_RATE_LIMIT": "100",
            "INCEPT_CORS_ORIGINS": "http://localhost:3000,http://example.com",
            "INCEPT_REQUEST_TIMEOUT": "60.0",
            "INCEPT_MODEL_PATH": "/models/v1/model.gguf",
        }
        with patch.dict(os.environ, env, clear=False):
            config = ServerConfig.from_env()
        assert config.host == "127.0.0.1"
        assert config.port == 9090
        assert config.api_key == "test-key-123"
        assert config.rate_limit == 100
        assert config.cors_origins == ["http://localhost:3000", "http://example.com"]
        assert config.request_timeout == 60.0
        assert config.model_path == "/models/v1/model.gguf"

    def test_api_key_none_by_default(self) -> None:
        config = ServerConfig()
        assert config.api_key is None

    def test_cors_origins_default(self) -> None:
        config = ServerConfig()
        assert config.cors_origins == []

    def test_safe_mode_env(self) -> None:
        with patch.dict(os.environ, {"INCEPT_SAFE_MODE": "false"}, clear=False):
            config = ServerConfig.from_env()
        assert config.safe_mode is False

    def test_log_level_env(self) -> None:
        with patch.dict(os.environ, {"INCEPT_LOG_LEVEL": "debug"}, clear=False):
            config = ServerConfig.from_env()
        assert config.log_level == "debug"

    def test_trust_proxy_default(self) -> None:
        config = ServerConfig()
        assert config.trust_proxy is False

    def test_trust_proxy_env(self) -> None:
        with patch.dict(os.environ, {"INCEPT_TRUST_PROXY": "true"}, clear=False):
            config = ServerConfig.from_env()
        assert config.trust_proxy is True

    def test_max_sessions_default(self) -> None:
        config = ServerConfig()
        assert config.max_sessions == 1000

    def test_max_sessions_env(self) -> None:
        with patch.dict(os.environ, {"INCEPT_MAX_SESSIONS": "500"}, clear=False):
            config = ServerConfig.from_env()
        assert config.max_sessions == 500
