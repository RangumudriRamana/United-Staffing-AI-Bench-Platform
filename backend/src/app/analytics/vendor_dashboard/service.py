from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.core.exceptions import AppException
from app.vendors.models import Vendor
from app.analytics.models import BusinessEvent
from app.analytics.enums import BusinessEventType
from app.analytics.vendor_dashboard.schemas import (
    VendorAnalyticsSummaryResponse, AccountFunnelStage, RelationshipHealthDTO, AccountResponseTimeMetrics
)

class VendorAnalyticsService:
    """
    Compiles macro commercial metrics, execution timelines, and funnel conversion
    ratios by parsing the central append-only event stream registry.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_vendor_profile_analytics(self, vendor_public_id: UUID) -> VendorAnalyticsSummaryResponse:
        """Processes account metrics synchronously from event logs to protect production table load speeds."""
        # 1. Resolve master relational entities safely
        vendor_stmt = select(Vendor).where(Vendor.public_id == vendor_public_id)
        vendor_res = await self.db.execute(vendor_stmt)
        vendor = vendor_res.scalars().first()
        if not vendor:
            raise AppException(status_code=404, message="Target vendor profile record not found.")

        # 2. Extract operational event counts from our stream logs
        req_count = await self._get_event_count_by_vendor(vendor.id, BusinessEventType.REQUIREMENT_OPENED)
        sub_count = await self._get_event_count_by_vendor(vendor.id, BusinessEventType.SUBMISSION_CREATED)
        int_count = await self._get_event_count_by_vendor(vendor.id, BusinessEventType.INTERVIEW_SCHEDULED)
        plc_count = await self._get_event_count_by_vendor(vendor.id, BusinessEventType.PLACEMENT_CREATED)

        # 3. Assemble the conversion pipeline funnel metrics
        funnel_stages = [
            AccountFunnelStage(stage_name="Requirements", count=req_count, conversion_rate=100.0),
            AccountFunnelStage(
                stage_name="Submissions", 
                count=sub_count, 
                conversion_rate=round((sub_count / req_count * 100), 2) if req_count > 0 else 0.0
            ),
            AccountFunnelStage(
                stage_name="Interviews", 
                count=int_count, 
                conversion_rate=round((int_count / sub_count * 100), 2) if sub_count > 0 else 0.0
            ),
            AccountFunnelStage(
                stage_name="Placements", 
                count=plc_count, 
                conversion_rate=round((plc_count / int_count * 100), 2) if int_count > 0 else 0.0
            )
        ]

        # 4. Calculate relationship health scores algorithmically
        health_assessment = self._calculate_account_health(sub_count, plc_count)

        return VendorAnalyticsSummaryResponse(
            vendor_public_id=vendor.public_id,
            vendor_name=vendor.name,
            funnel=funnel_stages,
            health=health_assessment,
            velocity=AccountResponseTimeMetrics(
                avg_days_req_to_submission=2.4,  # Defaults until timeline metrics engine goes async
                avg_days_submission_to_interview=4.1,
                avg_days_interview_to_feedback=1.8
            )
        )

    async def _get_event_count_by_vendor(self, vendor_id: int, event_type: BusinessEventType) -> int:
        """Helper to safely query transaction event blocks without lock contention."""
        stmt = (
            select(func.count(BusinessEvent.id))
            .where(
                BusinessEvent.event_type == event_type.value,
                BusinessEvent.aggregate_type == "VENDOR",
                BusinessEvent.aggregate_id == vendor_id
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar() or 0

    def _calculate_account_health(self, submission_count: int, placement_count: int) -> RelationshipHealthDTO:
        """Evaluates data trends to score account stability and operational depth."""
        factors = []
        score = 50  # Baseline target value configuration

        if submission_count > 15:
            score += 20
            factors.append("High submission velocity reinforces active partner pipeline traction.")
        else:
            score -= 10
            factors.append("Low transaction volume indicates potential account stagnation.")

        if placement_count > 0:
            score += 30
            factors.append("Proven placement history confirms strong requirements alignment.")
        else:
            score -= 15
            factors.append("Zero placement conversions within the tracking timeframe increases risk.")

        # Clamp calculations within strict 0-100 limits bounds
        final_score = max(0, min(score, 100))
        
        status = "STRATEGIC" if final_score >= 80 else "ACTIVE" if final_score >= 50 else "AT_RISK"
        
        return RelationshipHealthDTO(
            health_score=final_score,
            status_label=status,
            contributing_factors=factors
        )