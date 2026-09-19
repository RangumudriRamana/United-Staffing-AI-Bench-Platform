from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai_matching.models import AIMatchHistory
from app.consultants.models import Consultant
from app.requirements.models import Requirement


class AIMatchingRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_consultant(
        self,
        consultant_id: UUID,
    ) -> Consultant | None:

        result = await self.db.execute(
            select(Consultant)
            .options(
                selectinload(Consultant.technologies)
            )
            .where(
                Consultant.public_id == consultant_id
            )
        )

        return result.scalar_one_or_none()

    async def get_requirement(
        self,
        requirement_id: UUID,
    ) -> Requirement | None:

        result = await self.db.execute(
            select(Requirement)
            .options(
                selectinload(Requirement.technologies)
            )
            .where(
                Requirement.public_id == requirement_id
            )
        )

        return result.scalar_one_or_none()

    async def get_all_consultants(
        self,
    ) -> list[Consultant]:

        result = await self.db.execute(
            select(Consultant)
            .options(
                selectinload(Consultant.technologies)
            )
        )

        return list(
            result.scalars().unique().all()
        )

    async def create_match_history(
        self,
        consultant_id: int,
        requirement_id: int,
        match_score: float,
        recommendation: str,
    ) -> AIMatchHistory:

        history = AIMatchHistory(
            consultant_id=consultant_id,
            requirement_id=requirement_id,
            match_score=match_score,
            recommendation=recommendation,
        )

        self.db.add(history)

        await self.db.flush()

        return history

    async def get_match_history(
        self,
    ) -> list[AIMatchHistory]:

        result = await self.db.execute(
            select(AIMatchHistory)
            .options(
                selectinload(AIMatchHistory.consultant),
                selectinload(AIMatchHistory.requirement),
            )
            .order_by(
                AIMatchHistory.matched_at.desc()
            )
        )

        return list(
            result.scalars().all()
        )