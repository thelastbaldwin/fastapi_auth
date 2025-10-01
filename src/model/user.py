from sqlmodel import Field, SQLModel

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
