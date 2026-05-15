import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User, FoodItem, FoodLog, ActivityLog, WaterLog  # register all models

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # all connections share the same in-memory DB
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


USER_PAYLOAD = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "age": 25,
    "gender": "male",
    "weight_kg": 70.0,
    "height_cm": 175.0,
    "activity_level": "moderate",
}


@pytest.fixture
def auth_headers(client):
    resp = client.post("/api/v1/auth/register", json=USER_PAYLOAD)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def food_item():
    db = TestingSessionLocal()
    item = FoodItem(
        name="Chicken Breast",
        calories_per_100g=165.0,
        protein_per_100g=31.0,
        carb_per_100g=0.0,
        fat_per_100g=3.6,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    db.close()
    return item
