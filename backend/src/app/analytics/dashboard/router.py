from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database.session import get_db
from app.auth.dependencies import RequireRole, get_current_user
from app.auth.enums import Role
from app.models.user import User
from app.analytics.dashboard.service import RecruiterDashboardService
from app.analytics.dashboard.schemas import RecruiterDashboardResponse


router = APIRouter(
    prefix="/dashboard/recruiter",
    tags=["Recruiter Operations Workspace"],
)


async def get_dashboard_service(
    db: AsyncSession = Depends(get_db),
) -> RecruiterDashboardService:
    return RecruiterDashboardService(db)


@router.get(
    "",
    response_model=RecruiterDashboardResponse,
    status_code=status.HTTP_200_OK,
)
async def get_authenticated_recruiter_workspace(
    current_user: User = Depends(get_current_user),
    service: RecruiterDashboardService = Depends(get_dashboard_service),
    _role=Depends(
        RequireRole(
            [
                Role.ADMIN,
                Role.MANAGER,
                Role.RECRUITER,
            ]
        )
    ),
) -> Any:
    return await service.build_recruiter_dashboard(
        recruiter_id=current_user.id
    )