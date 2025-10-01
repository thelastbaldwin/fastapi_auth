from contextlib import asynccontextmanager
from fastapi import FastAPI
from .web.auth import router as authRouter
from .web.user import router as userRouter
from .data.init import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    #setup db
    create_db_and_tables()
    yield
    #cleanup here

app = FastAPI(lifespan=lifespan)

app.include_router(authRouter)
app.include_router(userRouter)