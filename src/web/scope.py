from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
import src.data.auth as data
from src.data.init import SessionDep
from src.model.auth import User, NewScope
from src.service.auth import get_current_active_user_with_all_scopes
from src.errors import Missing, Duplicate

router = APIRouter(prefix="/scope", tags=["authorization"])

@router.get("")
async def get_scopes(
        _current_user: Annotated[User, Depends(get_current_active_user_with_all_scopes(['scopes:read']))], 
        db: SessionDep):
    """
        Get a list of scopes. Requires scope 'scopes:read'
    """
    return data.get_scopes(db)

@router.post("")
async def add_scope(
    _current_user: Annotated[User, Depends(get_current_active_user_with_all_scopes(['scopes:create']))], 
    db: SessionDep,
    scope: NewScope 
): 
    """
        Define a new scope. Requires scope 'scopes:create'
    """
    try:
        return data.create_scope(scope.name, db)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.msg)

@router.delete("/{id}")
async def delete_scope(
    _current_user: Annotated[User, Depends(get_current_active_user_with_all_scopes(['scopes:delete']))], 
    db: SessionDep,
    id: int,
):
    """
        Requires scope 'scopes:delete'
    """
    try:
        return data.delete_scope(id, db)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.msg)

@router.patch("/assign/{scope_id}/user/{user_id}", status_code=204)
async def assign_scope_to_user(_current_user: Annotated[User, Depends(get_current_active_user_with_all_scopes(['scopes:assign']))], 
    db: SessionDep, 
    user_id: str,
    scope_id: str):
    """
        Requires scope 'scopes:assign'
    """
    try :
        data.assign_scope(user_id, scope_id, db)
    # possible to not find user, scope, or the scope has already been assigned
    except Missing as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.msg)
    except Duplicate as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.msg)
    

@router.patch("/unassign/{scope_id}/user/{user_id}", status_code=204)
async def unassign_scope_to_user(_current_user: Annotated[User, Depends(get_current_active_user_with_all_scopes(['scopes:assign']))], 
    db: SessionDep, 
    user_id: str,
    scope_id: str):
    """
        Requires scope 'scopes:assign'
    """
    try :
        return data.unassign_scope(user_id, scope_id, db)
    # possible to not find user, scope, or the scope has already been assigned
    except Missing as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.msg)
    except Duplicate as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.msg)
