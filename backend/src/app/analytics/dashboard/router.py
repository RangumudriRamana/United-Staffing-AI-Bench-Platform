from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database.base import get_db_session
from app.auth.guards import RequireRole, get_current_user
from app.auth.enums import UserRole
from app.analytics.dashboard.service import RecruiterDashboardService
from app.analytics.dashboard.schemas import RecruiterDashboardResponse

router = APIRouter(prefix="/dashboard/recruiter", tags=["Recruiter Operations Workspace"])

# Factory Dependency Handler
async def get_dashboard_service(db: AsyncSession = Depends(get_db_session)) -> RecruiterDashboardService:
    return RecruiterDashboardService(db)


@router.get("", response_model=RecruiterDashboardResponse, status_code=status.HTTP_200_OK)
async def get_authenticated_recruiter_workspace(
    current_user: Any = Depends(get_current_user),
    service: RecruiterDashboardService = Depends(get_dashboard_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """
    Exposes a unified widget-driven operational workspace matrix.
    Restricts internal analytics sorting structures based on current account privileges.
    """
    return await service.build_recruiter_dashboard(recruiter_id=current_user.id)