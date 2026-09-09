from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.db.config import DATABASE_URL, ASYNC_DATABASE_URL

engine = create_engine(
    url=DATABASE_URL,
    connect_args={"connect_timeout": 5}
)

async_engine = create_async_engine(
    url=ASYNC_DATABASE_URL,
    connect_args={"timeout": 5}
)

session_factory = sessionmaker(engine)

async_session_factory = async_sessionmaker(async_engine)

class Base(DeclarativeBase):
    pass