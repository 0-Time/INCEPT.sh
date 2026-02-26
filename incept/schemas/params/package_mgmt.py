"""Parameter schemas for Package Management (4 intents)."""


from pydantic import BaseModel


class InstallPackageParams(BaseModel):
    package: str
    assume_yes: bool = False
    version: str | None = None


class RemovePackageParams(BaseModel):
    package: str
    purge_config: bool = False


class UpdatePackagesParams(BaseModel):
    upgrade_all: bool = False


class SearchPackageParams(BaseModel):
    query: str
