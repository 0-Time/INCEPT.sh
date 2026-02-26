"""Tests for expanded intent compiler functions (Sprint 7.4).

Covers Docker, Git, SSH keys, Disk info, Firewall, DNS, Environment,
and Systemd timer intents.
"""

from __future__ import annotations

import pytest

from incept.compiler.expanded_ops import (
    compile_check_filesystem,
    compile_copy_ssh_key,
    compile_create_timer,
    compile_dns_lookup,
    compile_dns_resolve,
    compile_docker_build,
    compile_docker_exec,
    compile_docker_logs,
    compile_docker_ps,
    compile_docker_run,
    compile_docker_stop,
    compile_firewall_allow,
    compile_firewall_deny,
    compile_firewall_list,
    compile_generate_ssh_key,
    compile_git_branch,
    compile_git_commit,
    compile_git_diff,
    compile_git_log,
    compile_git_pull,
    compile_git_push,
    compile_git_status,
    compile_list_env_vars,
    compile_list_partitions,
    compile_list_timers,
    compile_set_env_var,
)
from incept.core.context import EnvironmentContext


@pytest.fixture()
def ctx() -> EnvironmentContext:
    return EnvironmentContext()


# ===================================================================
# Docker
# ===================================================================


class TestDockerRun:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_run({"image": "nginx"}, ctx)
        assert result.startswith("docker run")
        assert "nginx" in result

    def test_with_name(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_run({"image": "redis", "name": "my-redis"}, ctx)
        assert "--name" in result
        assert "my-redis" in result

    def test_detached(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_run({"image": "nginx", "detach": True}, ctx)
        assert "-d" in result

    def test_with_ports(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_run(
            {"image": "nginx", "ports": ["80:80", "443:443"]}, ctx
        )
        assert "-p 80:80" in result
        assert "-p 443:443" in result

    def test_with_volumes(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_run(
            {"image": "nginx", "volumes": ["/data:/data"]}, ctx
        )
        assert "-v /data:/data" in result

    def test_with_env(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_run(
            {"image": "app", "env_vars": ["FOO=bar"]}, ctx
        )
        assert "-e FOO=bar" in result


class TestDockerPs:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_ps({}, ctx)
        assert result.startswith("docker ps")

    def test_all(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_ps({"all": True}, ctx)
        assert "-a" in result


class TestDockerStop:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_stop({"container": "my-app"}, ctx)
        assert result.startswith("docker stop")
        assert "my-app" in result


class TestDockerLogs:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_logs({"container": "my-app"}, ctx)
        assert result.startswith("docker logs")
        assert "my-app" in result

    def test_follow(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_logs({"container": "web", "follow": True}, ctx)
        assert "-f" in result

    def test_tail(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_logs({"container": "web", "tail": 100}, ctx)
        assert "--tail" in result
        assert "100" in result


class TestDockerBuild:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_build({"path": "."}, ctx)
        assert result.startswith("docker build")
        assert "." in result

    def test_with_tag(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_build({"path": ".", "tag": "myapp:latest"}, ctx)
        assert "-t" in result
        assert "myapp:latest" in result

    def test_with_file(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_build(
            {"path": ".", "file": "Dockerfile.prod"}, ctx
        )
        assert "-f" in result
        assert "Dockerfile.prod" in result


class TestDockerExec:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_exec(
            {"container": "my-app", "command": "bash"}, ctx
        )
        assert result.startswith("docker exec")
        assert "my-app" in result
        assert "bash" in result

    def test_interactive(self, ctx: EnvironmentContext) -> None:
        result = compile_docker_exec(
            {"container": "my-app", "command": "bash", "interactive": True}, ctx
        )
        assert "-it" in result


# ===================================================================
# Git
# ===================================================================


class TestGitStatus:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_git_status({}, ctx)
        assert result == "git status"

    def test_short(self, ctx: EnvironmentContext) -> None:
        result = compile_git_status({"short": True}, ctx)
        assert "-s" in result


class TestGitCommit:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_git_commit({"message": "fix bug"}, ctx)
        assert "git commit" in result
        assert "-m" in result
        assert "fix bug" in result

    def test_all(self, ctx: EnvironmentContext) -> None:
        result = compile_git_commit({"message": "update", "all": True}, ctx)
        assert "-a" in result


class TestGitPush:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_git_push({}, ctx)
        assert result == "git push"

    def test_with_remote_and_branch(self, ctx: EnvironmentContext) -> None:
        result = compile_git_push({"remote": "origin", "branch": "main"}, ctx)
        assert "origin" in result
        assert "main" in result


class TestGitPull:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_git_pull({}, ctx)
        assert result == "git pull"

    def test_with_remote_and_branch(self, ctx: EnvironmentContext) -> None:
        result = compile_git_pull({"remote": "origin", "branch": "dev"}, ctx)
        assert "origin" in result
        assert "dev" in result


class TestGitLog:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_git_log({}, ctx)
        assert result == "git log"

    def test_with_count(self, ctx: EnvironmentContext) -> None:
        result = compile_git_log({"count": 10}, ctx)
        assert "-n 10" in result or "--max-count=10" in result

    def test_oneline(self, ctx: EnvironmentContext) -> None:
        result = compile_git_log({"oneline": True}, ctx)
        assert "--oneline" in result


class TestGitDiff:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_git_diff({}, ctx)
        assert result == "git diff"

    def test_staged(self, ctx: EnvironmentContext) -> None:
        result = compile_git_diff({"staged": True}, ctx)
        assert "--staged" in result

    def test_with_path(self, ctx: EnvironmentContext) -> None:
        result = compile_git_diff({"path": "src/main.py"}, ctx)
        assert "src/main.py" in result


class TestGitBranch:
    def test_list(self, ctx: EnvironmentContext) -> None:
        result = compile_git_branch({}, ctx)
        assert result == "git branch"

    def test_create(self, ctx: EnvironmentContext) -> None:
        result = compile_git_branch({"name": "feature/new"}, ctx)
        assert "feature/new" in result

    def test_delete(self, ctx: EnvironmentContext) -> None:
        result = compile_git_branch({"name": "old-branch", "delete": True}, ctx)
        assert "-d" in result
        assert "old-branch" in result

    def test_all(self, ctx: EnvironmentContext) -> None:
        result = compile_git_branch({"all": True}, ctx)
        assert "-a" in result


# ===================================================================
# SSH Keys
# ===================================================================


class TestGenerateSshKey:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_generate_ssh_key({}, ctx)
        assert "ssh-keygen" in result

    def test_with_type(self, ctx: EnvironmentContext) -> None:
        result = compile_generate_ssh_key({"key_type": "ed25519"}, ctx)
        assert "-t ed25519" in result

    def test_with_comment(self, ctx: EnvironmentContext) -> None:
        result = compile_generate_ssh_key({"comment": "user@host"}, ctx)
        assert "-C" in result
        assert "user@host" in result

    def test_with_file(self, ctx: EnvironmentContext) -> None:
        result = compile_generate_ssh_key({"file": "~/.ssh/mykey"}, ctx)
        assert "-f" in result
        assert "~/.ssh/mykey" in result


class TestCopySshKey:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_copy_ssh_key({"host": "server.example.com"}, ctx)
        assert "ssh-copy-id" in result
        assert "server.example.com" in result

    def test_with_user(self, ctx: EnvironmentContext) -> None:
        result = compile_copy_ssh_key(
            {"host": "server.com", "user": "deploy"}, ctx
        )
        assert "deploy@server.com" in result

    def test_with_identity_file(self, ctx: EnvironmentContext) -> None:
        result = compile_copy_ssh_key(
            {"host": "server.com", "identity_file": "~/.ssh/id_ed25519.pub"}, ctx
        )
        assert "-i" in result
        assert "~/.ssh/id_ed25519.pub" in result


# ===================================================================
# Disk Info
# ===================================================================


class TestListPartitions:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_list_partitions({}, ctx)
        assert "lsblk" in result or "fdisk" in result

    def test_with_device(self, ctx: EnvironmentContext) -> None:
        result = compile_list_partitions({"device": "/dev/sda"}, ctx)
        assert "/dev/sda" in result


class TestCheckFilesystem:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_check_filesystem({"device": "/dev/sda1"}, ctx)
        assert "fsck" in result
        assert "/dev/sda1" in result


# ===================================================================
# Firewall
# ===================================================================


class TestFirewallAllow:
    def test_basic_debian(self, ctx: EnvironmentContext) -> None:
        result = compile_firewall_allow({"port": 80}, ctx)
        assert "ufw allow" in result
        assert "80" in result

    def test_with_protocol(self, ctx: EnvironmentContext) -> None:
        result = compile_firewall_allow({"port": 443, "protocol": "tcp"}, ctx)
        assert "443" in result

    def test_rhel_context(self) -> None:
        rhel = EnvironmentContext(distro_family="rhel")
        result = compile_firewall_allow({"port": 80}, rhel)
        assert "firewall-cmd" in result
        assert "80" in result


class TestFirewallDeny:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_firewall_deny({"port": 22}, ctx)
        assert "ufw deny" in result or "firewall-cmd" in result
        assert "22" in result


class TestFirewallList:
    def test_basic_debian(self, ctx: EnvironmentContext) -> None:
        result = compile_firewall_list({}, ctx)
        assert "ufw status" in result

    def test_rhel_context(self) -> None:
        rhel = EnvironmentContext(distro_family="rhel")
        result = compile_firewall_list({}, rhel)
        assert "firewall-cmd" in result


# ===================================================================
# DNS
# ===================================================================


class TestDnsLookup:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_dns_lookup({"domain": "example.com"}, ctx)
        assert "dig" in result or "nslookup" in result
        assert "example.com" in result

    def test_with_record_type(self, ctx: EnvironmentContext) -> None:
        result = compile_dns_lookup(
            {"domain": "example.com", "record_type": "MX"}, ctx
        )
        assert "MX" in result


class TestDnsResolve:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_dns_resolve({"domain": "example.com"}, ctx)
        assert "example.com" in result
        assert "host" in result or "dig" in result or "nslookup" in result


# ===================================================================
# Environment
# ===================================================================


class TestSetEnvVar:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_set_env_var(
            {"name": "MY_VAR", "value": "hello"}, ctx
        )
        assert "export" in result
        assert "MY_VAR" in result
        assert "hello" in result


class TestListEnvVars:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_list_env_vars({}, ctx)
        assert "env" in result or "printenv" in result

    def test_with_filter(self, ctx: EnvironmentContext) -> None:
        result = compile_list_env_vars({"filter": "PATH"}, ctx)
        assert "PATH" in result


# ===================================================================
# Systemd Timers
# ===================================================================


class TestCreateTimer:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_create_timer(
            {"name": "backup", "on_calendar": "daily", "command": "/opt/backup.sh"},
            ctx,
        )
        assert "systemd" in result.lower() or "timer" in result.lower()
        assert "backup" in result

    def test_with_description(self, ctx: EnvironmentContext) -> None:
        result = compile_create_timer(
            {
                "name": "cleanup",
                "on_calendar": "weekly",
                "command": "/opt/cleanup.sh",
                "description": "Weekly cleanup",
            },
            ctx,
        )
        assert "cleanup" in result


class TestListTimers:
    def test_basic(self, ctx: EnvironmentContext) -> None:
        result = compile_list_timers({}, ctx)
        assert "systemctl" in result
        assert "timer" in result.lower()
