from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from src.errors import Duplicate, Missing
from src.model.auth import User, PublicUser

def add_user(user: User, db: Session):
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        raise Duplicate(msg = f"User {user.username} already exists")

    return get_user(user.id, db)

def get_user_by_username(username: str, db: Session) -> User:
    statement = select(User).where(User.username == username)
    result = db.exec(statement).first()

    if not result:
        raise Missing(msg=f"User {username} not found")
    
    return result

def get_user(user_id: str, db: Session) -> User:
    user = db.get(User, user_id)

    if not user:
        raise Missing(msg=f"User {user_id} not found")
    
    return user

def get_public_user(user_id: str, db: Session) -> PublicUser:

    user = get_user(user_id, db)

    if not user:
        raise Missing(msg=f"User {user_id} not found")
    
    return PublicUser(
        id=user.id,
        username=user.username, 
        full_name=user.full_name
    )
    
