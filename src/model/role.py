# User
from typing import TYPE_CHECKING, List
from sqlmodel import Field, SQLModel, Relationship, MetaData
from .user_role import UserRole

if TYPE_CHECKING:
    from .user import User

class NewRole(SQLModel):
    name: str = Field(unique=True, index=True)
    description: str | None = Field(default=None)

class Role(NewRole, table=True):
    id: int | None = Field(default = None, primary_key=True, index=True)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)