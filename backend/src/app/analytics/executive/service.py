from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.service import MetricsEngineService
from app.analytics.models import BusinessEvent
from app.analytics.enums import BusinessEventType
from app.auth.enums import Role
from app.models.user import User
from app.consultants.models import Consultant
from app.consultants.enums import AvailabilityStatus, MarketingStatus
from app.requirements.models import Requirement
from app.requirements.enums import RequirementStatus
from app.analytics.executive.schemas import (
    ExecutiveDashboardResponse,
    ExecutiveSummaryDTO,
    BenchHealthDTO,
    RecruiterPerformanceSummaryDTO,
    ForecastIndicatorsDTO,
)


class ExecutiveDashboardService:
    """
    High-level read model composition facade aggregating organization KPIs.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.metrics_service = MetricsEngineService(db)

    async def build_executive_dashboard(
        self,
    ) -> ExecutiveDashboardResponse:
        """Assembles leadership reporting projections."""

        # ------------------------------------------------------------------
        # 1. Core structural inventory counts
        # ------------------------------------------------------------------

        total_con = (
            await self.db.execute(
                select(func.count(Consultant.id))
            )
        ).scalar() or 0

        avail_con = (
            await self.db.execute(
                select(func.count(Consultant.id)).where(
                    Consultant.availability_status
                    == AvailabilityStatus.AVAILABLE_NOW
                )
            )
        ).scalar() or 0

        active_req = (
            await self.db.execute(
                select(func.count(Requirement.id)).where(
                    Requirement.status == RequirementStatus.OPEN
                )
            )
        ).scalar() or 0

        # ------------------------------------------------------------------
        # 2. Business event counters
        # ------------------------------------------------------------------

        sub_count = (
            await self.db.execute(
                select(func.count(BusinessEvent.id)).where(
                    BusinessEvent.event_type
                    == BusinessEventType.SUBMISSION_CREATED.value
                )
            )
        ).scalar() or 0

        plc_count = (
            await self.db.execute(
                select(func.count(BusinessEvent.id)).where(
                    BusinessEvent.event_type
                    == BusinessEventType.PLACEMENT_CREATED.value
                )
            )
        ).scalar() or 0

        summary_widget = ExecutiveSummaryDTO(
            total_consultants=total_con,
            available_consultants=avail_con,
            active_requirements=active_req,
            active_submissions=sub_count,
            placements_this_month=plc_count,
        )

        # ------------------------------------------------------------------
        # 3. Bench health
        # ------------------------------------------------------------------

        marketing_active = (
            await self.db.execute(
                select(func.count(Consultant.id)).where(
                    Consultant.marketing_status
                    == MarketingStatus.MARKETING_ACTIVE
                )
            )
        ).scalar() or 0

        placed_active = (
            await self.db.execute(
                select(func.count(Consultant.id)).where(
                    Consultant.marketing_status
                    == MarketingStatus.PLACED
                )
            )
        ).scalar() or 0

        bench_widget = BenchHealthDTO(
            available=avail_con,
            marketing_active=marketing_active,
            placed=placed_active,
            idle_greater_30_days=max(
                0,
                avail_con - marketing_active,
            ),
        )

        # ------------------------------------------------------------------
        # 4. Recruiter performance
        # ------------------------------------------------------------------

        recruiter_result = await self.db.execute(
            select(User)
            .where(
                User.role == Role.BENCH_SALES_RECRUITER
            )
            .order_by(User.first_name, User.last_name)
        )

        recruiters = recruiter_result.scalars().all()

        recruiter_performance = []

        for recruiter in recruiters:
            submissions_result = await self.db.execute(
                select(func.count(BusinessEvent.id)).where(
                    BusinessEvent.event_type
                    == BusinessEventType.SUBMISSION_CREATED.value,
                    BusinessEvent.actor_id == recruiter.id,
                )
            )

            submissions_count = submissions_result.scalar() or 0

            placements_result = await self.db.execute(
                select(func.count(BusinessEvent.id)).where(
                    BusinessEvent.event_type
                    == BusinessEventType.PLACEMENT_CREATED.value,
                    BusinessEvent.actor_id == recruiter.id,
                )
            )

            placements_count = placements_result.scalar() or 0

            conversion_rate = 0.0

            if submissions_count > 0:
                conversion_rate = round(
                    (placements_count / submissions_count) * 100,
                    2,
                )

            recruiter_performance.append(
                RecruiterPerformanceSummaryDTO(
                    recruiter_name=(
                        f"{recruiter.first_name} "
                        f"{recruiter.last_name}"
                    ).strip(),
                    submissions_count=submissions_count,
                    placements_count=placements_count,
                    conversion_rate=conversion_rate,
                )
            )

        # ------------------------------------------------------------------
        # 5. Forecast indicators
        # ------------------------------------------------------------------

        forecast_widget = ForecastIndicatorsDTO(
            expected_placements_this_month=plc_count + 1,
            pipeline_growth_velocity=(
                "STABLE"
                if sub_count < 100
                else "ACCELERATING"
            ),
        )

        # ------------------------------------------------------------------
        # 6. Final executive dashboard response
        # ------------------------------------------------------------------

        return ExecutiveDashboardResponse(
            summary=summary_widget,
            bench_health=bench_widget,
            recruiter_performance=recruiter_performance,
            forecast=forecast_widget,
        )