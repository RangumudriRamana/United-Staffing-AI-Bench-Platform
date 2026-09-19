from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.requirements.models import Requirement
from app.requirements.schemas import RequirementSearchCriteria
from app.requirements.search import build_requirement_search_pipeline
from app.shared.schemas import PaginationParams, SortParams
from app.shared.query_builder import paginate_repository_query


class RequirementRepository:
    """Orchestrates low-level database operations and multi-tier loading architectures."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def create(self, **kwargs) -> Requirement:
        new_req = Requirement(**kwargs)
        self.db.add(new_req)
        return new_req

    async def get_by_public_id(
        self,
        public_id: UUID,
        eager_load_details: bool = False,
    ) -> Requirement | None:
        """Loads requirement data with optional eager loading for detail screens."""

        stmt = select(Requirement).where(
            Requirement.public_id == public_id
        )

        if eager_load_details:
            stmt = stmt.options(
                selectinload(Requirement.technologies),
                selectinload(Requirement.documents),
                selectinload(Requirement.history),
            )

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_requirements_paginated(
        self,
        criteria: RequirementSearchCriteria,
        pagination: PaginationParams,
        sort: SortParams,
    ) -> tuple[list[Requirement], any]:
        """Loads requirement list records together with their response relationships."""

        base_query = build_requirement_search_pipeline(criteria)

        # Prevent async lazy-loading / MissingGreenlet during
        # FastAPI response serialization.
        base_query = base_query.options(
            selectinload(Requirement.technologies),
            selectinload(Requirement.history),
        )

        return await paginate_repository_query(
            db=self.db,
            query=base_query,
            model=Requirement,
            pagination_params=pagination,
            sort_params=sort,
            filter_params=None,
        )