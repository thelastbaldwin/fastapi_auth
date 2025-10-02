from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None

class UserScope(SQLModel, table = True):
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
    scope_id: int = Field(default=None, foreign_key="scope.id", primary_key=True)

class Scope(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key=True, index=True)
    name: str = Field(unique=True)
    users: list["User"] = Relationship(back_populates="scopes", link_model=UserScope)

class PublicUser(SQLModel):
    id: int | None = Field(default=None, primary_key=True, index=True)
    username: str = Field(index = True, unique = True)
    full_name: str | None = Field(default=None)

class BaseUser(PublicUser):
    email: str  = Field(unique=True)
    disabled: bool = Field(default=False)

class NewUser(BaseUser):
    password: str = Field()

class User(BaseUser, table=True):
    hashed_password: str = Field()
    scopes: list["Scope"] = Relationship(back_populates="users", link_model=UserScope)
