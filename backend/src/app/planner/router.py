from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, RequireRole
from app.auth.enums import UserRole
from app.database.base import get_db_session
from app.planner.schemas import PlannerResponse
from app.planner.service import PlannerService

router = APIRouter(
    prefix="/planner",
    tags=["Daily Planner"],
)


async def get_planner_service(
    db: AsyncSession = Depends(get_db_session),
) -> PlannerService:
    return PlannerService(db)


@router.get(
    "/daily",
    response_model=PlannerResponse,
)
async def get_daily_planner(
    planner_date: date | None = Query(
        default=None,
        description="Planner date. Defaults to today.",
    ),
    current_user: Any = Depends(get_current_user),
    service: PlannerService = Depends(get_planner_service),
    _role: Any = Depends(
        RequireRole(
            [
                UserRole.ADMIN,
                UserRole.MANAGER,
                UserRole.RECRUITER,
            ]
        )
    ),
) -> Any:
    target_date = planner_date or date.today()

    return await service.get_daily_plan(
        user_id=current_user.id,
        planner_date=target_date,
    )