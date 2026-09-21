from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.main import lifespan, root


@pytest.mark.asyncio
async def test_lifespan_runs_startup_and_shutdown():
    mock_db = MagicMock()

    class MockSessionContext:
        async def __aenter__(self):
            return mock_db

        async def __aexit__(self, exc_type, exc, tb):
            return False

    with patch("app.main.SessionLocal", return_value=MockSessionContext()), \
         patch("app.main.ensure_initial_admin", new_callable=AsyncMock) as mock_admin:

        async with lifespan(MagicMock()):
            pass

    mock_admin.assert_awaited_once_with(mock_db)


@pytest.mark.asyncio
async def test_root_endpoint():
    result = await root()

    assert result == {
        "application": "United Staffing AI Bench Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }