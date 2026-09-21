from datetime import date, datetime, timezone as dt_timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import AppException
from app.consultants.enums import MarketingStatus
from app.submissions.enums import (
    InterviewType,
    InterviewStatus,
    OfferStatus,
    PlacementStatus,
    SubmissionStatus,
)
from app.submissions.service import SubmissionService


def make_submission(
    status=SubmissionStatus.DRAFT,
    public_id="11111111-1111-1111-1111-111111111111",
):
    return SimpleNamespace(
        id=1,
        public_id=public_id,
        consultant_id=10,
        vendor_id=20,
        client_id=30,
        requirement_id=40,
        job_id="JOB-001",
        job_title="Java Developer",
        job_location="Remote",
        employment_type=SimpleNamespace(value="C2C"),
        rate=Decimal("75"),
        currency="USD",
        submission_status=status,
        expected_start_date=date(2026, 10, 1),
        submission_notes="Test submission",
        submitted_by=99,
    )


def make_service():
    db = MagicMock()
    db.scalar = AsyncMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()

    service = SubmissionService(db)

    service.repo = MagicMock()
    service.repo.get_by_public_id = AsyncMock()
    service.repo.exists_active_submission = AsyncMock(return_value=False)
    service.repo.create = MagicMock()

    service.audit_service = MagicMock()
    service.audit_service.write_audit_entry = AsyncMock()
    service.audit_service.get_next_entity_version = AsyncMock(return_value=1)

    service.consultant_service = MagicMock()
    service.consultant_service.transition_marketing_status = AsyncMock()

    return service, db


def test_submission_audit_snapshot():
    service, _ = make_service()

    submission = make_submission()

    snapshot = service._submission_audit_snapshot(submission)

    assert snapshot["public_id"] == str(submission.public_id)
    assert snapshot["consultant_id"] == 10
    assert snapshot["vendor_id"] == 20
    assert snapshot["client_id"] == 30
    assert snapshot["requirement_id"] == 40
    assert snapshot["job_title"] == "Java Developer"
    assert snapshot["employment_type"] == "C2C"
    assert snapshot["rate"] == "75"
    assert snapshot["submission_status"] == "DRAFT"
    assert snapshot["expected_start_date"] == "2026-10-01"


def test_submission_audit_snapshot_without_expected_start_date():
    service, _ = make_service()

    submission = make_submission()
    submission.expected_start_date = None

    snapshot = service._submission_audit_snapshot(submission)

    assert snapshot["expected_start_date"] is None


@pytest.mark.asyncio
async def test_transition_unknown_submission():
    service, _ = make_service()

    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.transition_submission_status(
            public_id="11111111-1111-1111-1111-111111111111",
            target_status=SubmissionStatus.SUBMITTED,
            user_id=99,
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_transition_same_status_returns_existing_submission():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.DRAFT)
    service.repo.get_by_public_id.return_value = submission

    result = await service.transition_submission_status(
        public_id=submission.public_id,
        target_status=SubmissionStatus.DRAFT,
        user_id=99,
    )

    assert result is submission
    db.commit.assert_not_awaited()
    service.audit_service.write_audit_entry.assert_not_awaited()


