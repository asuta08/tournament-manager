import os

import pytest_asyncio
from asgi_lifespan import LifespanManager
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text, NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from unittest.mock import patch

from app.db import config

load_dotenv()
TEST_ASYNC_DATABASE_URL = os.getenv("TEST_ASYNC_DATABASE_URL")
TEST_SYNC_DATABASE_URL = os.getenv("TEST_SYNC_DATABASE_URL")
config.ASYNC_DATABASE_URL = TEST_ASYNC_DATABASE_URL


from app.main import app
from app.db.models import Base

sync_engine = create_engine(TEST_SYNC_DATABASE_URL)
test_engine = create_async_engine(config.ASYNC_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(test_engine)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    Base.metadata.create_all(sync_engine)
    yield
    Base.metadata.drop_all(sync_engine)

@pytest_asyncio.fixture(scope="function")
async def client(setup_database):
    with patch('app.db.database.async_engine', test_engine), \
        patch('app.main.async_engine', test_engine), \
        patch('app.db.database.async_session_factory', TestingSessionLocal), \
        patch('app.db.repository.async_session_factory', TestingSessionLocal):

        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as async_client:
                yield async_client

        async with test_engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE"))

@pytest_asyncio.fixture
async def auth_token(client):
    await client.post("/auth/register", json={"username": "Test User", "password": "test_password"})

    response = await client.post("/auth/login", json={"username": "Test User", "password": "test_password"})

    return response.json()["access_token"]
