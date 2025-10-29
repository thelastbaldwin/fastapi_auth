from typing import List
from pwdlib import PasswordHash
from src.model.client import Client
import random
import string
import base64
import hashlib

password_hash = PasswordHash.recommended()

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def all_scopes(client: Client, scopes: List[str]):
    """
        verify that the client has each of the scopes provided
    """
    client_scopes = {scope.name for scope in client.scopes}

    for scope in scopes:
        if scope not in client_scopes:
            return False
    
    return True

def random_string(length):
    """
    Generates a random string of a given length,
    containing a mix of uppercase letters, lowercase letters, and digits.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for i in range(length))
    return random_string

def process_code_verifier(code: str, _method:str = "S256")-> str:
    return base64.b64encode(hashlib.sha256(code));
    