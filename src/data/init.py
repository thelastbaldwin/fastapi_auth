from fastapi import Depends
from typing import Annotated
from sqlmodel import Session, SQLModel, create_engine
from src.config import get_settings

settings = get_settings()

engine = create_engine(settings.db_url , connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    with Session(engine) as session:
        return session
    
SessionDep = Annotated[Session, Depends(get_session)]