@pytest.mark.asyncio
async def test_transition_valid_path_updates_status_and_audits():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.DRAFT)
    service.repo.get_by_public_id.side_effect = [
        submission,
        submission,
    ]

    result = await service.transition_submission_status(
        public_id=submission.public_id,
        target_status=SubmissionStatus.SUBMITTED,
        user_id=99,
        reason="Ready for client",
        notes="Submission approved",
    )

    assert result is submission
    assert submission.submission_status == SubmissionStatus.SUBMITTED

    db.execute.assert_awaited_once()
    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_transition_rolls_back_when_transaction_fails():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.DRAFT)
    service.repo.get_by_public_id.return_value = submission

    db.execute.side_effect = RuntimeError("database failure")

    with pytest.raises(RuntimeError, match="database failure"):
        await service.transition_submission_status(
            public_id=submission.public_id,
            target_status=SubmissionStatus.SUBMITTED,
            user_id=99,
        )

    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_schedule_interview_rejects_unknown_submission():
    service, _ = make_service()

    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.schedule_interview(
            public_id="11111111-1111-1111-1111-111111111111",
            round_number=1,
            interview_type=InterviewType.TECHNICAL,
            scheduled_at=datetime(2026, 9, 20, 15, 0),
            timezone="Asia/Kolkata",
            interviewer="Test Interviewer",
            user_id=99,
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_create_offer_unknown_submission():
    service, _ = make_service()

    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.create_offer(
            public_id="11111111-1111-1111-1111-111111111111",
            offered_rate=Decimal("80"),
            currency="USD",
            start_date=date(2026, 10, 1),
            user_id=99,
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_create_placement_unknown_submission():
    service, _ = make_service()

    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.create_placement(
            public_id="11111111-1111-1111-1111-111111111111",
            started_on=date(2026, 10, 1),
            ended_on=None,
            billing_rate=Decimal("100"),
            pay_rate=Decimal("80"),
            user_id=99,
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_submission_returns_loaded_submission():
    service, _ = make_service()

    submission = make_submission()
    service.repo.get_by_public_id.return_value = submission

    result = await service.get_submission(submission.public_id)

    assert result is submission
    service.repo.get_by_public_id.assert_awaited_once_with(
        submission.public_id,
        eager_load_details=True,
    )


@pytest.mark.asyncio
async def test_get_submission_returns_404_when_missing():
    service, _ = make_service()

    service.repo.get_by_public_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.get_submission(
            "11111111-1111-1111-1111-111111111111"
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_list_submissions_delegates_to_repository():
    service, _ = make_service()

    criteria = MagicMock()
    pagination = MagicMock()
    sort = MagicMock()

    expected = ([make_submission()], MagicMock())

    service.repo.list_submissions_paginated = AsyncMock(
        return_value=expected
    )

    result = await service.list_submissions(
        criteria=criteria,
        pagination=pagination,
        sort=sort,
    )

    assert result == expected

    service.repo.list_submissions_paginated.assert_awaited_once_with(
        criteria,
        pagination,
        sort,
    )


@pytest.mark.asyncio
async def test_get_consultant_public_id_success():
    service, db = make_service()

    consultant = SimpleNamespace(
        public_id="22222222-2222-2222-2222-222222222222"
    )

    db.scalar.return_value = consultant

    result = await service._get_consultant_public_id(10)

    assert result == consultant.public_id


@pytest.mark.asyncio
async def test_get_consultant_public_id_missing():
    service, db = make_service()

    db.scalar.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service._get_consultant_public_id(999)

    assert exc_info.value.status_code == 404

# ---------------------------------------------------------------------------
# create_submission - additional service coverage
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_submission_success():
    service, db = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)
    client = SimpleNamespace(id=30, vendor_id=20)

    submission = make_submission()

    db.scalar.side_effect = [
        consultant,
        vendor,
        client,
    ]

    service.repo.create.return_value = submission

    payload = {
        "consultant_public_id": "consultant-public-id",
        "vendor_public_id": "vendor-public-id",
        "client_public_id": "client-public-id",
        "job_title": "Java Developer",
        "job_id": "JOB-001",
        "job_location": "Remote",
        "employment_type": SimpleNamespace(value="C2C"),
        "rate": Decimal("75"),
        "currency": "USD",
        "expected_start_date": date(2026, 10, 1),
        "submission_notes": "Test submission",
    }

    result = await service.create_submission(
        payload,
        current_user_id=99,
    )

    assert result is submission
    assert service.repo.create.call_args.kwargs["consultant_id"] == 10
    assert service.repo.create.call_args.kwargs["vendor_id"] == 20
    assert service.repo.create.call_args.kwargs["client_id"] == 30
    assert service.repo.create.call_args.kwargs["vendor_contact_id"] is None
    assert service.repo.create.call_args.kwargs["requirement_id"] is None
    assert service.repo.create.call_args.kwargs["submitted_by"] == 99
    assert (
        service.repo.create.call_args.kwargs["submission_status"]
        == SubmissionStatus.DRAFT
    )

    db.flush.assert_awaited_once()
    db.commit.assert_awaited()
    assert db.commit.await_count == 2
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_submission_vendor_not_found():
    service, _ = make_service()

    consultant = SimpleNamespace(id=10)

    service.db.scalar.side_effect = [
        consultant,
        None,
    ]

    payload = {
        "consultant_public_id": "consultant-public-id",
        "vendor_public_id": "missing-vendor",
        "client_public_id": "client-public-id",
        "job_title": "Java Developer",
        "rate": Decimal("75"),
    }

    with pytest.raises(AppException) as exc:
        await service.create_submission(payload, current_user_id=99)

    assert exc.value.status_code == 404
    assert exc.value.message == "Vendor not found."


@pytest.mark.asyncio
async def test_create_submission_client_vendor_mismatch():
    service, _ = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)

    service.db.scalar.side_effect = [
        consultant,
        vendor,
        None,
    ]

    payload = {
        "consultant_public_id": "consultant-public-id",
        "vendor_public_id": "vendor-public-id",
        "client_public_id": "wrong-client",
        "job_title": "Java Developer",
        "rate": Decimal("75"),
    }

    with pytest.raises(AppException) as exc:
        await service.create_submission(payload, current_user_id=99)

    assert exc.value.status_code == 404
    assert "selected vendor" in exc.value.message


@pytest.mark.asyncio
async def test_create_submission_vendor_contact_not_found():
    service, _ = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)
    client = SimpleNamespace(id=30, vendor_id=20)

    service.db.scalar.side_effect = [
        consultant,
        vendor,
        client,
        None,
    ]

    payload = {
        "consultant_public_id": "consultant-public-id",
        "vendor_public_id": "vendor-public-id",
        "client_public_id": "client-public-id",
        "vendor_contact_public_id": "missing-contact",
        "job_title": "Java Developer",
        "rate": Decimal("75"),
    }

    with pytest.raises(AppException) as exc:
        await service.create_submission(payload, current_user_id=99)

    assert exc.value.status_code == 404
    assert "Vendor contact" in exc.value.message


@pytest.mark.asyncio
async def test_create_submission_requirement_not_found_for_vendor_client():
    service, _ = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)
    client = SimpleNamespace(id=30, vendor_id=20)

    service.db.scalar.side_effect = [
        consultant,
        vendor,
        client,
        None,
    ]

    payload = {
        "consultant_public_id": "consultant-public-id",
        "vendor_public_id": "vendor-public-id",
        "client_public_id": "client-public-id",
        "requirement_public_id": "missing-requirement",
        "job_title": "Java Developer",
        "rate": Decimal("75"),
    }

    with pytest.raises(AppException) as exc:
        await service.create_submission(payload, current_user_id=99)

    assert exc.value.status_code == 404
    assert "Requirement not found" in exc.value.message


