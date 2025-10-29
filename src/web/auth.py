from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from datetime import timedelta, datetime
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from src.data.client import get_client
from src.data.init import SessionDep
from src.data.user import get_user
from src.model.token import Token
from src.model.auth import OAuth2PKCEAuthorization, OAuth2PKCETokenRequest
from src.model.user import User
from src.service.auth import authenticate_user, create_access_token, decode_token
from src.config import get_settings
from src.errors import Missing
from src.util.auth import process_code_verifier, random_string
import urllib.parse

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["authentication"])

def access_token_payload(user: User):
    return {
        "sub": str(user.id),
        "roles": " ".join([role.name for role in user.roles])
    }

class RefreshBody(BaseModel):
    refresh_token: str
@router.post("/refresh")
async def refresh_access_token(
    body: RefreshBody,
    db: SessionDep) -> Token:
    """
        Get a new access token, provided the refresh_token is valid
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

@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
) -> TokenRespose:
    """
        Resource Owner Password Flow.
        https://auth0.com/docs/get-started/authentication-and-authorization-flow/resource-owner-password-flow
    """
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

challenges = {}
@router.get("/pkce/authorize")
async def register_challenge(
    params: OAuth2PKCEAuthorization, 
) -> RedirectResponse:
    challenges[params.code_challenge] = {
        "client_id": params.client_id,
    }
    return RedirectResponse(f"/secure/login?redirect_uri={params.redirect_uri}")

# TODO: move this to session storage or, ideally, somewhere where it could be shared between instances
accessCodes = {}
@router.post("/pkce/login")
async def login_for_access_code(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
    redirect_uri=str
) -> RedirectResponse:
    """
        Authenticate with username and password
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    code = random_string(16);
    current_datetime = datetime.now();
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    # associate the access code with the later jwt data and an issued date
    accessCodes[code] = {
        "sub": user.id,
        "roles": " ".join([role.name for role in user.roles]),
        "iss": formatted_datetime
    }

    decoded = urllib.parse.unquote(redirect_uri)
    params = urllib.parse.urlencode({"code": code})
    return RedirectResponse(f"{decoded}?{params}")


@router.post("/pkce/token")
async def trade_access_code_for_tokens(
    params: OAuth2PKCETokenRequest,
    db: SessionDep
) -> TokenRespose:
    # handle challenge 
    code_challenge = process_code_verifier(params.code_verifier)
    if not challenges[code_challenge] or challenges[code_challenge]["client_id"] != params.client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )
    # ensure process needs to be repeated
    del challenges[code_challenge]
    
    code = params.code
    if code is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing code"
        )

    if code not in accessCodes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid code"
        )
    
    now = datetime.now()
    then = datetime.strptime(accessCodes[code], "%Y-%m-%d %H:%M:%S")
    diff = now - then
    if diff.min > 10:
        del accessCodes[code]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Code expired"
        )

    try:
        client = get_client(params.client_id, db)
    except Missing as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.msg
        )
    
    # combine client scopes and user roles, stored in access code dict
    scopes = {scope.name for scope in client.scopes}
    user_id = accessCodes[code]["sub"]
    roles = accessCodes[code]["roles"]
    token_data = {
        "sub": user_id,
        "roles": roles,
        "scopes": " ".join([scope.name for scope in scopes]),
    }

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )

    # access token sub is <client_id>:<user_id>
    refresh_token = create_access_token(
        data={
            "sub": f"{user_id}:{params.client_id}",
        }, expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes))
    del accessCodes[code]
    
    #TODO: properly handle the redirect_uri
    # https://fastapi.tiangolo.com/advanced/custom-response/#response
    return TokenRespose(
        access_token=access_token, token_type="bearer",refresh_token=refresh_token, expires_in=settings.access_token_expire_minutes
    )

                 