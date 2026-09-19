from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database.base import get_db_session
from app.auth.dependencies import RequireRole, get_current_user
from app.auth.enums import Role
from app.communications.service import CommunicationService
from app.communications.schemas import CommunicationResponse, InternalNoteRequest

router = APIRouter(prefix="/communications", tags=["Interaction Center & Timelines"])

async def get_communication_service(db: AsyncSession = Depends(get_db_session)) -> CommunicationService:
    return CommunicationService(db)


@router.post("/note", response_model=CommunicationResponse, status_code=status.HTTP_201_CREATED)
async def create_shared_internal_note(
    payload: InternalNoteRequest,
    current_user: Any = Depends(get_current_user),
    service: CommunicationService = Depends(get_communication_service),
    _role = Depends(RequireRole([Role.ADMIN, Role.MANAGER, Role.RECRUITER]))
) -> Any:
    """Registers an un-erasable teammate note and appends it to target workspace profiles."""
    return await service.record_internal_note(payload=payload, author_user_id=current_user.id)


@router.get("/entity/{entity_type}/{entity_id}", response_model=list[dict], status_code=status.HTTP_200_OK)
async def get_unified_entity_interaction_timeline(
    entity_type: str,
    entity_id: int,
    service: CommunicationService = Depends(get_communication_service),
    _role = Depends(RequireRole([Role.ADMIN, Role.MANAGER, Role.RECRUITER]))
) -> Any:
    """Assembles a chronological blend of emails, calls, and historical workflow traces for specific rows."""
    return await service.fetch_entity_unified_timeline(entity_type=entity_type, entity_id=entity_id)