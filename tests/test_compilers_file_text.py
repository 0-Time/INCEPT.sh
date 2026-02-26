"""Tests for file_ops and text_ops compiler functions.

Verifies that each compiler translates a params dict + EnvironmentContext
into the expected shell command string.
"""

from __future__ import annotations

import pytest

from incept.compiler.file_ops import (
    compile_change_ownership,
    compile_change_permissions,
    compile_compare_files,
    compile_copy_files,
    compile_create_directory,
    compile_create_symlink,
    compile_delete_files,
    compile_disk_usage,
    compile_find_files,
    compile_list_directory,
    compile_move_files,
    compile_view_file,
)
from incept.compiler.text_ops import (
    compile_compress_archive,
    compile_count_lines,
    compile_extract_archive,
    compile_extract_columns,
    compile_replace_text,
    compile_search_text,
    compile_sort_output,
    compile_unique_lines,
)
from incept.core.context import EnvironmentContext

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def ctx() -> EnvironmentContext:
    """Default Debian/bash context."""
    return EnvironmentContext()


@pytest.fixture()
def rhel_ctx() -> EnvironmentContext:
    """RHEL context for distro-aware tests."""
    return EnvironmentContext(distro_family="rhel")


# ===================================================================
# compile_find_files
# ===================================================================


