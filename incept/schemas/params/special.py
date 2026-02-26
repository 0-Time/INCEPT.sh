"""Parameter schemas for Special intents (CLARIFY, OUT_OF_SCOPE, UNSAFE_REQUEST)."""

from typing import Literal

from pydantic import BaseModel


class ClarifyParams(BaseModel):
    reason: Literal[
        "missing_required_param",
        "ambiguous_intent",
        "ambiguous_scope",
        "missing_distro",
        "unclear_target",
    ]
    template_key: Literal[
        "which_package",
        "which_directory",
        "which_distro",
        "which_compression",
        "which_service",
        "which_user",
        "which_file",
        "confirm_scope",
        "clarify_intent",
    ]


class OutOfScopeParams(BaseModel):
    reason: str | None = None


class UnsafeRequestParams(BaseModel):
    reason: str | None = None
