from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database.session import get_db
from app.auth.dependencies import RequireRole
from app.auth.enums import Role
from app.analytics.executive.service import ExecutiveDashboardService
from app.analytics.executive.schemas import ExecutiveDashboardResponse


router = APIRouter(
    prefix="/dashboard/executive",
    tags=["Executive Firm Analytics"],
)


async def get_executive_service(
    db: AsyncSession = Depends(get_db),
) -> ExecutiveDashboardService:
    return ExecutiveDashboardService(db)


@router.get(
    "",
    response_model=ExecutiveDashboardResponse,
    status_code=status.HTTP_200_OK,
)
async def get_firm_wide_executive_dashboard(
    service: ExecutiveDashboardService = Depends(get_executive_service),
    _role=Depends(RequireRole([Role.ADMIN, Role.MANAGER])),
) -> Any:
    return await service.build_executive_dashboard()