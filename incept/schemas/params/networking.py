"""Parameter schemas for Networking (6 intents)."""


from pydantic import BaseModel, Field


class NetworkInfoParams(BaseModel):
    interface: str | None = None


class TestConnectivityParams(BaseModel):
    host: str
    count: int | None = Field(default=None, ge=1)
    timeout: int | None = Field(default=None, ge=1)


class DownloadFileParams(BaseModel):
    url: str
    output_path: str | None = None
    follow_redirects: bool = True


class TransferFileParams(BaseModel):
    source: str
    destination: str
    recursive: bool = False
    port: int | None = Field(default=None, ge=1, le=65535)


class SshConnectParams(BaseModel):
    host: str
    user: str | None = None
    port: int | None = Field(default=None, ge=1, le=65535)
    key_file: str | None = None


class PortCheckParams(BaseModel):
    port: int | None = Field(default=None, ge=1, le=65535)
    host: str | None = None
