import src.data.user as data
from src.util.auth import get_password_hash


def get_user(username: str):
    return data.get_user(username)

def add_user(username: str, email: str | None, full_name: str | None, password: str):
    return data.add_user(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password)
    )
