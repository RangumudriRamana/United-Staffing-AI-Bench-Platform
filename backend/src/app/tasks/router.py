from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Any

from app.database.base import get_db_session
from app.auth.guards import RequireRole, get_current_user
from app.auth.enums import UserRole
from app.tasks.service import TaskService
from app.tasks.schemas import TaskResponse, TaskCreatePayload

router = APIRouter(prefix="/tasks", tags=["Task & Sourcing Queue Management"])

async def get_task_service(db: AsyncSession = Depends(get_db_session)) -> TaskService:
    return TaskService(db)


@router.get("/my", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
async def list_authenticated_user_tasks(
    current_user: Any = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Collects all unresolved active operations items explicitly mapped to the caller account."""
    return await service.fetch_user_active_queue(user_id=current_user.id)


@router.post("/{public_id}/complete", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def mark_active_task_completed(
    public_id: UUID,
    current_user: Any = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Advances task workflow states to COMPLETED and injects chronological closing stamps."""
    return await service.complete_target_task(public_id=public_id, current_user_id=current_user.id)