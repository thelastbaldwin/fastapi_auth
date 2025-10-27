# import base64
import base64
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from jwcrypto import jwk
from .web.auth import router as authRouter
from .web.user import router as userRouter
from .web.scope import router as scopeRouter
from .data.init import create_db_and_tables
from .config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(authRouter)
app.include_router(scopeRouter)
app.include_router(userRouter)

public_jwk = jwk.JWK.from_pem(base64.b64decode(get_settings().public_key)).export_public(as_dict=True)
public_jwk["use"] = "sig"
public_jwk["alg"] = "RS256"

@app.get("/.well-known/jwks.json")
def json_web_key_set():
    return {
        "keys": [
            public_jwk
        ]
    }

app.mount("/login", StaticFiles(directory="src/static", html=True), name="static")