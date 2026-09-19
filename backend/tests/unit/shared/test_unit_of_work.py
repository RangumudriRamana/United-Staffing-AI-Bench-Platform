from unittest.mock import AsyncMock, MagicMock

import pytest

from app.shared.unit_of_work import UnitOfWork


@pytest.fixture
def db():
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def unit_of_work(db):
    return UnitOfWork(db)


@pytest.mark.asyncio
async def test_commit_delegates_to_database(unit_of_work, db):
    result = await unit_of_work.commit()

    assert result is None
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_rollback_delegates_to_database(unit_of_work, db):
    result = await unit_of_work.rollback()

    assert result is None
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_flush_delegates_to_database(unit_of_work, db):
    result = await unit_of_work.flush()

    assert result is None
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_delegates_to_database(unit_of_work, db):
    entity = object()

    result = await unit_of_work.refresh(entity)

    assert result is None
    db.refresh.assert_awaited_once_with(entity)