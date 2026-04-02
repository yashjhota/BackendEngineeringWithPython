from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_cache_hit():
    # create user, get once (miss), get again (hit)
    # both responses should return same data
    response = client.post(
        "/users/",
        json={"name": "Cache Test", "email": "jhots@gmail.com", "password": "test"},
    )
    response1 = client.get(f"/users/{response.json()['id']}")
    response2 = client.get(f"/users/{response.json()['id']}")

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json() == response2.json()


def test_cache_invalidation_on_update():
    # create user, get once (miss), update user, get again (should be fresh data)
    response = client.post(
        "/users/",
        json={"name": "Cache Update", "email": "update@gmail.com", "password": "test"},
    )
    response1 = client.get(f"/users/{response.json()['id']}")
    client.put(f"/users/{response.json()['id']}", json={"name": "Cache Updated"})
    response2 = client.get(f"/users/{response.json()['id']}")

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json() != response2.json()


def test_rate_limit():
    # hit the same endpoint 11 times
    for i in range(10):
        response = client.get("/users/")
        assert response.status_code == 200

    # 11th request should be rate limited
    response = client.get("/users/")
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]
