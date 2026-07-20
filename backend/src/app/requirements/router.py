from uuid import UUID
from typing import Any
from fastapi import APIRouter, Depends, status

from app.database.base import get_db_session
from app.auth.guards import RequireRole, get_current_user
from app.auth.enums import UserRole
from app.shared.schemas import PaginationParams, SortParams
from app.requirements.service import RequirementService
from app.requirements.schemas import (
    CreateRequirementRequest, RequirementSearchCriteria, RequirementResponse,
    RequirementTransitionRequest, RequirementTechnologyRequest, RequirementDocumentRequest, OwnerReassignmentRequest
)

router = APIRouter(prefix="/requirements", tags=["Job Requirements Management"])

# Bounded Service Dependency Provider
async def get_requirement_service(db = Depends(get_db_session)) -> RequirementService:
    return RequirementService(db)


@router.post("", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
async def create_new_job_requirement(
    payload: CreateRequirementRequest,
    service: RequirementService = Depends(get_requirement_service),
    current_user: Any = Depends(get_current_user),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Ingests position payloads and boots up an isolated draft requirement row."""
    return await service.create_requirement(payload.model_dump(), current_user.id)


@router.get("", response_model=list[RequirementResponse])
async def list_pipeline_requirements(
    criteria: RequirementSearchCriteria = Depends(),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    service: RequirementService = Depends(get_requirement_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Delegates paginated multi-conditional collections filtering down to persistence pipes."""
    results, _metadata = await service.list_requirements(criteria, pagination, sort)
    return results


@router.get("/{public_id}", response_model=RequirementResponse)
async def get_detailed_requirement_summary(
    public_id: UUID,
    service: RequirementService = Depends(get_requirement_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Resolves selectinload execution strategies to gather all related skills and records."""
    return await service.get_requirement(public_id)


@router.post("/{public_id}/transition", response_model=RequirementResponse)
async def transition_requirement_lifecycle_state(
    public_id: UUID,
    payload: RequirementTransitionRequest,
    service: RequirementService = Depends(get_requirement_service),
    current_user: Any = Depends(get_current_user),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Advances job tracking states across our Finite State Machine constraint matrices."""
    return await service.transition_requirement_status(
        public_id=public_id,
        target_status=payload.target_status,
        user_id=current_user.id,
        reason=payload.reason,
        notes=payload.notes
    )


@router.post("/{public_id}/technologies", status_code=status.HTTP_201_CREATED)
async def bind_technology_constraint(
    public_id: UUID,
    payload: RequirementTechnologyRequest,
    service: RequirementService = Depends(get_requirement_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Appends explicit core technical skills thresholds to evaluate candidates against."""
    return await service.assign_technology(
        public_id=public_id,
        technology_id=payload.technology_id,
        minimum_years=payload.minimum_years,
        mandatory=payload.mandatory,
        notes=payload.notes
    )


@router.post("/{public_id}/documents", status_code=status.HTTP_201_CREATED)
async def bind_compliance_document_requirement(
    public_id: UUID,
    payload: RequirementDocumentRequest,
    service: RequirementService = Depends(get_requirement_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Appends mandatory vetting onboarding paperwork metrics directly onto the role profile."""
    return await service.assign_required_document(
        public_id=public_id,
        document_type=payload.document_type,
        mandatory=payload.mandatory,
        notes=payload.notes
    )


@router.post("/{public_id}/owner", response_model=RequirementResponse)
async def reassign_requirement_account_coverage(
    public_id: UUID,
    payload: OwnerReassignmentRequest,
    service: RequirementService = Depends(get_requirement_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
) -> Any:
    """Administrative override route restricted exclusively to Managers and Admins."""
    return await service.reassign_owner(public_id=public_id, new_owner_id=payload.new_owner_id)