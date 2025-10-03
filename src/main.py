# import base64
from contextlib import asynccontextmanager
# from cryptography.hazmat.primitives import serialization
from fastapi import FastAPI
from .web.auth import router as authRouter
from .web.user import router as userRouter
from .web.scope import router as scopeRouter
from .data.init import create_db_and_tables
# from .config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(authRouter)
app.include_router(scopeRouter)
app.include_router(userRouter)


# TODO: figure out how to implement this properly
# @app.get("/.well-known/jwks.json")
# def json_web_key_set():
#     encoded_bytes = get_settings().public_key
#     decoded = base64.b64decode(encoded_bytes)

#     public_key = serialization.load_pem_public_key(
#         decoded
#     )

#     public_numbers = public_key.public_numbers()
#     formatted = "".join(decoded.decode("utf-8").split("\n")[1:-2])

#     return {
#         "keys": [
#             {
#             "alg": get_settings().user_token_algorithm,
#             "kty": "RSA",
#             "use": "sig",
#             "kid": "TODO",
#             "e": str(public_numbers.e),
#             "n": str(public_numbers.n),
#             "key_ops": "verify",
#             "x5c": [formatted]
#             }
#         ]
#     }