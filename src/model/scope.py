from typing import TYPE_CHECKING, List
from sqlmodel import Field, SQLModel, Relationship, MetaData
from .client_scope import ClientScope

if TYPE_CHECKING:
    from .client import Client

class NewScope(SQLModel):
    name: str = Field(unique=True, index=True)
    description: str | None = Field(default=None)

class Scope(NewScope, table=True):
    id: int | None = Field(default = None, primary_key=True, index=True)
    clients: List["Client"] = Relationship(back_populates="scopes", link_model=ClientScope)