from uuid import UUID
from decimal import Decimal
from datetime import datetime, date, timezone as dt_timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.exceptions import AppException
from app.submissions.models import (
    Submission,
    SubmissionHistory,
    Interview,
    Offer,
    Placement,
)

from app.submissions.repositories import SubmissionRepository
from app.submissions.schemas import (
    SubmissionSearchFilters,
)

from app.submissions.enums import (
    SubmissionStatus,
    InterviewStatus,
    OfferStatus,
    PlacementStatus,
    InterviewType,
)

from app.consultants.service import ConsultantService
from app.consultants.enums import MarketingStatus
from app.consultants.models import Consultant

from app.vendors.models import Vendor, VendorContact, Client

from app.requirements.models import Requirement

from app.shared.schemas import PaginationParams, SortParams

from app.audit.enums import AuditActionType
from app.audit.schemas import AuditRecordCreatePayload
from app.audit.service import AuditService



class SubmissionService:
    """
    Orchestrates transactional business logic, FSM transitions,
    validation policies, interview tracking, offers, and placements.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SubmissionRepository(db)
        self.consultant_service = ConsultantService(db)
        self.audit_service = AuditService(db)

    def _submission_audit_snapshot(
        self,
        submission: Submission,
    ) -> dict:
        return {
            "public_id": str(submission.public_id),
            "consultant_id": submission.consultant_id,
            "vendor_id": submission.vendor_id,
            "client_id": submission.client_id,
            "requirement_id": submission.requirement_id,
            "job_id": submission.job_id,
            "job_title": submission.job_title,
            "job_location": submission.job_location,
            "employment_type": submission.employment_type.value,
            "rate": str(submission.rate),
            "currency": submission.currency,
            "submission_status": submission.submission_status.value,
            "expected_start_date": (
                submission.expected_start_date.isoformat()
                if submission.expected_start_date is not None
                else None
            ),
            "submission_notes": submission.submission_notes,
        }

    async def create_submission(
        self,
        payload: dict,
        current_user_id: int,
    ) -> Submission:
        """Creates a new Submission in DRAFT status."""

        # --------------------------------------------------------
        # Resolve Consultant
        # --------------------------------------------------------
        consultant = await self.db.scalar(
            select(Consultant).where(
                Consultant.public_id == payload["consultant_public_id"],
                Consultant.deleted_at.is_(None),
            )
        )

        if not consultant:
            raise AppException(
                status_code=404,
                message="Consultant not found.",
            )

        # --------------------------------------------------------
        # Resolve Vendor
        # --------------------------------------------------------
        vendor = await self.db.scalar(
            select(Vendor).where(
                Vendor.public_id == payload["vendor_public_id"],
            )
        )

        if not vendor:
            raise AppException(
                status_code=404,
                message="Vendor not found.",
            )

        # --------------------------------------------------------
        # Resolve Client and verify Vendor relationship
        # --------------------------------------------------------
        client = await self.db.scalar(
            select(Client).where(
                Client.public_id == payload["client_public_id"],
                Client.vendor_id == vendor.id,
            )
        )

        if not client:
            raise AppException(
                status_code=404,
                message="Client not found for the selected vendor.",
            )

        # --------------------------------------------------------
        # Resolve Vendor Contact
        # --------------------------------------------------------
        vendor_contact_id = None

        if payload.get("vendor_contact_public_id") is not None:
            vendor_contact = await self.db.scalar(
                select(VendorContact).where(
                    VendorContact.public_id
                    == payload["vendor_contact_public_id"],
                    VendorContact.vendor_id == vendor.id,
                    VendorContact.is_active.is_(True),
                )
            )

            if not vendor_contact:
                raise AppException(
                    status_code=404,
                    message="Vendor contact not found for the selected vendor.",
                )

            vendor_contact_id = vendor_contact.id

        # --------------------------------------------------------
        # Resolve Requirement and verify Vendor + Client
        # --------------------------------------------------------
        requirement_id = None

        if payload.get("requirement_public_id") is not None:
            requirement = await self.db.scalar(
                select(Requirement).where(
                    Requirement.public_id
                    == payload["requirement_public_id"],
                    Requirement.vendor_id == vendor.id,
                    Requirement.client_id == client.id,
                )
            )

            if not requirement:
                raise AppException(
                    status_code=404,
                    message=(
                        "Requirement not found for the selected "
                        "vendor and client."
                    ),
                )

            requirement_id = requirement.id

        # --------------------------------------------------------
        # Duplicate protection
        # --------------------------------------------------------
        is_duplicate = await self.repo.exists_active_submission(
            consultant_id=consultant.id,
            client_id=client.id,
            job_title=payload["job_title"],
        )

        if is_duplicate:
            raise AppException(
                status_code=400,
                message=(
                    "An active pipeline tracking instance already exists "
                    "for this consultant-client opportunity combination."
                ),
            )

        # --------------------------------------------------------
        # Rate validation
        # --------------------------------------------------------
        if payload["rate"] <= 0:
            raise AppException(
                status_code=400,
                message="Submission billing rate must be greater than zero.",
            )

        # --------------------------------------------------------
        # Build internal database payload
        # --------------------------------------------------------
        submission_payload = {
            key: value
            for key, value in payload.items()
            if key not in {
                "consultant_public_id",
                "vendor_public_id",
                "vendor_contact_public_id",
                "client_public_id",
                "requirement_public_id",
            }
        }

        submission_payload["consultant_id"] = consultant.id
        submission_payload["vendor_id"] = vendor.id
        submission_payload["vendor_contact_id"] = vendor_contact_id
        submission_payload["client_id"] = client.id
        submission_payload["requirement_id"] = requirement_id

        submission_payload["submitted_by"] = current_user_id
        submission_payload["submission_status"] = SubmissionStatus.DRAFT
        submission_payload["submitted_at"] = datetime.now(dt_timezone.utc)

        # --------------------------------------------------------
        # Transaction
        # --------------------------------------------------------
        try:
            new_submission = self.repo.create(**submission_payload)

            await self.db.flush()

            initial_history = SubmissionHistory(
                submission_id=new_submission.id,
                changed_by=current_user_id,
                status=SubmissionStatus.DRAFT,
                effective_from=datetime.utcnow(),
                reason="Initial tracking profile draft initialized.",
            )

            self.db.add(initial_history)

            self.db.add(initial_history)

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=current_user_id,
                    action_type=AuditActionType.CREATE,
                    source_context="SUBMISSION_SERVICE",
                    entity_type="SUBMISSION",
                    entity_public_id=str(new_submission.public_id),
                    entity_version=await self.audit_service.get_next_entity_version(
                        entity_type="SUBMISSION",
                        entity_public_id=str(new_submission.public_id),
                    ),
                    before_snapshot_json=None,
                    after_snapshot_json=self._submission_audit_snapshot(new_submission),
                    metadata_json={
                        "operation": "create_submission",
                    },
                )
            )

            await self.db.commit()

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
        notes: str | None = None,
    ) -> Submission:
        """Transitions a Submission through the controlled FSM."""

        submission = await self.repo.get_by_public_id(
            public_id,
            eager_load_details=False,
        )

        if not submission:
            raise AppException(
                status_code=404,
                message="Submission record not found.",
            )

        old_status = submission.submission_status
        before_snapshot = self._submission_audit_snapshot(submission)

        if old_status == target_status:
            return submission

        allowed_graph = {
            SubmissionStatus.DRAFT: [
                SubmissionStatus.SUBMITTED,
                SubmissionStatus.WITHDRAWN,
            ],
            SubmissionStatus.SUBMITTED: [
                SubmissionStatus.UNDER_REVIEW,
                SubmissionStatus.REJECTED,
                SubmissionStatus.WITHDRAWN,
            ],
            SubmissionStatus.UNDER_REVIEW: [
                SubmissionStatus.INTERVIEW_SCHEDULED,
                SubmissionStatus.REJECTED,
                SubmissionStatus.WITHDRAWN,
            ],
            SubmissionStatus.INTERVIEW_SCHEDULED: [
                SubmissionStatus.INTERVIEW_COMPLETED,
                SubmissionStatus.REJECTED,
                SubmissionStatus.WITHDRAWN,
            ],
            SubmissionStatus.INTERVIEW_COMPLETED: [
                SubmissionStatus.OFFER_RECEIVED,
                SubmissionStatus.INTERVIEW_SCHEDULED,
                SubmissionStatus.REJECTED,
                SubmissionStatus.WITHDRAWN,
            ],
            SubmissionStatus.OFFER_RECEIVED: [
                SubmissionStatus.OFFER_ACCEPTED,
                SubmissionStatus.CLOSED,
                SubmissionStatus.REJECTED,
            ],
            SubmissionStatus.OFFER_ACCEPTED: [
                SubmissionStatus.PLACED,
                SubmissionStatus.CLOSED,
            ],
            SubmissionStatus.PLACED: [
                SubmissionStatus.CLOSED,
            ],
            SubmissionStatus.REJECTED: [],
            SubmissionStatus.WITHDRAWN: [],
            SubmissionStatus.CLOSED: [],
        }

        if target_status not in allowed_graph.get(old_status, []):
            raise AppException(
                status_code=400,
                message=(
                    f"Invalid pipeline evolution track path: "
                    f"Cannot transition from {old_status.value} "
                    f"to {target_status.value}."
                ),
            )

        now_timestamp = datetime.utcnow()

        try:
            await self.db.execute(
                update(SubmissionHistory)
                .where(
                    SubmissionHistory.submission_id == submission.id,
                    SubmissionHistory.effective_until.is_(None),
                )
                .values(effective_until=now_timestamp)
            )

            new_log = SubmissionHistory(
                submission_id=submission.id,
                changed_by=user_id,
                status=target_status,
                effective_from=now_timestamp,
                reason=reason,
                notes=notes,
            )

            self.db.add(new_log)

            submission.submission_status = target_status

            await self.db.flush()

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=user_id,
                    action_type=AuditActionType.STATUS_CHANGE,
                    source_context="SUBMISSION_SERVICE",
                    entity_type="SUBMISSION",
                    entity_public_id=str(submission.public_id),
                    entity_version=await self.audit_service.get_next_entity_version(
                        entity_type="SUBMISSION",
                        entity_public_id=str(submission.public_id),
                    ),
                    before_snapshot_json=before_snapshot,
                    after_snapshot_json=self._submission_audit_snapshot(submission),
                    metadata_json={
                        "operation": "transition_submission_status",
                        "from_status": old_status.value,
                        "to_status": target_status.value,
                        "reason": reason,
                    },
                )
            )

            await self.db.commit()

            updated_submission = await self.repo.get_by_public_id(
                public_id,
                eager_load_details=True,
            )

            if not updated_submission:
                raise AppException(
                    status_code=404,
                    message="Submission record not found after transition.",
                )

            return updated_submission

        except Exception as err:
            await self.db.rollback()
            raise err

    async def schedule_interview(
        self,
        public_id: UUID,
        round_number: int,
        interview_type: InterviewType,
        scheduled_at: datetime,
        timezone: str,
        interviewer: str | None,
        user_id: int,
    ) -> Interview:
        """Creates the requested interview round and advances the Submission."""

        submission = await self.repo.get_by_public_id(
            public_id,
            eager_load_details=True,
        )

        if not submission:
            raise AppException(
                status_code=404,
                message="Submission record not found.",
            )

        old_status = submission.submission_status
        before_snapshot = self._submission_audit_snapshot(submission)

        allowed_statuses = {
            SubmissionStatus.UNDER_REVIEW,
            SubmissionStatus.INTERVIEW_COMPLETED,
        }

        if old_status not in allowed_statuses:
            raise AppException(
                status_code=400,
                message=(
                    f"Cannot schedule an interview while submission "
                    f"is in {old_status.value} status."
                ),
            )

        expected_round = len(submission.interviews) + 1

        if round_number != expected_round:
            raise AppException(
                status_code=400,
                message=(
                    f"Invalid interview round. Expected round "
                    f"{expected_round}, received {round_number}."
                ),
            )

        # Interview.scheduled_at is a timezone-naive database column.
        # Normalize an aware datetime to UTC, then remove timezone info.
        if scheduled_at.tzinfo is not None:
            scheduled_at_db = scheduled_at.astimezone(dt_timezone.utc).replace(
                tzinfo=None
            )
        else:
            scheduled_at_db = scheduled_at

        try:
            new_interview = Interview(
                submission_id=submission.id,
                round_number=round_number,
                interview_type=interview_type,
                status=InterviewStatus.SCHEDULED,
                scheduled_at=scheduled_at_db,
                timezone=timezone,
                interviewer=interviewer,
            )

            self.db.add(new_interview)

            now_timestamp = datetime.utcnow()

            await self.db.execute(
                update(SubmissionHistory)
                .where(
                    SubmissionHistory.submission_id == submission.id,
                    SubmissionHistory.effective_until.is_(None),
                )
                .values(effective_until=now_timestamp)
            )

            self.db.add(
                SubmissionHistory(
                    submission_id=submission.id,
                    changed_by=user_id,
                    status=SubmissionStatus.INTERVIEW_SCHEDULED,
                    effective_from=now_timestamp,
                    reason=f"Interview round {round_number} scheduled.",
                )
            )

            submission.submission_status = SubmissionStatus.INTERVIEW_SCHEDULED

            await self.db.flush()

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=user_id,
                    action_type=AuditActionType.STATUS_CHANGE,
                    source_context="SUBMISSION_SERVICE",
                    entity_type="SUBMISSION",
                    entity_public_id=str(submission.public_id),
                    entity_version=await self.audit_service.get_next_entity_version(
                        entity_type="SUBMISSION",
                        entity_public_id=str(submission.public_id),
                    ),
                    before_snapshot_json=before_snapshot,
                    after_snapshot_json=self._submission_audit_snapshot(submission),
                    metadata_json={
                        "operation": "schedule_interview",
                        "from_status": old_status.value,
                        "to_status": SubmissionStatus.INTERVIEW_SCHEDULED.value,
                        "round_number": round_number,
                        "interview_type": interview_type.value,
                        "scheduled_at": scheduled_at.isoformat(),
                        "timezone": timezone,
                    },
                )
            )

            await self.db.commit()

            return new_interview

        except Exception as err:
            await self.db.rollback()
            raise err

    async def create_offer(
        self,
        public_id: UUID,
        offered_rate: Decimal,
        currency: str,
        start_date: date,
        expiration_date: date | None = None,
        notes: str | None = None,
        user_id: int | None = None,
    ) -> Offer:
        """Creates a client offer and advances the Submission to OFFER_RECEIVED."""

        submission = await self.repo.get_by_public_id(
            public_id,
            eager_load_details=False,
        )

        if not submission:
            raise AppException(
                status_code=404,
                message="Submission record not found.",
            )

        if offered_rate <= 0:
            raise AppException(
                status_code=400,
                message="Offered placement rate terms must be positive.",
            )

        if expiration_date is not None and expiration_date < start_date:
            raise AppException(
                status_code=400,
                message="Offer expiration date cannot be before the offer start date.",
            )

        if submission.submission_status != SubmissionStatus.INTERVIEW_COMPLETED:
            raise AppException(
                status_code=400,
                message=(
                    "An offer can only be created when the submission "
                    "is in INTERVIEW_COMPLETED status."
                ),
            )
        before_snapshot = self._submission_audit_snapshot(submission)

        try:
            new_offer = Offer(
                submission_id=submission.id,
                offered_rate=offered_rate,
                currency=currency,
                start_date=start_date,
                expiration_date=expiration_date,
                offer_status=OfferStatus.PENDING,
                notes=notes,
            )

            self.db.add(new_offer)

            await self.db.flush()

            now_timestamp = datetime.utcnow()

            await self.db.execute(
                update(SubmissionHistory)
                .where(
                    SubmissionHistory.submission_id == submission.id,
                    SubmissionHistory.effective_until.is_(None),
                )
                .values(effective_until=now_timestamp)
            )

            self.db.add(
                SubmissionHistory(
                    submission_id=submission.id,
                    changed_by=user_id if user_id is not None else submission.submitted_by,
                    status=SubmissionStatus.OFFER_RECEIVED,
                    effective_from=now_timestamp,
                    reason="Client offer received.",
                )
            )

            submission.submission_status = SubmissionStatus.OFFER_RECEIVED

            await self.db.flush()

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=user_id if user_id is not None else submission.submitted_by,
                    action_type=AuditActionType.STATUS_CHANGE,
                    source_context="SUBMISSION_SERVICE",
                    entity_type="SUBMISSION",
                    entity_public_id=str(submission.public_id),
                    entity_version=await self.audit_service.get_next_entity_version(
                        entity_type="SUBMISSION",
                        entity_public_id=str(submission.public_id),
                    ),
                    before_snapshot_json=before_snapshot,
                    after_snapshot_json=self._submission_audit_snapshot(submission),
                    metadata_json={
                        "operation": "create_offer",
                        "from_status": SubmissionStatus.INTERVIEW_COMPLETED.value,
                        "to_status": SubmissionStatus.OFFER_RECEIVED.value,
                        "offered_rate": str(offered_rate),
                        "currency": currency,
                        "start_date": start_date.isoformat(),
                        "expiration_date": (
                            expiration_date.isoformat()
                            if expiration_date is not None
                            else None
                        ),
                    },
                )
            )

            await self.db.commit()

            return new_offer

        except Exception as err:
            await self.db.rollback()
            raise err
    async def create_placement(
        self,
        public_id: UUID,
        started_on: date,
        ended_on: date | None,
        billing_rate: Decimal,
        pay_rate: Decimal,
        user_id: int,
    ) -> Placement:
        """
        Creates a placement, moves the Submission to PLACED,
        and moves the linked Consultant to PLACED.
        """

        submission = await self.repo.get_by_public_id(
            public_id,
            eager_load_details=False,
        )

        if not submission:
            raise AppException(
                status_code=404,
                message="Submission record not found.",
            )

        if billing_rate <= pay_rate:
            raise AppException(
                status_code=400,
                message=(
                    "Billing margins are invalid: "
                    "Pay rate cannot outpace billable limits."
                ),
            )

        if submission.submission_status != SubmissionStatus.OFFER_ACCEPTED:
            raise AppException(
                status_code=400,
                message=(
                    "A placement can only be created when the submission "
                    "is in OFFER_ACCEPTED status."
                ),
            )
        before_snapshot = self._submission_audit_snapshot(submission)

        if ended_on is not None and ended_on < started_on:
            raise AppException(
                status_code=400,
                message="Placement end date cannot be before the start date.",
            )

        try:
            new_placement = Placement(
                submission_id=submission.id,
                started_on=started_on,
                ended_on=ended_on,
                billing_rate=billing_rate,
                pay_rate=pay_rate,
                placement_status=PlacementStatus.ACTIVE,
            )

            self.db.add(new_placement)

            await self.db.flush()

            now_timestamp = datetime.utcnow()

            await self.db.execute(
                update(SubmissionHistory)
                .where(
                    SubmissionHistory.submission_id == submission.id,
                    SubmissionHistory.effective_until.is_(None),
                )
                .values(effective_until=now_timestamp)
            )

            self.db.add(
                SubmissionHistory(
                    submission_id=submission.id,
                    changed_by=user_id,
                    status=SubmissionStatus.PLACED,
                    effective_from=now_timestamp,
                    reason="Consultant successfully placed on active client project.",
                )
            )

            submission.submission_status = SubmissionStatus.PLACED

            await self.db.flush()

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=user_id,
                    action_type=AuditActionType.STATUS_CHANGE,
                    source_context="SUBMISSION_SERVICE",
                    entity_type="SUBMISSION",
                    entity_public_id=str(submission.public_id),
                    entity_version=await self.audit_service.get_next_entity_version(
                        entity_type="SUBMISSION",
                        entity_public_id=str(submission.public_id),
                    ),
                    before_snapshot_json=before_snapshot,
                    after_snapshot_json=self._submission_audit_snapshot(submission),
                    metadata_json={
                        "operation": "create_placement",
                        "from_status": SubmissionStatus.OFFER_ACCEPTED.value,
                        "to_status": SubmissionStatus.PLACED.value,
                        "started_on": started_on.isoformat(),
                        "ended_on": ended_on.isoformat() if ended_on is not None else None,
                        "billing_rate": str(billing_rate),
                        "pay_rate": str(pay_rate),
                    },
                )
            )

            await self.consultant_service.transition_marketing_status(
                public_id=await self._get_consultant_public_id(
                    submission.consultant_id
                ),
                new_status=MarketingStatus.PLACED,
                changed_by_user_id=user_id,
                reason=(
                    f"Automated linkage trigger driven by successful "
                    f"placement on Submission ID: {public_id}"
                ),
                commit=False,
            )

            await self.db.commit()

            return new_placement

        except Exception as err:
            await self.db.rollback()
            raise err

    async def _get_consultant_public_id(
        self,
        consultant_id: int,
    ) -> UUID:
        """Resolves the Submission's consultant database ID to its public UUID."""

        consultant = await self.db.scalar(
            __import__("sqlalchemy").select(Consultant).where(
                Consultant.id == consultant_id,
                Consultant.deleted_at.is_(None),
            )
        )

        if not consultant:
            raise AppException(
                status_code=404,
                message="Consultant linked to submission was not found.",
            )

        return consultant.public_id

    async def get_submission(
        self,
        public_id: UUID,
    ) -> Submission:
        """Fetches a detailed Submission including child records."""

        submission = await self.repo.get_by_public_id(
            public_id,
            eager_load_details=True,
        )

        if not submission:
            raise AppException(
                status_code=404,
                message="Submission record not found.",
            )

        return submission

    async def list_submissions(
        self,
        criteria: SubmissionSearchFilters,
        pagination: PaginationParams,
        sort: SortParams,
    ):
        """Returns paginated Submission records."""

        return await self.repo.list_submissions_paginated(
            criteria,
            pagination,
            sort,
        )