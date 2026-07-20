from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database.base import get_db_session
from app.auth.guards import RequireRole, get_current_user
from app.auth.enums import UserRole
from app.automation.service import WorkflowAutomationService
from app.automation.schemas import WorkflowRuleResponse, WorkflowRuleCreateRequest, WorkflowExecutionResponse

router = APIRouter(prefix="/automation", tags=["Workflow Automation Engine"])

async def get_automation_service(db: AsyncSession = Depends(get_db_session)) -> WorkflowAutomationService:
    return WorkflowAutomationService(db)


@router.post("/workflows", response_model=WorkflowRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_background_workflow_rule(
    payload: WorkflowRuleCreateRequest,
    service: WorkflowAutomationService = Depends(get_automation_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
) -> Any:
    """Registers automated background tracking rules sets. Restricted to corporate Admins/Managers."""
    return await service.register_workflow_rule(payload=payload)


@router.get("/executions", response_model=list[WorkflowExecutionResponse], status_code=status.HTTP_200_OK)
async def list_rule_execution_logs(
    service: WorkflowAutomationService = Depends(get_automation_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
) -> Any:
    """Exposes historical processing run lists to assist technical management diagnostics monitoring."""
    return await service.get_rule_execution_logs()