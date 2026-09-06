import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.db import config

config.DATABASE_URL = "postgresql+psycopg://asuta:t3aBl8*f^ll@localhost:5432/test_db"

from app.main import app
from app.db import database
from app.db.models import Base

test_engine = create_engine(config.DATABASE_URL)
TestingSessionLocal = sessionmaker(test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)

@pytest.fixture(scope="function")
def client(setup_database):
    with patch('app.db.database.engine', test_engine):
        with patch('app.db.database.session_factory', TestingSessionLocal):
            yield TestClient(app)

            with test_engine.connect() as conn:
                for table in reversed(Base.metadata.sorted_tables):
                    conn.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE"))
                conn.commit()

@pytest.fixture
def auth_token(client):
    client.post("/auth/register", json={"username": "Test User", "password": "test_password"})

    response = client.post("/auth/login", json={"username": "Test User", "password": "test_password"})

    return response.json()["access_token"]
