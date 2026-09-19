from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.auth.repositories import UserRepository
from app.models.user import User


def make_repository():
    db = MagicMock()
    db.execute = AsyncMock()
    repository = UserRepository(db)
    return repository, db


@pytest.mark.asyncio
async def test_get_by_email_found():
    repository, db = make_repository()

    user = User()
    user.email = "john@example.com"

    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    db.execute.return_value = result

    found = await repository.get_by_email("john@example.com")

    assert found is user
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_email_not_found():
    repository, db = make_repository()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    found = await repository.get_by_email("missing@example.com")

    assert found is None
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_public_id_found():
    repository, db = make_repository()

    public_id = uuid4()

    user = User()
    user.public_id = public_id

    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    db.execute.return_value = result

    found = await repository.get_by_public_id(public_id)

    assert found is user
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_public_id_not_found():
    repository, db = make_repository()

    public_id = uuid4()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    found = await repository.get_by_public_id(public_id)

    assert found is None
    db.execute.assert_awaited_once()