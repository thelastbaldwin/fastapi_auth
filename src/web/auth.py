from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from typing import Annotated
from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from src.data.init import SessionDep
from src.model.auth import NewUser, User, PublicUser, Token
from src.service.auth import add_user, authenticate_user, create_access_token, get_current_active_user, decode_token
from src.config import get_settings
from src.errors import Duplicate

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post('/register', status_code=201, response_model=PublicUser)
async def register(
    new_user: NewUser,
    db: SessionDep
    ):
    try:
        return add_user(new_user, db)
    except Duplicate as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.msg)

@router.post("/refresh")
async def refresh_access_token(
    current_user: Annotated[User, Depends(get_current_active_user)],    
    refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None, ):
    """
        Get a new access token, provided the refresh_token and current access_token are valid
    """

    decode_token(refresh_token)

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(current_user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
    response: Response
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    # set refresh token on response as httpOnly cookie
    refresh_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes))
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return Token(access_token=access_token, token_type="bearer")