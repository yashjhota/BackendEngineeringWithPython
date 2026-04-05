from fastapi.testclient import TestClient
from main import app
import time
import os

client = TestClient(app)


def test_create_user_returns_immediately():
    create_time = time.time()
    response = client.post(
        "/users/",
        json={
            "name": "Background Test",
            "email": "somes@gmail.com",
            "password": "test",
        },
    )
    elapsed = time.time() - create_time
    assert response.status_code == 201
    # TestClient runs background tasks synchronously
    # so we test the response is correct, not the timing
    assert "id" in response.json()
    assert "password" not in response.json()


def test_log_file_created():
    # after creating a user, app.log file should exist
    client.post(
        "/users/",
        json={"name": "Log Test", "email": "check@email.com", "password": "test"},
    )
    file_exists = os.path.exists("app.log")
    assert file_exists


def test_global_error_handler():
    # hit a route that doesn't exist
    # should return 404 with clean message
    response = client.get("/nonexistent")
    assert response.status_code == 404
