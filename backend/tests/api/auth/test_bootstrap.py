from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.auth.bootstrap import ensure_initial_admin
from app.auth.enums import Role


def make_settings():
    return SimpleNamespace(
        initial_admin_email="admin@example.com",
        initial_admin_password="StrongPassword123!",
        initial_admin_first_name="Initial",
        initial_admin_last_name="Admin",
    )


@pytest.mark.asyncio
async def test_ensure_initial_admin_returns_when_admin_exists():
    db = MagicMock()
    result = MagicMock()
    existing_admin = MagicMock()

    result.scalar_one_or_none.return_value = existing_admin
    db.execute = AsyncMock(return_value=result)

    with patch(
        "app.auth.bootstrap.get_settings",
        return_value=make_settings(),
    ), patch(
        "app.auth.bootstrap.hash_password"
    ) as mock_hash:
        await ensure_initial_admin(db)

    db.execute.assert_awaited_once()
    result.scalar_one_or_none.assert_called_once_with()
    db.add.assert_not_called()
    db.commit.assert_not_called()
    mock_hash.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_initial_admin_creates_admin_when_missing():
    db = MagicMock()
    result = MagicMock()

    result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result)
    db.commit = AsyncMock()

    settings = make_settings()

    with patch(
        "app.auth.bootstrap.get_settings",
        return_value=settings,
    ), patch(
        "app.auth.bootstrap.hash_password",
        return_value="hashed-password",
    ) as mock_hash:
        await ensure_initial_admin(db)

    db.execute.assert_awaited_once()
    result.scalar_one_or_none.assert_called_once_with()

    mock_hash.assert_called_once_with(settings.initial_admin_password)

    db.add.assert_called_once()
    created_admin = db.add.call_args.args[0]

    assert created_admin.email == settings.initial_admin_email
    assert created_admin.hashed_password == "hashed-password"
    assert created_admin.first_name == settings.initial_admin_first_name
    assert created_admin.last_name == settings.initial_admin_last_name
    assert created_admin.role == Role.ADMIN
    assert created_admin.is_active is True

    db.commit.assert_awaited_once()