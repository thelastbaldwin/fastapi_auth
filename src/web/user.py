from typing import Annotated
from fastapi import APIRouter, Depends
from src.service.auth import get_current_active_user
from src.model.auth import User, PublicUser

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/me/", response_model=PublicUser)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]