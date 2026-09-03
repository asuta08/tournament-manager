import pytest

from app.db.repository import UserRepository, TournamentRepository
from tests.conftest import client, auth_token


def test_register(client):
    response = client.post("/auth/register", json={"username": "Test User", "password": "test_password"})

    assert response.status_code == 201
    assert response.json()["user_id"] == 1

    user = UserRepository.get_user_by_id(1)

    assert user.username == "Test User"
    assert user.hashed_password != "test_password"

def test_already_registered(client):

    client.post("/auth/register", json={"username": "Test User", "password": "test_password"})

    response = client.post("/auth/register", json={"username": "Test User", "password": "test_password"})

    assert response.status_code == 400
    assert response.json()["error"] == "User is already registered!"

def test_login(client):

    client.post("/auth/register", json={"username": "Test User", "password": "test_password"})

    response = client.post("/auth/login", json={"username": "Test User", "password": "test_password"})

    assert response.status_code == 200
    assert isinstance(response.json()["access_token"], str)

@pytest.mark.parametrize(
    "username, password",
    [
        ("Wrong User", "wrong_password"),
        ("Test User", "wrong_password"),
        ("Wrong User", "test_password")
    ]
)
def test_invalid_login(client, username, password):
    client.post("/auth/register", json={"username": "Test User", "password": "test_password"})

    response = client.post("/auth/login", json={"username": username, "password": password})

    assert response.status_code == 401
    assert response.json()["error"] in ["Invalid password!", "User is not registered!"]

def test_get_me(client, auth_token):
    response = client.get("/users/me", headers={"Authorization": f"Bearer {auth_token}"})

    assert response.status_code == 200
    assert response.json()["user_id"] == 1
    assert response.json()["username"] == "Test User"

def test_action_without_token(client):
    response = client.post("/tournaments", json={"name": "Test Tournament", "teams": [1, 2, 3, 4]})

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_create_tournament(client, auth_token):
    response = client.post(
        "/tournaments",
        json={"name": "Test Tournament", "teams": [1, 2, 3, 4]},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    assert response.json()["tournament_id"] == 1

    tournament_db = TournamentRepository.load_tournament(1)

    assert tournament_db.name == "Test Tournament"
    assert tournament_db.teams == [1, 2, 3, 4]
    assert len(tournament_db.bracket) == 3

@pytest.mark.parametrize(
    "name, teams",
    [
        ("Test Tournament", [1]),
        ("Test Tournament", [1, 1]),
        ("Test Tournament", "1, 2, 3"),
        ("", [1, 2]),
        (123, [1, 2])
    ]
)
def test_create_tournament_invalid_data(client, auth_token, name, teams):
    response = client.post(
        "/tournaments",
        json={"name": name, "teams": teams},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422

def test_get_tournament(client, auth_token):
    client.post(
        "/tournaments",
        json={"name": "Test Tournament", "teams": [1, 2, 3, 4]},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    response = client.get(
        "/tournaments/1"
    )

    data = response.json()
    assert response.status_code == 200
    assert data["tournament_id"] == 1
    assert data["name"] == "Test Tournament"
    assert data["current_round"] == 1
    assert data["status"] == "in_progress"
    assert data["winner_id"] is None

def test_get_tournament_not_found(client, auth_token):
    response = client.get("/tournaments/42")

    assert response.status_code == 404
    assert response.json()["error"] == "Tournament not found!"