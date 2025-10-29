from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session, StaticPool
from src.data.init import get_session
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


def test_register(db):
    with TestClient(app) as client:

        request = {
            "username": "testeroni",
            "full_name": "testy tester",
            "email": "testytester@gmail.com",
            "password": "123456"
        }

        response = client.post('/user/register', json=request)

        resp = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert resp["id"] is not None
        assert isinstance(resp["id"], int)
        assert resp["full_name"] == request["full_name"]
        assert resp["username"] == request["username"]

def test_register_duplicate(db):
    with TestClient(app) as client:
        request = {
            "username": "testeroni",
            "full_name": "testy tester",
            "email": "testytester@gmail.com",
            "password": "123456"
        }

        client.post('/user/register', json=request)
        
        duplicateResp = client.post('/user/register', json=request)
        json = duplicateResp.json()

        assert duplicateResp.status_code == status.HTTP_403_FORBIDDEN
        assert json["detail"] == f"User {request["username"]} already exists"

def test_token(db):
    with TestClient(app) as client:
        request = {
                "username": "testeroni",
                "full_name": "testy tester",
                "email": "testytester@gmail.com",
                "password": "123456"
            }

        client.post('/user/register', json=request)

        resp = client.post('/auth/login', data={
            "username": request["username"],
            "password": request["password"]
        })
        json = resp.json()

        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(json["access_token"], str)
        assert json["token_type"] == "bearer"

def test_token_unauthorized(db):
    with TestClient(app) as client:      
        resp = client.post('/auth/login', data={
            "username": "iamnotregistered",
            "password": "123456"
        })
        json = resp.json()

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert json["detail"] == "Incorrect username or password"

def test_refresh(db):
    with TestClient(app) as client:
        request = {
                "username": "testeroni",
                "full_name": "testy tester",
                "email": "testytester@gmail.com",
                "password": "123456"
            }

        # register
        client.post('/user/register', json=request)

        # get token and refresh token
        tokenResponse = client.post('/auth/login', data={
            "username": request["username"],
            "password": request["password"]
        })
        tokenJson = tokenResponse.json()

        # get new token from refresh
        refreshResponse = client.post(
            '/auth/refresh', 
            json={
                "refresh_token": tokenJson["refresh_token"]
            }
        )
        refreshJson = refreshResponse.json()

        assert refreshResponse.status_code == status.HTTP_200_OK
        assert isinstance(refreshJson["access_token"], str)

def test_refresh_expired(db):
    # TODO
    pass


def test_refresh_disabled_user(db):
    """
    TODO: register a user, get tokens, disable user, try to refresh, expect failure
    """
    pass
   
        

