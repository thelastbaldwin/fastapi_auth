from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session, StaticPool
from src.data.init import get_session
from src.service.auth import create_access_token
from datetime import timedelta
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


def test_register(db):
    with TestClient(app) as client:

        request = {
            "username": "testeroni",
            "full_name": "testy tester",
            "email": "testytester@gmail.com",
            "password": "123456"
        }

        response = client.post('/auth/register', json=request)

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

        client.post('/auth/register', json=request)
        
        duplicateResp = client.post('/auth/register', json=request)
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

        client.post('/auth/register', json=request)

        resp = client.post('/auth/token', data={
            "username": request["username"],
            "password": request["password"]
        })
        json = resp.json()

        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(json["access_token"], str)
        assert json["token_type"] == "bearer"

def test_token_unauthorized(db):
    with TestClient(app) as client:      
        resp = client.post('/auth/token', data={
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
        registerResponse = client.post('/auth/register', json=request)
        registerJson = registerResponse.json()

        # get token and refresh token
        tokenResponse = client.post('/auth/token', data={
            "username": request["username"],
            "password": request["password"]
        })
        tokenJson = tokenResponse.json()
        client.cookies = tokenResponse.cookies

        # get new token from refresh
        refreshResponse = client.post(
            '/auth/refresh', 
            headers={"Authorization": f"Bearer {tokenJson["access_token"]}"}, 
        )
        refreshJson = refreshResponse.json()

        assert refreshResponse.status_code == status.HTTP_200_OK
        assert isinstance(refreshJson["access_token"], str)


def test_refresh_expired(db):
    with TestClient(app) as client:
        request = {
                "username": "testeroni",
                "full_name": "testy tester",
                "email": "testytester@gmail.com",
                "password": "123456"
            }

        # register
        registerResponse = client.post('/auth/register', json=request)
        registerJson = registerResponse.json()

        # get auth and refresh tokens
        tokenResponse = client.post('/auth/token', data={
            "username": request["username"],
            "password": request["password"]
        })
        
        # create an auth_token in the past
        expired_auth_token = create_access_token(
            data={"sub": str(registerJson["id"])}, 
            expires_delta=timedelta(minutes=-5))
        
        # use the good refresh token and the bad auth_token
        client.cookies = tokenResponse.cookies
        refreshResponse = client.post("/auth/refresh", headers={"authorization": f"Bearer {expired_auth_token}"})

        # expect a 401
        assert refreshResponse.status_code == status.HTTP_401_UNAUTHORIZED
        

