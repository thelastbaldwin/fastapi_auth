from fastapi.exceptions import HTTPException
from sqlmodel import create_engine, SQLModel, Session, StaticPool
from datetime import timedelta
from src.model.auth import NewUser
import src.service.auth as service
from src.data.init import get_session, get_settings
import pytest

from src.main import app

@pytest.fixture()
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # pass the engine for cleanup in the next fixture
        yield (session, engine)

@pytest.fixture(name="db")  
def client_fixture(session_fixture):
    session, engine = session_fixture  
    def get_session_override():  
        return session

    app.dependency_overrides[get_session] = get_session_override  
    yield session
    SQLModel.metadata.drop_all(engine)
    app.dependency_overrides.clear()

def test_add_user(db):
    new_user = NewUser(
        username="test",
        full_name="test user",
        email="test@test.com",
        password="123456"
    )

    resp = service.add_user(new_user, db)

    assert resp.id is not None
    assert resp.username == new_user.username
    assert resp.full_name == new_user.full_name
    assert resp.email == new_user.email
    assert resp.hashed_password != None
    assert resp.hashed_password != new_user.password
    assert resp.disabled == False


def test_encode_decode_access_token():
    settings = get_settings()
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = service.create_access_token(
        data={"sub": "1"}, expires_delta=access_token_expires
    )

    assert isinstance(access_token, str)

    token_data = service.decode_token(access_token)

    assert token_data.user_id == 1

def test_decode_access_token_invalid():
    access_token_expires = timedelta(minutes=-5)
    access_token = service.create_access_token(
        data={"sub": "1"}, expires_delta=access_token_expires
    )

    assert isinstance(access_token, str)

    with pytest.raises(HTTPException):
        service.decode_token(access_token)