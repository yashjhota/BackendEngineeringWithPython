from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_login_success():

    # create a user first, then login, check token is returned
    client.post(
        "/users/",
        json={"name": "Test User", "email": "test@test.com", "password": "test"},
    )

    response = client.post(
        "/auth/login", json={"email": "test@test.com", "password": "test"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password():
    # should return 401
    client.post(
        "/users/",
        json={"name": "Test User2", "email": "test@2test.com", "password": "test1"},
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "test@2test.com",
            "password": "wrgprd",  # wrong password → 401
        },
    )
    assert response.status_code == 401


def test_protected_route_without_token():
    # hit /users/me without token, should return 401
    response = client.get("/users/me")
    assert response.status_code == 401
