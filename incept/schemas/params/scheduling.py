"""Parameter schemas for Scheduling (3 intents)."""


from pydantic import BaseModel


class ScheduleCronParams(BaseModel):
    schedule: str
    command: str
    user: str | None = None


class ListCronParams(BaseModel):
    user: str | None = None


class RemoveCronParams(BaseModel):
    job_id_or_pattern: str
    user: str | None = None
