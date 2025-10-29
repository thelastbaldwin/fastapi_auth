# import base64
import base64
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from jwcrypto import jwk
from .web.auth import router as authRouter
from .web.user import router as userRouter
from .web.scope import router as scopeRouter
from .web.client import router as clientRouter
from .data.init import create_db_and_tables
from .config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/client/static", StaticFiles(directory="src/static"), name="static")

app.include_router(authRouter)
app.include_router(scopeRouter)
app.include_router(userRouter)
app.include_router(clientRouter)

public_key = get_settings().public_key
decoded_key = base64.b64decode(public_key)
public_jwk = jwk.JWK.from_pem(decoded_key).export_public(as_dict=True)
public_jwk["use"] = "sig"
public_jwk["alg"] = "RS256"

@app.get("/.well-known/jwks.json")
def json_web_key_set():
    return {
        "keys": [
            public_jwk
        ]
    }


