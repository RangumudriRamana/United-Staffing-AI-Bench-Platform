from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database.base import get_db_session
from app.auth.guards import RequireRole, get_current_user
from app.auth.enums import UserRole
from app.audit.service import AuditService
from app.audit.schemas import AuditRecordResponse

router = APIRouter(prefix="/audit", tags=["Audit, Compliance & System Governance"])

async def get_audit_service(db: AsyncSession = Depends(get_db_session)) -> AuditService:
    return AuditService(db)


@router.get("/entity/{entity_type}/{entity_public_id}", response_model=list[AuditRecordResponse], status_code=status.HTTP_200_OK)
async def get_polymorphic_entity_audit_trail(
    entity_type: str,
    entity_public_id: str,
    service: AuditService = Depends(get_audit_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
) -> Any:
    """Collects historical version snapshots tracking entity mutations. Restricted to Managers and Admins."""
    return await service.fetch_entity_version_history(entity_type=entity_type, entity_public_id=entity_public_id)


@router.get("/trace/{correlation_id}", response_model=list[AuditRecordResponse], status_code=status.HTTP_200_OK)
async def get_transaction_correlation_chain(
    correlation_id: str,
    service: AuditService = Depends(get_audit_service),
    _role = Depends(RequireRole([UserRole.ADMIN]))
) -> Any:
    """Assembles full transactional flow maps bound to a single cross-module correlation string."""
    return await service.resolve_correlation_chain(correlation_id=correlation_id)