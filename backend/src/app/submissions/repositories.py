from uuid import UUID
from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.submissions.models import Submission
from app.submissions.schemas import SubmissionSearchCriteria
from app.submissions.search import build_submission_search_pipeline
from app.shared.schemas import PaginationParams, SortParams, PagedResponse
from app.shared.query_builder import paginate_repository_query

class SubmissionRepository:
    """Handles low-level persistence operations, duplicate validation looks, and aggregate loading."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    def create(self, **kwargs) -> Submission:
        """Instantiates a fresh uncommitted database entity model row block."""
        new_submission = Submission(**kwargs)
        self.db.add(new_submission)
        return new_submission

    async def get_by_public_id(self, public_id: UUID, eager_load_details: bool = False) -> Submission | None:
        """
        Retrieves a target profile. Implements strategic split aggregate loading paths
        to avoid heavy vertical database traffic over list summaries.
        """
        stmt = select(Submission).where(Submission.public_id == public_id, Submission.deleted_at == None)
        
        if eager_load_details:
            # Complete Detail View Loading Strategy: Fetch deep child tables via unified batch selectinload queries
            stmt = stmt.options(
                selectinload(Submission.history),
                selectinload(Submission.interviews),
                selectinload(Submission.feedback),
                selectinload(Submission.offers),
                selectinload(Submission.placements)
            )
            
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def exists_active_submission(self, consultant_id: int, client_name: str, job_title: str) -> bool:
        """Helper to safely check duplicate submission attempts across active candidate logs."""
        stmt = select(exists().where(
            Submission.consultant_id == consultant_id,
            Submission.client_name.ilike(client_name.strip()),
            Submission.job_title.ilike(job_title.strip()),
            Submission.deleted_at == None
        ))
        result = await self.db.execute(stmt)
        return result.scalar() or False

    async def list_submissions_paginated(
        self,
        criteria: SubmissionSearchCriteria,
        pagination: PaginationParams,
        sort: SortParams
    ) -> tuple[list[Submission], any]:
        """Leverages the shared platform query framework to deliver optimized paginated collections."""
        base_query = build_submission_search_pipeline(criteria)
        
        return await paginate_repository_query(
            db=self.db,
            query=base_query,
            model=Submission,
            pagination_params=pagination,
            sort_params=sort,
            filter_params=None  # Filters are already injected via our custom pipeline execution step
        )