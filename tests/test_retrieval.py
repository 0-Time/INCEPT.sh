"""Tests for retrieval layer: BM25 index and distro maps (incept.retrieval)."""

from __future__ import annotations

from typing import Any

import pytest

from incept.retrieval.bm25 import BM25Index, SearchResult, _tokenize
from incept.retrieval.distro_maps import (
    PACKAGE_MAP,
    PATH_DEFAULTS,
    SERVICE_MAP,
    _resolve_family,
    get_package,
    get_path,
    get_service,
)

# ===================================================================
# Tokenizer
# ===================================================================


class TestTokenize:
    """Tests for the BM25 tokenizer."""

    def test_simple_text(self) -> None:
        assert _tokenize("Hello World") == ["hello", "world"]

    def test_preserves_hyphens_and_underscores(self) -> None:
        tokens = _tokenize("build-essential python3_pip")
        assert "build-essential" in tokens
        assert "python3_pip" in tokens

    def test_removes_punctuation(self) -> None:
        tokens = _tokenize("hello, world! (test)")
        assert tokens == ["hello", "world", "test"]

    def test_empty_string(self) -> None:
        assert _tokenize("") == []

    def test_lowercases(self) -> None:
        tokens = _tokenize("UPPER case Mixed")
        assert tokens == ["upper", "case", "mixed"]


# ===================================================================
# BM25Index basics
# ===================================================================


class TestBM25IndexBasics:
    """Basic add/search operations on BM25Index."""

    def test_add_and_search(self) -> None:
        idx = BM25Index()
        idx.add_document("d1", "install nginx web server")
        idx.add_document("d2", "configure firewall rules")
        idx.add_document("d3", "nginx reverse proxy setup")

        results = idx.search("nginx")
        assert len(results) >= 1
        doc_ids = [r.doc_id for r in results]
        assert "d1" in doc_ids
        assert "d3" in doc_ids

    def test_document_count(self) -> None:
        idx = BM25Index()
        assert idx.document_count == 0
        idx.add_document("d1", "test document")
        assert idx.document_count == 1
        idx.add_document("d2", "another document")
        assert idx.document_count == 2

    def test_vocabulary_size(self) -> None:
        idx = BM25Index()
        idx.add_document("d1", "hello world")
        assert idx.vocabulary_size == 2

    def test_empty_index_search_returns_empty(self) -> None:
        idx = BM25Index()
        assert idx.search("anything") == []

    def test_empty_query_returns_empty(self) -> None:
        idx = BM25Index()
        idx.add_document("d1", "some text")
        assert idx.search("") == []

    def test_no_match_returns_empty(self) -> None:
        idx = BM25Index()
        idx.add_document("d1", "hello world")
        assert idx.search("zzzzzzz") == []

    def test_results_sorted_by_score_descending(self) -> None:
        idx = BM25Index()
        idx.add_document("d1", "nginx nginx nginx web server")
        idx.add_document("d2", "nginx web proxy")
        idx.add_document("d3", "firewall configuration")

        results = idx.search("nginx")
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_top_k_limits_results(self) -> None:
        idx = BM25Index()
        for i in range(20):
            idx.add_document(f"d{i}", f"document about topic {i} and nginx")
        results = idx.search("nginx", top_k=5)
        assert len(results) <= 5

    def test_search_result_is_pydantic_model(self) -> None:
        idx = BM25Index()
        idx.add_document("d1", "test document", metadata={"key": "val"})
        results = idx.search("test")
        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].doc_id == "d1"
        assert results[0].score >= 0.0
        assert results[0].text == "test document"
        assert results[0].metadata == {"key": "val"}

    def test_overwrite_document(self) -> None:
        idx = BM25Index()
        idx.add_document("d1", "old content about nginx")
        idx.add_document("d1", "new content about firewall")

        assert idx.document_count == 1
        results = idx.search("nginx")
        assert len(results) == 0
        results = idx.search("firewall")
        assert len(results) == 1

    def test_metadata_preserved(self) -> None:
        idx = BM25Index()
        meta = {"type": "flag", "command": "find"}
        idx.add_document("d1", "find files recursively", metadata=meta)
        results = idx.search("find")
        assert results[0].metadata == meta


# ===================================================================
# BM25Index bulk loaders
# ===================================================================


class TestBM25BulkLoaders:
    """Tests for build_from_flag_tables and build_from_distro_maps."""

    def test_build_from_flag_tables_loads_real_tables(self) -> None:
        idx = BM25Index()
        count = idx.build_from_flag_tables()
        assert count > 0
        assert idx.document_count == count

    def test_build_from_flag_tables_nonexistent_dir(self, tmp_path: Any) -> None:
        idx = BM25Index()
        count = idx.build_from_flag_tables(tmp_path / "nonexistent")
        assert count == 0

    def test_flag_table_doc_ids_have_prefix(self) -> None:
        idx = BM25Index()
        idx.build_from_flag_tables()
        results = idx.search("recursive")
        for r in results:
            assert r.doc_id.startswith("flag:")

    def test_build_from_distro_maps(self) -> None:
        idx = BM25Index()
        count = idx.build_from_distro_maps()
        assert count > 0
        assert idx.document_count == count

    def test_distro_map_doc_ids_have_type_prefix(self) -> None:
        idx = BM25Index()
        idx.build_from_distro_maps()
        # Search for a known package
        results = idx.search("nginx")
        doc_ids = [r.doc_id for r in results]
        prefixes = {did.split(":")[0] for did in doc_ids}
        # Should have pkg and/or svc prefixes
        assert len(prefixes) > 0

    def test_build_all_combines_both(self) -> None:
        idx = BM25Index()
        total = idx.build_all()
        assert total > 0

        # Should have both flag and distro-map docs
        flag_results = idx.search("recursive find")
        distro_results = idx.search("apache2 httpd web server")
        assert len(flag_results) > 0 or len(distro_results) > 0

    def test_search_finds_flag_entries(self) -> None:
        idx = BM25Index()
        idx.build_from_flag_tables()
        results = idx.search("grep ignore case")
        assert len(results) > 0

    def test_search_finds_distro_packages(self) -> None:
        idx = BM25Index()
        idx.build_from_distro_maps()
        results = idx.search("web_server apache2 httpd")
        assert len(results) > 0