@pytest.mark.asyncio
async def test_create_submission_duplicate():
    service, _ = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)
    client = SimpleNamespace(id=30, vendor_id=20)

    service.db.scalar.side_effect = [
        consultant,
        vendor,
        client,
    ]

    service.repo.exists_active_submission.return_value = True

    payload = {
        "consultant_public_id": "consultant-public-id",
        "vendor_public_id": "vendor-public-id",
        "client_public_id": "client-public-id",
        "job_title": "Java Developer",
        "rate": Decimal("75"),
    }

    with pytest.raises(AppException) as exc:
        await service.create_submission(payload, current_user_id=99)

    assert exc.value.status_code == 400
    assert "active pipeline" in exc.value.message


@pytest.mark.asyncio
async def test_create_submission_zero_rate():
    service, _ = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)
    client = SimpleNamespace(id=30, vendor_id=20)

    service.db.scalar.side_effect = [
        consultant,
        vendor,
        client,
    ]

    payload = {
        "consultant_public_id": "consultant-public-id",
        "vendor_public_id": "vendor-public-id",
        "client_public_id": "client-public-id",
        "job_title": "Java Developer",
        "rate": Decimal("0"),
    }

    with pytest.raises(AppException) as exc:
        await service.create_submission(payload, current_user_id=99)

    assert exc.value.status_code == 400
    assert "greater than zero" in exc.value.message


@pytest.mark.asyncio
async def test_create_submission_rolls_back_on_failure():
    service, db = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)
    client = SimpleNamespace(id=30, vendor_id=20)

    db.scalar.side_effect = [
        consultant,
        vendor,
        client,
    ]

    service.repo.create.side_effect = RuntimeError("database failure")

    payload = {
        "consultant_public_id": "consultant-public-id",
        "vendor_public_id": "vendor-public-id",
        "client_public_id": "client-public-id",
        "job_title": "Java Developer",
        "rate": Decimal("75"),
    }

    with pytest.raises(RuntimeError, match="database failure"):
        await service.create_submission(payload, current_user_id=99)

    db.rollback.assert_awaited_once()


