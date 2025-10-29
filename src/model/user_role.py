from sqlmodel import Field, SQLModel

class UserRole(SQLModel, table = True):
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: int = Field(default=None, foreign_key="role.id", primary_key=True)