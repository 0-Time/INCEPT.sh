"""Zvec-backed knowledge store for INCEPT RAG.

Collections:
  - examples:    Training NL->command pairs (few-shot bank)
                 Hybrid search: dense embedding + sparse keywords
  - corrections: User corrections learned over time

Uses HNSW index with INT8 quantization and cosine similarity for
sub-millisecond retrieval even at 100K+ vectors. Inverted index on
the distro field for fast filtered search.

Graceful degradation: if zvec is not installed or index missing,
all methods return empty results and the engine works as before.
"""

from __future__ import annotations

import contextlib
import hashlib
import logging
from pathlib import Path

from incept.knowledge.vectorizer import (
    DENSE_DIM,
    hash_vectorize,
    sparse_vectorize,
)

logger = logging.getLogger(__name__)

_DEFAULT_DB_DIR = Path.home() / ".incept"
_ZVEC_INITIALIZED = False


def _ensure_zvec_init() -> None:
    """Call zvec.init() once for edge-optimized configuration."""
    global _ZVEC_INITIALIZED
    if _ZVEC_INITIALIZED:
        return
    try:
        import zvec

        zvec.init(
            log_level=zvec.LogLevel.WARN,
            query_threads=2,  # edge device: keep CPU overhead low
            optimize_threads=1,  # background indexing uses 1 thread
        )
        _ZVEC_INITIALIZED = True
    except Exception:
        _ZVEC_INITIALIZED = True  # don't retry on failure


class Example:
    """A retrieved few-shot example."""

    __slots__ = ("query", "command", "distro", "score")

    def __init__(self, query: str, command: str, distro: str = "", score: float = 0.0):
        self.query = query
        self.command = command
        self.distro = distro
        self.score = score


