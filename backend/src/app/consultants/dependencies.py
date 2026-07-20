from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.consultants.service import ConsultantService

def get_consultant_service(db: AsyncSession = Depends(get_db)) -> ConsultantService:
    """Provides an isolated ConsultantService execution instance bound to the active request database session."""
    return ConsultantService(db)