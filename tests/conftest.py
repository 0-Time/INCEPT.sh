"""Global test fixtures."""

from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _no_model_autoload() -> None:  # type: ignore[misc]
    """Prevent tests from auto-loading the real GGUF model."""
    # Reset the server route engine singleton between tests
    import incept.server.routes.command as _cmd_route

    _cmd_route._engine = None

    with (
        patch("incept.core.engine.get_model", return_value=None),
        patch("incept.core.direct_pipeline.get_model", return_value=None),
        patch("incept.core.pipeline.get_model", return_value=None),
    ):
        yield  # type: ignore[misc]
