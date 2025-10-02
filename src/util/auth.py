from typing import List
from pwdlib import PasswordHash
from src.model.auth import User

password_hash = PasswordHash.recommended()

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def all_scopes(user: User, scopes: List[str]):
    """
        verify that the user has each of the scopes provided
    """
    user_scopes = {scope.name for scope in user.scopes}

    for scope in scopes:
        if scope not in user_scopes:
            return False
    
    return True

def one_scope(user: User, scopes: List[str]):
    """
        verify that the user has one of the scopes provided
    """
    user_scopes = {scope.name for scope in user.scopes}
    for scope in scopes:
        if scope in user_scopes:
            return True
        
    return False
    