# ---------------------------------------------------------------------------
# transition_submission_status - additional branches
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_transition_submission_reload_failure():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.DRAFT)

    service.repo.get_by_public_id.side_effect = [
        submission,
        None,
    ]

    with pytest.raises(AppException) as exc:
        await service.transition_submission_status(
            public_id=submission.public_id,
            target_status=SubmissionStatus.SUBMITTED,
            user_id=99,
        )

    assert exc.value.status_code == 404
    db.rollback.assert_awaited_once()

# ---------------------------------------------------------------------------
# schedule_interview - success / normalization / rollback
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_schedule_interview_success():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.UNDER_REVIEW)
    submission.interviews = []

    service.repo.get_by_public_id.return_value = submission

    scheduled_at = datetime(2026, 9, 20, 15, 0)

    result = await service.schedule_interview(
        public_id=submission.public_id,
        round_number=1,
        interview_type=InterviewType.TECHNICAL,
        scheduled_at=scheduled_at,
        timezone="Asia/Kolkata",
        interviewer="Test Interviewer",
        user_id=99,
    )

    assert isinstance(result, object)
    assert result.status == InterviewStatus.SCHEDULED
    assert result.round_number == 1
    assert result.interview_type == InterviewType.TECHNICAL
    assert result.scheduled_at == scheduled_at
    assert result.timezone == "Asia/Kolkata"
    assert result.interviewer == "Test Interviewer"

    assert submission.submission_status == SubmissionStatus.INTERVIEW_SCHEDULED
    db.execute.assert_awaited_once()
    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_schedule_interview_aware_datetime_is_normalized_to_utc():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.UNDER_REVIEW)
    submission.interviews = []

    service.repo.get_by_public_id.return_value = submission

    aware_datetime = datetime(
        2026,
        9,
        20,
        20,
        30,
        tzinfo=dt_timezone.utc,
    )

    result = await service.schedule_interview(
        public_id=submission.public_id,
        round_number=1,
        interview_type=InterviewType.TECHNICAL,
        scheduled_at=aware_datetime,
        timezone="Asia/Kolkata",
        interviewer=None,
        user_id=99,
    )

    assert result.scheduled_at == datetime(2026, 9, 20, 20, 30)
    assert result.scheduled_at.tzinfo is None


@pytest.mark.asyncio
async def test_schedule_interview_second_round():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.INTERVIEW_COMPLETED)
    submission.interviews = [
        SimpleNamespace(round_number=1)
    ]

    service.repo.get_by_public_id.return_value = submission

    result = await service.schedule_interview(
        public_id=submission.public_id,
        round_number=2,
        interview_type=InterviewType.TECHNICAL,
        scheduled_at=datetime(2026, 9, 21, 15, 0),
        timezone="Asia/Kolkata",
        interviewer="Manager",
        user_id=99,
    )

    assert result.round_number == 2
    assert result.status == InterviewStatus.SCHEDULED
    assert submission.submission_status == SubmissionStatus.INTERVIEW_SCHEDULED
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_schedule_interview_rolls_back_on_failure():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.UNDER_REVIEW)
    submission.interviews = []

    service.repo.get_by_public_id.return_value = submission
    db.execute.side_effect = RuntimeError("database failure")

    with pytest.raises(RuntimeError, match="database failure"):
        await service.schedule_interview(
            public_id=submission.public_id,
            round_number=1,
            interview_type=InterviewType.TECHNICAL,
            scheduled_at=datetime(2026, 9, 20, 15, 0),
            timezone="Asia/Kolkata",
            interviewer="Interviewer",
            user_id=99,
        )

    db.rollback.assert_awaited_once()


