from typing import Union,Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI,UploadFile,HTTPException,Depends
from fastapi.websockets import WebSocket
from .routers import authRouter,fileRouter,chatRouter
from .models import create_db_and_tables,SessionDep
from .routers.auth import get_current_user
from sqlmodel import delete,select
from redis.asyncio import Redis
from .models import User,File
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter,WebSocketRateLimiter
from dotenv import load_dotenv
import os



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: create tables
    print("Starting up: Creating database tables...")
    redis_connection = Redis.from_url(os.getenv("REDIS_URL"), encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)
    # SQLModel.metadata.create_all(bind=engine)
    create_db_and_tables()

    yield  
    # Shutdown logic
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.include_router(authRouter, prefix="/auth", tags=["auth"])
app.include_router(fileRouter,prefix="/file",tags=["file"])
app.include_router(chatRouter,prefix="/chat",tags=["chat"])

@app.get("/",dependencies=[Depends(RateLimiter(times=5,seconds=20))])
def read_root():
    return {"message": "Server is running"}




   