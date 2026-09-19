from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.audit.service import AuditService

from app.audit.enums import AuditActionType
from app.audit.schemas import AuditRecordCreatePayload

from app.shared.schemas import (
    PaginationParams,
    SortParams,
    PaginationMetadata,
)

from app.vendors.models import (
    Vendor,
    VendorContact,
    Client,
)

from app.vendors.repositories import (
    VendorRepository,
    ClientRepository,
)

from app.vendors.schemas import (
    VendorCreateRequest,
    VendorUpdateRequest,
    VendorFilters,
    ClientCreateRequest,
    ClientUpdateRequest,
    ClientFilters,
)

from app.vendors.enums import (
    VendorStatus,
    ClientStatus,
)


class VendorService:
    """
    Application service responsible for orchestrating the Vendor aggregate.

    Responsibilities
    ----------------
    • Business validation
    • Duplicate protection
    • Input normalization
    • Transaction boundaries
    • Repository orchestration
    • Exception translation

    Persistence concerns intentionally remain inside repositories.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.vendor_repo = VendorRepository(db)
        self.client_repo = ClientRepository(db)
        self.audit_service = AuditService(db)

    # ==========================================================
    # Private Helper Methods
    # ==========================================================

    async def _get_client_or_raise(
        self,
        public_id: UUID,
        *,
        eager_load_vendor: bool = False,
    ) -> Client:
        """
        Retrieves a Client entity or raises a 404 if not found.
        """

        client = await self.client_repo.get_by_public_id(
            public_id=public_id,
            eager_load_vendor=eager_load_vendor,
        )

        if client is None:
            raise AppException(
                status_code=404,
                message="Client record not found.",
            )

        return client

    @staticmethod
    def _normalize_client_payload(data: dict) -> dict:
        """
        Applies consistent normalization to Client string fields.
        """

        if "name" in data:
            data["name"] = VendorService._normalize_name(data["name"])

        for field in (
            "display_name",
            "industry",
            "website",
            "primary_location",
            "notes",
        ):
            if field in data:
                data[field] = VendorService._normalize_optional(
                    data[field]
                )

        return data

    @staticmethod
    def _vendor_audit_snapshot(vendor: Vendor) -> dict:
        return {
            "public_id": str(vendor.public_id),
            "name": vendor.name,
            "vendor_type": vendor.vendor_type.value,
            "tier": vendor.tier.value,
            "status": vendor.status.value,
            "website": vendor.website,
            "preferred": vendor.preferred,
            "notes": vendor.notes,
        }
    def _client_audit_snapshot(
        self,
        client: Client,
    ) -> dict:
        return {
            "public_id": str(client.public_id),
            "vendor_id": client.vendor_id,
            "name": client.name,
            "status": client.status.value,
            "notes": client.notes,
        }

    @staticmethod
    def _normalize_name(value: str) -> str:
        """
        Normalize business names before persistence.

        Example:
            "  united staffing associates  "

        becomes

            "United Staffing Associates"
        """

        return " ".join(value.strip().split()).title()

    @staticmethod
    def _normalize_optional(value: str | None) -> str | None:
        """
        Normalize optional string fields.

        Empty strings are converted to None.
        """

        if value is None:
            return None

        cleaned = value.strip()

        return cleaned or None

    @staticmethod
    def _normalize_email(email: str) -> str:
        """
        Email addresses are stored in lowercase.
        """

        return email.strip().lower()

    async def _get_vendor_or_raise(
        self,
        public_id: UUID,
        *,
        eager_load_contacts: bool = False,
    ) -> Vendor:
        """
        Retrieve a Vendor aggregate or raise a 404.
        """

        vendor = await self.vendor_repo.get_by_public_id(
            public_id=public_id,
            eager_load_contacts=eager_load_contacts,
        )

        if vendor is None:
            raise AppException(
                status_code=404,
                message="Vendor record not found.",
            )

        return vendor

    async def _ensure_unique_vendor_name(
        self,
        name: str,
        *,
        exclude_id: int | None = None,
    ) -> None:
        """
        Enforce unique vendor names across the platform.
        """

        duplicate = await self.vendor_repo.exists_duplicate_name(
            name=name,
            exclude_id=exclude_id,
        )

        if duplicate:
            raise AppException(
                status_code=400,
                message="Vendor name already exists.",
            )

    @staticmethod
    def _apply_vendor_updates(
        vendor: Vendor,
        update_data: dict,
    ) -> None:
        """
        Apply partial updates to the Vendor entity.

        Audit fields are intentionally handled separately.
        """

        for field, value in update_data.items():
            setattr(vendor, field, value)

    # ==========================================================
    # Vendor CRUD Operations
    # ==========================================================

    async def create_vendor(
        self,
        payload: VendorCreateRequest,
        current_user_id: int,
    ) -> Vendor:
        """
        Creates a new Vendor aggregate together with any initial
        VendorContact records supplied during registration.

        Responsibilities
        ----------------
        • Normalize incoming values
        • Enforce duplicate protection
        • Populate audit fields
        • Create nested contacts
        • Commit as a single transaction
        """

        vendor_name = self._normalize_name(payload.name)

        await self._ensure_unique_vendor_name(vendor_name)

        vendor_data = payload.model_dump(exclude={"contacts"})

        vendor_data["name"] = vendor_name
        vendor_data["website"] = self._normalize_optional(
            vendor_data.get("website")
        )
        vendor_data["notes"] = self._normalize_optional(
            vendor_data.get("notes")
        )

        vendor_data["created_by"] = current_user_id

        try:
            vendor = self.vendor_repo.create(**vendor_data)

            #
            # Create initial vendor contacts
            #
            for contact_payload in payload.contacts:

                contact_data = contact_payload.model_dump()

                contact = VendorContact(
                    name=self._normalize_name(contact_data["name"]),
                    email=self._normalize_email(contact_data["email"]),
                    title=self._normalize_optional(
                        contact_data.get("title")
                    ),
                    phone=self._normalize_optional(
                        contact_data.get("phone")
                    ),
                    linkedin=self._normalize_optional(
                        contact_data.get("linkedin")
                    ),
                    timezone=contact_data.get("timezone", "EST"),
                    preferred_contact=contact_data.get(
                        "preferred_contact",
                        False,
                    ),
                    is_active=contact_data.get(
                        "is_active",
                        True,
                    ),
                )

                vendor.contacts.append(contact)

            #
            # Flush before commit so SQLAlchemy assigns identifiers
            #
            await self.db.flush()

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=current_user_id,
                    action_type=AuditActionType.CREATE,
                    source_context="VENDOR_SERVICE",
                    entity_type="VENDOR",
                    entity_public_id=str(vendor.public_id),
                    entity_version=1,
                    after_snapshot_json=self._vendor_audit_snapshot(vendor),
                    metadata_json={
                        "operation": "create_vendor",
                    },
                )
            )

            await self.db.commit()

            #
            # Reload aggregate with contacts
            #
            vendor = await self.vendor_repo.get_by_public_id(
                vendor.public_id,
                eager_load_contacts=True,
            )

            if vendor is None:
                raise AppException(
                    status_code=500,
                    message="Vendor was created but could not be reloaded.",
                )

            return vendor

        except AppException:
            await self.db.rollback()
            raise

        except Exception:
            await self.db.rollback()
            raise

    async def get_vendor(self, public_id: UUID) -> Vendor:
        """
        Retrieves a Vendor aggregate with all associated contacts.
        """

        return await self._get_vendor_or_raise(
            public_id=public_id,
            eager_load_contacts=True,
        )

    async def list_vendors(
        self,
        pagination: PaginationParams,
        sort: SortParams,
        filters: VendorFilters,
    ) -> tuple[list[Vendor], PaginationMetadata]:
        """
        Returns paginated vendor records using the shared pagination framework.
        """

        return await self.vendor_repo.list_vendors_paginated(
            filters=filters,
            pagination=pagination,
            sort=sort,
        )

    async def update_vendor(
        self,
        public_id: UUID,
        payload: VendorUpdateRequest,
        current_user_id: int,
    ) -> Vendor:
        """
        Updates vendor information while preserving aggregate integrity.
        """

        vendor = await self._get_vendor_or_raise(
            public_id=public_id,
            eager_load_contacts=True,
        )

        update_data = payload.model_dump(exclude_unset=True)

        #
        # Normalize mutable fields
        #
        if "name" in update_data:
            update_data["name"] = self._normalize_name(update_data["name"])

            if update_data["name"] != vendor.name:
                await self._ensure_unique_vendor_name(
                    update_data["name"],
                    exclude_id=vendor.id,
                )

        if "website" in update_data:
            update_data["website"] = self._normalize_optional(
                update_data["website"]
            )

        if "notes" in update_data:
            update_data["notes"] = self._normalize_optional(
                update_data["notes"]
            )

        before_snapshot = self._vendor_audit_snapshot(vendor)

        self._apply_vendor_updates(vendor, update_data)

        vendor.updated_by = current_user_id

        try:
            await self.db.flush()

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=current_user_id,
                    action_type=AuditActionType.UPDATE,
                    source_context="VENDOR_SERVICE",
                    entity_type="VENDOR",
                    entity_public_id=str(vendor.public_id),
                    entity_version=await self.audit_service.get_next_entity_version(
                        entity_type="VENDOR",
                        entity_public_id=str(vendor.public_id),
                    ),
                    before_snapshot_json=before_snapshot,
                    after_snapshot_json=self._vendor_audit_snapshot(vendor),
                    metadata_json={
                        "operation": "update_vendor",
                    },
                )
            )

            await self.db.commit()
            await self.db.refresh(vendor)

            vendor = await self.vendor_repo.get_by_public_id(
                vendor.public_id,
                eager_load_contacts=True,
            )

            if vendor is None:
                raise AppException(
                    status_code=500,
                    message="Unable to reload updated vendor.",
                )

            return vendor

        except AppException:
            await self.db.rollback()
            raise

        except Exception:
            await self.db.rollback()
            raise

    async def archive_vendor(
        self,
        public_id: UUID,
        current_user_id: int,
    ) -> None:
        """
        Archives (deactivates) a Vendor and records the lifecycle transition.
        """

        vendor = await self._get_vendor_or_raise(
            public_id=public_id,
            eager_load_contacts=False,
        )

        before_snapshot = self._vendor_audit_snapshot(vendor)

        vendor.status = VendorStatus.INACTIVE
        vendor.updated_by = current_user_id

        try:
            await self.db.flush()

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=current_user_id,
                    action_type=AuditActionType.STATUS_CHANGE,
                    source_context="VENDOR_SERVICE",
                    entity_type="VENDOR",
                    entity_public_id=str(vendor.public_id),
                    entity_version=await self.audit_service.get_next_entity_version(
                        entity_type="VENDOR",
                        entity_public_id=str(vendor.public_id),
                    ),
                    before_snapshot_json=before_snapshot,
                    after_snapshot_json=self._vendor_audit_snapshot(vendor),
                    metadata_json={
                        "operation": "archive_vendor",
                        "new_status": VendorStatus.INACTIVE.value,
                    },
                )
            )

            await self.db.commit()

        except AppException:
            await self.db.rollback()
            raise

        except Exception:
            await self.db.rollback()
            raise

    # ==========================================================
    # Client CRUD Operations
    # ==========================================================

    async def create_client(
        self,
        payload: ClientCreateRequest,
        current_user_id: int,
    ) -> Client:
        """
        Creates a Client beneath an existing Vendor.
        """

        vendor = await self._get_vendor_or_raise(
            payload.vendor_public_id,
            eager_load_contacts=False,
        )

        client_data = payload.model_dump(
            exclude={"vendor_public_id"}
        )

        client_data = self._normalize_client_payload(client_data)

        duplicate = await self.client_repo.exists_duplicate_under_vendor(
            vendor_id=vendor.id,
            name=client_data["name"],
        )

        if duplicate:
            raise AppException(
                status_code=400,
                message="A client with this name already exists for the selected vendor.",
            )

        client_data["vendor_id"] = vendor.id
        client_data["created_by"] = current_user_id

        try:
            client = self.client_repo.create(
                **client_data
            )

            await self.db.flush()

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=current_user_id,
                    action_type=AuditActionType.CREATE,
                    source_context="VENDOR_SERVICE",
                    entity_type="CLIENT",
                    entity_public_id=str(client.public_id),
                    entity_version=await self.audit_service.get_next_entity_version(
                        entity_type="CLIENT",
                        entity_public_id=str(client.public_id),
                    ),
                    before_snapshot_json=None,
                    after_snapshot_json=self._client_audit_snapshot(client),
                    metadata_json={
                        "operation": "create_client",
                    },
                )
            )

            await self.db.commit()
            await self.db.refresh(client)

            client = await self.client_repo.get_by_public_id(
                client.public_id,
                eager_load_vendor=True,
            )

            if client is None:
                raise AppException(
                    status_code=500,
                    message="Client was created but could not be reloaded.",
                )

            return client

        except AppException:
            await self.db.rollback()
            raise

        except Exception:
            await self.db.rollback()
            raise

    async def get_client(
        self,
        public_id: UUID,
    ) -> Client:
        """
        Retrieves a Client by public identifier.
        """

        return await self._get_client_or_raise(
            public_id,
            eager_load_vendor=True,
        )

    async def list_clients(
        self,
        pagination: PaginationParams,
        sort: SortParams,
        filters: ClientFilters,
    ) -> tuple[list[Client], PaginationMetadata]:
        """
        Returns paginated Client records.
        """

        return await self.client_repo.list_clients_paginated(
            filters=filters,
            pagination=pagination,
            sort=sort,
        )

    async def update_client(
        self,
        public_id: UUID,
        payload: ClientUpdateRequest,
        current_user_id: int,
    ) -> Client:
        """
        Updates an existing Client while enforcing duplicate
        protections and audit tracking.
        """

        client = await self._get_client_or_raise(
            public_id,
            eager_load_vendor=True,
        )

        update_data = payload.model_dump(exclude_unset=True)

        update_data = self._normalize_client_payload(update_data)

        #
        # Duplicate validation
        #
        if (
            "name" in update_data
            and update_data["name"] != client.name
        ):
            duplicate = await self.client_repo.exists_duplicate_under_vendor(
                vendor_id=client.vendor_id,
                name=update_data["name"],
                exclude_id=client.id,
            )

            if duplicate:
                raise AppException(
                    status_code=400,
                    message="A client with this name already exists for this vendor.",
                )

        #
        # Apply updates
        #
        before_snapshot = self._client_audit_snapshot(client)

        for field, value in update_data.items():
            setattr(client, field, value)

        client.updated_by = current_user_id

        try:

            await self.db.flush()

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=current_user_id,
                    action_type=AuditActionType.UPDATE,
                    source_context="VENDOR_SERVICE",
                    entity_type="CLIENT",
                    entity_public_id=str(client.public_id),
                    entity_version=await self.audit_service.get_next_entity_version(
                        entity_type="CLIENT",
                        entity_public_id=str(client.public_id),
                    ),
                    before_snapshot_json=before_snapshot,
                    after_snapshot_json=self._client_audit_snapshot(client),
                    metadata_json={
                        "operation": "update_client",
                    },
                )
            )

            await self.db.commit()

            await self.db.refresh(client)

            client = await self.client_repo.get_by_public_id(
                client.public_id,
                eager_load_vendor=True,
            )

            if client is None:
                raise AppException(
                    status_code=500,
                    message="Unable to reload updated client.",
                )

            return client

        except AppException:
            await self.db.rollback()
            raise

        except Exception:
            await self.db.rollback()
            raise

    async def archive_client(
        self,
        public_id: UUID,
        current_user_id: int,
    ) -> None:
        """
        Archives a Client by transitioning it to INACTIVE.
        """

        client = await self._get_client_or_raise(
            public_id,
            eager_load_vendor=False,
        )

        before_snapshot = self._client_audit_snapshot(client)

        client.status = ClientStatus.INACTIVE
        client.updated_by = current_user_id

        try:

            await self.db.flush()

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=current_user_id,
                    action_type=AuditActionType.STATUS_CHANGE,
                    source_context="VENDOR_SERVICE",
                    entity_type="CLIENT",
                    entity_public_id=str(client.public_id),
                    entity_version=await self.audit_service.get_next_entity_version(
                        entity_type="CLIENT",
                        entity_public_id=str(client.public_id),
                    ),
                    before_snapshot_json=before_snapshot,
                    after_snapshot_json=self._client_audit_snapshot(client),
                    metadata_json={
                        "operation": "archive_client",
                        "new_status": ClientStatus.INACTIVE.value,
                    },
                )
            )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise
