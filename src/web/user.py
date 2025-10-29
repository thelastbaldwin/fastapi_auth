from typing import Annotated
from fastapi import APIRouter, Security, HTTPException, status
from src.service.auth import validate_token, add_user
from src.model.token import TokenData
from src.model.user import User, PublicUser, NewUser
from src.data.init import SessionDep
from src.data.user import get_user
from src.errors import Duplicate

router = APIRouter(prefix="/user", tags=["user"])

@router.post('/register', status_code=201, response_model=PublicUser)
async def register(
    new_user: NewUser,
    db: SessionDep
    ):
    try:
        return add_user(new_user, db)
    except Duplicate as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.msg)

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