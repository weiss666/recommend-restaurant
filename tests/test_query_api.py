from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


def test_health():
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["ok"] is True


def test_restaurants_default_city():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        res = client.get("/api/restaurants")
        assert res.status_code == 200
        payload = res.json()
        assert "items" in payload