class TestCompileFindFiles:
    def test_default_path(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({}, ctx)
        assert result == "find ."

    def test_with_explicit_path(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({"path": "/var/log"}, ctx)
        assert result.startswith("find")
        assert "/var/log" in result

    def test_with_name_pattern(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({"name_pattern": "*.txt"}, ctx)
        assert "-name" in result
        assert "'*.txt'" in result

    def test_with_type_file(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({"type": "file"}, ctx)
        assert "-type f" in result

    def test_with_type_directory(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({"type": "directory"}, ctx)
        assert "-type d" in result

    def test_with_type_link(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({"type": "link"}, ctx)
        assert "-type l" in result

    def test_with_size_gt(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({"size_gt": "100M"}, ctx)
        assert "-size +100M" in result

    def test_with_mtime_days_gt(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({"mtime_days_gt": 30}, ctx)
        assert "-mtime +30" in result

    def test_with_user(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({"user": "www-data"}, ctx)
        assert "-user" in result
        assert "www-data" in result

    def test_all_options_combined(self, ctx: EnvironmentContext) -> None:
        params = {
            "path": "/opt",
            "name_pattern": "*.log",
            "type": "file",
            "size_gt": "10M",
            "mtime_days_gt": 7,
            "user": "root",
        }
        result = compile_find_files(params, ctx)

        assert result.startswith("find")
        assert "/opt" in result
        assert "-name" in result
        assert "-type f" in result
        assert "-size +10M" in result
        assert "-mtime +7" in result
        assert "-user" in result
        assert "root" in result

    def test_with_size_lt(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({"size_lt": "1k"}, ctx)
        assert "-size -1k" in result

    def test_with_mtime_days_lt(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({"mtime_days_lt": 2}, ctx)
        assert "-mtime -2" in result

    def test_with_permissions(self, ctx: EnvironmentContext) -> None:
        result = compile_find_files({"permissions": "644"}, ctx)
        assert "-perm" in result
        assert "644" in result


# ===================================================================
# compile_copy_files
# ===================================================================


class TestCompileCopyFiles:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_copy_files({"source": "a.txt", "destination": "b.txt"}, ctx)
        assert result.startswith("cp")
        assert "a.txt" in result
        assert "b.txt" in result

    def test_recursive(self, ctx: EnvironmentContext) -> None:
        result = compile_copy_files(
            {"source": "/src", "destination": "/dst", "recursive": True}, ctx
        )
        assert "-r" in result

    def test_preserve_attrs(self, ctx: EnvironmentContext) -> None:
        result = compile_copy_files(
            {"source": "a", "destination": "b", "preserve_attrs": True}, ctx
        )
        assert "-p" in result

    def test_recursive_and_preserve(self, ctx: EnvironmentContext) -> None:
        result = compile_copy_files(
            {"source": "a", "destination": "b", "recursive": True, "preserve_attrs": True}, ctx
        )
        assert "-r" in result
        assert "-p" in result

    def test_no_flags(self, ctx: EnvironmentContext) -> None:
        result = compile_copy_files(
            {"source": "a", "destination": "b", "recursive": False, "preserve_attrs": False}, ctx
        )
        assert result.startswith("cp ")
        assert "-r" not in result
        assert "-p" not in result


# ===================================================================
# compile_move_files
# ===================================================================


class TestCompileMoveFiles:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_move_files({"source": "old.txt", "destination": "new.txt"}, ctx)
        assert result.startswith("mv")
        assert "old.txt" in result
        assert "new.txt" in result

    def test_paths_with_spaces(self, ctx: EnvironmentContext) -> None:
        result = compile_move_files(
            {"source": "my file.txt", "destination": "other dir/file.txt"}, ctx
        )
        assert result.startswith("mv")
        assert "'my file.txt'" in result
        assert "'other dir/file.txt'" in result


# ===================================================================
# compile_delete_files
# ===================================================================


class TestCompileDeleteFiles:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_delete_files({"target": "junk.tmp"}, ctx)
        assert result.startswith("rm")
        assert "junk.tmp" in result

    def test_recursive_and_force(self, ctx: EnvironmentContext) -> None:
        result = compile_delete_files(
            {"target": "/tmp/old", "recursive": True, "force": True}, ctx
        )
        assert "-r" in result
        assert "-f" in result

    def test_root_target_raises_valueerror(self, ctx: EnvironmentContext) -> None:
        with pytest.raises(ValueError, match="root or empty"):
            compile_delete_files({"target": "/"}, ctx)

    def test_empty_target_raises_valueerror(self, ctx: EnvironmentContext) -> None:
        with pytest.raises(ValueError, match="root or empty"):
            compile_delete_files({"target": ""}, ctx)

    def test_missing_target_raises_valueerror(self, ctx: EnvironmentContext) -> None:
        with pytest.raises(ValueError, match="root or empty"):
            compile_delete_files({}, ctx)

    def test_whitespace_root_raises_valueerror(self, ctx: EnvironmentContext) -> None:
        with pytest.raises(ValueError, match="root or empty"):
            compile_delete_files({"target": " / "}, ctx)


# ===================================================================
# compile_change_permissions
# ===================================================================


class TestCompileChangePermissions:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_change_permissions({"permissions": "644", "target": "file.txt"}, ctx)
        assert result.startswith("chmod")
        assert "644" in result
        assert "file.txt" in result

    def test_recursive(self, ctx: EnvironmentContext) -> None:
        result = compile_change_permissions(
            {"permissions": "755", "target": "/opt/app", "recursive": True}, ctx
        )
        assert "-R" in result

    def test_octal_755(self, ctx: EnvironmentContext) -> None:
        result = compile_change_permissions({"permissions": "755", "target": "/usr/bin/foo"}, ctx)
        assert "755" in result
        assert "/usr/bin/foo" in result

    def test_symbolic_permissions(self, ctx: EnvironmentContext) -> None:
        result = compile_change_permissions({"permissions": "u+x", "target": "script.sh"}, ctx)
        assert "u+x" in result

    def test_no_recursive(self, ctx: EnvironmentContext) -> None:
        result = compile_change_permissions({"permissions": "600", "target": "secret.key"}, ctx)
        assert "-R" not in result


# ===================================================================
# compile_change_ownership
# ===================================================================


class TestCompileChangeOwnership:
    def test_owner_only(self, ctx: EnvironmentContext) -> None:
        result = compile_change_ownership({"owner": "root", "target": "/opt/app"}, ctx)
        assert result.startswith("chown")
        assert "root" in result
        # No colon when group is absent
        assert "root:" not in result

    def test_owner_and_group(self, ctx: EnvironmentContext) -> None:
        result = compile_change_ownership(
            {"owner": "www-data", "group": "www-data", "target": "/var/www"}, ctx
        )
        assert "www-data:www-data" in result

    def test_recursive(self, ctx: EnvironmentContext) -> None:
        result = compile_change_ownership(
            {"owner": "deploy", "target": "/srv", "recursive": True}, ctx
        )
        assert "-R" in result

    def test_no_recursive(self, ctx: EnvironmentContext) -> None:
        result = compile_change_ownership({"owner": "nobody", "target": "/tmp/x"}, ctx)
        assert "-R" not in result

    def test_owner_group_recursive(self, ctx: EnvironmentContext) -> None:
        result = compile_change_ownership(
            {"owner": "app", "group": "staff", "target": "/data", "recursive": True}, ctx
        )
        assert "-R" in result
        assert "app:staff" in result


# ===================================================================
# compile_create_directory
# ===================================================================


class TestCompileCreateDirectory:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_create_directory({"path": "/tmp/newdir"}, ctx)
        assert result.startswith("mkdir")
        assert "/tmp/newdir" in result
        assert "-p" not in result

    def test_with_parents(self, ctx: EnvironmentContext) -> None:
        result = compile_create_directory({"path": "/a/b/c", "parents": True}, ctx)
        assert "-p" in result

    def test_without_parents(self, ctx: EnvironmentContext) -> None:
        result = compile_create_directory({"path": "/tmp/x", "parents": False}, ctx)
        assert "-p" not in result


# ===================================================================
# compile_list_directory
# ===================================================================


class TestCompileListDirectory:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_list_directory({}, ctx)
        assert result == "ls"

    def test_long_and_all(self, ctx: EnvironmentContext) -> None:
        result = compile_list_directory({"long_format": True, "all_files": True}, ctx)
        assert "-l" in result
        assert "-a" in result

    def test_sort_by_size(self, ctx: EnvironmentContext) -> None:
        result = compile_list_directory({"sort_by": "size"}, ctx)
        assert "-S" in result

    def test_sort_by_time(self, ctx: EnvironmentContext) -> None:
        result = compile_list_directory({"sort_by": "time"}, ctx)
        assert "-t" in result

    def test_sort_by_name_no_flag(self, ctx: EnvironmentContext) -> None:
        result = compile_list_directory({"sort_by": "name"}, ctx)
        assert "-S" not in result
        assert "-t" not in result

    def test_with_path(self, ctx: EnvironmentContext) -> None:
        result = compile_list_directory({"path": "/var/log"}, ctx)
        assert "/var/log" in result


# ===================================================================
# compile_disk_usage
# ===================================================================


class TestCompileDiskUsage:
    def test_default_human_readable(self, ctx: EnvironmentContext) -> None:
        result = compile_disk_usage({}, ctx)
        assert result.startswith("du")
        assert "-h" in result

    def test_max_depth_debian(self, ctx: EnvironmentContext) -> None:
        result = compile_disk_usage({"max_depth": 2}, ctx)
        assert "--max-depth=2" in result

    def test_max_depth_rhel(self, rhel_ctx: EnvironmentContext) -> None:
        result = compile_disk_usage({"max_depth": 2}, rhel_ctx)
        assert "-d 2" in result
        assert "--max-depth" not in result

    def test_specific_path(self, ctx: EnvironmentContext) -> None:
        result = compile_disk_usage({"path": "/home"}, ctx)
        assert "/home" in result

    def test_no_human_readable(self, ctx: EnvironmentContext) -> None:
        result = compile_disk_usage({"human_readable": False}, ctx)
        assert "-h" not in result


# ===================================================================
# compile_view_file
# ===================================================================


class TestCompileViewFile:
    def test_cat_default(self, ctx: EnvironmentContext) -> None:
        result = compile_view_file({"file": "/etc/hosts"}, ctx)
        assert result.startswith("cat")
        assert "/etc/hosts" in result

    def test_head_with_lines(self, ctx: EnvironmentContext) -> None:
        result = compile_view_file({"file": "/etc/passwd", "lines": 10}, ctx)
        assert result.startswith("head")
        assert "-n 10" in result

    def test_tail_with_from_end(self, ctx: EnvironmentContext) -> None:
        result = compile_view_file({"file": "log.txt", "lines": 50, "from_end": True}, ctx)
        assert result.startswith("tail")
        assert "-n 50" in result

    def test_lines_without_from_end(self, ctx: EnvironmentContext) -> None:
        result = compile_view_file({"file": "data.csv", "lines": 5, "from_end": False}, ctx)
        assert result.startswith("head")

    def test_from_end_without_lines_uses_cat(self, ctx: EnvironmentContext) -> None:
        result = compile_view_file({"file": "readme.md", "from_end": True}, ctx)
        # lines is None so condition for tail is not met
        assert result.startswith("cat")


# ===================================================================
# compile_create_symlink
# ===================================================================


class TestCompileCreateSymlink:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_create_symlink(
            {"target": "/usr/bin/python3", "link_name": "/usr/bin/python"}, ctx
        )
        assert result.startswith("ln")
        assert "-s" in result
        assert "/usr/bin/python3" in result
        assert "/usr/bin/python" in result

    def test_ordering(self, ctx: EnvironmentContext) -> None:
        result = compile_create_symlink({"target": "original", "link_name": "link"}, ctx)
        parts = result.split()
        # ln -s target link_name
        assert parts[0] == "ln"
        assert parts[1] == "-s"
        assert parts[2] == "original"
        assert parts[3] == "link"


# ===================================================================
# compile_compare_files
# ===================================================================


class TestCompileCompareFiles:
    def test_default_unified_diff(self, ctx: EnvironmentContext) -> None:
        result = compile_compare_files({"file1": "a.txt", "file2": "b.txt"}, ctx)
        assert result.startswith("diff")
        assert "-u" in result
        assert "a.txt" in result
        assert "b.txt" in result

    def test_with_context_lines(self, ctx: EnvironmentContext) -> None:
        result = compile_compare_files(
            {"file1": "a.txt", "file2": "b.txt", "context_lines": 5}, ctx
        )
        assert "-C 5" in result
        assert "-u" not in result

    def test_context_lines_zero(self, ctx: EnvironmentContext) -> None:
        result = compile_compare_files(
            {"file1": "x", "file2": "y", "context_lines": 0}, ctx
        )
        assert "-C 0" in result


# ===================================================================
# compile_search_text
# ===================================================================


class TestCompileSearchText:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_search_text({"pattern": "error", "path": "/var/log/syslog"}, ctx)
        assert result.startswith("grep")
        assert "error" in result
        assert "/var/log/syslog" in result

    def test_recursive_and_ignore_case(self, ctx: EnvironmentContext) -> None:
        result = compile_search_text(
            {"pattern": "TODO", "path": "/src", "recursive": True, "ignore_case": True}, ctx
        )
        assert "-r" in result
        assert "-i" in result

    def test_perl_regex(self, ctx: EnvironmentContext) -> None:
        result = compile_search_text(
            {"pattern": r"\d{3}-\d{4}", "regex_type": "perl"}, ctx
        )
        assert "-P" in result

    def test_extended_regex(self, ctx: EnvironmentContext) -> None:
        result = compile_search_text(
            {"pattern": "foo|bar", "regex_type": "extended"}, ctx
        )
        assert "-E" in result

    def test_line_numbers(self, ctx: EnvironmentContext) -> None:
        result = compile_search_text(
            {"pattern": "main", "path": "prog.c", "show_line_numbers": True}, ctx
        )
        assert "-n" in result

    def test_basic_regex_no_flag(self, ctx: EnvironmentContext) -> None:
        result = compile_search_text(
            {"pattern": "hello", "regex_type": "basic"}, ctx
        )
        assert "-P" not in result
        assert "-E" not in result

    def test_no_path(self, ctx: EnvironmentContext) -> None:
        result = compile_search_text({"pattern": "needle"}, ctx)
        # Only grep + pattern, no path
        parts = result.split()
        assert parts[0] == "grep"
        assert len(parts) == 2


# ===================================================================
# compile_replace_text
# ===================================================================


class TestCompileReplaceText:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_replace_text(
            {"pattern": "old", "replacement": "new", "file": "config.txt"}, ctx
        )
        assert result.startswith("sed")
        assert "s/old/new/g" in result
        assert "config.txt" in result

    def test_in_place(self, ctx: EnvironmentContext) -> None:
        result = compile_replace_text(
            {"pattern": "foo", "replacement": "bar", "file": "f.txt", "in_place": True}, ctx
        )
        assert "-i" in result

    def test_with_backup(self, ctx: EnvironmentContext) -> None:
        result = compile_replace_text(
            {
                "pattern": "a",
                "replacement": "b",
                "file": "f.txt",
                "in_place": True,
                "backup": ".bak",
            },
            ctx,
        )
        assert "-i" in result
        assert ".bak" in result

    def test_non_global(self, ctx: EnvironmentContext) -> None:
        result = compile_replace_text(
            {
                "pattern": "x",
                "replacement": "y",
                "file": "f.txt",
                "global_replace": False,
            },
            ctx,
        )
        # Should end with s/x/y/ (no trailing g)
        assert "s/x/y/" in result
        assert "s/x/y/g" not in result

    def test_global_is_default(self, ctx: EnvironmentContext) -> None:
        result = compile_replace_text(
            {"pattern": "a", "replacement": "b", "file": "f.txt"}, ctx
        )
        assert "s/a/b/g" in result


# ===================================================================
# compile_sort_output
# ===================================================================


class TestCompileSortOutput:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_sort_output({"input_file": "data.txt"}, ctx)
        assert result.startswith("sort")
        assert "data.txt" in result

    def test_reverse_and_numeric(self, ctx: EnvironmentContext) -> None:
        result = compile_sort_output(
            {"input_file": "nums.txt", "reverse": True, "numeric": True}, ctx
        )
        assert "-r" in result
        assert "-n" in result

    def test_unique(self, ctx: EnvironmentContext) -> None:
        result = compile_sort_output({"input_file": "list.txt", "unique": True}, ctx)
        assert "-u" in result

    def test_field_sort(self, ctx: EnvironmentContext) -> None:
        result = compile_sort_output({"input_file": "table.csv", "field": 3}, ctx)
        assert "-k 3" in result

    def test_no_input_file(self, ctx: EnvironmentContext) -> None:
        result = compile_sort_output({}, ctx)
        assert result == "sort"


# ===================================================================
# compile_count_lines
# ===================================================================


class TestCompileCountLines:
    def test_lines_default(self, ctx: EnvironmentContext) -> None:
        result = compile_count_lines({"input_file": "data.txt"}, ctx)
        assert result.startswith("wc")
        assert "-l" in result

    def test_words(self, ctx: EnvironmentContext) -> None:
        result = compile_count_lines({"input_file": "essay.txt", "mode": "words"}, ctx)
        assert "-w" in result

    def test_chars(self, ctx: EnvironmentContext) -> None:
        result = compile_count_lines({"input_file": "doc.txt", "mode": "chars"}, ctx)
        assert "-c" in result

    def test_no_input_file(self, ctx: EnvironmentContext) -> None:
        result = compile_count_lines({"mode": "lines"}, ctx)
        assert result == "wc -l"


# ===================================================================
# compile_extract_columns
# ===================================================================


class TestCompileExtractColumns:
    def test_basic_field_spec(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_columns({"field_spec": "1,3", "input_file": "data.txt"}, ctx)
        assert result.startswith("awk")
        assert "$1" in result
        assert "$3" in result
        assert "data.txt" in result

    def test_with_delimiter(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_columns(
            {"field_spec": "2", "delimiter": ",", "input_file": "data.csv"}, ctx
        )
        assert "-F" in result

    def test_single_field(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_columns({"field_spec": "5"}, ctx)
        assert "$5" in result

    def test_multiple_fields(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_columns({"field_spec": "1,2,4,7"}, ctx)
        assert "$1" in result
        assert "$2" in result
        assert "$4" in result
        assert "$7" in result


# ===================================================================
# compile_unique_lines
# ===================================================================


class TestCompileUniqueLines:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_unique_lines({"input_file": "data.txt"}, ctx)
        assert "sort" in result
        assert "uniq" in result
        assert "|" in result
        assert "data.txt" in result

    def test_with_count(self, ctx: EnvironmentContext) -> None:
        result = compile_unique_lines({"input_file": "log.txt", "count": True}, ctx)
        assert "-c" in result

    def test_duplicates_only(self, ctx: EnvironmentContext) -> None:
        result = compile_unique_lines({"input_file": "list.txt", "only_duplicates": True}, ctx)
        assert "-d" in result

    def test_no_input_file(self, ctx: EnvironmentContext) -> None:
        result = compile_unique_lines({}, ctx)
        assert result == "sort | uniq"

    def test_count_and_duplicates(self, ctx: EnvironmentContext) -> None:
        result = compile_unique_lines(
            {"input_file": "f.txt", "count": True, "only_duplicates": True}, ctx
        )
        assert "-c" in result
        assert "-d" in result


# ===================================================================
# compile_compress_archive
# ===================================================================


class TestCompileCompressArchive:
    def test_tar_gz_default(self, ctx: EnvironmentContext) -> None:
        result = compile_compress_archive({"source": "mydir"}, ctx)
        assert result.startswith("tar")
        assert "czf" in result
        assert "mydir.tar.gz" in result
        assert "mydir" in result

    def test_tar_bz2(self, ctx: EnvironmentContext) -> None:
        result = compile_compress_archive({"source": "data", "format": "tar.bz2"}, ctx)
        assert "cjf" in result
        assert "data.tar.bz2" in result

    def test_tar_xz(self, ctx: EnvironmentContext) -> None:
        result = compile_compress_archive({"source": "backup", "format": "tar.xz"}, ctx)
        assert "cJf" in result
        assert "backup.tar.xz" in result

    def test_zip(self, ctx: EnvironmentContext) -> None:
        result = compile_compress_archive({"source": "project", "format": "zip"}, ctx)
        assert result.startswith("zip")
        assert "-r" in result
        assert "project.zip" in result

    def test_with_exclude(self, ctx: EnvironmentContext) -> None:
        result = compile_compress_archive(
            {"source": "src", "exclude_pattern": "*.pyc"}, ctx
        )
        assert "--exclude" in result
        assert "*.pyc" in result

    def test_zip_with_exclude(self, ctx: EnvironmentContext) -> None:
        result = compile_compress_archive(
            {"source": "app", "format": "zip", "exclude_pattern": "*.log"}, ctx
        )
        assert "-x" in result
        assert "*.log" in result

    def test_custom_destination(self, ctx: EnvironmentContext) -> None:
        result = compile_compress_archive(
            {"source": "docs", "destination": "/tmp/docs-backup.tar.gz"}, ctx
        )
        assert "/tmp/docs-backup.tar.gz" in result


# ===================================================================
# compile_extract_archive
# ===================================================================


class TestCompileExtractArchive:
    def test_tar_gz(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_archive({"source": "archive.tar.gz"}, ctx)
        assert result.startswith("tar")
        assert "xzf" in result

    def test_tar_bz2(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_archive({"source": "data.tar.bz2"}, ctx)
        assert "xjf" in result

    def test_tar_xz(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_archive({"source": "pkg.tar.xz"}, ctx)
        assert "xJf" in result

    def test_zip(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_archive({"source": "files.zip"}, ctx)
        assert result.startswith("unzip")
        assert "files.zip" in result

    def test_with_destination(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_archive(
            {"source": "archive.tar.gz", "destination": "/opt/extracted"}, ctx
        )
        assert "-C" in result
        assert "/opt/extracted" in result

    def test_tgz_extension(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_archive({"source": "bundle.tgz"}, ctx)
        assert result.startswith("tar")
        assert "xzf" in result

    def test_zip_with_destination(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_archive(
            {"source": "release.zip", "destination": "/tmp/release"}, ctx
        )
        assert "-d" in result
        assert "/tmp/release" in result

    def test_unknown_extension_fallback(self, ctx: EnvironmentContext) -> None:
        result = compile_extract_archive({"source": "data.tar"}, ctx)
        assert "xf" in result
