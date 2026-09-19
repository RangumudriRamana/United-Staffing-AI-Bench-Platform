import pytest

from app.models.user import User
from app.vendors.models import Vendor, Client
from app.consultants.models import Consultant
from app.submissions.models import Submission
from app.submissions.enums import SubmissionStatus


async def create_test_submission(db_session, sample_admin: User):
    vendor = Vendor(
        name="Transition Test Vendor",
        created_by=sample_admin.id,
    )
    db_session.add(vendor)
    await db_session.flush()

    client_record = Client(
        vendor_id=vendor.id,
        created_by=sample_admin.id,
        name="Transition Test Client",
        display_name="Transition Test Client",
    )
    db_session.add(client_record)

    consultant = Consultant(
        first_name="Transition",
        last_name="Test",
        email="transition.test@example.com",
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
        job_title_snapshot="Transition Developer",
        job_title="Transition Developer",
        employment_type="C2C",
        rate=75,
        currency="USD",
        submission_status=SubmissionStatus.DRAFT,
        submitted_by=sample_admin.id,
    )

    db_session.add(submission)
    await db_session.commit()
    await db_session.refresh(submission)

    return submission


@pytest.mark.api
@pytest.mark.asyncio
async def test_transition_submission_draft_to_submitted(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission = await create_test_submission(
        db_session,
        sample_admin,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/transition",
        json={
            "target_status": "SUBMITTED",
            "reason": "Submitting candidate to client.",
            "notes": "Transition regression test.",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["submission_status"] == SubmissionStatus.SUBMITTED.value


@pytest.mark.api
@pytest.mark.asyncio
async def test_transition_submission_rejects_invalid_path(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission = await create_test_submission(
        db_session,
        sample_admin,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/transition",
        json={
            "target_status": "REJECTED",
            "reason": "Invalid transition regression test.",
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

    data = response.json()

    assert "Cannot transition from DRAFT to REJECTED" in data["message"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_transition_submission_returns_404_for_unknown_submission(
    client,
    admin_headers,
):
    from uuid import uuid4

    response = await client.post(
        f"/api/v1/submissions/{uuid4()}/transition",
        json={
            "target_status": "SUBMITTED",
            "reason": "Unknown submission regression test.",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404


@pytest.mark.api
@pytest.mark.asyncio
async def test_transition_submission_same_status_is_noop(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    submission = await create_test_submission(
        db_session,
        sample_admin,
    )

    response = await client.post(
        f"/api/v1/submissions/{submission.public_id}/transition",
        json={
            "target_status": "DRAFT",
            "reason": "Same status regression test.",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["submission_status"] == SubmissionStatus.DRAFT.value