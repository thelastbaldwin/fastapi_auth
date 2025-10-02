from sqlmodel import create_engine, SQLModel, Session, StaticPool
from src.model.auth import User
import src.data.user as data
from src.data.init import get_session 
from src.errors import Duplicate, Missing
import pytest

from src.main import app

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="db")  
def client_fixture(session):
    def get_session_override():  
        return session

    app.dependency_overrides[get_session] = get_session_override  
    yield session
    app.dependency_overrides.clear()  

def test_add_user(db):
    test_user = User(
        username="test",
        full_name="test user",
        email="test@test.com",
        hashed_password="1209jlskdjfsdj"
    )
    resp = data.add_user(test_user, db)

    assert test_user.username == resp.username
    assert test_user.full_name == resp.full_name
    assert test_user.email == resp.email
    assert test_user.hashed_password == resp.hashed_password
    assert resp.id is not None
    assert resp.disabled == False

def test_add_user_duplicate(db):
    test_user, test_user2 = User(
        username="test",
        full_name="test user",
        email="test@test.com",
        hashed_password="1209jlskdjfsdj"
    ), User(
        username="test",
        full_name="test user",
        email="test@test.com",
        hashed_password="1209jlskdjfsdj"
    )
    data.add_user(test_user, db)

    with pytest.raises(Duplicate):
        data.add_user(test_user2, db)

def test_get_user(db):
    test_user = User(
        username="test",
        full_name="test user",
        email="test@test.com",
        hashed_password="1209jlskdjfsdj"
    )
    data.add_user(test_user, db)

    resp = data.get_user(test_user.id, db)

    assert test_user.username == resp.username
    assert test_user.full_name == resp.full_name
    assert test_user.email == resp.email
    assert test_user.hashed_password == resp.hashed_password
    assert resp.id is not None
    assert resp.disabled == False

def test_user_missing(db):
    with pytest.raises(Missing):
        data.get_user(1, db)