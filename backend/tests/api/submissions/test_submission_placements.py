import pytest

from app.models.user import User
from app.vendors.models import Vendor, Client
from app.consultants.models import Consultant
from app.submissions.models import Submission
from app.submissions.enums import SubmissionStatus


async def create_test_submission(db_session, sample_admin: User, status):
    vendor = Vendor(
        name="Placement Test Vendor",
        created_by=sample_admin.id,
    )
    db_session.add(vendor)
    await db_session.flush()

    client_record = Client(
        vendor_id=vendor.id,
        created_by=sample_admin.id,
        name="Placement Test Client",
        display_name="Placement Test Client",
    )
    db_session.add(client_record)

    consultant = Consultant(
        first_name="Placement",
        last_name="Test",
        email="placement.test@example.com",
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
        job_title_snapshot="Placement Developer",
        job_title="Placement Developer",
        employment_type="C2C",
        rate=75,
        currency="USD",
        submission_status=status,
        submitted_by=sample_admin.id,
    )

    db_session.add(submission)
    await db_session.commit()
    await db_session.refresh(submission)

    return submission, consultant


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_placement_success(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission, consultant = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.OFFER_ACCEPTED,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/placement",
        json={
            "started_on": "2026-10-01",
            "ended_on": "2027-10-01",
            "billing_rate": "100",
            "pay_rate": "80",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["started_on"] == "2026-10-01"
    assert data["ended_on"] == "2027-10-01"
    assert data["billing_rate"] == "100"
    assert data["pay_rate"] == "80"
    assert data["placement_status"] == "ACTIVE"


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_placement_rejects_wrong_submission_status(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission, _ = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.INTERVIEW_COMPLETED,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/placement",
        json={
            "started_on": "2026-10-01",
            "billing_rate": "100",
            "pay_rate": "80",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    data = response.json()

    assert "OFFER_ACCEPTED" in data["message"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_placement_rejects_invalid_billing_margin(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission, _ = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.OFFER_ACCEPTED,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/placement",
        json={
            "started_on": "2026-10-01",
            "billing_rate": "80",
            "pay_rate": "80",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    data = response.json()

    assert "Billing margins are invalid" in data["message"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_placement_rejects_invalid_end_date(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission, _ = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.OFFER_ACCEPTED,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/placement",
        json={
            "started_on": "2026-10-15",
            "ended_on": "2026-10-01",
            "billing_rate": "100",
            "pay_rate": "80",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    data = response.json()

    assert "end date cannot be before" in data["message"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_placement_returns_404_for_unknown_submission(
    client,
    admin_headers,
):
    from uuid import uuid4

    response = await client.post(
        f"/api/v1/submissions/{uuid4()}/placement",
        json={
            "started_on": "2026-10-01",
            "billing_rate": "100",
            "pay_rate": "80",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404

@pytest.mark.api
@pytest.mark.asyncio
async def test_recruiter_cannot_create_placement(
    client,
    sample_admin: User,
    user_headers,
    db_session,
):
    submission, _ = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.OFFER_ACCEPTED,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/placement",
        json={
            "started_on": "2026-10-01",
            "billing_rate": "100",
            "pay_rate": "80",
        },
        headers=user_headers,
    )

    assert response.status_code == 403