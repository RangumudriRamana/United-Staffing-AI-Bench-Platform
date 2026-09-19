import pytest_asyncio
from datetime import datetime, timezone

from app.auth.models import AuthSession
from app.auth.security import create_access_token, decode_access_token
from app.models.user import User


async def create_test_session(user: User, db_session) -> str:
    """Create a valid JWT and matching active AuthSession for API tests."""
    token, jti = create_access_token(str(user.public_id))
    payload = decode_access_token(token)

    session = AuthSession(
        user_id=user.id,
        jti=jti,
        expires_at=datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc,
        ),
    )

    db_session.add(session)
    await db_session.flush()

    return token


@pytest_asyncio.fixture
async def user_headers(sample_user, db_session):
    token = await create_test_session(sample_user, db_session)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(sample_admin, db_session):
    token = await create_test_session(sample_admin, db_session)
    return {"Authorization": f"Bearer {token}"}