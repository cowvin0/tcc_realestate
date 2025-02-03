from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from app.main import app
from app.database import engine, Base
from app.models import *


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def lifespan(app: FastAPI):
    await init_db()
    yield


api = FastAPI(lifespan=lifespan)
api.mount("/", WSGIMiddleware(app.server))