# ---------------------------------------------------------------------------
# create_offer - success / rollback
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_offer_success():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.INTERVIEW_COMPLETED)
    service.repo.get_by_public_id.return_value = submission

    result = await service.create_offer(
        public_id=submission.public_id,
        offered_rate=Decimal("85"),
        currency="USD",
        start_date=date(2026, 10, 1),
        expiration_date=date(2026, 10, 10),
        notes="Client offer",
        user_id=99,
    )

    assert isinstance(result, object)
    assert result.offered_rate == Decimal("85")
    assert result.currency == "USD"
    assert result.start_date == date(2026, 10, 1)
    assert result.expiration_date == date(2026, 10, 10)
    assert result.offer_status == OfferStatus.PENDING
    assert result.notes == "Client offer"

    assert submission.submission_status == SubmissionStatus.OFFER_RECEIVED
    db.flush.assert_awaited()
    db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_offer_without_expiration_date():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.INTERVIEW_COMPLETED)
    service.repo.get_by_public_id.return_value = submission

    result = await service.create_offer(
        public_id=submission.public_id,
        offered_rate=Decimal("90"),
        currency="USD",
        start_date=date(2026, 10, 1),
        expiration_date=None,
        user_id=None,
    )

    assert result.expiration_date is None
    assert result.offer_status == OfferStatus.PENDING
    assert submission.submission_status == SubmissionStatus.OFFER_RECEIVED
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_offer_rolls_back_on_failure():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.INTERVIEW_COMPLETED)
    service.repo.get_by_public_id.return_value = submission

    db.flush.side_effect = RuntimeError("database failure")

    with pytest.raises(RuntimeError, match="database failure"):
        await service.create_offer(
            public_id=submission.public_id,
            offered_rate=Decimal("85"),
            currency="USD",
            start_date=date(2026, 10, 1),
            user_id=99,
        )

    db.rollback.assert_awaited_once()


# ---------------------------------------------------------------------------
# create_placement - success / consultant linkage / rollback
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_placement_success():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.OFFER_ACCEPTED)
    service.repo.get_by_public_id.return_value = submission

    consultant = SimpleNamespace(
        public_id="22222222-2222-2222-2222-222222222222"
    )
    db.scalar.return_value = consultant

    result = await service.create_placement(
        public_id=submission.public_id,
        started_on=date(2026, 10, 1),
        ended_on=date(2027, 10, 1),
        billing_rate=Decimal("120"),
        pay_rate=Decimal("90"),
        user_id=99,
    )

    assert isinstance(result, object)
    assert result.started_on == date(2026, 10, 1)
    assert result.ended_on == date(2027, 10, 1)
    assert result.billing_rate == Decimal("120")
    assert result.pay_rate == Decimal("90")
    assert result.placement_status == PlacementStatus.ACTIVE

    assert submission.submission_status == SubmissionStatus.PLACED

    service.consultant_service.transition_marketing_status.assert_awaited_once()
    call_kwargs = (
        service.consultant_service.transition_marketing_status.call_args.kwargs
    )

    assert call_kwargs["public_id"] == consultant.public_id
    assert call_kwargs["new_status"] == MarketingStatus.PLACED
    assert call_kwargs["changed_by_user_id"] == 99
    assert call_kwargs["commit"] is False

    db.commit.assert_awaited_once()
    service.audit_service.write_audit_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_placement_without_end_date():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.OFFER_ACCEPTED)
    service.repo.get_by_public_id.return_value = submission

    consultant = SimpleNamespace(
        public_id="22222222-2222-2222-2222-222222222222"
    )
    db.scalar.return_value = consultant

    result = await service.create_placement(
        public_id=submission.public_id,
        started_on=date(2026, 10, 1),
        ended_on=None,
        billing_rate=Decimal("120"),
        pay_rate=Decimal("90"),
        user_id=99,
    )

    assert result.ended_on is None
    assert result.placement_status == PlacementStatus.ACTIVE
    assert submission.submission_status == SubmissionStatus.PLACED
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_placement_rolls_back_when_consultant_transition_fails():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.OFFER_ACCEPTED)
    service.repo.get_by_public_id.return_value = submission

    consultant = SimpleNamespace(
        public_id="22222222-2222-2222-2222-222222222222"
    )
    db.scalar.return_value = consultant

    service.consultant_service.transition_marketing_status.side_effect = (
        RuntimeError("marketing transition failed")
    )

    with pytest.raises(RuntimeError, match="marketing transition failed"):
        await service.create_placement(
            public_id=submission.public_id,
            started_on=date(2026, 10, 1),
            ended_on=None,
            billing_rate=Decimal("120"),
            pay_rate=Decimal("90"),
            user_id=99,
        )

    db.rollback.assert_awaited_once()
    db.commit.assert_not_awaited()

