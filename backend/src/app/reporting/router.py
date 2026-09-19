from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Any

from app.database.base import get_db_session
from app.auth.dependencies import RequireRole, get_current_user
from app.auth.enums import Role
from app.reporting.service import ReportingService
from app.reporting.schemas import ReportDefinitionResponse, ReportDefinitionCreateRequest, ReportExecutionResponse

router = APIRouter(prefix="/reports", tags=["Reporting & Data Export Platform"])

async def get_reporting_service(db: AsyncSession = Depends(get_db_session)) -> ReportingService:
    return ReportingService(db)


@router.post("", response_model=ReportDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_report_profile(
    payload: ReportDefinitionCreateRequest,
    current_user: Any = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
    _role = Depends(RequireRole([Role.ADMIN, Role.MANAGER]))
) -> Any:
    """Registers reusable report parameter definitions. Restricted to Admins and Managers."""
    return await service.create_report_definition(payload=payload, user_id=current_user.id)


@router.post("/{public_id}/run", response_model=ReportExecutionResponse, status_code=status.HTTP_200_OK)
async def execute_report_generation(
    public_id: UUID,
    current_user: Any = Depends(get_current_user),
    service: ReportingService = Depends(get_reporting_service),
    _role = Depends(RequireRole([Role.ADMIN, Role.MANAGER]))
) -> Any:
    """Triggers snapshot generation routines immediately and logs processing performance speeds."""
    return await service.trigger_on_demand_execution(public_id=public_id, executioner_user_id=current_user.id)


@router.get("/history", response_model=list[ReportExecutionResponse], status_code=status.HTTP_200_OK)
async def list_report_execution_history(
    service: ReportingService = Depends(get_reporting_service),
    _role = Depends(RequireRole([Role.ADMIN, Role.MANAGER]))
) -> Any:
    """Exposes high-level audit records tracking file exports history profiles across the platform."""
    return await service.fetch_execution_history_logs()