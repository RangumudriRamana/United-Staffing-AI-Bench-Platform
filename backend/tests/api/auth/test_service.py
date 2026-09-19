from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.auth.schemas import LoginRequest, RegisterRequest
from app.auth.service import AuthenticationService
from app.core.exceptions import AppException


def make_service():
    db = MagicMock()

    service = AuthenticationService(db)

    service.users = MagicMock()
    service.users.get_by_email = AsyncMock()
    service.users.add = AsyncMock()
    service.users.get_by_public_id = AsyncMock()

    service.uow = MagicMock()
    service.uow.db = db
    service.uow.commit = AsyncMock()
    service.uow.refresh = AsyncMock()

    service.audit_service = MagicMock()
    service.audit_service.write_audit_entry = AsyncMock()
    service.audit_service.get_next_entity_version = AsyncMock(return_value=1)

    return service, db


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_success(monkeypatch):
    service, _ = make_service()

    request = RegisterRequest(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        password="SecurePassword123!",
    )

    service.users.get_by_email.return_value = None

    monkeypatch.setattr(
        "app.auth.service.hash_password",
        MagicMock(return_value="hashed-password"),
    )

    user = SimpleNamespace(
        id=1,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
    )

    service.users.add.side_effect = lambda obj: None

    async def fake_refresh(obj):
        obj.id = 1

    service.uow.refresh.side_effect = fake_refresh

    # Capture the User passed to repository
    added_user = None

    async def capture_add(obj):
        nonlocal added_user
        added_user = obj

    service.users.add.side_effect = capture_add

    result = await service.register(request)

    assert result is added_user
    assert added_user.first_name == "John"
    assert added_user.last_name == "Doe"
    assert added_user.email == "john@example.com"
    assert added_user.hashed_password == "hashed-password"

    service.users.get_by_email.assert_awaited_once_with(request.email)
    service.users.add.assert_awaited_once()
    service.uow.commit.assert_awaited_once()
    service.uow.refresh.assert_awaited_once_with(added_user)


@pytest.mark.asyncio
async def test_register_duplicate_email():
    service, _ = make_service()

    existing_user = SimpleNamespace(id=1)
    service.users.get_by_email.return_value = existing_user

    request = RegisterRequest(
        first_name="John",
        last_name="Doe",
        email="existing@example.com",
        password="SecurePassword123!",
    )

    with pytest.raises(AppException) as exc_info:
        await service.register(request)

    assert exc_info.value.status_code == 409
    assert exc_info.value.error_code == "EMAIL_ALREADY_EXISTS"

    service.users.add.assert_not_awaited()
    service.uow.commit.assert_not_awaited()


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_unknown_email():
    service, _ = make_service()

    service.users.get_by_email.return_value = None

    request = LoginRequest(
        email="missing@example.com",
        password="Password123!",
    )

    with pytest.raises(AppException) as exc_info:
        await service.login(request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_wrong_password(monkeypatch):
    service, _ = make_service()

    user = SimpleNamespace(
        id=1,
        email="john@example.com",
        hashed_password="hashed-password",
        is_active=True,
        public_id="11111111-1111-1111-1111-111111111111",
    )

    service.users.get_by_email.return_value = user

    monkeypatch.setattr(
        "app.auth.service.verify_password",
        MagicMock(return_value=False),
    )

    request = LoginRequest(
        email="john@example.com",
        password="WrongPassword!",
    )

    with pytest.raises(AppException) as exc_info:
        await service.login(request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_inactive_account(monkeypatch):
    service, _ = make_service()

    user = SimpleNamespace(
        id=1,
        email="john@example.com",
        hashed_password="hashed-password",
        is_active=False,
        public_id="11111111-1111-1111-1111-111111111111",
    )

    service.users.get_by_email.return_value = user

    monkeypatch.setattr(
        "app.auth.service.verify_password",
        MagicMock(return_value=True),
    )

    request = LoginRequest(
        email="john@example.com",
        password="Password123!",
    )

    with pytest.raises(AppException) as exc_info:
        await service.login(request)

    assert exc_info.value.status_code == 403
    assert exc_info.value.error_code == "ACCOUNT_DISABLED"


@pytest.mark.asyncio
async def test_login_success(monkeypatch):
    service, db = make_service()

    user = SimpleNamespace(
        id=1,
        email="john@example.com",
        hashed_password="hashed-password",
        is_active=True,
        public_id="11111111-1111-1111-1111-111111111111",
    )

    service.users.get_by_email.return_value = user

    monkeypatch.setattr(
        "app.auth.service.verify_password",
        MagicMock(return_value=True),
    )

    monkeypatch.setattr(
        "app.auth.service.create_access_token",
        MagicMock(
            return_value=(
                "access-token",
                "test-jti",
            )
        ),
    )

    request = LoginRequest(
        email="john@example.com",
        password="Password123!",
    )

    token, result = await service.login(request)

    assert token == "access-token"
    assert result is user

    db.add.assert_called_once()

    session = db.add.call_args.args[0]

    assert session.user_id == user.id
    assert session.jti == "test-jti"

    service.audit_service.write_audit_entry.assert_awaited_once()
    service.uow.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# logout
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_logout_success():
    service, _ = make_service()

    current_user = SimpleNamespace(
        id=1,
        public_id="11111111-1111-1111-1111-111111111111",
        email="john@example.com",
        is_active=True,
    )

    session = SimpleNamespace(
        public_id="22222222-2222-2222-2222-222222222222",
        jti="test-jti",
        revoked_at=None,
    )

    await service.logout(current_user, session)

    assert session.revoked_at is not None

    service.audit_service.write_audit_entry.assert_awaited_once()
    service.uow.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# get_current_user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_success():
    service, _ = make_service()

    user = SimpleNamespace(
        id=1,
        public_id="11111111-1111-1111-1111-111111111111",
    )

    service.users.get_by_public_id.return_value = user

    result = await service.get_current_user(user.public_id)

    assert result is user

    service.users.get_by_public_id.assert_awaited_once_with(
        user.public_id
    )


@pytest.mark.asyncio
async def test_get_current_user_not_found():
    service, _ = make_service()

    service.users.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.get_current_user(
            "11111111-1111-1111-1111-111111111111"
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.error_code == "USER_NOT_FOUND"