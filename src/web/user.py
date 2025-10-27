from typing import Annotated
from fastapi import APIRouter, Depends, Security
from src.service.auth import get_current_active_user, validate_token
from src.model.auth import User, PublicUser, TokenData
from src.data.init import SessionDep
from src.data.user import get_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/me/", response_model=PublicUser)
async def read_users_me(
    token: Annotated[User, Security(validate_token)],
    db: SessionDep
):
    """
        This is an example of a protected route. If you register and then 
        request a token via /auth/token you will be able to access this endpoint
    """
    return get_user(token.sub, db)

@router.get("/me/v2", response_model=PublicUser)
async def read_users_me2(
    token: Annotated[TokenData, Security(validate_token, scopes=["scopes:read"])],
    db: SessionDep
):
    """
        This is an example of a protected route. If you register and then 
        request a token via /auth/token you will be able to access this endpoint. 
        Additionally, this endpoint requires that your user has the scope "scopes:read"
        and the system contains such a scope
    """
    return get_user(token.sub, db)