import app.api.api_method as db_data
from fastapi import FastAPI
from app.api.database import engine, Base
from app.api.models import *


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def lifespan(app: FastAPI):
    await init_db()
    yield


api = FastAPI(lifespan=lifespan)
api.include_router(db_data.router)
