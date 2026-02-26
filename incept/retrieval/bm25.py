"""Lightweight BM25 search index with no external dependencies.

Implements Okapi BM25 scoring from scratch for ranked retrieval over
flag-table entries and distro-map data.  Used by the INCEPT retrieval
layer (Story 3.5) to surface relevant commands, flags, and
distro-specific information during command compilation.

References
----------
- Robertson & Zaragoza, "The Probabilistic Relevance Framework: BM25 and
  Beyond", *Foundations and Trends in IR*, 2009.
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_FLAG_TABLE_DIR: Path = Path(__file__).resolve().parent.parent / "compiler" / "flag_tables"

# Pre-compiled regex for tokenisation: split on anything that is not
# alphanumeric, underscore, or hyphen.
_TOKEN_SPLIT_RE: re.Pattern[str] = re.compile(r"[^a-z0-9_-]+")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class SearchResult(BaseModel):
    """A single ranked search result."""

    doc_id: str
    score: float = Field(ge=0.0)
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> list[str]:
    """Lowercase and split *text* on whitespace / punctuation.

    Returns a list of non-empty tokens.  Tokens are lower-cased, and the
    split pattern removes everything that is not alphanumeric, underscore,
    or hyphen.
    """
    return [tok for tok in _TOKEN_SPLIT_RE.split(text.lower()) if tok]


# ---------------------------------------------------------------------------
# BM25 Index
# ---------------------------------------------------------------------------


class BM25Index:
    """In-memory BM25 index.

    Parameters
    ----------
    k1:
        Term-frequency saturation parameter.  Typical range: 1.2 -- 2.0.
    b:
        Length-normalisation parameter.  ``0`` = no normalisation, ``1`` =
        full normalisation relative to average document length.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self._k1: float = k1
        self._b: float = b

        # doc_id -> raw text
        self._docs: dict[str, str] = {}

        # doc_id -> metadata dict
        self._meta: dict[str, dict[str, Any]] = {}

        # doc_id -> list of tokens
        self._doc_tokens: dict[str, list[str]] = {}

        # doc_id -> token -> count  (term frequencies)
        self._tf: dict[str, dict[str, int]] = {}

        # token -> set of doc_ids that contain the token
        self._inverted: dict[str, set[str]] = defaultdict(set)

        # Running stats for average document length
        self._total_token_count: int = 0
        self._doc_count: int = 0

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Tokenize and add a document to the index.

        If *doc_id* already exists it will be silently overwritten so that
        re-indexing is idempotent.

        Parameters
        ----------
        doc_id:
            Unique identifier for the document.
        text:
            The full text content to index.
        metadata:
            Arbitrary metadata returned alongside search results.
        """
        # If the doc already exists, remove its contribution first so that
        # re-indexing is safe.
        if doc_id in self._docs:
            self._remove_document(doc_id)

        tokens = _tokenize(text)
        tf: dict[str, int] = defaultdict(int)
        for token in tokens:
            tf[token] += 1

        self._docs[doc_id] = text
        self._meta[doc_id] = metadata or {}
        self._doc_tokens[doc_id] = tokens
        self._tf[doc_id] = dict(tf)

        for token in tf:
            self._inverted[token].add(doc_id)

        self._total_token_count += len(tokens)
        self._doc_count += 1

    def _remove_document(self, doc_id: str) -> None:
        """Remove a previously indexed document (internal helper)."""
        old_tokens = self._doc_tokens.get(doc_id, [])
        old_tf = self._tf.get(doc_id, {})

        for token in old_tf:
            postings = self._inverted.get(token)
            if postings is not None:
                postings.discard(doc_id)
                if not postings:
                    del self._inverted[token]

        self._total_token_count -= len(old_tokens)
        self._doc_count -= 1

        self._docs.pop(doc_id, None)
        self._meta.pop(doc_id, None)
        self._doc_tokens.pop(doc_id, None)
        self._tf.pop(doc_id, None)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """Return up to *top_k* results ranked by BM25 score.

        Parameters
        ----------
        query:
            Free-text query string.
        top_k:
            Maximum number of results to return.  Capped to the total
            number of documents.

        Returns
        -------
        list[SearchResult]
            Results sorted by descending BM25 score.
        """
        if self._doc_count == 0:
            return []

        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        avgdl = self._total_token_count / self._doc_count
        n = self._doc_count

        # Accumulate scores per document
        scores: dict[str, float] = defaultdict(float)

        for qt in query_tokens:
            postings = self._inverted.get(qt)
            if postings is None:
                continue

            # IDF: log((N - df + 0.5) / (df + 0.5) + 1)
            df = len(postings)
            idf = math.log((n - df + 0.5) / (df + 0.5) + 1.0)

            for doc_id in postings:
                tf = self._tf[doc_id].get(qt, 0)
                dl = len(self._doc_tokens[doc_id])

                # BM25 TF component
                numerator = tf * (self._k1 + 1.0)
                denominator = tf + self._k1 * (1.0 - self._b + self._b * dl / avgdl)
                scores[doc_id] += idf * (numerator / denominator)

        if not scores:
            return []

        # Sort by score descending, then by doc_id for determinism
        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        results: list[SearchResult] = []
        for doc_id, score in ranked[:top_k]:
            results.append(
                SearchResult(
                    doc_id=doc_id,
                    score=round(score, 6),
                    text=self._docs[doc_id],
                    metadata=self._meta[doc_id],
                )
            )
        return results

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def document_count(self) -> int:
        """Number of indexed documents."""
        return self._doc_count

    @property
    def vocabulary_size(self) -> int:
        """Number of unique tokens in the index."""
        return len(self._inverted)

    # ------------------------------------------------------------------
    # Bulk loaders
    # ------------------------------------------------------------------

    def build_from_flag_tables(
        self,
        flag_tables_dir: str | Path | None = None,
    ) -> int:
        """Load and index all flag-table JSON files.

        Each flag-table file is named ``{command}.json`` and contains a
        mapping of ``flag_name`` -> ``{flag, description, min_version,
        fallback}``.

        A single document is created per *flag entry* with a composite
        text containing the command name, flag name, actual flag string,
        and description.

        Parameters
        ----------
        flag_tables_dir:
            Directory containing the JSON files.  Defaults to the
            built-in ``incept/compiler/flag_tables/`` directory.

        Returns
        -------
        int
            Number of documents (flag entries) indexed.
        """
        directory = Path(flag_tables_dir) if flag_tables_dir is not None else _FLAG_TABLE_DIR
        if not directory.is_dir():
            return 0

        count = 0
        for json_path in sorted(directory.glob("*.json")):
            command = json_path.stem
            try:
                with open(json_path) as fh:
                    table: dict[str, Any] = json.load(fh)
            except (json.JSONDecodeError, OSError):
                continue

            if not isinstance(table, dict):
                continue

            for flag_name, entry in table.items():
                if not isinstance(entry, dict):
                    continue

                flag_str: str = str(entry.get("flag", ""))
                description: str = str(entry.get("description", ""))
                fallback_raw = entry.get("fallback")
                fallback: str = str(fallback_raw) if fallback_raw is not None else ""

                # Build composite text for indexing
                parts = [command, flag_name, flag_str, description]
                if fallback:
                    parts.append(f"fallback {fallback}")
                text = " ".join(parts)

                doc_id = f"flag:{command}:{flag_name}"
                metadata: dict[str, Any] = {
                    "type": "flag",
                    "command": command,
                    "flag_name": flag_name,
                    "flag": flag_str,
                    "description": description,
                    "min_version": entry.get("min_version", {}),
                    "fallback": fallback_raw,
                }
                self.add_document(doc_id, text, metadata)
                count += 1

        return count

    def build_from_distro_maps(self) -> int:
        """Index entries from :mod:`incept.retrieval.distro_maps`.

        Creates one document per entry in ``PACKAGE_MAP``, ``SERVICE_MAP``,
        and ``PATH_DEFAULTS``, combining the generic name with all
        distro-specific values for broad search coverage.

        Returns
        -------
        int
            Number of documents indexed.
        """
        # Import here to avoid circular imports; the module is a pure
        # data file with no dependencies on this module.
        from incept.retrieval.distro_maps import PACKAGE_MAP, PATH_DEFAULTS, SERVICE_MAP

        count = 0

        for generic_name, variants in PACKAGE_MAP.items():
            parts = [f"package {generic_name}"]
            for distro, pkg in variants.items():
                parts.append(f"{distro} {pkg}")
            text = " ".join(parts)
            doc_id = f"pkg:{generic_name}"
            metadata: dict[str, Any] = {
                "type": "package",
                "generic_name": generic_name,
                "variants": variants,
            }
            self.add_document(doc_id, text, metadata)
            count += 1

        for generic_name, variants in SERVICE_MAP.items():
            parts = [f"service {generic_name}"]
            for distro, svc in variants.items():
                parts.append(f"{distro} {svc}")
            text = " ".join(parts)
            doc_id = f"svc:{generic_name}"
            metadata = {
                "type": "service",
                "generic_name": generic_name,
                "variants": variants,
            }
            self.add_document(doc_id, text, metadata)
            count += 1

        for category, variants in PATH_DEFAULTS.items():
            parts = [f"path {category}"]
            for distro, path_val in variants.items():
                parts.append(f"{distro} {path_val}")
            text = " ".join(parts)
            doc_id = f"path:{category}"
            metadata = {
                "type": "path",
                "category": category,
                "variants": variants,
            }
            self.add_document(doc_id, text, metadata)
            count += 1

        return count

    def build_all(self, flag_tables_dir: str | Path | None = None) -> int:
        """Convenience method: index both flag tables and distro maps.

        Parameters
        ----------
        flag_tables_dir:
            Optional override for the flag-tables directory.

        Returns
        -------
        int
            Total number of documents indexed.
        """
        total = self.build_from_flag_tables(flag_tables_dir)
        total += self.build_from_distro_maps()
        return total
