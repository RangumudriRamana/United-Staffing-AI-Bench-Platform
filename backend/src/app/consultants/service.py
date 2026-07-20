from uuid import UUID
from datetime import date, datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.consultants.models import Consultant, ConsultantMarketingHistory
from app.consultants.repositories import ConsultantRepository, ConsultantFilters
from app.consultants.schemas import ConsultantCreateRequest, UpdateConsultantRequest, ConsultantFilterParams
from app.shared.schemas import PaginationParams, SortParams, PaginationMetadata
from app.consultants.enums import MarketingStatus, AvailabilityStatus


class ConsultantService:
    """
    Core Domain Service layer orchestrating business validations, transactional boundaries,
    and finite state machine transitions for the Consultant aggregate root.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ConsultantRepository(db)

    # --- Standard Profile Management Operations ---

    async def create_consultant(self, payload: ConsultantCreateRequest, current_user_id: int) -> Consultant:
        """Enforces duplicate controls and initializes the baseline profile record."""
        if await self.repo.exists_by_email(payload.email):
            raise AppException(status_code=400, message="Email is already registered.")

        if payload.expected_rate is not None and payload.expected_rate < 0:
            raise AppException(status_code=400, message="Expected compensation rate cannot be negative.")

        consultant_data = payload.model_dump()
        consultant_data["recruiter_id"] = current_user_id
        consultant_data["created_by"] = current_user_id
        consultant_data["marketing_status"] = MarketingStatus.NEW
        consultant_data["availability_status"] = AvailabilityStatus.AVAILABLE_NOW

        try:
            new_consultant = self.repo.create(**consultant_data)
            await self.db.flush()  # Extract the tracking ID primary key safely

            # Initialize the very first historical log entry ledger row
            initial_history = ConsultantMarketingHistory(
                consultant_id=new_consultant.id,
                changed_by=current_user_id,
                status=MarketingStatus.NEW,
                effective_from=datetime.now(timezone.utc),
                reason="Initial profile registration setup."
            )
            self.db.add(initial_history)
            
            await self.db.commit()
            await self.db.refresh(new_consultant)
            return new_consultant
        except Exception as err:
            await self.db.rollback()
            raise err

    async def get_consultant(self, public_id: UUID) -> Consultant:
        """Retrieves a single active profile entity by its unique public UUID."""
        consultant = await self.repo.get_by_public_id(public_id, eager_load_recruiter=True)
        if not consultant:
            raise AppException(status_code=404, message="Consultant record not found.")
        return consultant

    async def list_consultants(
        self,
        pagination: PaginationParams,
        sort: SortParams,
        filters: ConsultantFilterParams
    ) -> tuple[list[Consultant], PaginationMetadata]:
        """Validates query combinations and passes parameters to the backend repository runner."""
        repo_filters = ConsultantFilters(
            visa_status=filters.visa_status,
            search=filters.search
        )
        return await self.repo.list_paginated(
            pagination_params=pagination,
            sort_params=sort,
            filter_params=repo_filters
        )

    async def update_consultant(self, public_id: UUID, payload: UpdateConsultantRequest, current_user_id: int) -> Consultant:
        """Executes targeted structural mutations (excluding direct FSM status modifications)."""
        consultant = await self.repo.get_by_public_id(public_id, eager_load_recruiter=False)
        if not consultant:
            raise AppException(status_code=404, message="Consultant record not found.")

        update_data = payload.model_dump(exclude_unset=True)

        # block direct status injection attempts through the generic patch route
        update_data.pop("marketing_status", None)
        update_data.pop("availability_status", None)

        if "email" in update_data and update_data["email"] != consultant.email:
            if await self.repo.exists_by_email(update_data["email"]):
                raise AppException(status_code=400, message="Email is already registered.")

        for key, val in update_data.items():
            setattr(consultant, key, val)
        
        consultant.updated_by = current_user_id

        try:
            await self.db.commit()
            await self.db.refresh(consultant)
            return consultant
        except Exception as err:
            await self.db.rollback()
            raise err

    async def archive_consultant(self, public_id: UUID) -> None:
        """Logical row masking sequence to execute secure soft-deletions."""
        consultant = await self.repo.get_by_public_id(public_id, eager_load_recruiter=False)
        if not consultant:
            raise AppException(status_code=404, message="Consultant record not found.")

        consultant.deleted_at = datetime.now(timezone.utc)
        try:
            await self.db.commit()
        except Exception as err:
            await self.db.rollback()
            raise err

    # --- Core Finite State Machine (FSM) Transition Routines ---

    async def transition_marketing_status(
        self, 
        public_id: UUID, 
        new_status: MarketingStatus, 
        changed_by_user_id: int, 
        reason: str | None = None, 
        notes: str | None = None
    ) -> Consultant:
        """
        Enforces strict lifecycle sequence transition matrices, terminates past history 
        rows, and applies matching availability updates dynamically.
        """
        consultant = await self.repo.get_by_public_id(public_id, eager_load_recruiter=False)
        if not consultant:
            raise AppException(status_code=404, message="Consultant record not found.")

        old_status = consultant.marketing_status
        if old_status == new_status:
            return consultant

        # 1. Enforce Valid Lifecycle FSM Traversal Contraints
        allowed_transitions = {
            MarketingStatus.NEW: [MarketingStatus.READY_FOR_MARKETING, MarketingStatus.INACTIVE],
            MarketingStatus.READY_FOR_MARKETING: [MarketingStatus.MARKETING_ACTIVE, MarketingStatus.UNAVAILABLE, MarketingStatus.INACTIVE],
            MarketingStatus.MARKETING_ACTIVE: [MarketingStatus.INTERVIEWING, MarketingStatus.UNAVAILABLE, MarketingStatus.INACTIVE],
            MarketingStatus.INTERVIEWING: [MarketingStatus.OFFER_PENDING, MarketingStatus.MARKETING_ACTIVE, MarketingStatus.INACTIVE],
            MarketingStatus.OFFER_PENDING: [MarketingStatus.PLACED, MarketingStatus.MARKETING_ACTIVE, MarketingStatus.INACTIVE],
            MarketingStatus.PLACED: [MarketingStatus.ON_PROJECT, MarketingStatus.MARKETING_ACTIVE],
            MarketingStatus.ON_PROJECT: [MarketingStatus.MARKETING_ACTIVE, MarketingStatus.UNAVAILABLE, MarketingStatus.INACTIVE],
            MarketingStatus.UNAVAILABLE: [MarketingStatus.READY_FOR_MARKETING, MarketingStatus.INACTIVE],
            MarketingStatus.INACTIVE: [MarketingStatus.NEW]
        }

        if new_status not in allowed_transitions.get(old_status, []):
            raise AppException(
                status_code=400, 
                message=f"Invalid state transition rules path requested: Cannot move from {old_status.value} to {new_status.value}."
            )

        # 2. Derive Automated Availability States Based on Operations Matrix
        if new_status in [MarketingStatus.PLACED, MarketingStatus.ON_PROJECT, MarketingStatus.UNAVAILABLE, MarketingStatus.INACTIVE]:
            consultant.availability_status = AvailabilityStatus.NOT_AVAILABLE
            consultant.available_from = None
        elif new_status in [MarketingStatus.READY_FOR_MARKETING, MarketingStatus.MARKETING_ACTIVE]:
            consultant.availability_status = AvailabilityStatus.AVAILABLE_NOW
            consultant.available_from = date.today()

        now_timestamp = datetime.now(timezone.utc)

        try:
            # 3. Terminate the active chronological record row item
            await self.db.execute(
                update(ConsultantMarketingHistory)
                .where(
                    ConsultantMarketingHistory.consultant_id == consultant.id,
                    ConsultantMarketingHistory.effective_until == None
                )
                .values(effective_until=now_timestamp)
            )

            # 4. Instantiate a fresh chronological timeline entry block
            new_history_log = ConsultantMarketingHistory(
                consultant_id=consultant.id,
                changed_by=changed_by_user_id,
                status=new_status,
                effective_from=now_timestamp,
                reason=reason,
                notes=notes
            )
            self.db.add(new_history_log)

            # 5. Save the state changes back onto the parent record
            consultant.marketing_status = new_status
            consultant.updated_by = changed_by_user_id

            await self.db.commit()
            await self.db.refresh(consultant)
            return consultant

        except Exception as failure:
            await self.db.rollback()
            raise failure