import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.database.base import Base
from app.models.user import User

settings = get_settings()

TEST_DATABASE_URL = settings.database_url.replace(
    settings.database_url.split("/")[-1], "usai_test"
)

# NullPool forces connection closure immediately after use to prevent cross-test socket locks
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    """Runs once per session to guarantee a clean test catalog exists with built tables."""
    admin_engine = create_async_engine(settings.database_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    async with admin_engine.connect() as conn:
        try:
            await conn.execute(text("CREATE DATABASE usai_test"))
        except Exception:
            pass
    await admin_engine.dispose()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    """Provides a thread-safe connection session that safely rolls back everything written during a test execution."""
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        
        async with TestingSessionLocal(bind=connection) as session:
            yield session
            await session.close()
            
        await transaction.rollback()