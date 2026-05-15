import pytest


def test_create_activity_log(client, auth_headers):
    payload = {"steps_count": 10000, "log_date": "2026-05-15"}
    resp = client.post("/api/v1/activity-logs", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["steps_count"] == 10000
    # test user weight_kg=70, formula: 10000 * 0.0005 * 70 = 350.0
    assert data["calories_burned"] == pytest.approx(350.0)
    assert data["log_date"] == "2026-05-15"


def test_create_activity_log_calories_scale_with_steps(client, auth_headers):
    resp1 = client.post("/api/v1/activity-logs", json={"steps_count": 5000, "log_date": "2026-05-14"}, headers=auth_headers)
    resp2 = client.post("/api/v1/activity-logs", json={"steps_count": 10000, "log_date": "2026-05-15"}, headers=auth_headers)
    assert resp2.json()["calories_burned"] == pytest.approx(resp1.json()["calories_burned"] * 2)


def test_get_activity_logs(client, auth_headers):
    client.post("/api/v1/activity-logs", json={"steps_count": 5000, "log_date": "2026-05-15"}, headers=auth_headers)
    resp = client.get("/api/v1/activity-logs", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_activity_logs_empty(client, auth_headers):
    resp = client.get("/api/v1/activity-logs", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_activity_logs_filtered_by_date(client, auth_headers):
    client.post("/api/v1/activity-logs", json={"steps_count": 5000, "log_date": "2026-05-14"}, headers=auth_headers)
    client.post("/api/v1/activity-logs", json={"steps_count": 8000, "log_date": "2026-05-15"}, headers=auth_headers)
    resp = client.get("/api/v1/activity-logs?log_date=2026-05-14", headers=auth_headers)
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 1
    assert logs[0]["steps_count"] == 5000
