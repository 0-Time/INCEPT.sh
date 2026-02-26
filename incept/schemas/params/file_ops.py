"""Parameter schemas for File Operations (12 intents)."""

from typing import Literal

from pydantic import BaseModel, Field


class FindFilesParams(BaseModel):
    path: str | None = None
    name_pattern: str | None = None
    type: Literal["file", "directory", "link"] | None = None
    size_gt: str | None = None
    size_lt: str | None = None
    mtime_days_gt: int | None = None
    mtime_days_lt: int | None = None
    user: str | None = None
    permissions: str | None = None


class CopyFilesParams(BaseModel):
    source: str
    destination: str
    recursive: bool = False
    preserve_attrs: bool = False


class MoveFilesParams(BaseModel):
    source: str
    destination: str


class DeleteFilesParams(BaseModel):
    target: str
    recursive: bool = False
    force: bool = False


class ChangePermissionsParams(BaseModel):
    target: str
    permissions: str
    recursive: bool = False


class ChangeOwnershipParams(BaseModel):
    target: str
    owner: str
    group: str | None = None
    recursive: bool = False


class CreateDirectoryParams(BaseModel):
    path: str
    parents: bool = False


class ListDirectoryParams(BaseModel):
    path: str | None = None
    long_format: bool = False
    all_files: bool = False
    sort_by: Literal["name", "size", "time"] | None = None


class DiskUsageParams(BaseModel):
    path: str | None = None
    human_readable: bool = True
    max_depth: int | None = None


class ViewFileParams(BaseModel):
    file: str
    lines: int | None = None
    from_end: bool = False


class CreateSymlinkParams(BaseModel):
    target: str
    link_name: str


class CompareFilesParams(BaseModel):
    file1: str
    file2: str
    context_lines: int | None = Field(default=None, ge=0)
