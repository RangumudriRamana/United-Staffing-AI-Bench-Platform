from fastapi import APIRouter, Depends, status
from uuid import UUID
from typing import Any

from app.shared.schemas import PagedResponse, PaginationParams, SortParams
from app.consultants.schemas import (
    ConsultantCreateRequest,
    UpdateConsultantRequest,
    ConsultantResponse,
    ConsultantFilterParams,
    ConsultantStatusTransitionRequest,
    ConsultantMarketingHistoryResponse,
)
from app.consultants.dependencies import get_consultant_service
from app.consultants.service import ConsultantService

from app.auth.dependencies import get_current_user, RequireRole
from app.auth.enums import UserRole

router = APIRouter(prefix="/consultants", tags=["Consultants"])

@router.get(
    "/{public_id}/marketing/history",
    response_model=list[ConsultantMarketingHistoryResponse],
    dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))]
)
async def get_consultant_marketing_history(
    public_id: UUID,
    service: ConsultantService = Depends(get_consultant_service)
) -> Any:
    """
    Returns the consultant's complete marketing lifecycle history,
    ordered from the most recent transition to the oldest.
    """
    print("HTTP HISTORY PUBLIC ID:", public_id)
    print("HTTP SERVICE DB ID:", id(service.db))

    return await service.get_marketing_history(public_id)

@router.post(
    "",
    response_model=ConsultantResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))]
)
async def create_consultant(
    payload: ConsultantCreateRequest,
    service: ConsultantService = Depends(get_consultant_service),
    current_user: Any = Depends(get_current_user)
) -> Any:
    """Protected endpoint enabling authorized staff profiles to register new bench records."""
    return await service.create_consultant(payload, current_user_id=current_user.id)


@router.get(
    "/{public_id}",
    response_model=ConsultantResponse,
    dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))]
)
async def get_consultant(
    public_id: UUID,
    service: ConsultantService = Depends(get_consultant_service)
) -> Any:
    """Fetches full details for a distinct active profile matching the provided UUID."""
    return await service.get_consultant(public_id)


@router.get(
    "",
    response_model=PagedResponse[ConsultantResponse],
    dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))]
)
@router.get(
    "/",
    response_model=PagedResponse[ConsultantResponse],
    dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))]
)
async def list_consultants(
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    filters: ConsultantFilterParams = Depends(),
    service: ConsultantService = Depends(get_consultant_service)
) -> Any:
    """Exercises our shared query framework to deliver fully paginated, filtered, and sorted records."""
    records, metadata = await service.list_consultants(pagination, sort, filters)
    return {"data": records, "pagination": metadata}


@router.patch(
    "/{public_id}",
    response_model=ConsultantResponse,
    dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))]
)
async def update_consultant(
    public_id: UUID,
    payload: UpdateConsultantRequest,
    service: ConsultantService = Depends(get_consultant_service),
    current_user: Any = Depends(get_current_user)
) -> Any:
    """Executes a true partial modification of specified consultant record attributes."""
    return await service.update_consultant(public_id, payload, current_user_id=current_user.id)


@router.delete(
    "/{public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))]
)
async def archive_consultant(
    public_id: UUID,
    service: ConsultantService = Depends(get_consultant_service),
    current_user: Any = Depends(get_current_user)
) -> None:
    """Restricted administrative endpoint applying a logical mask string to execute soft deletions."""
    await service.archive_consultant(
        public_id,
        current_user_id=current_user.id
    )


@router.post(
    "/{public_id}/marketing/transition",
    response_model=ConsultantResponse,
    dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))]
)
async def transition_consultant_status(
    public_id: UUID,
    payload: ConsultantStatusTransitionRequest,
    service: ConsultantService = Depends(get_consultant_service),
    current_user: Any = Depends(get_current_user)
) -> Any:
    """
    Exposes explicit operational state transitions. Enforces coarse RBAC at the perimeter,
    then passes execution to the internal service layer state machine.
    """
    return await service.transition_marketing_status(
        public_id=public_id,
        new_status=payload.target_status,
        changed_by_user_id=current_user.id,
        reason=payload.reason,
        notes=payload.notes
    )
