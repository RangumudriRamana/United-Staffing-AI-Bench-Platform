from typing import Any
from uuid import UUID
from sqlalchemy import select, exists, Select
from sqlalchemy.orm import joinedload

from app.shared.repository import BaseRepository
from app.consultants.models import Consultant
from app.shared.schemas import PaginationParams, SortParams, PaginationMetadata
from app.shared.query_builder import paginate_repository_query


class ConsultantFilters:
    """Implements structural domain filter rules matching Package 1.7 Protocol contracts."""
    def __init__(self, visa_status: str | None = None, search: str | None = None):
        self.visa_status = visa_status
        self.search = search

    def apply(self, query: Select, model: type[Consultant]) -> Select:
        # Enforce structural filter logic to hide soft-deleted profiles by default
        query = query.where(model.deleted_at == None)
        
        if self.visa_status:
            query = query.where(model.visa_status == self.visa_status)
        if self.search:
            query = query.where(
                model.first_name.ilike(f"%{self.search}%") | 
                model.last_name.ilike(f"%{self.search}%") |
                model.email.ilike(f"%{self.search}%")
            )
        return query


class ConsultantRepository(BaseRepository[Consultant]):
    """
    Handles optimized database persistence operations for the Consultant aggregate root.
    Strictly isolated from business rules, HTTP states, and incoming DTO handling layers.
    """

    @property
    def model_cls(self) -> type[Consultant]:
        return Consultant

    # --- 1. Identity Lookups ---

    async def get_by_public_id(self, public_id: UUID, eager_load_recruiter: bool = True) -> Consultant | None:
        """Fetches a single active consultant record while cleanly preventing N+1 relationship query lags."""
        query = select(Consultant).where(
            Consultant.public_id == public_id,
            Consultant.deleted_at == None
        )
        
        if eager_load_recruiter:
            query = query.options(joinedload(Consultant.recruiter))
            
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Consultant | None:
        """Looks up a consultant by their unique email address sequence."""
        query = select(Consultant).where(
            Consultant.email == email.strip().lower(),
            Consultant.deleted_at == None
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def exists_by_email(self, email: str) -> bool:
        """Highly optimized boolean check to instantly detect existing email identities."""
        query = select(
            exists().where(
                Consultant.email == email.strip().lower(),
                Consultant.deleted_at == None
            )
        )
        result = await self.db.execute(query)
        return bool(result.scalar())

    # --- 2. Collection Queries ---

    async def list_paginated(
        self,
        pagination_params: PaginationParams,
        sort_params: SortParams,
        filter_params: ConsultantFilters | None = None
    ) -> tuple[list[Consultant], PaginationMetadata]:
        """Leverages our shared framework to extract data batches and securely sort collections."""
        base_query = select(Consultant).where(Consultant.deleted_at == None)
        
        return await paginate_repository_query(
            db=self.db,
            query=base_query,
            model=Consultant,
            pagination_params=pagination_params,
            sort_params=sort_params,
            filter_params=filter_params
        )