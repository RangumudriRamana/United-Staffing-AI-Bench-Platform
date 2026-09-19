from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.requirements.models import Requirement, RequirementHistory, RequirementTechnology, RequirementDocument
from app.requirements.repositories import RequirementRepository
from app.requirements.schemas import RequirementSearchCriteria
from app.requirements.enums import RequirementStatus, RequirementPriority
from app.consultants.enums import DocumentType
from app.shared.schemas import PaginationParams, SortParams

class RequirementService:
    """
    Coordinates complex business workflows, domain validation rule checks,
    and state transitions for the central Requirement aggregate root context.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RequirementRepository(db)

    async def create_requirement(
        self,
        payload: dict,
        current_user_id: int
    ) -> Requirement:
        """Initializes raw position profiles and registers the baseline log ledger entries."""

        # Prevent duplicate job codes
        if payload.get("job_code"):
            existing_requirement = await self.db.scalar(
                select(Requirement).where(
                    Requirement.job_code == payload["job_code"]
                )
            )

            if existing_requirement:
                raise AppException(
                    status_code=409,
                    message=f"Requirement with job code '{payload['job_code']}' already exists.",
                )

        # Validate billing range
        if (
            payload.get("rate_min") is not None
            and payload.get("rate_max") is not None
        ):
            if payload["rate_min"] > payload["rate_max"]:
                raise AppException(
                    status_code=400,
                    message="Minimum billing range limits cannot cross maximum boundaries."
                )

        # Bind operational owner attributes
        payload["owner_recruiter_id"] = current_user_id
        payload["status"] = RequirementStatus.DRAFT
        payload["received_date"] = datetime.now(timezone.utc)

        try:
            new_req = self.repo.create(**payload)

            await self.db.flush()

            initial_history = RequirementHistory(
                requirement_id=new_req.id,
                changed_by=current_user_id,
                status=RequirementStatus.DRAFT,
                effective_from=datetime.now(timezone.utc),
                reason="Initial requirement profile entry created."
            )

            self.db.add(initial_history)

            await self.db.commit()

            created_requirement = await self.repo.get_by_public_id(
                new_req.public_id,
                eager_load_details=True,
            )

            if not created_requirement:
                raise AppException(
                    status_code=404,
                    message="Requirement record not found after creation.",
                )

            return created_requirement

        except Exception as failure:
            await self.db.rollback()
            raise failure
    async def transition_requirement_status(
        self,
        public_id: UUID,
        target_status: RequirementStatus,
        user_id: int,
        reason: str | None = None,
        notes: str | None = None
    ) -> Requirement:
        """Enforces workflow traversal validation paths, closing past log layers atomically."""
        requirement = await self.repo.get_by_public_id(public_id, eager_load_details=False)
        if not requirement:
            raise AppException(status_code=404, message="Requirement record not found.")

        old_status = requirement.status
        if old_status == target_status:
            refreshed_requirement = await self.repo.get_by_public_id(
                requirement.public_id,
                eager_load_details=True,
            )

            if not refreshed_requirement:
                raise AppException(
                    status_code=404,
                    message="Requirement record not found.",
                )

            return refreshed_requirement

        # Enforce valid sourcing progression lifecycle phases
        allowed_graph = {
            RequirementStatus.DRAFT: [RequirementStatus.OPEN, RequirementStatus.CANCELLED],
            RequirementStatus.OPEN: [RequirementStatus.SOURCING, RequirementStatus.ON_HOLD, RequirementStatus.CANCELLED],
            RequirementStatus.SOURCING: [RequirementStatus.SUBMITTING, RequirementStatus.ON_HOLD, RequirementStatus.CANCELLED],
            RequirementStatus.SUBMITTING: [RequirementStatus.INTERVIEWING, RequirementStatus.ON_HOLD, RequirementStatus.CANCELLED],
            RequirementStatus.INTERVIEWING: [RequirementStatus.FILLED, RequirementStatus.ON_HOLD, RequirementStatus.CANCELLED],
            RequirementStatus.ON_HOLD: [RequirementStatus.OPEN, RequirementStatus.CANCELLED, RequirementStatus.CLOSED],
            RequirementStatus.FILLED: [RequirementStatus.CLOSED],
            RequirementStatus.CANCELLED: [],
            RequirementStatus.CLOSED: []
        }

        if target_status not in allowed_graph.get(old_status, []):
            raise AppException(
                status_code=400,
                message=f"Invalid sourcing machine trajectory: Transition from {old_status.value} to {target_status.value} is unauthorized."
            )

        now_timestamp = datetime.now(timezone.utc)
        try:
            # Terminate interval history segment block execution
            await self.db.execute(
                update(RequirementHistory)
                .where(RequirementHistory.requirement_id == requirement.id, RequirementHistory.effective_until == None)
                .values(effective_until=now_timestamp)
            )

            # Generate modern logging entries
            new_log = RequirementHistory(
                requirement_id=requirement.id,
                changed_by=user_id,
                status=target_status,
                effective_from=now_timestamp,
                reason=reason,
                notes=notes
            )
            self.db.add(new_log)

            requirement.status = target_status
            await self.db.commit()

            # Reload the aggregate with all response relationships eagerly loaded.
            updated_requirement = await self.repo.get_by_public_id(
                public_id,
                eager_load_details=True
            )

            if not updated_requirement:
                raise AppException(
                    status_code=404,
                    message="Requirement record not found after transition."
                )

            return updated_requirement
        except Exception as error:
            await self.db.rollback()
            raise error

    async def assign_technology(
        self,
        public_id: UUID,
        technology_id: int,
        minimum_years: int,
        mandatory: bool,
        notes: str | None = None
    ) -> RequirementTechnology:
        """Binds normalized target skills catalog links straight into the open job profile."""
        requirement = await self.repo.get_by_public_id(public_id, eager_load_details=True)
        if not requirement:
            raise AppException(status_code=404, message="Requirement record not found.")

        if minimum_years < 0:
            raise AppException(status_code=400, message="Experience constraints cannot settle on negative values.")

        # Prevent duplicate technology stack maps inside the same requirement sandbox
        for tech in requirement.technologies:
            if tech.technology_id == technology_id:
                raise AppException(status_code=400, message="Target technical parameter already mapped to requirement details.")

        new_tech_link = RequirementTechnology(
            requirement_id=requirement.id,
            technology_id=technology_id,
            minimum_years=minimum_years,
            mandatory=mandatory,
            notes=notes
        )
        self.db.add(new_tech_link)
        await self.db.commit()
        return new_tech_link

    async def assign_required_document(
        self,
        public_id: UUID,
        document_type: DocumentType,
        mandatory: bool,
        notes: str | None = None
    ) -> RequirementDocument:
        """Maps prerequisite document compliance criteria directly into position footprints."""
        requirement = await self.repo.get_by_public_id(public_id, eager_load_details=True)
        if not requirement:
            raise AppException(status_code=404, message="Requirement record not found.")

        for doc in requirement.documents:
            if doc.document_type == document_type:
                raise AppException(status_code=400, message="Target compliance document profile already linked.")

        new_doc_link = RequirementDocument(
            requirement_id=requirement.id,
            document_type=document_type,
            mandatory=mandatory,
            notes=notes
        )
        self.db.add(new_doc_link)
        await self.db.commit()
        return new_doc_link

    async def reassign_owner(self, public_id: UUID, new_owner_id: int) -> Requirement:
        """Modifies core staff coverage accounts assignments safely."""
        requirement = await self.repo.get_by_public_id(public_id, eager_load_details=False)
        if not requirement:
            raise AppException(status_code=404, message="Requirement record not found.")

        requirement.owner_recruiter_id = new_owner_id
        await self.db.commit()

        updated_requirement = await self.repo.get_by_public_id(
            public_id,
            eager_load_details=True,
        )

        if not updated_requirement:
            raise AppException(
                status_code=404,
                message="Requirement record not found after owner reassignment.",
            )

        return updated_requirement

    async def get_requirement(self, public_id: UUID) -> Requirement:
        """Fetches unified multi-tier child details trees securely via repository pipelines."""
        requirement = await self.repo.get_by_public_id(public_id, eager_load_details=True)
        if not requirement:
            raise AppException(status_code=404, message="Requirement record not found.")
        return requirement

    async def list_requirements(self, criteria: RequirementSearchCriteria, pagination: PaginationParams, sort: SortParams):
        """Passes search scopes and structured parameter parameters straight down to persistence layers."""
        return await self.repo.list_requirements_paginated(criteria, pagination, sort)
