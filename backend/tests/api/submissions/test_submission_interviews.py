import pytest
from datetime import datetime, timezone

from app.models.user import User
from app.vendors.models import Vendor, Client
from app.consultants.models import Consultant
from app.submissions.models import Submission
from app.submissions.enums import SubmissionStatus, InterviewType


async def create_test_submission(db_session, sample_admin: User, status):
    vendor = Vendor(
        name="Interview Test Vendor",
        created_by=sample_admin.id,
    )
    db_session.add(vendor)
    await db_session.flush()

    client_record = Client(
        vendor_id=vendor.id,
        created_by=sample_admin.id,
        name="Interview Test Client",
        display_name="Interview Test Client",
    )
    db_session.add(client_record)

    consultant = Consultant(
        first_name="Interview",
        last_name="Test",
        email="interview.test@example.com",
        visa_status="H1B",
        recruiter_id=sample_admin.id,
    )
    db_session.add(consultant)

    await db_session.commit()

    await db_session.refresh(vendor)
    await db_session.refresh(client_record)
    await db_session.refresh(consultant)

    submission = Submission(
        consultant_id=consultant.id,
        vendor_id=vendor.id,
        client_id=client_record.id,
        client_name_snapshot=client_record.name,
        vendor_name_snapshot=vendor.name,
        job_title_snapshot="Interview Developer",
        job_title="Interview Developer",
        employment_type="C2C",
        rate=75,
        currency="USD",
        submission_status=status,
        submitted_by=sample_admin.id,
    )

    db_session.add(submission)
    await db_session.commit()
    await db_session.refresh(submission)

    return submission


@pytest.mark.api
@pytest.mark.asyncio
async def test_schedule_interview_success(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.UNDER_REVIEW,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/interviews",
        json={
            "round_number": 1,
            "interview_type": "TECHNICAL",
            "scheduled_at": "2026-09-20T15:00:00+05:30",
            "timezone": "Asia/Kolkata",
            "interviewer": "Test Interviewer",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["round_number"] == 1
    assert data["interview_type"] == InterviewType.TECHNICAL.value
    assert data["status"] == "SCHEDULED"
    assert data["timezone"] == "Asia/Kolkata"
    assert data["interviewer"] == "Test Interviewer"


@pytest.mark.api
@pytest.mark.asyncio
async def test_schedule_interview_rejects_wrong_submission_status(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.DRAFT,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/interviews",
        json={
            "round_number": 1,
            "interview_type": "TECHNICAL",
            "scheduled_at": "2026-09-20T15:00:00+05:30",
            "timezone": "Asia/Kolkata",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    data = response.json()

    assert "Cannot schedule an interview" in data["message"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_schedule_interview_rejects_non_sequential_round(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.UNDER_REVIEW,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/interviews",
        json={
            "round_number": 2,
            "interview_type": "TECHNICAL",
            "scheduled_at": "2026-09-20T15:00:00+05:30",
            "timezone": "Asia/Kolkata",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    data = response.json()

    assert "Expected round 1, received 2" in data["message"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_schedule_interview_normalizes_aware_datetime(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.UNDER_REVIEW,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/interviews",
        json={
            "round_number": 1,
            "interview_type": "CLIENT",
            "scheduled_at": "2026-09-20T15:00:00+05:30",
            "timezone": "Asia/Kolkata",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    scheduled_at = datetime.fromisoformat(data["scheduled_at"])

    expected_utc = datetime(
        2026,
        9,
        20,
        9,
        30,
    )

    assert scheduled_at.replace(tzinfo=None) == expected_utc


@pytest.mark.api
@pytest.mark.asyncio
async def test_schedule_interview_returns_404_for_unknown_submission(
    client,
    admin_headers,
):
    from uuid import uuid4

    response = await client.post(
        f"/api/v1/submissions/{uuid4()}/interviews",
        json={
            "round_number": 1,
            "interview_type": "TECHNICAL",
            "scheduled_at": "2026-09-20T15:00:00+05:30",
            "timezone": "Asia/Kolkata",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404