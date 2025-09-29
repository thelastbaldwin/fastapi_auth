from pydantic import BaseModel

class BaseUser(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None

class User(BaseUser):
    disabled: bool | None = None

class NewUser(BaseUser):
    password: str

class UserInDb(User):
    hashed_password: str