"""Retrieval layer: BM25 search and distro-specific mapping data."""

from __future__ import annotations

from incept.retrieval.bm25 import BM25Index, SearchResult
from incept.retrieval.distro_maps import (
    PACKAGE_MAP,
    PATH_DEFAULTS,
    SERVICE_MAP,
    get_package,
    get_path,
    get_service,
)

__all__: list[str] = [
    # BM25
    "BM25Index",
    "SearchResult",
    # Distro maps — data
    "PACKAGE_MAP",
    "SERVICE_MAP",
    "PATH_DEFAULTS",
    # Distro maps — helpers
    "get_package",
    "get_service",
    "get_path",
]
