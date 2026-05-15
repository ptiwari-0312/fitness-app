REGISTER_PAYLOAD = {
    "name": "Alice",
    "email": "alice@example.com",
    "password": "secret123",
    "age": 28,
    "gender": "female",
    "weight_kg": 60.0,
    "height_cm": 165.0,
    "activity_level": "light",
}


def test_register_returns_token(client):
    resp = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    resp = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


def test_login_success(client):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "pass"},
    )
    assert resp.status_code == 401


def test_protected_route_without_token(client):
    resp = client.get("/api/v1/food-items")
    assert resp.status_code == 401


def test_protected_route_with_invalid_token(client):
    resp = client.get("/api/v1/food-items", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401
