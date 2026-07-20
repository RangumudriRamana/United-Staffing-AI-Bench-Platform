from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.requirements.models import Requirement
from app.models.consultant import Consultant
from app.matching.schemas import MatchPolicyWeights, RankedConsultantResponse
from app.matching.scoring import PureScoringEngine

class MatchingService:
    """Coordinates aggregate data preloading and drives execution across our pure scoring pipelines."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_ranked_matches_for_requirement(
        self, 
        requirement_public_id: UUID, 
        policy: MatchPolicyWeights | None = None
    ) -> list[RankedConsultantResponse]:
        """Loads requirement criteria parameters, maps potential matches, and sorts by score ranking."""
        if policy is None:
            policy = MatchPolicyWeights()

        # 1. Eagerly preload requirement constraint matrices
        req_stmt = select(Requirement).where(Requirement.public_id == requirement_public_id).options(
            selectinload(Requirement.technologies)
        )
        req_res = await self.db.execute(req_stmt)
        requirement = req_res.scalars().first()
        
        if not requirement:
            raise AppException(status_code=404, message="Target job requirement profile not found.")

        # 2. Gather active candidate lists alongside matching skills catalogs
        con_stmt = select(Consultant).options(
            selectinload(Consultant.technologies)
        )
        con_res = await self.db.execute(con_stmt)
        all_consultants = con_res.scalars().all()

        ranked_candidates = []

        # 3. Stream data blocks through stateless pipeline steps
        for consultant in all_consultants:
            match_dto = PureScoringEngine.calculate_match(consultant, requirement, policy)
            if match_dto:
                ranked_candidates.append(match_dto)

        # 4. Separate Ranking: Sort final output collection descending by absolute score value metrics
        ranked_candidates.sort(key=lambda x: x.scores.overall_score, reverse=True)
        
        return ranked_candidates