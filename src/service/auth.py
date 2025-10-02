from typing import Annotated, List
from sqlmodel import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from src.model.auth import TokenData, User, NewUser
from src.data.init import SessionDep
import src.data.user as userData
from src.util.auth import verify_password, get_password_hash, all_scopes
from src.config import get_settings
from src.errors import Missing

settings = get_settings()

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "auth/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def add_user(newUser: NewUser, db: Session) -> User:
    toAdd = User(
        username=newUser.username,
        email=newUser.email,
        full_name=newUser.full_name,
        hashed_password=get_password_hash(newUser.password)
    )

    return userData.add_user(toAdd, db)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=settings.secret_key, algorithm=settings.user_token_algorithm)
    return encoded_jwt

def authenticate_user(username: str, password: str, db: Session):
    try:
        user = userData.get_user_by_username(username, db)
    except Missing:
        return False
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def decode_token(token) -> TokenData:
    try:
        payload = jwt.decode(token, key=settings.secret_key, algorithms=[settings.user_token_algorithm], options={"verify_exp": True})
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
        return token_data
    except InvalidTokenError:
        raise credentials_exception

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    token_data: TokenData = decode_token(token)
    user = userData.get_user(token_data.user_id, db)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive User")
    return current_user

def get_current_active_user_with_all_scopes(scopes: List[str]):
    def inner_function(current_user: Annotated[User, Depends(get_current_active_user)]):
        if all_scopes(current_user, scopes):
            return current_user
        raise credentials_exception

    return inner_function