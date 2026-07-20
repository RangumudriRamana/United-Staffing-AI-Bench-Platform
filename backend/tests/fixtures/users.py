import pytest
import pytest_asyncio
from app.auth.enums import Role
from tests.factories.user_factory import UserFactory


@pytest_asyncio.fixture
async def sample_user(db_session):
    """Provides a standard active recruiter profile persisted inside the test database context."""
    user = UserFactory.build(role=Role.BENCH_SALES_RECRUITER)
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def sample_admin(db_session):
    """Provides an administrative profile with elevated privilege permissions."""
    user = UserFactory.build(role=Role.ADMIN)
    db_session.add(user)
    await db_session.commit()
    return user