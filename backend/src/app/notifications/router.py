from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Any

from app.database.base import get_db_session
from app.auth.dependencies import RequireRole, get_current_user
from app.auth.enums import Role
from app.notifications.service import NotificationService
from app.notifications.schemas import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notification & System Alerts Hub"])

async def get_notification_service(db: AsyncSession = Depends(get_db_session)) -> NotificationService:
    return NotificationService(db)


@router.get("/unread", response_model=list[NotificationResponse], status_code=status.HTTP_200_OK)
async def list_active_unread_notifications(
    current_user: Any = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
    _role = Depends(RequireRole([Role.ADMIN, Role.MANAGER, Role.RECRUITER]))
) -> Any:
    """Collects all pending messages and alert vectors assigned to the authenticated user profile."""
    return await service.fetch_user_unread_alerts(recipient_user_id=current_user.id)


@router.post("/{public_id}/read", response_model=NotificationResponse, status_code=status.HTTP_200_OK)
async def acknowledge_notification_alert(
    public_id: UUID,
    current_user: Any = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
    _role = Depends(RequireRole([Role.ADMIN, Role.MANAGER, Role.RECRUITER]))
) -> Any:
    """Advances status parameters from UNREAD to READ and sets structural time metrics hooks."""
    return await service.mark_notification_as_read(public_id=public_id, recipient_user_id=current_user.id)