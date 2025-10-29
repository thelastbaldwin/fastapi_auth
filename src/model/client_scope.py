from sqlmodel import Field, SQLModel

class ClientScope(SQLModel, table = True):
    user_id: int = Field(default=None, foreign_key="client.id", primary_key=True)
    scope_id: int = Field(default=None, foreign_key="scope.id", primary_key=True)