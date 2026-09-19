from uuid import UUID
from typing import Any
from fastapi import APIRouter, Depends, status

from app.database.base import get_db_session  # standard session provider
from app.auth.dependencies import RequireRole, get_current_user
from app.auth.enums import UserRole
from app.shared.schemas import PaginationParams, SortParams
from app.submissions.service import SubmissionService
from app.submissions.schemas import (
    SubmissionCreateRequest,
    SubmissionSearchFilters,
    SubmissionResponse,
    SubmissionDetailResponse,
    SubmissionTransitionRequest,
    InterviewCreateRequest,
    InterviewResponse,
    OfferCreateRequest,
    OfferResponse,
    PlacementCreateRequest,
    PlacementResponse,
)

router = APIRouter(prefix="/submissions", tags=["Submissions & Pipeline Engagement"])

# Opaque Factory Dependency Provider
async def get_submission_service(db = Depends(get_db_session)) -> SubmissionService:
    return SubmissionService(db)


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_submission(
    payload: SubmissionCreateRequest,
    service: SubmissionService = Depends(get_submission_service),
    current_user: Any = Depends(get_current_user),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Ingests data payloads, registers initial draft tracking rows via security boundaries."""
    return await service.create_submission(payload.model_dump(), current_user.id)


@router.get("", response_model=list[SubmissionResponse])
async def list_pipeline_submissions(
    criteria: SubmissionSearchFilters = Depends(),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    service: SubmissionService = Depends(get_submission_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Delegates paginated collection lookups straight into the optimized pipeline repositories."""
    results, _metadata = await service.list_submissions(criteria, pagination, sort)
    return results


@router.get("/{public_id}", response_model=SubmissionDetailResponse,)
async def get_detailed_submission_summary(
    public_id: UUID,
    service: SubmissionService = Depends(get_submission_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Leverages selectinload configurations to serve comprehensive sub-entity trees."""
    return await service.get_submission(public_id)


@router.post("/{public_id}/transition", response_model=SubmissionResponse)
async def transition_pipeline_state(
    public_id: UUID,
    payload: SubmissionTransitionRequest,
    service: SubmissionService = Depends(get_submission_service),
    current_user: Any = Depends(get_current_user),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Advances pipeline statuses via explicit Finite State Machine rules matrices."""
    return await service.transition_submission_status(
        public_id=public_id,
        target_status=payload.target_status,
        user_id=current_user.id,
        reason=payload.reason,
        notes=payload.notes
    )


@router.post("/{public_id}/interviews",response_model=InterviewResponse,status_code=status.HTTP_201_CREATED)
async def schedule_submission_interview_round(
    public_id: UUID,
    payload: InterviewCreateRequest,
    service: SubmissionService = Depends(get_submission_service),
    current_user: Any = Depends(get_current_user),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Appends explicit sequential interview tracking nodes and advances pipeline markers."""
    return await service.schedule_interview(
    public_id=public_id,
    round_number=payload.round_number,
    interview_type=payload.interview_type,
    scheduled_at=payload.scheduled_at,
    timezone=payload.timezone,
    interviewer=payload.interviewer,
    user_id=current_user.id,
    )


@router.post(
    "/{public_id}/offer",
    response_model=OfferResponse,
    status_code=status.HTTP_201_CREATED,
)
async def issue_client_offer_terms(
    public_id: UUID,
    payload: OfferCreateRequest,
    service: SubmissionService = Depends(get_submission_service),
    current_user: Any = Depends(get_current_user),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """Validates financial invariants and generates client proposal options parameters."""
    return await service.create_offer(
        public_id=public_id,
        offered_rate=payload.offered_rate,
        currency=payload.currency,
        start_date=payload.start_date,
        expiration_date=payload.expiration_date,
        notes=payload.notes,
        user_id=current_user.id,
    )


@router.post(
    "/{public_id}/placement",
    response_model=PlacementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def convert_offer_to_active_placement(
    public_id: UUID,
    payload: PlacementCreateRequest,
    service: SubmissionService = Depends(get_submission_service),
    current_user: Any = Depends(get_current_user),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
) -> Any:
    """
    Triggers multi-aggregate transaction executions: updates submission status, 
    instantiates billing values, and locks consultant core marketing records.
    """
    return await service.create_placement(
    public_id=public_id,
    started_on=payload.started_on,
    ended_on=payload.ended_on,
    billing_rate=payload.billing_rate,
    pay_rate=payload.pay_rate,
    user_id=current_user.id,
    )