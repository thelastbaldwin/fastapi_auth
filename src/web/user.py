from typing import Annotated
from fastapi import APIRouter, Depends
from src.service.auth import get_current_active_user
from src.model.auth import User, PublicUser

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/me/", response_model=PublicUser)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
        This is just an example of a protected route. If you register and then 
        request a token via /auth/token you will be able to access this endpoint
    """
    return current_user