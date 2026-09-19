from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.health.router import get_db, router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def test_health_check():
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()

    assert body["message"] == "Service is healthy - TEST"
    assert body["data"] == {"status": "ok"}


def test_liveness_check():
    app = create_app()
    client = TestClient(app)

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_check_database_success():
    app = create_app()

    mock_db = AsyncMock()

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
    mock_db.execute.assert_awaited_once()


def test_readiness_check_database_failure():
    app = create_app()

    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("connection failed")

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database connectivity check failed: connection failed"
    }
    mock_db.execute.assert_awaited_once()