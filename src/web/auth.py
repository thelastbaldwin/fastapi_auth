from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Annotated
from datetime import timedelta
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from src.data.init import SessionDep
from src.data.user import get_user
from src.model.token import Token
from src.model.auth import NewUser, User, PublicUser
from src.service.auth import add_user, authenticate_user, create_access_token, decode_token
from src.config import get_settings
from src.errors import Duplicate

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["authentication"])

def access_token_payload(user: User):
    return {
        "sub": str(user.id),
        "scopes": " ".join([scope.name for scope in user.scopes])
    }

@router.post('/register', status_code=201, response_model=PublicUser)
async def register(
    new_user: NewUser,
    db: SessionDep
    ):
    try:
        return add_user(new_user, db)
    except Duplicate as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.msg)

class RefreshBody(BaseModel):
    refresh_token: str
@router.post("/refresh")
async def refresh_access_token(
    body: RefreshBody,
    db: SessionDep) -> Token:
    """
        Get a new access token, provided the refresh_token and current access_token are valid
    """

    decoded = decode_token(body.refresh_token)
    user = get_user(decoded.sub, db)
    if user is None or user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data=access_token_payload(user), expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

class TokenRespose(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
) -> TokenRespose:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data=access_token_payload(user), expires_delta=access_token_expires
    )

    refresh_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes))

    return TokenRespose(
        access_token=access_token, token_type="bearer",refresh_token=refresh_token, expires_in=settings.access_token_expire_minutes
    )

                 