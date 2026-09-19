from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.database.session import get_db
from app.ai_matching.schemas import MatchHistoryResponse

from app.ai_matching.schemas import (
    BatchMatchRequest,
    BatchMatchResponse,
)
from app.ai_matching.service import AIMatchingService

router = APIRouter(tags=["AI Matching"])


@router.post(
    "/match",
    response_model=BatchMatchResponse,
    summary="Match Consultant with Requirement",
)
async def match(
    request: BatchMatchRequest,
    db: AsyncSession = Depends(get_db),
) -> BatchMatchResponse:

    service = AIMatchingService(db)

    return await service.match(request)

@router.get(
    "/history",
    response_model=MatchHistoryResponse,
    summary="AI Match History",
)
async def get_history(
    db: AsyncSession = Depends(get_db),
) -> MatchHistoryResponse:

    service = AIMatchingService(db)

    return await service.get_history()

@router.post(
    "/batch-match",
    response_model=BatchMatchResponse,
    summary="Batch AI Matching",
)
async def batch_match(
    request: BatchMatchRequest,
    db: AsyncSession = Depends(get_db),
) -> BatchMatchResponse:

    service = AIMatchingService(db)

    return await service.batch_match(request)
