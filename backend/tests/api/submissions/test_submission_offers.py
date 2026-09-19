import pytest
from datetime import date

from app.models.user import User
from app.vendors.models import Vendor, Client
from app.consultants.models import Consultant
from app.submissions.models import Submission
from app.submissions.enums import SubmissionStatus


async def create_test_submission(db_session, sample_admin: User, status):
    vendor = Vendor(
        name="Offer Test Vendor",
        created_by=sample_admin.id,
    )
    db_session.add(vendor)
    await db_session.flush()

    client_record = Client(
        vendor_id=vendor.id,
        created_by=sample_admin.id,
        name="Offer Test Client",
        display_name="Offer Test Client",
    )
    db_session.add(client_record)

    consultant = Consultant(
        first_name="Offer",
        last_name="Test",
        email="offer.test@example.com",
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
        job_title_snapshot="Offer Developer",
        job_title="Offer Developer",
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
async def test_create_offer_success(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.INTERVIEW_COMPLETED,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/offer",
        json={
            "offered_rate": "80",
            "currency": "USD",
            "start_date": "2026-10-01",
            "expiration_date": "2026-10-15",
            "notes": "Offer regression test.",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["offered_rate"] == "80"
    assert data["currency"] == "USD"
    assert data["start_date"] == "2026-10-01"
    assert data["expiration_date"] == "2026-10-15"
    assert data["offer_status"] == "PENDING"
    assert data["notes"] == "Offer regression test."


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_offer_rejects_wrong_submission_status(
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
        f"/api/v1/submissions/{submission.public_id}/offer",
        json={
            "offered_rate": "80",
            "currency": "USD",
            "start_date": "2026-10-01",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    data = response.json()

    assert "INTERVIEW_COMPLETED" in data["message"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_offer_rejects_invalid_expiration_date(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.INTERVIEW_COMPLETED,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/offer",
        json={
            "offered_rate": "80",
            "currency": "USD",
            "start_date": "2026-10-15",
            "expiration_date": "2026-10-01",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    data = response.json()

    assert "expiration date cannot be before" in data["message"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_offer_rejects_non_positive_rate(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission = await create_test_submission(
        db_session,
        sample_admin,
        SubmissionStatus.INTERVIEW_COMPLETED,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/offer",
        json={
            "offered_rate": "0",
            "currency": "USD",
            "start_date": "2026-10-01",
        },
        headers=admin_headers,
    )

    assert response.status_code == 422


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_offer_returns_404_for_unknown_submission(
    client,
    admin_headers,
):
    from uuid import uuid4

    response = await client.post(
        f"/api/v1/submissions/{uuid4()}/offer",
        json={
            "offered_rate": "80",
            "currency": "USD",
            "start_date": "2026-10-01",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404