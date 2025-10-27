from sqlmodel import Field, SQLModel, Relationship

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    sub: int | None = None
    scopes: list[str] = []