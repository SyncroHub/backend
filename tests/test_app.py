from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_frontend_login_is_served() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "SyncroHUB" in response.text


def test_static_asset_is_served() -> None:
    response = client.get("/assets/css/pages/login.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]

