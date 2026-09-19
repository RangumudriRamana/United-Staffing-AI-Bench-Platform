from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user, RequireRole
from app.auth.enums import Role
from app.marketing.schemas import (
    MarketingActivityCreateRequest,
    MarketingActivityResponse,
)
from app.marketing.service import MarketingActivityService
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/marketing/activities",
    tags=["Marketing Activities"],
)


def get_marketing_activity_service(
    db: AsyncSession = Depends(get_db),
) -> MarketingActivityService:
    return MarketingActivityService(db)


@router.post(
    "",
    response_model=MarketingActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_marketing_activity(
    payload: MarketingActivityCreateRequest,
    current_user: Any = Depends(get_current_user),
    service: MarketingActivityService = Depends(
        get_marketing_activity_service
    ),
    _role=Depends(
        RequireRole(
            [
                Role.ADMIN,
                Role.MANAGER,
                Role.BENCH_SALES_RECRUITER,
            ]
        )
    ),
) -> MarketingActivityResponse:
    """
    Records a completed consultant marketing activity.

    Optionally creates a follow-up task when
    follow_up_required is true.
    """

    return await service.create_activity(
        payload=payload,
        current_user_id=current_user.id,
    )


@router.get(
    "/consultant/{consultant_public_id}",
    response_model=list[MarketingActivityResponse],
    status_code=status.HTTP_200_OK,
)
async def list_consultant_marketing_activities(
    consultant_public_id: UUID,
    current_user: Any = Depends(get_current_user),
    service: MarketingActivityService = Depends(
        get_marketing_activity_service
    ),
    _role=Depends(
        RequireRole(
            [
                Role.ADMIN,
                Role.MANAGER,
                Role.BENCH_SALES_RECRUITER,
            ]
        )
    ),
) -> list[MarketingActivityResponse]:
    """
    Returns marketing activity history for one consultant.
    """

    return await service.list_consultant_activities(
        consultant_public_id=consultant_public_id,
    )


@router.get(
    "/{public_id}",
    response_model=MarketingActivityResponse,
    status_code=status.HTTP_200_OK,
)
async def get_marketing_activity(
    public_id: UUID,
    current_user: Any = Depends(get_current_user),
    service: MarketingActivityService = Depends(
        get_marketing_activity_service
    ),
    _role=Depends(
        RequireRole(
            [
                Role.ADMIN,
                Role.MANAGER,
                Role.BENCH_SALES_RECRUITER,
            ]
        )
    ),
) -> MarketingActivityResponse:
    """
    Returns one marketing activity by public identifier.
    """

    return await service.get_activity(
        public_id=public_id,
    )