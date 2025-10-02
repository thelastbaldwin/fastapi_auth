from contextlib import asynccontextmanager
from fastapi import FastAPI
from .web.auth import router as authRouter
from .web.user import router as userRouter
from .web.scope import router as scopeRouter
from .data.init import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(authRouter)
app.include_router(scopeRouter)
app.include_router(userRouter)

@app.get("/.well-known/jwks.json")
def json_web_key_set():
    return {
        "keys": [
            {
            "alg": "HS256",
            "kty": "TODO",
            "use": "sig",
            "key_ops": "verify",
            "kid": "TODO",
            "x5u": "TODO"
            }
        ]
    }