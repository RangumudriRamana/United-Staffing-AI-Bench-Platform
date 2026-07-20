from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Any

from app.database.base import get_db_session
from app.auth.guards import RequireRole, get_current_user
from app.auth.enums import UserRole
from app.analytics.vendor_dashboard.service import VendorAnalyticsService
from app.analytics.vendor_dashboard.schemas import VendorAnalyticsSummaryResponse

router = APIRouter(prefix="/dashboard/analytics", tags=["Commercial Operations Matrix"])

async def get_vendor_analytics_service(db: AsyncSession = Depends(get_db_session)) -> VendorAnalyticsService:
    return VendorAnalyticsService(db)


@router.get("/vendors/{vendor_public_id}", response_model=VendorAnalyticsSummaryResponse, status_code=status.HTTP_200_OK)
async def get_vendor_relationship_metrics(
    vendor_public_id: UUID,
    service: VendorAnalyticsService = Depends(get_vendor_analytics_service),
    _role = Depends(RequireRole([UserRole.ADMIN, UserRole.MANAGER]))
) -> Any:
    """
    Exposes transparent conversion funnel diagnostics and engagement health reviews.
    Access restricted exclusively to Management and Administrative tier accounts.
    """
    return await service.generate_vendor_profile_analytics(vendor_public_id=vendor_public_id)