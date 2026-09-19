from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.database import session


def test_engine_and_session_local_are_configured():
    assert session.engine is not None
    assert session.SessionLocal is not None


@pytest.mark.asyncio
async def test_get_db_yields_session():
    mock_session = MagicMock()

    async_context = MagicMock()
    async_context.__aenter__ = AsyncMock(return_value=mock_session)
    async_context.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.database.session.SessionLocal",
        return_value=async_context,
    ):
        generator = session.get_db()

        result = await generator.__anext__()

        assert result is mock_session

        with pytest.raises(StopAsyncIteration):
            await generator.__anext__()


@pytest.mark.asyncio
async def test_get_db_rolls_back_on_exception():
    mock_session = MagicMock()
    mock_session.rollback = AsyncMock()

    async_context = MagicMock()
    async_context.__aenter__ = AsyncMock(return_value=mock_session)
    async_context.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.database.session.SessionLocal",
        return_value=async_context,
    ):
        generator = session.get_db()

        result = await generator.__anext__()

        assert result is mock_session

        test_error = RuntimeError("database failure")

        with pytest.raises(RuntimeError, match="database failure"):
            await generator.athrow(test_error)

        mock_session.rollback.assert_awaited_once()