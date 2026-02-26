"""Parameter schemas for User Management (3 intents)."""


from pydantic import BaseModel


class CreateUserParams(BaseModel):
    username: str
    shell: str | None = None
    home_dir: str | None = None
    groups: list[str] | None = None


class DeleteUserParams(BaseModel):
    username: str
    remove_home: bool = False


class ModifyUserParams(BaseModel):
    username: str
    add_groups: list[str] | None = None
    shell: str | None = None
    home_dir: str | None = None
