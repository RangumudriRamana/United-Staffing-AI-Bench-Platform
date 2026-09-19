from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Any

from app.database.session import get_db
from app.auth.dependencies import RequireRole
from app.auth.enums import Role
from app.analytics.vendor_dashboard.service import VendorAnalyticsService
from app.analytics.vendor_dashboard.schemas import (
    VendorAnalyticsSummaryResponse,
)


router = APIRouter(
    prefix="/dashboard/analytics",
    tags=["Commercial Operations Matrix"],
)


async def get_vendor_analytics_service(
    db: AsyncSession = Depends(get_db),
) -> VendorAnalyticsService:
    return VendorAnalyticsService(db)


@router.get(
    "/vendors/{vendor_public_id}",
    response_model=VendorAnalyticsSummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_vendor_relationship_metrics(
    vendor_public_id: UUID,
    service: VendorAnalyticsService = Depends(
        get_vendor_analytics_service
    ),
    _role=Depends(
        RequireRole(
            [
                Role.ADMIN,
                Role.MANAGER,
            ]
        )
    ),
) -> Any:
    return await service.generate_vendor_profile_analytics(
        vendor_public_id=vendor_public_id
    )