class KnowledgeStore:
    """Zvec-backed retrieval store with hybrid dense+sparse search."""

    def __init__(self, db_dir: str | Path | None = None) -> None:
        self._db_dir = Path(db_dir) if db_dir else _DEFAULT_DB_DIR
        self._zvec = None  # lazy import
        self._examples = None  # examples collection
        self._corrections = None  # corrections collection
        self._ready = False
        self._hybrid = False  # True if sparse vector field exists
        self._init()

    def _init(self) -> None:
        """Try to open existing zvec collections."""
        try:
            import zvec

            self._zvec = zvec
        except ImportError:
            logger.info("zvec not installed — RAG disabled")
            return

        _ensure_zvec_init()

        db_path = self._db_dir / "examples.zvec"
        if not db_path.exists():
            logger.info("No knowledge index at %s — RAG disabled", db_path)
            return

        try:
            self._examples = zvec.open(
                path=str(db_path),
                option=zvec.CollectionOption(read_only=True, enable_mmap=True),
            )
            self._ready = True
            # Check if sparse field exists for hybrid search
            schema = self._examples.schema
            for vs in schema.vectors:
                if vs.name == "sparse":
                    self._hybrid = True
                    break
            stats = self._examples.stats
            logger.info(
                "Knowledge store loaded: %s docs, hybrid=%s, path=%s",
                getattr(stats, "doc_count", "?"),
                self._hybrid,
                db_path,
            )
        except Exception as exc:
            logger.warning("Failed to open knowledge store: %s", exc)

        # Optionally open corrections collection
        corrections_path = self._db_dir / "corrections.zvec"
        if corrections_path.exists():
            with contextlib.suppress(Exception):
                self._corrections = zvec.open(  # type: ignore[assignment]
                    path=str(corrections_path),
                    option=zvec.CollectionOption(read_only=False, enable_mmap=True),
                )

    @property
    def ready(self) -> bool:
        return self._ready

    def search_examples(self, query: str, distro: str = "", top_k: int = 3) -> list[Example]:
        """Retrieve the most similar training examples for a query.

        Uses hybrid search (dense + sparse with weighted fusion) when
        the index was built with sparse vectors, otherwise dense-only.
        """
        if not self._ready or self._examples is None:
            return []

        zvec = self._zvec
        dense_vec = hash_vectorize(query)

        try:
            if self._hybrid:
                # Hybrid: dense semantic + sparse keyword matching
                sparse_vec = sparse_vectorize(query)
                dense_vq = zvec.VectorQuery(
                    field_name="embedding",
                    vector=dense_vec,
                    param=zvec.HnswQueryParam(ef=200),
                )
                sparse_vq = zvec.VectorQuery(
                    field_name="sparse",
                    vector=sparse_vec,
                )
                filter_expr = f'distro = "{distro}"' if distro else None
                kwargs = {
                    "vectors": [dense_vq, sparse_vq],
                    "topk": top_k * 3,
                    "reranker": zvec.WeightedReRanker(
                        topn=top_k,
                        metric=zvec.MetricType.COSINE,
                        weights={"embedding": 1.0, "sparse": 0.5},
                    ),
                    "include_vector": False,
                    "output_fields": ["nl", "cmd", "distro"],
                }
                if filter_expr:
                    kwargs["filter"] = filter_expr
                results = self._examples.query(**kwargs)
            else:
                # Dense-only fallback
                vq = zvec.VectorQuery(
                    field_name="embedding",
                    vector=dense_vec,
                    param=zvec.HnswQueryParam(ef=200),
                )
                filter_expr = f'distro = "{distro}"' if distro else None
                kwargs = {
                    "vectors": vq,
                    "topk": top_k,
                    "include_vector": False,
                    "output_fields": ["nl", "cmd", "distro"],
                }
                if filter_expr:
                    kwargs["filter"] = filter_expr
                results = self._examples.query(**kwargs)
        except Exception as exc:
            logger.debug("Zvec search failed: %s", exc)
            return []

        examples = []
        for doc in results[:top_k]:
            examples.append(
                Example(
                    query=doc.field("nl") if doc.has_field("nl") else "",
                    command=doc.field("cmd") if doc.has_field("cmd") else "",
                    distro=doc.field("distro") if doc.has_field("distro") else "",
                    score=doc.score if doc.score is not None else 0.0,
                )
            )
        return examples

    def search_corrections(self, query: str, top_k: int = 2) -> list[Example]:
        """Retrieve relevant user corrections."""
        if self._corrections is None:
            return []
        vec = hash_vectorize(query)
        try:
            vq = self._zvec.VectorQuery(
                field_name="embedding",
                vector=vec,
                param=self._zvec.HnswQueryParam(ef=100),
            )
            results = self._corrections.query(
                vectors=vq,
                topk=top_k,
                include_vector=False,
                output_fields=["nl", "cmd"],
            )
        except Exception:
            return []
        return [
            Example(
                query=doc.field("nl") if doc.has_field("nl") else "",
                command=doc.field("cmd") if doc.has_field("cmd") else "",
                score=doc.score if doc.score is not None else 0.0,
            )
            for doc in results
        ]

    def add_correction(self, query: str, correct_command: str) -> bool:
        """Store a user correction for future retrieval."""
        if self._zvec is None:
            return False
        zvec = self._zvec

        # Create corrections collection if needed
        if self._corrections is None:
            try:
                schema = zvec.CollectionSchema(
                    name="corrections",
                    fields=[
                        zvec.FieldSchema(name="nl", data_type=zvec.DataType.STRING),
                        zvec.FieldSchema(name="cmd", data_type=zvec.DataType.STRING),
                    ],
                    vectors=[
                        zvec.VectorSchema(
                            name="embedding",
                            data_type=zvec.DataType.VECTOR_FP32,
                            dimension=DENSE_DIM,
                            index_param=zvec.HnswIndexParam(
                                metric_type=zvec.MetricType.COSINE,
                                m=16,
                                ef_construction=200,
                                quantize_type=zvec.QuantizeType.INT8,
                            ),
                        ),
                    ],
                )
                corrections_path = str(self._db_dir / "corrections.zvec")
                self._corrections = zvec.create_and_open(path=corrections_path, schema=schema)
            except Exception as exc:
                logger.warning("Failed to create corrections collection: %s", exc)
                return False
        try:
            doc_id = hashlib.sha256(f"{query}|{correct_command}".encode()).hexdigest()[:16]
            vec = hash_vectorize(query)
            # upsert so re-correcting the same query just updates
            self._corrections.upsert(
                zvec.Doc(
                    id=doc_id,
                    vectors={"embedding": vec},
                    fields={"nl": query, "cmd": correct_command},
                )
            )
            return True
        except Exception as exc:
            logger.warning("Failed to store correction: %s", exc)
            return False
