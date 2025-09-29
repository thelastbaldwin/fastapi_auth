from fastapi import FastAPI
from .web.auth import router as authRouter
from .web.user import router as userRouter

app = FastAPI()

app.include_router(authRouter)
app.include_router(userRouter)