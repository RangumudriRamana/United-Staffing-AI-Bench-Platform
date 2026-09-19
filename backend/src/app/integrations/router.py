from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Any

from app.database.base import get_db_session
from app.auth.dependencies import RequireRole
from app.auth.enums import Role
from app.integrations.service import IntegrationHubService
from app.integrations.schemas import IntegrationConnectionResponse, IntegrationConnectionCreateRequest, IntegrationHealthResponse

router = APIRouter(prefix="/integrations", tags=["Enterprise Integration Hub"])

async def get_integration_service(db: AsyncSession = Depends(get_db_session)) -> IntegrationHubService:
    return IntegrationHubService(db)


@router.post("", response_model=IntegrationConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_external_provider_connection(
    payload: IntegrationConnectionCreateRequest,
    service: IntegrationHubService = Depends(get_integration_service),
    _role = Depends(RequireRole([Role.ADMIN]))
) -> Any:
    """Registers an API connector node profile configuration. Restricted exclusively to system Admins."""
    return await service.register_connection_profile(payload=payload)


@router.post("/{public_id}/test", response_model=IntegrationHealthResponse, status_code=status.HTTP_200_OK)
async def trigger_connection_ping_test(
    public_id: UUID,
    service: IntegrationHubService = Depends(get_integration_service),
    _role = Depends(RequireRole([Role.ADMIN, Role.MANAGER]))
) -> Any:
    """Triggers out-of-band remote vendor heartbeat tests and measures data latency markers."""
    return await service.execute_connectivity_check(public_id=public_id)


@router.get("", response_model=list[IntegrationConnectionResponse], status_code=status.HTTP_200_OK)
async def list_active_integration_connections(
    service: IntegrationHubService = Depends(get_integration_service),
    _role = Depends(RequireRole([Role.ADMIN, Role.MANAGER]))
) -> Any:
    """Exposes high-level summaries mapping system connector statuses for configuration panels."""
    return await service.fetch_active_connections_list()