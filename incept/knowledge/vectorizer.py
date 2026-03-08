"""Feature-hashing vectorizer for INCEPT knowledge store.

Converts text to fixed-size dense vectors AND sparse keyword vectors
using the hashing trick. No vocabulary, no external dependencies,
deterministic output.

Two vector representations for hybrid search:
  - Dense (384-dim): Token unigrams + character trigrams hashed to
    fixed buckets. Captures fuzzy/morphological similarity
    ("listing" ~ "list", "filesystem" ~ "files").
  - Sparse (dict[int,float]): Raw token hashes with TF weights.
    Captures exact keyword matches for BM25-style retrieval.
"""

from __future__ import annotations

import hashlib
import math
import re

_TOKEN_RE = re.compile(r"[a-z0-9_/.-]+")
DENSE_DIM = 384
_SPARSE_SPACE = 2**16  # 65536 buckets for sparse vectors


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumeric, return tokens."""
    return _TOKEN_RE.findall(text.lower())


def _char_ngrams(token: str, n: int = 3) -> list[str]:
    """Generate character n-grams from a token with boundary markers."""
    padded = f"<{token}>"
    if len(padded) < n:
        return [padded]
    return [padded[i : i + n] for i in range(len(padded) - n + 1)]


def _token_bigrams(tokens: list[str]) -> list[str]:
    """Generate consecutive token bigrams."""
    return [f"{tokens[i]}_{tokens[i + 1]}" for i in range(len(tokens) - 1)]


def _md5_int(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest(), 16)


def hash_vectorize(text: str, n_features: int = DENSE_DIM) -> list[float]:
    """Convert text to a fixed-size dense vector via feature hashing.

    Features hashed into buckets:
      - Token unigrams (weight 1.0)
      - Token bigrams  (weight 0.7)  — captures phrase context
      - Character trigrams (weight 0.3) — captures morphological similarity

    Each feature is hashed to a bucket index (0..n_features-1).
    A second hash determines sign (+1/-1) to reduce collisions.
    Result is L2-normalized.
    """
    tokens = tokenize(text)
    vector = [0.0] * n_features

    def _accumulate(feature: str, weight: float) -> None:
        h = _md5_int(feature)
        idx = h % n_features
        sign = 1.0 if (h >> 32) % 2 == 0 else -1.0
        vector[idx] += sign * weight

    # Unigrams
    for token in tokens:
        _accumulate(token, 1.0)

    # Bigrams — capture word-pair context
    for bigram in _token_bigrams(tokens):
        _accumulate(bigram, 0.7)

    # Character trigrams — capture morphological similarity
    for token in tokens:
        for ngram in _char_ngrams(token):
            _accumulate(f"c3:{ngram}", 0.3)

    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector


def sparse_vectorize(text: str) -> dict[int, float]:
    """Convert text to a sparse keyword vector for BM25-style matching.

    Returns {dimension_index: weight} with only non-zero entries.
    Uses log(1 + count) TF weighting for repeated tokens.
    """
    tokens = tokenize(text)
    if not tokens:
        return {}

    # Count token frequencies
    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1

    sparse: dict[int, float] = {}
    for token, count in counts.items():
        h = _md5_int(token)
        idx = h % _SPARSE_SPACE
        weight = math.log1p(count)  # log(1+tf)
        # Handle hash collisions by accumulating
        sparse[idx] = sparse.get(idx, 0.0) + weight

    return sparse
