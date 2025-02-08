import os
import logging

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

USERNAMEDB = os.getenv("USERNAMEDB")
DBPASSWD = os.getenv("DBPASSWD")
HOSTDB = os.getenv("HOSTDB")
DBNAME = os.getenv("DBNAME")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{USERNAMEDB}:{DBPASSWD}@{HOSTDB}/{DBNAME}"
)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


async def get_async_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