# ===================================================================
# Distro maps: data size
# ===================================================================


class TestDistroMapSizes:
    """Verify distro maps have minimum expected entries."""

    def test_package_map_has_at_least_30_entries(self) -> None:
        assert len(PACKAGE_MAP) >= 30

    def test_service_map_has_at_least_25_entries(self) -> None:
        assert len(SERVICE_MAP) >= 25

    def test_path_defaults_has_at_least_20_entries(self) -> None:
        assert len(PATH_DEFAULTS) >= 20

    def test_all_package_entries_have_both_distros(self) -> None:
        for name, variants in PACKAGE_MAP.items():
            assert "debian" in variants, f"Package '{name}' missing debian variant"
            assert "rhel" in variants, f"Package '{name}' missing rhel variant"

    def test_all_service_entries_have_both_distros(self) -> None:
        for name, variants in SERVICE_MAP.items():
            assert "debian" in variants, f"Service '{name}' missing debian variant"
            assert "rhel" in variants, f"Service '{name}' missing rhel variant"

    def test_all_path_entries_have_both_distros(self) -> None:
        for name, variants in PATH_DEFAULTS.items():
            assert "debian" in variants, f"Path '{name}' missing debian variant"
            assert "rhel" in variants, f"Path '{name}' missing rhel variant"


# ===================================================================
# Distro maps: helper functions
# ===================================================================


class TestDistroMapHelpers:
    """Tests for get_package, get_service, get_path."""

    def test_get_package_debian(self) -> None:
        result = get_package("web_server", "debian")
        assert result == "apache2"

    def test_get_package_rhel(self) -> None:
        result = get_package("web_server", "rhel")
        assert result == "httpd"

    def test_get_package_alias_ubuntu(self) -> None:
        result = get_package("web_server", "ubuntu")
        assert result == "apache2"

    def test_get_package_alias_centos(self) -> None:
        result = get_package("web_server", "centos")
        assert result == "httpd"

    def test_get_package_unknown_returns_none(self) -> None:
        result = get_package("nonexistent_package", "debian")
        assert result is None

    def test_get_service_debian(self) -> None:
        result = get_service("cron", "debian")
        assert result == "cron"

    def test_get_service_rhel(self) -> None:
        result = get_service("cron", "rhel")
        assert result == "crond"

    def test_get_service_alias_fedora(self) -> None:
        result = get_service("ssh", "fedora")
        assert result == "sshd"

    def test_get_service_unknown_returns_none(self) -> None:
        result = get_service("nonexistent_service", "debian")
        assert result is None

    def test_get_path_debian(self) -> None:
        result = get_path("syslog", "debian")
        assert result == "/var/log/syslog"

    def test_get_path_rhel(self) -> None:
        result = get_path("syslog", "rhel")
        assert result == "/var/log/messages"

    def test_get_path_with_format_kwargs(self) -> None:
        result = get_path("ssh_authorized_keys", "debian", user="bob")
        assert result == "/home/bob/.ssh/authorized_keys"

    def test_get_path_unknown_returns_none(self) -> None:
        result = get_path("nonexistent_path", "debian")
        assert result is None

    def test_get_path_missing_format_kwarg_returns_raw(self) -> None:
        result = get_path("ssh_authorized_keys", "debian")
        assert "{user}" in result  # Format placeholder not expanded


# ===================================================================
# _resolve_family
# ===================================================================


class TestResolveFamily:
    """Tests for _resolve_family internal helper."""

    @pytest.mark.parametrize(
        "distro,expected",
        [
            ("debian", "debian"),
            ("rhel", "rhel"),
            ("ubuntu", "debian"),
            ("centos", "rhel"),
            ("fedora", "rhel"),
            ("rocky", "rhel"),
            ("alma", "rhel"),
            ("mint", "debian"),
            ("kali", "debian"),
            ("amzn", "rhel"),
            ("amazon", "rhel"),
            ("pop", "debian"),
            ("oracle", "rhel"),
            ("almalinux", "rhel"),
        ],
    )
    def test_known_distros(self, distro: str, expected: str) -> None:
        assert _resolve_family(distro) == expected

    def test_unknown_defaults_to_debian(self) -> None:
        assert _resolve_family("archlinux") == "debian"

    def test_case_insensitive(self) -> None:
        assert _resolve_family("DEBIAN") == "debian"
        assert _resolve_family("Ubuntu") == "debian"
        assert _resolve_family("RHEL") == "rhel"

    def test_strips_whitespace(self) -> None:
        assert _resolve_family("  debian  ") == "debian"
