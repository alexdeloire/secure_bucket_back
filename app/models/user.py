from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str
    email: str
    name: str | None = None
    roles: list[str] = []
    disabled: bool | None = None

class NewUser(BaseModel):
    username: str
    password: str
    email: str

class UserIdAndUsername(BaseModel):
    user_id: int
    username: str
