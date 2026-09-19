from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, or_, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from app.shared.query_builder import paginate_repository_query
from app.shared.schemas import PaginationParams, SortParams
from app.vendors.models import Client, Vendor
from app.vendors.schemas import ClientFilters, VendorFilters


class VendorRepository:
    """
    Handles all persistence operations for the Vendor aggregate root.

    Responsibilities:
    - CRUD persistence
    - Duplicate detection
    - Search pipelines
    - Eager-loading related entities
    - Pagination orchestration

    This repository intentionally contains no business rules,
    transaction handling, or validation logic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(self, **kwargs) -> Vendor:
        vendor = Vendor(**kwargs)
        self.db.add(vendor)
        return vendor

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    async def get_by_public_id(
        self,
        public_id: UUID,
        eager_load_contacts: bool = False,
    ) -> Vendor | None:
        """
        Loads a vendor by its public identifier.

        Contact collections are only loaded when explicitly requested.
        """

        stmt = select(Vendor).where(
            Vendor.public_id == public_id
        )

        if eager_load_contacts:
            stmt = stmt.options(
                selectinload(Vendor.contacts),
                selectinload(Vendor.clients),
            )

        result = await self.db.execute(stmt)
        return result.scalars().first()


    async def exists_duplicate_name(
        self,
        name: str,
        exclude_id: int | None = None,
    ) -> bool:
        """
        Determines whether another vendor already exists with the same
        normalized business name.

        exclude_id is primarily used during update operations to ignore
        the current entity.
        """

        normalized = name.strip()

        conditions = [
            Vendor.name.ilike(normalized),
        ]

        if exclude_id is not None:
            conditions.append(Vendor.id != exclude_id)

        stmt = select(
            exists().where(and_(*conditions))
        )

        result = await self.db.execute(stmt)
        return bool(result.scalar())

    async def list_vendors_paginated(
        self,
        filters: VendorFilters,
        pagination: PaginationParams,
        sort: SortParams,
    ):
        """
        Builds vendor search queries before delegating
        pagination to the shared query framework.
        """

        query = (
        select(Vendor)
        .options(
            selectinload(Vendor.contacts),
            selectinload(Vendor.clients),
        )
    )

        if filters.vendor_type is not None:
            query = query.where(Vendor.vendor_type == filters.vendor_type)

        if filters.tier is not None:
            query = query.where(Vendor.tier == filters.tier)

        if filters.status is not None:
            query = query.where(Vendor.status == filters.status)

        if filters.preferred_only:
            query = query.where(Vendor.preferred.is_(True))

        if filters.search_text:
            search = filters.search_text.strip()
            token = f"%{search}%"

            query = query.where(
                or_(
                    Vendor.name.ilike(token),
                    Vendor.website.ilike(token),
                )
            )

        return await paginate_repository_query(
            db=self.db,
            query=query,
            model=Vendor,
            pagination_params=pagination,
            sort_params=sort,
            filter_params=None,
        )


# ======================================================================
# Client Repository
# ======================================================================


class ClientRepository:
    """
    Handles persistence operations for Client entities.

    Business rules remain inside VendorService.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(self, **kwargs) -> Client:
        client = Client(**kwargs)
        self.db.add(client)
        return client

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    async def get_by_public_id(
        self,
        public_id: UUID,
        eager_load_vendor: bool = False,
    ) -> Client | None:
        """
        Loads a client by its public identifier.

        Vendor relationship is loaded only when requested.
        """

        stmt = select(Client).where(
            Client.public_id == public_id
        )

        if eager_load_vendor:
            stmt = stmt.options(
                selectinload(Client.vendor)
            )

        result = await self.db.execute(stmt)
        return result.scalars().first()


    async def exists_duplicate_under_vendor(
        self,
        vendor_id: int,
        name: str,
        exclude_id: int | None = None,
    ) -> bool:
        """
        Prevent duplicate client names beneath the same vendor while allowing
        the current client to update its own record.
        """

        normalized = name.strip()

        conditions = [
            Client.vendor_id == vendor_id,
            Client.name.ilike(normalized),
        ]

        if exclude_id is not None:
            conditions.append(Client.id != exclude_id)

        stmt = select(
            exists().where(and_(*conditions))
        )

        result = await self.db.execute(stmt)
        return bool(result.scalar())

    async def list_clients_paginated(
        self,
        filters: ClientFilters,
        pagination: PaginationParams,
        sort: SortParams,
    ):
        """
        Executes client search pipelines before passing
        them into the shared pagination framework.
        """

        from sqlalchemy.orm import selectinload

        query = (
            select(Client)
            .options(
                selectinload(Client.vendor)
            )
        )

        if filters.vendor_public_id is not None:
            query = query.join(
                Vendor,
                Client.vendor_id == Vendor.id,
            ).where(
                Vendor.public_id == filters.vendor_public_id
            )

        if filters.status is not None:
            query = query.where(
                Client.status == filters.status
            )

        if filters.industry:
            query = query.where(
                Client.industry.ilike(
                    f"%{filters.industry.strip()}%"
                )
            )

        if filters.preferred_only:
            query = query.where(
                Client.preferred.is_(True)
            )

        if filters.search_text:
            search = filters.search_text.strip()
            token = f"%{search}%"

            query = query.where(
                or_(
                    Client.name.ilike(token),
                    Client.display_name.ilike(token),
                    Client.industry.ilike(token),
                    Client.website.ilike(token),
                    Client.primary_location.ilike(token),
                )
            )

        return await paginate_repository_query(
            db=self.db,
            query=query,
            model=Client,
            pagination_params=pagination,
            sort_params=sort,
            filter_params=None,
        )