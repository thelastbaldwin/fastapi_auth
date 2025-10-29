from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from src.errors import Duplicate, Missing
from src.model.client import Client

def add_client(client: Client, db: Session):
    try:
        db.add(client)
        db.commit()
        db.refresh(client)
    except IntegrityError:
        raise Duplicate(msg = f"client {client.id} already exists")

    return client

def get_client(client_id: str, db: Session):
    client = db.get(Client, client_id)

    if not client:
        raise Missing(msg=f"Client {client_id} not found")
    
    return client

def update_client(id: str, disabled: bool | None, db: Session):
    client = db.get(Client, id)

    if not client:
        raise Missing(msg=f"Client {id} not found")
    
    if (disabled is not None):
        client.disabled = disabled
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return client;

def assign_scope_to_client(client_id: str, scope_id, db: Session):
    pass


def unassign_scope(user_id: str, scope_id: str, db: Session):
    pass

def unassign_scope_to_client(client_id: str, scope_id: str, db: Session):
    pass
