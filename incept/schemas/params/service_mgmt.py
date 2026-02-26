"""Parameter schemas for Service Management (5 intents)."""

from pydantic import BaseModel


class StartServiceParams(BaseModel):
    service_name: str


class StopServiceParams(BaseModel):
    service_name: str


class RestartServiceParams(BaseModel):
    service_name: str


class EnableServiceParams(BaseModel):
    service_name: str


class ServiceStatusParams(BaseModel):
    service_name: str
