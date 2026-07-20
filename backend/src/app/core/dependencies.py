from collections.abc import AsyncGenerator

from app.core.config import Settings, get_settings
from app.database.session import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

def get_app_settings() -> Settings:
    """
    Shared dependency for accessing application settings.
    """
    return get_settings()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Standard dynamic dependency for all async database tasks."""
    async with SessionLocal() as session:
        yield session