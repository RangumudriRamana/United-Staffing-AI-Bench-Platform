from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database.base import get_db_session
from app.auth.guards import RequireRole, get_current_user
from app.auth.enums import UserRole
from app.analytics.executive.service import ExecutiveDashboardService
from app.analytics.executive.schemas import ExecutiveDashboardResponse

router = APIRouter(prefix="/dashboard/executive", tags=["Executive Firm Analytics"])

async def get_executive_service(db: AsyncSession = Depends(get_db_session)) -> ExecutiveDashboardService:
    return ExecutiveDashboardService(db)


@router.get("", response_model=ExecutiveDashboardResponse, status_code=status.HTTP_200_OK)
async def get_firm_wide_executive_dashboard(
    service: ExecutiveDashboardService = Depends(get_executive_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
) -> Any:
    """
    Exposes high-level read projections outlining organizational delivery metrics.
    Access restricted exclusively to leadership accounts (Admins and Managers).
    """
    return await service.build_executive_dashboard()