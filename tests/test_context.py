"""Tests for the context resolver."""

import json

from incept.core.context import EnvironmentContext, parse_context


class TestEnvironmentContext:
    def test_defaults(self) -> None:
        ctx = EnvironmentContext()
        assert ctx.distro_id == "debian"
        assert ctx.distro_family == "debian"
        assert ctx.shell == "bash"
        assert ctx.is_root is False
        assert ctx.safe_mode is True
        assert ctx.allow_sudo is True

    def test_custom_values(self) -> None:
        ctx = EnvironmentContext(
            distro_id="ubuntu",
            distro_version="24.04",
            distro_family="debian",
            kernel_version="6.8.0-45-generic",
            shell="zsh",
            user="deploy",
            is_root=False,
            cwd="/home/deploy",
        )
        assert ctx.distro_id == "ubuntu"
        assert ctx.shell == "zsh"


class TestParseContext:
    def test_flat_json(self) -> None:
        data = {
            "distro_id": "ubuntu",
            "distro_version": "24.04",
            "distro_family": "debian",
            "shell": "bash",
            "user": "deploy",
            "is_root": False,
            "cwd": "/home/deploy",
        }
        ctx = parse_context(json.dumps(data))
        assert ctx.distro_id == "ubuntu"
        assert ctx.user == "deploy"

    def test_nested_json(self) -> None:
        data = {
            "environment": {
                "distro_id": "rhel",
                "distro_version": "9.2",
                "distro_family": "rhel",
                "kernel_version": "5.14.0",
                "shell": "bash",
                "user": "admin",
                "is_root": True,
                "cwd": "/root",
            },
            "settings": {
                "safe_mode": False,
                "verbosity": "verbose",
                "allow_sudo": True,
            },
        }
        ctx = parse_context(json.dumps(data))
        assert ctx.distro_id == "rhel"
        assert ctx.distro_family == "rhel"
        assert ctx.is_root is True
        assert ctx.safe_mode is False
        assert ctx.verbosity == "verbose"

    def test_missing_fields_use_defaults(self) -> None:
        ctx = parse_context('{"distro_id": "fedora"}')
        assert ctx.distro_id == "fedora"
        assert ctx.distro_family == "debian"  # default
        assert ctx.shell == "bash"  # default
        assert ctx.safe_mode is True  # default

    def test_empty_json(self) -> None:
        ctx = parse_context("{}")
        assert ctx.distro_id == "debian"

    def test_invalid_json(self) -> None:
        ctx = parse_context("not json")
        assert ctx.distro_id == "debian"  # all defaults

    def test_none_input(self) -> None:
        ctx = parse_context(None)  # type: ignore[arg-type]
        assert ctx.distro_id == "debian"

    def test_rhel_family(self) -> None:
        data = {
            "distro_id": "centos",
            "distro_family": "rhel",
            "shell": "bash",
            "user": "centos",
            "is_root": False,
        }
        ctx = parse_context(json.dumps(data))
        assert ctx.distro_family == "rhel"

    def test_extra_fields_ignored(self) -> None:
        data = {
            "distro_id": "ubuntu",
            "extra_field": "should be ignored",
            "another": 42,
        }
        ctx = parse_context(json.dumps(data))
        assert ctx.distro_id == "ubuntu"

    def test_partial_nested(self) -> None:
        data = {
            "environment": {
                "distro_id": "debian",
                "shell": "zsh",
            }
        }
        ctx = parse_context(json.dumps(data))
        assert ctx.distro_id == "debian"
        assert ctx.shell == "zsh"
