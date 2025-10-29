from typing import TYPE_CHECKING, List
from sqlmodel import Field, SQLModel, Relationship
from .client_scope import ClientScope

if TYPE_CHECKING:
    from .scope import Scope

class NewClient(SQLModel):
    user_id: int = Field(default=None, foreign_key="user.id")
    client_id: int|None = Field(unique=True, default = None, index = True)
    client_secret: str = Field(index=True)

class Client(NewClient, table=True):
    id: int | None = Field(default = None, primary_key=True, index=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    client_id: int|None = Field(unique=True, default = None, index = True)
    client_secret: str = Field(index=True)
    disabled: bool = Field(default=False)
    scopes: List["Scope"] = Relationship(back_populates="clients", link_model=ClientScope)