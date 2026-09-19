from uuid import UUID
from typing import Any
from fastapi import APIRouter, Depends

from app.database.base import get_db_session
from app.auth.guards import RequireRole, get_current_user
from app.auth.enums import UserRole
from app.matching.service import MatchingService
from app.matching.schemas import RankedConsultantResponse, MatchPolicyWeights

router = APIRouter(prefix="/requirements", tags=["Intelligent Recommendation Engine"])

async def get_matching_service(db = Depends(get_db_session)) -> MatchingService:
    return MatchingService(db)


@router.get("/{public_id}/matches", response_model=list[RankedConsultantResponse])
async def match_consultants_to_job_requirement(
    public_id: UUID,
    policy: MatchPolicyWeights = Depends(),
    service: MatchingService = Depends(get_matching_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER]))
) -> Any:
    """
    Exposes transparent, multi-factor recommendation calculations on demand.
    Accepts customized algorithmic runtime weight modifications seamlessly.
    """
    return await service.get_ranked_matches_for_requirement(
        requirement_public_id=public_id,
        policy=policy
    )
