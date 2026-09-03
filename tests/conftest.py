import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from unittest.mock import patch

from app.db import config

config.DATABASE_URL = "postgresql+psycopg://asuta:t3aBl8*f^ll@localhost:5432/test_db"

from app.main import app
from app.db import database
from app.db.models import Base


@pytest.fixture(scope="function")
def client():
    test_engine = create_engine(config.DATABASE_URL)

    with patch('app.db.database.engine', test_engine):
        with patch('app.db.database.session_factory', sessionmaker(test_engine)):
            Base.metadata.create_all(test_engine)

            yield TestClient(app)

            Base.metadata.drop_all(test_engine)

@pytest.fixture
def auth_token(client):
    client.post("/auth/register", json={"username": "Test User", "password": "test_password"})

    response = client.post("/auth/login", json={"username": "Test User", "password": "test_password"})

    return response.json()["access_token"]
