from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.models import BusinessEvent
from app.analytics.enums import BusinessEventType
from app.analytics.schemas import RecruiterKPIMetrics


class MetricsEngineService:
    """Orchestrates event log persistence updates and compiles derived analytics equations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_domain_event(
        self,
        event_type: BusinessEventType,
        aggregate_type: str,
        aggregate_id: int,
        actor_id: int,
        metadata: dict | None = None,
    ) -> BusinessEvent:
        """Appends a fresh immutable logging snapshot block to the event stream framework."""
        new_event = BusinessEvent(
            event_type=event_type.value,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            actor_id=actor_id,
            occurred_at=datetime.utcnow(),
            metadata_json=metadata,
        )

        self.db.add(new_event)
        await self.db.flush()

        return new_event

    async def compute_recruiter_kpis(
        self,
        recruiter_id: int,
    ) -> RecruiterKPIMetrics:
        """
        Gathers log counts across the event stream ledger to compute operational conversion
        rates without putting heavy locks on main workflow transaction tables.
        """

        # 1. Total submission event tracking counters
        sub_stmt = select(func.count(BusinessEvent.id)).where(
            BusinessEvent.event_type
            == BusinessEventType.SUBMISSION_CREATED.value,
            BusinessEvent.actor_id == recruiter_id,
        )

        sub_res = await self.db.execute(sub_stmt)
        submissions_count = sub_res.scalar() or 0

        # 2. Total active placement counters
        place_stmt = select(func.count(BusinessEvent.id)).where(
            BusinessEvent.event_type
            == BusinessEventType.PLACEMENT_CREATED.value,
            BusinessEvent.actor_id == recruiter_id,
        )

        place_res = await self.db.execute(place_stmt)
        placements_count = place_res.scalar() or 0

        # 3. Calculate absolute placement conversion percentage
        conversion_rate = 0.0

        if submissions_count > 0:
            conversion_rate = round(
                (placements_count / submissions_count) * 100,
                2,
            )

        return RecruiterKPIMetrics(
            recruiter_id=recruiter_id,
            total_submissions=submissions_count,
            placements_secured=placements_count,
            placement_conversion_rate=conversion_rate,
        )