# ---------------------------------------------------------------------------
# Remaining SubmissionService branch coverage
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_submission_with_vendor_contact_and_requirement():
    service, db = make_service()

    consultant = SimpleNamespace(id=10)
    vendor = SimpleNamespace(id=20)
    client = SimpleNamespace(id=30, vendor_id=20)
    vendor_contact = SimpleNamespace(id=40)
    requirement = SimpleNamespace(id=50)

    db.scalar.side_effect = [
        consultant,
        vendor,
        client,
        vendor_contact,
        requirement,
    ]

    submission = make_submission()
    service.repo.create.return_value = submission

    payload = {
        "consultant_public_id": "consultant-public-id",
        "vendor_public_id": "vendor-public-id",
        "client_public_id": "client-public-id",
        "vendor_contact_public_id": "contact-public-id",
        "requirement_public_id": "requirement-public-id",
        "job_title": "Java Developer",
        "job_id": "JOB-001",
        "rate": Decimal("75"),
    }

    result = await service.create_submission(payload, current_user_id=99)

    assert result is submission
    assert service.repo.create.call_args.kwargs["vendor_contact_id"] == 40
    assert service.repo.create.call_args.kwargs["requirement_id"] == 50


@pytest.mark.asyncio
async def test_create_offer_uses_submission_user_when_user_id_missing():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.INTERVIEW_COMPLETED)
    submission.submitted_by = 777
    service.repo.get_by_public_id.return_value = submission

    result = await service.create_offer(
        public_id=submission.public_id,
        offered_rate=Decimal("90"),
        currency="USD",
        start_date=date(2026, 10, 1),
        expiration_date=None,
        user_id=None,
    )

    assert result.offer_status == OfferStatus.PENDING

    audit_call = service.audit_service.write_audit_entry.call_args
    audit_payload = audit_call.args[0]

    assert audit_payload.actor_user_id == 777


@pytest.mark.asyncio
async def test_create_placement_consultant_lookup_failure_rolls_back():
    service, db = make_service()

    submission = make_submission(SubmissionStatus.OFFER_ACCEPTED)
    service.repo.get_by_public_id.return_value = submission

    db.scalar.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.create_placement(
            public_id=submission.public_id,
            started_on=date(2026, 10, 1),
            ended_on=None,
            billing_rate=Decimal("120"),
            pay_rate=Decimal("90"),
            user_id=99,
        )

    assert exc_info.value.status_code == 404
    assert (
        exc_info.value.message
        == "Consultant linked to submission was not found."
    )
    db.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_submission_consultant_not_found():
    service, _ = make_service()

    service.db.scalar.return_value = None

    payload = {
        "consultant_public_id": "missing-consultant",
        "vendor_public_id": "vendor-public-id",
        "client_public_id": "client-public-id",
        "job_title": "Java Developer",
        "rate": Decimal("75"),
    }

    with pytest.raises(AppException) as exc_info:
        await service.create_submission(payload, current_user_id=99)

    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "Consultant not found."


@pytest.mark.asyncio
async def test_transition_invalid_status_path():
    service, _ = make_service()

    submission = make_submission(SubmissionStatus.DRAFT)
    service.repo.get_by_public_id.return_value = submission

    with pytest.raises(AppException) as exc_info:
        await service.transition_submission_status(
            public_id=submission.public_id,
            target_status=SubmissionStatus.REJECTED,
            user_id=99,
        )

    assert exc_info.value.status_code == 400
    assert "Cannot transition from" in exc_info.value.message


@pytest.mark.asyncio
async def test_schedule_interview_invalid_submission_status():
    service, _ = make_service()

    submission = make_submission(SubmissionStatus.DRAFT)
    submission.interviews = []
    service.repo.get_by_public_id.return_value = submission

    with pytest.raises(AppException) as exc_info:
        await service.schedule_interview(
            public_id=submission.public_id,
            round_number=1,
            interview_type=InterviewType.TECHNICAL,
            scheduled_at=datetime(2026, 9, 20, 15, 0),
            timezone="Asia/Kolkata",
            interviewer="Interviewer",
            user_id=99,
        )

    assert exc_info.value.status_code == 400
    assert "Cannot schedule an interview" in exc_info.value.message


