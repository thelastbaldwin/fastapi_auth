from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from src.errors import Duplicate, Missing
from src.model.user import User, PublicUser

def add_user(user: User, db: Session):
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        raise Duplicate(msg = f"User {user.username} already exists")

    return get_user(user.username, db)

def get_user(username: str, db: Session) -> User:
    statement = select(User).where(User.username == username)
    result = db.exec(statement).first()

    if not result:
        raise Missing(msg=f"User {username} not found")
    
    return result

def get_public_user(username: str, db: Session) -> PublicUser:

    statement = select(User).where(User.username == username)
    result = db.exec(statement).first()

    if not result:
        raise Missing(msg=f"User {username} not found")
    
    return PublicUser(
        id=result.id,
        username=result.username, 
        full_name=result.full_name
    )
    
