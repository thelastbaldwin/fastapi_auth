from pydantic import BaseModel
from fastapi.param_functions import Form
from typing import Annotated
from typing_extensions import Doc

# https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1
class OAuth2PKCEAuthorization(BaseModel):
    def __init__(
            self,
            *,
            client_id: Annotated[str, Form()],
            code_challenge_method: Annotated[str, Doc("'plain' or 'S256'. Plain is not supported")],
            code_challenge: Annotated[str, Doc("Hashed and base64 encoded (in that order)")],
            redirect_uri: Annotated[str | None, Form()],
            response_type: Annotated[str, Form(pattern="code")],
            scope: Annotated[str | None, Form()],
            state: Annotated[str | None, Form()],
    ):
        self.client_id = client_id
        self.code_challenge = code_challenge
        self.code_challenge_method = code_challenge_method
        self.redirect_uri = redirect_uri
        self.response_type = response_type
        self.scope = scope
        self.state = state

class OAuth2PKCETokenRequest(BaseModel):
    def __init__(
            self, 
            *,
            grant_type: Annotated[str, Form(pattern="authorization_code")],
            code: str,
            redirect_uri: str,
            client_id: str,
            code_verifier: str,
    ):
        self.grant_type = grant_type
        self.code = code
        self.redirect_uri = redirect_uri
        self.client_id = client_id
        self.code_verifier = code_verifier
        
    