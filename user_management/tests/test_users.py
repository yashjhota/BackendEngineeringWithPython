from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# separate test database — never test against your real DB
TEST_DATABASE_URL = "postgresql://postgres:YASHJHOTA@localhost:5432/user_management_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# override the get_db dependency to use test DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# create tables before tests
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_create_user():
    response = client.post(
        "/users/",
        json={"name": "Alice", "email": "alice@test.com", "password": "secret123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "alice@test.com"
    assert "password" not in response.json()  # never expose password


def test_get_user_not_found():
    response = client.get("/users/99999")
    assert response.status_code == 404


def test_duplicate_email():
    client.post(
        "/users/",
        json={"name": "Bob", "email": "bob@test.com", "password": "secret123"},
    )
    # try creating same email again
    response = client.post(
        "/users/",
        json={"name": "Bob2", "email": "bob@test.com", "password": "secret456"},
    )
    assert response.status_code == 400


def test_update_user():
    # create first
    create = client.post(
        "/users/",
        json={"name": "Charlie", "email": "charlie@test.com", "password": "secret123"},
    )
    user_id = create.json()["id"]

    # then update
    response = client.put(f"/users/{user_id}", json={"name": "Charlie Updated"})
    assert response.status_code == 200
    assert response.json()["name"] == "Charlie Updated"


def test_delete_user():
    # create first
    create = client.post(
        "/users/",
        json={"name": "Dave", "email": "dave@test.com", "password": "secret123"},
    )
    user_id = create.json()["id"]

    # delete
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    # confirm gone
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404
