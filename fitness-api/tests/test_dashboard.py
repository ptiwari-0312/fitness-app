import pytest


# Test user: male, weight=70, height=175, age=25, moderate activity
# BMR = (10*70) + (6.25*175) - (5*25) + 5 = 1673.75
# TDEE = 1673.75 * 1.55 = 2594.3125


def test_summary_no_logs(client, auth_headers):
    resp = client.get("/api/v1/dashboard/summary?log_date=2026-05-15", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bmr"] == pytest.approx(1673.75)
    assert data["tdee"] == pytest.approx(2594.31, rel=1e-3)
    assert data["calories_consumed"] == 0.0
    assert data["calories_burned"] == 0.0
    assert data["net_calories"] == 0.0


def test_summary_defaults_to_today(client, auth_headers):
    resp = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert resp.status_code == 200
    assert "bmr" in resp.json()


def test_summary_with_food_log(client, auth_headers, food_item):
    # Chicken Breast 165 kcal/100g × 200g = 330 kcal
    client.post(
        "/api/v1/food-logs",
        json={"food_item_id": food_item.id, "quantity_grams": 200.0, "log_date": "2026-05-15"},
        headers=auth_headers,
    )
    resp = client.get("/api/v1/dashboard/summary?log_date=2026-05-15", headers=auth_headers)
    data = resp.json()
    assert data["calories_consumed"] == pytest.approx(330.0)
    assert data["net_calories"] == pytest.approx(330.0)


def test_summary_with_activity_log(client, auth_headers):
    # 10000 steps × 0.0005 × 70kg = 350 kcal
    client.post(
        "/api/v1/activity-logs",
        json={"steps_count": 10000, "log_date": "2026-05-15"},
        headers=auth_headers,
    )
    resp = client.get("/api/v1/dashboard/summary?log_date=2026-05-15", headers=auth_headers)
    data = resp.json()
    assert data["calories_burned"] == pytest.approx(350.0)
    assert data["net_calories"] == pytest.approx(-350.0)


def test_summary_net_calories_combined(client, auth_headers, food_item):
    client.post(
        "/api/v1/food-logs",
        json={"food_item_id": food_item.id, "quantity_grams": 200.0, "log_date": "2026-05-15"},
        headers=auth_headers,
    )
    client.post(
        "/api/v1/activity-logs",
        json={"steps_count": 10000, "log_date": "2026-05-15"},
        headers=auth_headers,
    )
    resp = client.get("/api/v1/dashboard/summary?log_date=2026-05-15", headers=auth_headers)
    data = resp.json()
    # 330 consumed - 350 burned = -20
    assert data["net_calories"] == pytest.approx(-20.0, abs=0.1)


def test_weekly_trend_returns_seven_days(client, auth_headers):
    resp = client.get("/api/v1/dashboard/weekly-trend", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 7
    for day in data:
        assert "log_date" in day
        assert "net_calories" in day
        assert "has_data" in day


def test_weekly_trend_no_data_flags(client, auth_headers):
    resp = client.get("/api/v1/dashboard/weekly-trend", headers=auth_headers)
    data = resp.json()
    assert all(not d["has_data"] for d in data)
    assert all(d["net_calories"] == 0.0 for d in data)
