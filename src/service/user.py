from sqlmodel import Session
import src.data.user as data
from src.model.user import User, NewUser
from src.util.auth import get_password_hash

def add_user(newUser: NewUser, db: Session) -> User:
    toAdd = User(
        username=newUser.username,
        email=newUser.email,
        full_name=newUser.full_name,
        hashed_password=get_password_hash(newUser.password)
    )

    return data.add_user(toAdd, db)