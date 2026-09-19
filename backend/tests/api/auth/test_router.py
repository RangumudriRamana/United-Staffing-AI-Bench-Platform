from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.auth.router import get_me, login, logout, register
from app.auth.schemas import LoginRequest, RegisterRequest
from app.auth.enums import Role


def make_user():
    return SimpleNamespace(
        id=1,
        public_id=uuid4(),
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role=Role.ADMIN,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_register_success():
    user = make_user()
    db = MagicMock()

    request = RegisterRequest(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        password="SecurePassword123!",
    )

    with patch("app.auth.router.AuthenticationService") as service_cls:
        service_cls.return_value.register = AsyncMock(return_value=user)

        response = await register(request=request, db=db)

    assert response.success is True
    assert response.message == "User registered successfully."
    assert response.data.user.email == user.email


@pytest.mark.asyncio
async def test_login_success():
    user = make_user()
    db = MagicMock()

    request = LoginRequest(
        email="john@example.com",
        password="SecurePassword123!",
    )

    with patch("app.auth.router.AuthenticationService") as service_cls:
        service_cls.return_value.login = AsyncMock(
            return_value=("access-token", user)
        )

        response = await login(request=request, db=db)

    assert response.success is True
    assert response.message == "Login successful."
    assert response.data.access_token == "access-token"
    assert response.data.user.email == user.email


@pytest.mark.asyncio
async def test_get_me_success():
    user = make_user()

    response = await get_me(current_user=user)

    assert response.success is True
    assert response.message == "Current user profile retrieved successfully."
    assert response.data.user.email == user.email


@pytest.mark.asyncio
async def test_logout_success():
    user = make_user()

    session = SimpleNamespace(
        public_id=uuid4(),
        jti="test-jti",
        revoked_at=None,
    )

    db = MagicMock()

    with patch("app.auth.router.AuthenticationService") as service_cls:
        service_cls.return_value.logout = AsyncMock()

        response = await logout(
            current_session=(user, session),
            db=db,
        )

    assert response.success is True
    assert response.message == "Logout successful."
    assert response.data == {}

    service_cls.return_value.logout.assert_awaited_once_with(
        current_user=user,
        session=session,
    )