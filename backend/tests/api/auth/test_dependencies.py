from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jwt import PyJWTError

from app.auth.dependencies import (
    RequireRole,
    get_current_session,
    get_current_user,
)
from app.auth.enums import Role
from app.core.exceptions import AppException


def make_credentials(token="test-token"):
    return SimpleNamespace(credentials=token)


def make_db():
    db = MagicMock()
    db.execute = AsyncMock()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None

    db.execute.return_value = result

    return db


def make_user():
    return SimpleNamespace(
        id=1,
        public_id="11111111-1111-1111-1111-111111111111",
        email="user@example.com",
        is_active=True,
        role=Role.ADMIN,
    )


def make_session():
    return SimpleNamespace(
        id=10,
        public_id="22222222-2222-2222-2222-222222222222",
        jti="test-jti",
        user_id=1,
        revoked_at=None,
    )


# ---------------------------------------------------------------------------
# get_current_user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_success():
    db = make_db()
    user = make_user()
    session = make_session()

    db.execute.return_value.scalar_one_or_none.return_value = session

    payload = {
        "sub": str(user.public_id),
        "jti": "test-jti",
    }

    with patch(
        "app.auth.dependencies.decode_access_token",
        return_value=payload,
    ), patch(
        "app.auth.dependencies.AuthenticationService"
    ) as service_cls:
        service_cls.return_value.get_current_user = AsyncMock(
            return_value=user
        )

        result = await get_current_user(
            token=make_credentials(),
            db=db,
        )

    assert result is user
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_current_user_missing_subject():
    db = make_db()

    with patch(
        "app.auth.dependencies.decode_access_token",
        return_value={"jti": "test-jti"},
    ):
        with pytest.raises(AppException) as exc_info:
            await get_current_user(
                token=make_credentials(),
                db=db,
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "UNAUTHORIZED"
    assert "subject identifier missing" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_current_user_missing_jti():
    db = make_db()

    with patch(
        "app.auth.dependencies.decode_access_token",
        return_value={
            "sub": "11111111-1111-1111-1111-111111111111",
        },
    ):
        with pytest.raises(AppException) as exc_info:
            await get_current_user(
                token=make_credentials(),
                db=db,
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "UNAUTHORIZED"
    assert "token identifier missing" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    db = make_db()

    with patch(
        "app.auth.dependencies.decode_access_token",
        side_effect=PyJWTError("invalid token"),
    ):
        with pytest.raises(AppException) as exc_info:
            await get_current_user(
                token=make_credentials(),
                db=db,
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "UNAUTHORIZED"
    assert "invalid or expired" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_current_user_invalid_uuid():
    db = make_db()

    with patch(
        "app.auth.dependencies.decode_access_token",
        return_value={
            "sub": "not-a-valid-uuid",
            "jti": "test-jti",
        },
    ):
        with pytest.raises(AppException) as exc_info:
            await get_current_user(
                token=make_credentials(),
                db=db,
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_current_user_invalid_session():
    db = make_db()

    payload = {
        "sub": "11111111-1111-1111-1111-111111111111",
        "jti": "revoked-jti",
    }

    with patch(
        "app.auth.dependencies.decode_access_token",
        return_value=payload,
    ):
        with pytest.raises(AppException) as exc_info:
            await get_current_user(
                token=make_credentials(),
                db=db,
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "UNAUTHORIZED"
    assert "revoked" in exc_info.value.message


# ---------------------------------------------------------------------------
# get_current_session
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_session_success():
    db = make_db()
    user = make_user()
    session = make_session()

    result = MagicMock()
    result.scalar_one_or_none.return_value = session
    db.execute.return_value = result

    payload = {
        "sub": str(user.public_id),
        "jti": session.jti,
    }

    with patch(
        "app.auth.dependencies.decode_access_token",
        return_value=payload,
    ), patch(
        "app.auth.dependencies.AuthenticationService"
    ) as service_cls:
        service_cls.return_value.get_current_user = AsyncMock(
            return_value=user
        )

        result_user, result_session = await get_current_session(
            token=make_credentials(),
            db=db,
        )

    assert result_user is user
    assert result_session is session


@pytest.mark.asyncio
async def test_get_current_session_missing_subject():
    db = make_db()

    with patch(
        "app.auth.dependencies.decode_access_token",
        return_value={"jti": "test-jti"},
    ):
        with pytest.raises(AppException) as exc_info:
            await get_current_session(
                token=make_credentials(),
                db=db,
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_current_session_missing_jti():
    db = make_db()

    with patch(
        "app.auth.dependencies.decode_access_token",
        return_value={
            "sub": "11111111-1111-1111-1111-111111111111",
        },
    ):
        with pytest.raises(AppException) as exc_info:
            await get_current_session(
                token=make_credentials(),
                db=db,
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_current_session_invalid_token():
    db = make_db()

    with patch(
        "app.auth.dependencies.decode_access_token",
        side_effect=PyJWTError("invalid token"),
    ):
        with pytest.raises(AppException) as exc_info:
            await get_current_session(
                token=make_credentials(),
                db=db,
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_current_session_invalid_session():
    db = make_db()
    user = make_user()

    payload = {
        "sub": str(user.public_id),
        "jti": "revoked-jti",
    }

    with patch(
        "app.auth.dependencies.decode_access_token",
        return_value=payload,
    ), patch(
        "app.auth.dependencies.AuthenticationService"
    ) as service_cls:
        service_cls.return_value.get_current_user = AsyncMock(
            return_value=user
        )

        with pytest.raises(AppException) as exc_info:
            await get_current_session(
                token=make_credentials(),
                db=db,
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.error_code == "UNAUTHORIZED"
    assert "revoked" in exc_info.value.message


# ---------------------------------------------------------------------------
# RequireRole
# ---------------------------------------------------------------------------


def test_require_role_allows_authorized_user():
    user = make_user()
    dependency = RequireRole([Role.ADMIN])

    result = dependency(user)

    assert result is user


def test_require_role_rejects_unauthorized_user():
    user = make_user()
    user.role = Role.RECRUITER

    dependency = RequireRole([Role.ADMIN])

    with pytest.raises(AppException) as exc_info:
        dependency(user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.error_code == "FORBIDDEN"
    assert "Access denied" in exc_info.value.message