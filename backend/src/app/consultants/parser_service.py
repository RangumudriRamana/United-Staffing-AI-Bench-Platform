import re
from typing import Literal
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.technology_alias import TechnologyAlias
from app.models.consultant_technology import ConsultantTechnology
from app.consultants.enums import ProficiencyLevel


class ExtractedSkillSignal(BaseModel):
    """Implementation-agnostic payload carrying a single detected skill attribute."""
    raw_term: str
    inferred_years: int = Field(default=1, ge=0)


class ParsedResumeOutput(BaseModel):
    """Canonical transport schema representing implementation-agnostic parsed results."""
    skills: list[ExtractedSkillSignal] = Field(default_factory=list)
    inferred_title: str | None = None
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)


class ResumeParsingPipeline:
    """
    Orchestrates deterministic, multi-stage data processing pipelines.
    Extracts, normalizes, resolves aliases, and syncs data to profiles.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    def normalize_extracted_text(self, text: str) -> str:
        """Stage 2: Cleans structural white spaces and removes punctuation distortion flags."""
        if not text:
            return ""
        # Lowercase, clean repetitive spacings, and strip edge components
        cleaned = text.lower().strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    async def resolve_canonical_technology(self, raw_token: str) -> int | None:
        """Stage 3: Resolves synonymous keywords against the master alias database registry."""
        search_token = raw_token.strip().lower()
        
        # Query our structural alias catalog table staged in Package 2.0.2
        stmt = select(TechnologyAlias.technology_id).where(
            TechnologyAlias.alias.ilike(search_token)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def synchronize_consultant_profile(
        self, 
        consultant_id: int, 
        parsed_data: ParsedResumeOutput
    ) -> list[int]:
        """Stage 5: Idempotently merges newly extracted data vectors into the profile tables."""
        synced_tech_ids = []

        for skill_signal in parsed_data.skills:
            # Look up the canonical ID through our alias dictionary framework
            canonical_tech_id = await self.resolve_canonical_technology(skill_signal.raw_term)
            
            if not canonical_tech_id:
                # Skip or route unknown words to administrative audit boards
                continue

            # Check if this consultant profile already records this technical asset link
            check_stmt = select(ConsultantTechnology).where(
                ConsultantTechnology.consultant_id == consultant_id,
                ConsultantTechnology.technology_id == canonical_tech_id
            )
            check_res = await self.db.execute(check_stmt)
            existing_link = check_res.scalars().first()

            if existing_link:
                # Update experience metrics if the parsed evaluation displays higher counts
                if skill_signal.inferred_years > existing_link.years_of_experience:
                    existing_link.years_of_experience = skill_signal.inferred_years
                synced_tech_ids.append(canonical_tech_id)
            else:
                # Instantiate a fresh, clean row mapping relation record
                new_skill_map = ConsultantTechnology(
                    consultant_id=consultant_id,
                    technology_id=canonical_tech_id,
                    years_of_experience=max(1, skill_signal.inferred_years),
                    proficiency_level=ProficiencyLevel.INTERMEDIATE,
                    currently_using=True,
                    verified=False  # Stays false until manual recruiter audit verification
                )
                self.db.add(new_skill_map)
                synced_tech_ids.append(canonical_tech_id)

        try:
            await self.db.commit()
            return synced_tech_ids
        except Exception as err:
            await self.db.rollback()
            raise err