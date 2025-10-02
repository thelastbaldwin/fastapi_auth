from sqlmodel import create_engine, SQLModel, Session, StaticPool
import src.service.auth as authService
from src.model.auth import NewUser
import src.data.auth as data
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


def test_create_scope(db):
    name = "scope:test"
    scope = data.create_scope(name, db)

    assert scope.name == name

def test_create_scope_duplicate(db):
    name = "scope:test"
    data.create_scope(name, db)

    with pytest.raises(Duplicate):
        data.create_scope(name, db)

def test_get_scopes(db):
    names = "scope:test1", "scope:test2"
    for name in names:
        data.create_scope(name, db)

    result = data.get_scopes(db)

    assert len(result) == 2
    result_names = [scope.name for scope in result]
    assert names[0] in result_names
    assert names[1] in result_names

def test_get_scopes(db):
    result = data.get_scopes(db)

    assert len(result) == 0
    assert isinstance(result, list)


def test_get_scope(db):
    name = "scope:test"
    scope = data.create_scope(name, db)

    result = data.get_scope(scope.id, db)
    assert result.name == name

def test_get_scope_missing(db):
    with pytest.raises(Missing):
        data.get_scope("foo", db)

def test_delete_scope(db):
    scope = data.create_scope("scope:test", db)

    result = data.delete_scope(scope.id, db)
    assert result.id == scope.id
    assert result.name == scope.name

def test_delete_scope_missing(db):
    with pytest.raises(Missing):
        data.delete_scope("foo", db)

def test_assign_scope(db):
    user = authService.add_user(newUser=NewUser(
        username="testuser",
        full_name="test user",
        email="test@user.com",
        password="123456"
    ), db=db)
    scope_name = "scope:test"
    scope = data.create_scope(scope_name, db)

    result = data.assign_scope(user.id, scope.id, db)

    assert len(result.scopes) == 1
    assert scope_name in [scope.name for scope in user.scopes]

def test_assign_scope_missing_user(db):
    scope = data.create_scope("scope:test", db)

    with pytest.raises(Missing):
        data.assign_scope(1, scope.id, db)


def test_assign_scope_missing_scope(db):
    user = authService.add_user(newUser=NewUser(
        username="testuser",
        full_name="test user",
        email="test@user.com",
        password="123456"
    ), db=db)

    with pytest.raises(Missing):
        data.assign_scope(user.id, 1, db)

def test_assign_scope_duplicate(db):
    user = authService.add_user(newUser=NewUser(
        username="testuser",
        full_name="test user",
        email="test@user.com",
        password="123456"
    ), db=db)
    scope_name = "scope:test"
    scope = data.create_scope(scope_name, db)

    data.assign_scope(user.id, scope.id, db)

    with pytest.raises(Duplicate):
        data.assign_scope(user.id, scope.id, db)

def test_unassign_scope(db):
    user = authService.add_user(newUser=NewUser(
        username="testuser",
        full_name="test user",
        email="test@user.com",
        password="123456"
    ), db=db)
    scope_name = "scope:test"
    scope = data.create_scope(scope_name, db)

    assigned = data.assign_scope(user.id, scope.id, db)
    assert len(assigned.scopes) == 1

    response = data.unassign_scope(user.id, scope.id, db)

    assert response.id == user.id
    assert len(response.scopes) == 0

def test_unassign_scope_missing_user(db):
    scope_name = "scope:test"
    scope = data.create_scope(scope_name, db)

    with pytest.raises(Missing):
        data.unassign_scope(1, scope.id, db)

def test_unassign_scope_missing_scope(db):
    user = authService.add_user(newUser=NewUser(
        username="testuser",
        full_name="test user",
        email="test@user.com",
        password="123456"
    ), db=db)

    with pytest.raises(Missing):
        data.unassign_scope(user.id, 1, db)

def test_unassign_scope_not_assigned(db):
    user = authService.add_user(newUser=NewUser(
        username="testuser",
        full_name="test user",
        email="test@user.com",
        password="123456"
    ), db=db)
    scope_name = "scope:test"

    scope = data.create_scope(scope_name, db)

    with pytest.raises(Missing):
        data.unassign_scope(user.id, scope.id, db)




