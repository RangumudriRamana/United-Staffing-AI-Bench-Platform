from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_matching.repository import AIMatchingRepository
from app.ai_matching.schemas import (
    BatchMatchRequest,
    BatchMatchResponse,
    BatchMatchItem,
    MatchHistoryItem,
    MatchHistoryResponse,
)
from app.ai_matching.utils import (
    calculate_experience_score,
    calculate_final_match_score,
    calculate_location_score,
    calculate_skill_score,
    extract_consultant_technology_names,
    extract_requirement_technology_names,
)


class AIMatchingService:

    def __init__(self, db: AsyncSession):
        self.repository = AIMatchingRepository(db)

    async def match(
        self,
        request: BatchMatchRequest,
    ) -> BatchMatchResponse:

        return await self.batch_match(request)

    async def batch_match(
        self,
        request: BatchMatchRequest,
    ) -> BatchMatchResponse:

        requirement = await self.repository.get_requirement(
            request.requirement_id
        )

        if requirement is None:
            raise ValueError("Requirement not found")

        consultants = await self.repository.get_all_consultants()

        requirement_skills = extract_requirement_technology_names(
            requirement
        )

        matches: list[BatchMatchItem] = []

        for consultant in consultants:

            consultant_skills = extract_consultant_technology_names(
                consultant
            )

            skill_score, matched, missing = calculate_skill_score(
                consultant_skills,
                requirement_skills,
            )

            experience_score = calculate_experience_score(
                consultant.total_experience_years,
                requirement.experience_min,
            )

            visa_score = 100

            location_score = calculate_location_score(
                consultant.current_location,
                requirement.location,
            )

            final_score = calculate_final_match_score(
                skill_score=skill_score,
                experience_score=experience_score,
                location_score=location_score,
                visa_score=visa_score,
            )

            recommendation = (
                "Excellent Match"
                if final_score >= 85
                else "Good Match"
                if final_score >= 70
                else "Average Match"
                if final_score >= 50
                else "Poor Match"
            )

            matches.append(
                BatchMatchItem(
                    consultant_id=consultant.public_id,
                    consultant_name=(
                        f"{consultant.first_name} "
                        f"{consultant.last_name}"
                    ),
                    score=final_score,
                    recommendation=recommendation,
                )
            )

            await self.repository.create_match_history(
                consultant_id=consultant.id,
                requirement_id=requirement.id,
                match_score=final_score,
                recommendation=recommendation,
            )

        matches.sort(
            key=lambda match: match.score,
            reverse=True,
        )

        await self.repository.db.commit()

        return BatchMatchResponse(
            matches=matches
        )

    async def get_history(
        self,
    ) -> MatchHistoryResponse:

        history_records = (
            await self.repository.get_match_history()
        )

        history = [
            MatchHistoryItem(
                consultant_id=record.consultant.public_id,
                consultant_name=(
                    f"{record.consultant.first_name} "
                    f"{record.consultant.last_name}"
                ),
                requirement_id=record.requirement.public_id,
                requirement_name=(
                    f"{record.requirement.job_title}"
                    + (
                        f" — {record.requirement.job_code}"
                        if record.requirement.job_code
                        else ""
                    )
                ),
                match_score=record.match_score,
                recommendation=record.recommendation,
                matched_at=record.matched_at,
            )
            for record in history_records
        ]

        return MatchHistoryResponse(
            history=history
        )