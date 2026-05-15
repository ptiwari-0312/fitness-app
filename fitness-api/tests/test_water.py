def test_create_water_log(client, auth_headers):
    payload = {"amount_ml": 500.0, "log_date": "2026-05-15"}
    resp = client.post("/api/v1/water-logs", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["amount_ml"] == 500.0
    assert data["log_date"] == "2026-05-15"
    assert "id" in data
    assert "created_at" in data


def test_create_multiple_water_logs_same_day(client, auth_headers):
    client.post("/api/v1/water-logs", json={"amount_ml": 250.0, "log_date": "2026-05-15"}, headers=auth_headers)
    client.post("/api/v1/water-logs", json={"amount_ml": 500.0, "log_date": "2026-05-15"}, headers=auth_headers)
    resp = client.get("/api/v1/water-logs?log_date=2026-05-15", headers=auth_headers)
    assert len(resp.json()) == 2
    total = sum(l["amount_ml"] for l in resp.json())
    assert total == 750.0


def test_get_water_logs_all(client, auth_headers):
    client.post("/api/v1/water-logs", json={"amount_ml": 250.0, "log_date": "2026-05-14"}, headers=auth_headers)
    client.post("/api/v1/water-logs", json={"amount_ml": 500.0, "log_date": "2026-05-15"}, headers=auth_headers)
    resp = client.get("/api/v1/water-logs", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_water_logs_empty(client, auth_headers):
    resp = client.get("/api/v1/water-logs", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_water_logs_filtered_by_date(client, auth_headers):
    client.post("/api/v1/water-logs", json={"amount_ml": 250.0, "log_date": "2026-05-14"}, headers=auth_headers)
    client.post("/api/v1/water-logs", json={"amount_ml": 500.0, "log_date": "2026-05-15"}, headers=auth_headers)
    resp = client.get("/api/v1/water-logs?log_date=2026-05-14", headers=auth_headers)
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 1
    assert logs[0]["amount_ml"] == 250.0


def test_water_logs_isolated_per_user(client):
    user_a = {"name": "A", "email": "a@example.com", "password": "pass", "age": 25, "gender": "male", "weight_kg": 70.0, "height_cm": 175.0, "activity_level": "moderate"}
    user_b = {"name": "B", "email": "b@example.com", "password": "pass", "age": 25, "gender": "male", "weight_kg": 70.0, "height_cm": 175.0, "activity_level": "moderate"}
    token_a = client.post("/api/v1/auth/register", json=user_a).json()["access_token"]
    token_b = client.post("/api/v1/auth/register", json=user_b).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    client.post("/api/v1/water-logs", json={"amount_ml": 500.0, "log_date": "2026-05-15"}, headers=headers_a)
    resp = client.get("/api/v1/water-logs", headers=headers_b)
    assert resp.json() == []


def test_create_water_log_unauthorized(client):
    resp = client.post("/api/v1/water-logs", json={"amount_ml": 250.0, "log_date": "2026-05-15"})
    assert resp.status_code == 401


def test_get_water_logs_unauthorized(client):
    resp = client.get("/api/v1/water-logs")
    assert resp.status_code == 401
