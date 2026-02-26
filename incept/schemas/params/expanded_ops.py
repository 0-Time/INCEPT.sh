"""Param models for expanded intents (Sprint 7.4).

Docker, Git, SSH keys, Disk info, Firewall, DNS, Environment, Systemd timers.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------


class DockerRunParams(BaseModel):
    image: str
    name: str | None = None
    detach: bool = False
    ports: list[str] = Field(default_factory=list)
    volumes: list[str] = Field(default_factory=list)
    env_vars: list[str] = Field(default_factory=list)
    command: str | None = None


class DockerPsParams(BaseModel):
    all: bool = False


class DockerStopParams(BaseModel):
    container: str


class DockerLogsParams(BaseModel):
    container: str
    follow: bool = False
    tail: int | None = None


class DockerBuildParams(BaseModel):
    path: str = "."
    tag: str | None = None
    file: str | None = None


class DockerExecParams(BaseModel):
    container: str
    command: str
    interactive: bool = False


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------


class GitStatusParams(BaseModel):
    short: bool = False


class GitCommitParams(BaseModel):
    message: str
    all: bool = False


class GitPushParams(BaseModel):
    remote: str | None = None
    branch: str | None = None


class GitPullParams(BaseModel):
    remote: str | None = None
    branch: str | None = None


class GitLogParams(BaseModel):
    count: int | None = None
    oneline: bool = False


class GitDiffParams(BaseModel):
    staged: bool = False
    path: str | None = None


class GitBranchParams(BaseModel):
    name: str | None = None
    delete: bool = False
    all: bool = False


# ---------------------------------------------------------------------------
# SSH Keys
# ---------------------------------------------------------------------------


class GenerateSshKeyParams(BaseModel):
    key_type: Literal["rsa", "ed25519", "ecdsa"] | None = None
    comment: str | None = None
    file: str | None = None


class CopySshKeyParams(BaseModel):
    host: str
    user: str | None = None
    identity_file: str | None = None


# ---------------------------------------------------------------------------
# Disk Info
# ---------------------------------------------------------------------------


class ListPartitionsParams(BaseModel):
    device: str | None = None


class CheckFilesystemParams(BaseModel):
    device: str


# ---------------------------------------------------------------------------
# Firewall
# ---------------------------------------------------------------------------


class FirewallAllowParams(BaseModel):
    port: int = Field(ge=1, le=65535)
    protocol: Literal["tcp", "udp"] | None = None


class FirewallDenyParams(BaseModel):
    port: int = Field(ge=1, le=65535)
    protocol: Literal["tcp", "udp"] | None = None


class FirewallListParams(BaseModel):
    pass


# ---------------------------------------------------------------------------
# DNS
# ---------------------------------------------------------------------------


class DnsLookupParams(BaseModel):
    domain: str
    record_type: Literal["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"] | None = None


class DnsResolveParams(BaseModel):
    domain: str


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------


class SetEnvVarParams(BaseModel):
    name: str
    value: str


class ListEnvVarsParams(BaseModel):
    filter: str | None = None


# ---------------------------------------------------------------------------
# Systemd Timers
# ---------------------------------------------------------------------------


class CreateTimerParams(BaseModel):
    name: str
    on_calendar: str
    command: str
    description: str | None = None


class ListTimersParams(BaseModel):
    all: bool = False
