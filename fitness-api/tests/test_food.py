import pytest


def test_list_food_items(client, auth_headers, food_item):
    resp = client.get("/api/v1/food-items", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["name"] == "Chicken Breast"
    assert items[0]["calories_per_100g"] == 165.0


def test_list_food_items_empty(client, auth_headers):
    resp = client.get("/api/v1/food-items", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_food_log(client, auth_headers, food_item):
    payload = {"food_item_id": food_item.id, "quantity_grams": 200.0, "log_date": "2026-05-15"}
    resp = client.post("/api/v1/food-logs", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["quantity_grams"] == 200.0
    assert data["log_date"] == "2026-05-15"
    assert data["food_item"]["name"] == "Chicken Breast"


def test_create_food_log_invalid_food_item(client, auth_headers):
    payload = {"food_item_id": 999, "quantity_grams": 100.0, "log_date": "2026-05-15"}
    resp = client.post("/api/v1/food-logs", json=payload, headers=auth_headers)
    assert resp.status_code == 404


def test_get_food_logs(client, auth_headers, food_item):
    client.post(
        "/api/v1/food-logs",
        json={"food_item_id": food_item.id, "quantity_grams": 100.0, "log_date": "2026-05-15"},
        headers=auth_headers,
    )
    resp = client.get("/api/v1/food-logs", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_food_logs_empty(client, auth_headers):
    resp = client.get("/api/v1/food-logs", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_food_logs_filtered_by_date(client, auth_headers, food_item):
    client.post(
        "/api/v1/food-logs",
        json={"food_item_id": food_item.id, "quantity_grams": 100.0, "log_date": "2026-05-14"},
        headers=auth_headers,
    )
    client.post(
        "/api/v1/food-logs",
        json={"food_item_id": food_item.id, "quantity_grams": 150.0, "log_date": "2026-05-15"},
        headers=auth_headers,
    )
    resp = client.get("/api/v1/food-logs?log_date=2026-05-14", headers=auth_headers)
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 1
    assert logs[0]["quantity_grams"] == 100.0


def test_delete_food_log(client, auth_headers, food_item):
    create_resp = client.post(
        "/api/v1/food-logs",
        json={"food_item_id": food_item.id, "quantity_grams": 100.0, "log_date": "2026-05-15"},
        headers=auth_headers,
    )
    log_id = create_resp.json()["id"]
    resp = client.delete(f"/api/v1/food-logs/{log_id}", headers=auth_headers)
    assert resp.status_code == 204
    remaining = client.get("/api/v1/food-logs", headers=auth_headers).json()
    assert remaining == []


def test_delete_nonexistent_food_log(client, auth_headers):
    resp = client.delete("/api/v1/food-logs/999", headers=auth_headers)
    assert resp.status_code == 404