@pytest.mark.asyncio
async def test_schedule_interview_invalid_round():
    service, _ = make_service()

    submission = make_submission(SubmissionStatus.UNDER_REVIEW)
    submission.interviews = [
        SimpleNamespace(round_number=1)
    ]
    service.repo.get_by_public_id.return_value = submission

    with pytest.raises(AppException) as exc_info:
        await service.schedule_interview(
            public_id=submission.public_id,
            round_number=3,
            interview_type=InterviewType.TECHNICAL,
            scheduled_at=datetime(2026, 9, 20, 15, 0),
            timezone="Asia/Kolkata",
            interviewer="Interviewer",
            user_id=99,
        )

    assert exc_info.value.status_code == 400
    assert "Expected round 2" in exc_info.value.message


@pytest.mark.asyncio
async def test_create_offer_rejects_non_positive_rate():
    service, _ = make_service()

    submission = make_submission(SubmissionStatus.INTERVIEW_COMPLETED)
    service.repo.get_by_public_id.return_value = submission

    with pytest.raises(AppException) as exc_info:
        await service.create_offer(
            public_id=submission.public_id,
            offered_rate=Decimal("0"),
            currency="USD",
            start_date=date(2026, 10, 1),
            user_id=99,
        )

    assert exc_info.value.status_code == 400
    assert "must be positive" in exc_info.value.message


@pytest.mark.asyncio
async def test_create_offer_rejects_expiration_before_start():
    service, _ = make_service()

    submission = make_submission(SubmissionStatus.INTERVIEW_COMPLETED)
    service.repo.get_by_public_id.return_value = submission

    with pytest.raises(AppException) as exc_info:
        await service.create_offer(
            public_id=submission.public_id,
            offered_rate=Decimal("85"),
            currency="USD",
            start_date=date(2026, 10, 10),
            expiration_date=date(2026, 10, 1),
            user_id=99,
        )

    assert exc_info.value.status_code == 400
    assert "expiration date cannot be before" in exc_info.value.message


@pytest.mark.asyncio
async def test_create_offer_rejects_wrong_submission_status():
    service, _ = make_service()

    submission = make_submission(SubmissionStatus.SUBMITTED)
    service.repo.get_by_public_id.return_value = submission

    with pytest.raises(AppException) as exc_info:
        await service.create_offer(
            public_id=submission.public_id,
            offered_rate=Decimal("85"),
            currency="USD",
            start_date=date(2026, 10, 1),
            user_id=99,
        )

    assert exc_info.value.status_code == 400
    assert "INTERVIEW_COMPLETED" in exc_info.value.message


@pytest.mark.asyncio
async def test_create_placement_rejects_invalid_margin():
    service, _ = make_service()

    submission = make_submission(SubmissionStatus.OFFER_ACCEPTED)
    service.repo.get_by_public_id.return_value = submission

    with pytest.raises(AppException) as exc_info:
        await service.create_placement(
            public_id=submission.public_id,
            started_on=date(2026, 10, 1),
            ended_on=None,
            billing_rate=Decimal("80"),
            pay_rate=Decimal("80"),
            user_id=99,
        )

    assert exc_info.value.status_code == 400
    assert "Billing margins are invalid" in exc_info.value.message


@pytest.mark.asyncio
async def test_create_placement_rejects_wrong_submission_status():
    service, _ = make_service()

    submission = make_submission(SubmissionStatus.INTERVIEW_COMPLETED)
    service.repo.get_by_public_id.return_value = submission

    with pytest.raises(AppException) as exc_info:
        await service.create_placement(
            public_id=submission.public_id,
            started_on=date(2026, 10, 1),
            ended_on=None,
            billing_rate=Decimal("120"),
            pay_rate=Decimal("90"),
            user_id=99,
        )

    assert exc_info.value.status_code == 400
    assert "OFFER_ACCEPTED" in exc_info.value.message


@pytest.mark.asyncio
async def test_create_placement_rejects_end_date_before_start():
    service, _ = make_service()

    submission = make_submission(SubmissionStatus.OFFER_ACCEPTED)
    service.repo.get_by_public_id.return_value = submission

    with pytest.raises(AppException) as exc_info:
        await service.create_placement(
            public_id=submission.public_id,
            started_on=date(2026, 10, 10),
            ended_on=date(2026, 10, 1),
            billing_rate=Decimal("120"),
            pay_rate=Decimal("90"),
            user_id=99,
        )

    assert exc_info.value.status_code == 400
    assert "end date cannot be before" in exc_info.value.message