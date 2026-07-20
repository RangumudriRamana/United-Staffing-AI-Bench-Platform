from uuid import UUID
from sqlalchemy import select, exists, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.vendors.models import Client
from app.vendors.enums import ClientStatus
from app.shared.schemas import PaginationParams, SortParams
from app.shared.query_builder import paginate_repository_query

class ClientSearchCriteria(BaseModel):
    vendor_id: int | None = None
    status: ClientStatus | None = None
    industry: str | None = None
    preferred_only: bool = False
    search_text: str | None = None


class ClientRepository:
    """Handles pure metadata query isolation structures targeting client entities."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    def create(self, **kwargs) -> Client:
        new_client = Client(**kwargs)
        self.db.add(new_client)
        return new_client

    async def get_by_public_id(self, public_id: UUID) -> Client | None:
        stmt = select(Client).where(Client.public_id == public_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def exists_duplicate_under_vendor(self, vendor_id: int, name: str) -> bool:
        stmt = select(exists().where(
            Client.vendor_id == vendor_id,
            Client.name.ilike(name.strip())
        ))
        result = await self.db.execute(stmt)
        return result.scalar() or False

    async def list_clients_paginated(
        self,
        criteria: ClientSearchCriteria,
        pagination: PaginationParams,
        sort: SortParams
    ) -> tuple[list[Client], any]:
        """Assembles composable pipeline filter chains matching our data patterns."""
        query = select(Client)

        if criteria.vendor_id is not None:
            query = query.where(Client.vendor_id == criteria.vendor_id)
        if criteria.status:
            query = query.where(Client.status == criteria.status)
        if criteria.industry:
            query = query.where(Client.industry.ilike(f"%{criteria.industry}%"))
        if criteria.preferred_only:
            query = query.where(Client.preferred == True)

        if criteria.search_text:
            token = f"%{criteria.search_text}%"
            query = query.where(
                or_(
                    Client.name.ilike(token),
                    Client.display_name.ilike(token),
                    Client.industry.ilike(token)
                )
            )

        return await paginate_repository_query(
            db=self.db,
            query=query,
            model=Client,
            pagination_params=pagination,
            sort_params=sort,
            filter_params=None
        )