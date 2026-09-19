from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.shared.repository import BaseRepository


class TestBase(DeclarativeBase):
    pass


class FakeModel(TestBase):
    __tablename__ = "test_repository_entities"

    id: Mapped[int] = mapped_column(primary_key=True)


def make_db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.delete = AsyncMock()
    return db


def make_result(
    scalar_one_or_none=None,
    scalars_all=None,
):
    result = MagicMock()

    result.scalar_one_or_none.return_value = scalar_one_or_none

    scalars = MagicMock()
    scalars.all.return_value = (
        scalars_all if scalars_all is not None else []
    )
    result.scalars.return_value = scalars

    return result


@pytest.mark.asyncio
async def test_get_by_id_returns_entity():
    db = make_db()

    entity = SimpleNamespace(id=1)

    db.execute.return_value = make_result(
        scalar_one_or_none=entity
    )

    repository = BaseRepository(db, FakeModel)

    result = await repository.get_by_id(1)

    assert result == entity
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_not_found():
    db = make_db()

    db.execute.return_value = make_result(
        scalar_one_or_none=None
    )

    repository = BaseRepository(db, FakeModel)

    result = await repository.get_by_id(999)

    assert result is None
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_returns_entities():
    db = make_db()

    entities = [
        SimpleNamespace(id=1),
        SimpleNamespace(id=2),
    ]

    db.execute.return_value = make_result(
        scalars_all=entities
    )

    repository = BaseRepository(db, FakeModel)

    result = await repository.get_all()

    assert result == entities
    assert len(result) == 2
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_adds_and_flushes_entity():
    db = make_db()

    entity = SimpleNamespace(id=1)

    repository = BaseRepository(db, FakeModel)

    result = await repository.add(entity)

    assert result is entity
    db.add.assert_called_once_with(entity)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_deletes_and_flushes_entity():
    db = make_db()

    entity = SimpleNamespace(id=1)

    repository = BaseRepository(db, FakeModel)

    result = await repository.delete(entity)

    assert result is None
    db.delete.assert_awaited_once_with(entity)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_exists_returns_true_when_entity_exists():
    db = make_db()

    entity = SimpleNamespace(id=1)

    db.execute.return_value = make_result(
        scalar_one_or_none=entity
    )

    repository = BaseRepository(db, FakeModel)

    result = await repository.exists(1)

    assert result is True
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_exists_returns_false_when_entity_does_not_exist():
    db = make_db()

    db.execute.return_value = make_result(
        scalar_one_or_none=None
    )

    repository = BaseRepository(db, FakeModel)

    result = await repository.exists(999)

    assert result is False