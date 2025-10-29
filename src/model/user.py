from typing import TYPE_CHECKING, List
from sqlmodel import Field, SQLModel, Relationship
from .user_role import UserRole

if TYPE_CHECKING:
    from .role import Role

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
    email_verified: str = Field(default = False)
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole)