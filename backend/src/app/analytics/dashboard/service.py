from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from app.analytics.service import MetricsEngineService
from app.analytics.models import BusinessEvent
from app.analytics.enums import BusinessEventType
from app.analytics.dashboard.schemas import RecruiterDashboardResponse, FollowUpItem, DashboardTimelineEvent

class RecruiterDashboardService:
    """
    Assembles decoupled analytical records and projects them into actionable workspace elements.
    Completely isolated from direct raw database mutations.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.metrics_service = MetricsEngineService(db)

    async def build_recruiter_dashboard(self, recruiter_id: int) -> RecruiterDashboardResponse:
        """Composition layer fetching distinct widgets concurrently to construct the primary panel view."""
        # 1. Fetch core KPI counters through our performance service engine
        kpi_summary = await self.metrics_service.compute_recruiter_kpis(recruiter_id)

        # 2. Gather chronological trace projections
        timeline_events = await self.get_recent_activity_timeline(recruiter_id)

        # 3. Compile predictive follow-up queues
        followup_queue = await self.generate_actionable_followups(recruiter_id)

        return RecruiterDashboardResponse(
            summary=kpi_summary,
            followups=followup_queue,
            timeline=timeline_events
        )

    async def get_recent_activity_timeline(self, recruiter_id: int, limit: int = 10) -> list[DashboardTimelineEvent]:
        """Queries append-only ledger entries directly to construct a localized log timeline."""
        stmt = (
            select(BusinessEvent)
            .where(BusinessEvent.actor_id == recruiter_id)
            .order_by(desc(BusinessEvent.occurred_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        events = res.scalars().all()

        return [
            DashboardTimelineEvent(
                event_type=evt.event_type,
                summary=f"Event type registration recorded automatically for context ID: {evt.aggregate_id}",
                occurred_at=evt.occurred_at,
                actor_id=evt.actor_id
            )
            for evt in events
        ]

    async def generate_actionable_followups(self, recruiter_id: int) -> list[FollowUpItem]:
        """
        Scans operational timestamps from log files to alert users about
        stalled pipeline submissions or candidate gaps.
        """
        items = []
        now = datetime.now(timezone.utc)

        # Rule Target 1: Intercept submissions that have stalled in review for over 5 days
        stalled_stmt = (
            select(BusinessEvent)
            .where(
                BusinessEvent.event_type == BusinessEventType.SUBMISSION_CREATED.value,
                BusinessEvent.actor_id == recruiter_id,
                BusinessEvent.occurred_at <= now - timedelta(days=5)
            )
            .limit(5)
        )
        stalled_res = await self.db.execute(stalled_stmt)
        for old_sub in stalled_res.scalars().all():
            items.append(
                FollowUpItem(
                    task_type="STALLED_SUBMISSION",
                    description=f"Submission tracking index {old_sub.aggregate_id} has spent over 5 days awaiting client feedback review.",
                    severity="HIGH",
                    target_public_id=str(old_sub.aggregate_id)
                )
            )

        # Fallback check items if queue runs empty
        if not items:
            items.append(
                FollowUpItem(
                    task_type="ROUTINE_CHECK",
                    description="All tracked opportunities show active movement. Review new incoming requirements for potential matches.",
                    severity="LOW"
                )
            )

        return items