from sqlmodel import select
from src.model.auth import Scope
from sqlalchemy.exc import IntegrityError
from src.data.init import Session
from src.data.user import get_user
from src.errors import Missing, Duplicate

def create_scope(name: str, db: Session):
    scope = Scope(name=name)

    try:
        db.add(scope)
        db.commit()
        db.refresh(scope)
    except IntegrityError:
        raise Duplicate(msg = f"Scope {name} already exists")
    
    return scope

def get_scopes(db: Session):
    statement = select(Scope)
    results = db.exec(statement)

    return results.all()

def get_scope(id: str, db: Session):
    scope = db.get(Scope, id)

    if not scope:
        raise Missing(msg = f"Scope {id} not found")
    
    return scope

def delete_scope(id: str, db: Session):
    scope = get_scope(id, db)

    db.delete(scope)
    db.commit()

    return scope

def assign_scope(user_id: str, scope_id: str, db: Session):
    user = get_user(user_id, db)
    scope = get_scope(scope_id, db)

    user.scopes.append(scope)

    try: 
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise Duplicate(msg = f"User {user_id} already assigned scope {scope_id}")
    
    return user

def unassign_scope(user_id: str, scope_id: str, db: Session):
    user = get_user(user_id, db)
    scope = get_scope(scope_id, db)
    
    try:
        user.scopes.remove(scope)
    except ValueError:
        raise Missing(msg = f"User {user_id} not assigned scope {scope_id}")
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise Missing(msg = f"User {user_id} not assigned scope {scope_id}")
    
    return user
