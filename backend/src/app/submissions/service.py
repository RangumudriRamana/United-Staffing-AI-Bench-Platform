from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone, date
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.submissions.models import Submission, SubmissionHistory, Interview, ClientFeedback, Offer, Placement
from app.submissions.repositories import SubmissionRepository
from app.submissions.schemas import SubmissionSearchCriteria
from app.submissions.enums import SubmissionStatus, InterviewStatus, OfferStatus, PlacementStatus, InterviewType
from app.consultants.service import ConsultantService
from app.consultants.enums import MarketingStatus
from app.shared.schemas import PaginationParams, SortParams

class SubmissionService:
    """
    Orchestrates the transactional business logic, Finite State Machine (FSM) 
    transitions, and validation policies governing the submission aggregate lifecycle.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SubmissionRepository(db)
        # Reuse existing marketing FSM coordinator to enforce cross-module invariants
        self.consultant_service = ConsultantService(db)

    async def create_submission(self, payload: dict, current_user_id: int) -> Submission:
        """Validates duplicate submission boundaries and creates the aggregate root record."""
        # 1. Enforce strict duplicate prevention per client-job mapping criteria
        is_duplicate = await self.repo.exists_active_submission(
            consultant_id=payload["consultant_id"],
            client_name=payload["client_name"],
            job_title=payload["job_title"]
        )
        if is_duplicate:
            raise AppException(
                status_code=400, 
                message="An active pipeline tracking instance already exists for this consultant-client opportunity combination."
            )

        if payload["rate"] <= 0:
            raise AppException(status_code=400, message="Submission billing rate must be greater than zero.")

        # 2. Build out the central record structure
        payload["submitted_by"] = current_user_id
        payload["submission_status"] = SubmissionStatus.DRAFT
        payload["submitted_at"] = datetime.now(timezone.utc)

        try:
            new_submission = self.repo.create(**payload)
            await self.db.flush()  # Extract the system ID safely

            # 3. Append the baseline timeline tracking point log ledger row
            initial_history = SubmissionHistory(
                submission_id=new_submission.id,
                changed_by=current_user_id,
                status=SubmissionStatus.DRAFT,
                effective_from=datetime.now(timezone.utc),
                reason="Initial tracking profile draft initialized."
            )
            self.db.add(initial_history)
            
            await self.db.commit()
            return new_submission
        except Exception as err:
            await self.db.rollback()
            raise err

    async def transition_submission_status(
        self, 
        public_id: UUID, 
        target_status: SubmissionStatus, 
        user_id: int, 
        reason: str | None = None, 
        notes: str | None = None
    ) -> Submission:
        """Implements the structural Finite State Machine tracking grid graph boundaries."""
        submission = await self.repo.get_by_public_id(public_id, eager_load_details=False)
        if not submission:
            raise AppException(status_code=404, message="Submission record not found.")

        old_status = submission.submission_status
        if old_status == target_status:
            return submission

        # Enforce valid external submission pipeline journey steps
        allowed_graph = {
            SubmissionStatus.DRAFT: [SubmissionStatus.SUBMITTED, SubmissionStatus.WITHDRAWN],
            SubmissionStatus.SUBMITTED: [SubmissionStatus.UNDER_REVIEW, SubmissionStatus.REJECTED, SubmissionStatus.WITHDRAWN],
            SubmissionStatus.UNDER_REVIEW: [SubmissionStatus.INTERVIEW_SCHEDULED, SubmissionStatus.REJECTED, SubmissionStatus.WITHDRAWN],
            SubmissionStatus.INTERVIEW_SCHEDULED: [SubmissionStatus.INTERVIEW_COMPLETED, SubmissionStatus.REJECTED, SubmissionStatus.WITHDRAWN],
            SubmissionStatus.INTERVIEW_COMPLETED: [SubmissionStatus.OFFER_RECEIVED, SubmissionStatus.INTERVIEW_SCHEDULED, SubmissionStatus.REJECTED, SubmissionStatus.WITHDRAWN],
            SubmissionStatus.OFFER_RECEIVED: [SubmissionStatus.OFFER_ACCEPTED, SubmissionStatus.CLOSED, SubmissionStatus.REJECTED],
            SubmissionStatus.OFFER_ACCEPTED: [SubmissionStatus.PLACED, SubmissionStatus.CLOSED],
            SubmissionStatus.PLACED: [SubmissionStatus.CLOSED],
            SubmissionStatus.REJECTED: [],
            SubmissionStatus.WITHDRAWN: [],
            SubmissionStatus.CLOSED: []
        }

        if target_status not in allowed_graph.get(old_status, []):
            raise AppException(
                status_code=400, 
                message=f"Invalid pipeline evolution track path: Cannot transition from {old_status.value} to {target_status.value}."
            )

        now_timestamp = datetime.now(timezone.utc)
        try:
            # Atomic Ledger Modification: Terminate the historical entry row interval segment
            await self.db.execute(
                update(SubmissionHistory)
                .where(SubmissionHistory.submission_id == submission.id, SubmissionHistory.effective_until == None)
                .values(effective_until=now_timestamp)
            )

            # Insert new sequential transition tracking point
            new_log = SubmissionHistory(
                submission_id=submission.id,
                changed_by=user_id,
                status=target_status,
                effective_from=now_timestamp,
                reason=reason,
                notes=notes
            )
            self.db.add(new_log)

            submission.submission_status = target_status
            await self.db.commit()
            return submission
        except Exception as err:
            await self.db.rollback()
            raise err

    async def schedule_interview(
        self, 
        public_id: UUID, 
        interview_type: InterviewType, 
        scheduled_at: datetime, 
        user_id: int
    ) -> Interview:
        """Appends sequential interview rounds and updates the core pipeline status flag."""
        submission = await self.repo.get_by_public_id(public_id, eager_load_details=True)
        if not submission:
            raise AppException(status_code=404, message="Submission record not found.")

        next_round = len(submission.interviews) + 1

        new_interview = Interview(
            submission_id=submission.id,
            round_number=next_round,
            interview_type=interview_type,
            status=InterviewStatus.SCHEDULED,
            scheduled_at=scheduled_at
        )
        self.db.add(new_interview)
        
        # Advance the core FSM pipeline status to indicate active interview tracking loops
        await self.transition_submission_status(
            public_id=public_id, 
            target_status=SubmissionStatus.INTERVIEW_SCHEDULED, 
            user_id=user_id,
            reason=f"Automated trigger: Round {next_round} interview loop successfully mounted."
        )
        return new_interview

    async def create_offer(self, public_id: UUID, offered_rate: Decimal, start_date: datetime, notes: str | None = None) -> Offer:
        """Validates financial invariants and generates client offer parameters."""
        submission = await self.repo.get_by_public_id(public_id, eager_load_details=False)
        if not submission:
            raise AppException(status_code=404, message="Submission record not found.")

        if offered_rate <= 0:
            raise AppException(status_code=400, message="Offered placement rate terms must be positive.")

        new_offer = Offer(
            submission_id=submission.id,
            offered_rate=offered_rate,
            start_date=start_date,
            offer_status=OfferStatus.PENDING,
            notes=notes
        )
        self.db.add(new_offer)
        await self.db.commit()
        return new_offer

    async def create_placement(
        self, 
        public_id: UUID, 
        consultant_public_id: UUID, 
        billing_rate: Decimal, 
        pay_rate: Decimal, 
        user_id: int
    ) -> Placement:
        """
        Executes cross-module transactional operations: registers financial project mappings, 
        moves pipeline steps to PLACED, and locks consultant availability vectors.
        """
        submission = await self.repo.get_by_public_id(public_id, eager_load_details=False)
        if not submission:
            raise AppException(status_code=404, message="Submission record not found.")

        if billing_rate <= pay_rate:
            raise AppException(status_code=400, message="Billing margins are invalid: Pay rate cannot outpace billable limits.")

        try:
            # 1. Instantiate the placement billing parameters
            new_placement = Placement(
                submission_id=submission.id,
                started_on=datetime.now(timezone.utc),
                billing_rate=billing_rate,
                pay_rate=pay_rate,
                placement_status=PlacementStatus.ACTIVE
            )
            self.db.add(new_placement)

            # 2. Advance our pipeline step indicators to full placement visibility status
            await self.transition_submission_status(
                public_id=public_id,
                target_status=SubmissionStatus.PLACED,
                user_id=user_id,
                reason="Consultant successfully locked down on active client billable operations."
            )

            # 3. Layer 4 Cross-Module Link: Drive state updates inside the Consultant aggregate root boundaries
            await self.consultant_service.transition_marketing_status(
                public_id=consultant_public_id,
                new_status=MarketingStatus.PLACED,
                changed_by_user_id=user_id,
                reason=f"Automated linkage trigger driven by successful closing on Submission ID: {public_id}"
            )

            await self.db.commit()
            return new_placement
        except Exception as err:
            await self.db.rollback()
            raise err

    async def get_submission(self, public_id: UUID) -> Submission:
        """Fetches a detailed profile view including deep child table components."""
        submission = await self.repo.get_by_public_id(public_id, eager_load_details=True)
        if not submission:
            raise AppException(status_code=404, message="Submission record not found.")
        return submission

    async def list_submissions(self, criteria: SubmissionSearchCriteria, pagination: PaginationParams, sort: SortParams):
        """Delegates paginated collection lookups directly to the query mapping repositories."""
        return await self.repo.list_submissions_paginated(criteria, pagination, sort)