"""Parameter schemas for Disk/Mount Operations (2 intents)."""


from pydantic import BaseModel


class MountDeviceParams(BaseModel):
    device: str
    mount_point: str
    filesystem_type: str | None = None
    options: str | None = None


class UnmountDeviceParams(BaseModel):
    mount_point: str
    force: bool = False
    lazy: bool = False
