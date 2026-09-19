import pytest

from app.models.user import User
from app.vendors.models import Vendor, VendorContact, Client
from app.consultants.models import Consultant
from app.submissions.enums import SubmissionStatus


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_submission_success(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    vendor = Vendor(
        name="Submission Test Vendor",
        created_by=sample_admin.id,
    )
    db_session.add(vendor)
    await db_session.flush()

    vendor_contact = VendorContact(
        vendor_id=vendor.id,
        name="Submission Recruiter",
        email="submission.recruiter@testvendor.com",
        is_active=True,
    )
    db_session.add(vendor_contact)

    client_record = Client(
        vendor_id=vendor.id,
        created_by=sample_admin.id,
        name="Submission Test Client",
        display_name="Submission Test Client",
    )
    db_session.add(client_record)

    consultant = Consultant(
        first_name="Submission",
        last_name="Test",
        email="submission.test@example.com",
        visa_status="H1B",
        recruiter_id=sample_admin.id,
    )
    db_session.add(consultant)

    await db_session.commit()

    await db_session.refresh(vendor)
    await db_session.refresh(vendor_contact)
    await db_session.refresh(client_record)
    await db_session.refresh(consultant)

    response = await client.post(
        "/api/v1/submissions",
        json={
            "consultant_public_id": str(consultant.public_id),
            "vendor_public_id": str(vendor.public_id),
            "vendor_contact_public_id": str(vendor_contact.public_id),
            "client_public_id": str(client_record.public_id),
            "client_name_snapshot": client_record.name,
            "vendor_name_snapshot": vendor.name,
            "job_title_snapshot": "Senior Java Developer",
            "job_id": "SUB-TEST-001",
            "job_title": "Senior Java Developer",
            "job_location": "Remote",
            "employment_type": "C2C",
            "rate": "75",
            "currency": "USD",
            "submission_notes": "Submission creation regression test.",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["consultant_id"] == consultant.id
    assert data["vendor_id"] == vendor.id
    assert data["vendor_contact_id"] == vendor_contact.id
    assert data["client_id"] == client_record.id
    assert data["job_title"] == "Senior Java Developer"
    assert data["employment_type"] == "C2C"
    assert data["rate"] == "75"
    assert data["submission_status"] == SubmissionStatus.DRAFT.value


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_submission_rejects_unknown_consultant(
    client,
    sample_admin: User,
    admin_headers,
):
    from uuid import uuid4

    response = await client.post(
        "/api/v1/submissions",
        json={
            "consultant_public_id": str(uuid4()),
            "vendor_public_id": str(uuid4()),
            "client_public_id": str(uuid4()),
            "client_name_snapshot": "Test Client",
            "vendor_name_snapshot": "Test Vendor",
            "job_title_snapshot": "Developer",
            "job_title": "Developer",
            "employment_type": "C2C",
            "rate": "75",
            "currency": "USD",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_submission_rejects_client_from_different_vendor(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    vendor_a = Vendor(
        name="Submission Vendor A",
        created_by=sample_admin.id,
    )
    vendor_b = Vendor(
        name="Submission Vendor B",
        created_by=sample_admin.id,
    )

    db_session.add_all([vendor_a, vendor_b])
    await db_session.flush()

    client_a = Client(
        vendor_id=vendor_a.id,
        created_by=sample_admin.id,
        name="Client A",
        display_name="Client A",
    )
    consultant = Consultant(
        first_name="Cross",
        last_name="Vendor",
        email="cross.vendor@example.com",
        visa_status="H1B",
        recruiter_id=sample_admin.id,
    )

    db_session.add_all([client_a, consultant])
    await db_session.commit()

    await db_session.refresh(vendor_b)
    await db_session.refresh(client_a)
    await db_session.refresh(consultant)

    response = await client.post(
        "/api/v1/submissions",
        json={
            "consultant_public_id": str(consultant.public_id),
            "vendor_public_id": str(vendor_b.public_id),
            "client_public_id": str(client_a.public_id),
            "client_name_snapshot": client_a.name,
            "vendor_name_snapshot": vendor_b.name,
            "job_title_snapshot": "Java Developer",
            "job_title": "Java Developer",
            "employment_type": "C2C",
            "rate": "75",
            "currency": "USD",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_submission_rejects_duplicate_active_submission(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    vendor = Vendor(
        name="Duplicate Submission Vendor",
        created_by=sample_admin.id,
    )
    db_session.add(vendor)
    await db_session.flush()

    client_record = Client(
        vendor_id=vendor.id,
        created_by=sample_admin.id,
        name="Duplicate Client",
        display_name="Duplicate Client",
    )
    consultant = Consultant(
        first_name="Duplicate",
        last_name="Submission",
        email="duplicate.submission@example.com",
        visa_status="H1B",
        recruiter_id=sample_admin.id,
    )

    db_session.add_all([client_record, consultant])
    await db_session.commit()

    await db_session.refresh(vendor)
    await db_session.refresh(client_record)
    await db_session.refresh(consultant)

    payload = {
        "consultant_public_id": str(consultant.public_id),
        "vendor_public_id": str(vendor.public_id),
        "client_public_id": str(client_record.public_id),
        "client_name_snapshot": client_record.name,
        "vendor_name_snapshot": vendor.name,
        "job_title_snapshot": "Duplicate Java Developer",
        "job_title": "Duplicate Java Developer",
        "employment_type": "C2C",
        "rate": "75",
        "currency": "USD",
    }

    first_response = await client.post(
        "/api/v1/submissions",
        json=payload,
        headers=admin_headers,
    )

    assert first_response.status_code == 201

    second_response = await client.post(
        "/api/v1/submissions",
        json=payload,
        headers=admin_headers,
    )

    assert second_response.status_code == 400


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_submission_rejects_non_positive_rate(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    vendor = Vendor(
        name="Invalid Rate Vendor",
        created_by=sample_admin.id,
    )
    db_session.add(vendor)
    await db_session.flush()

    client_record = Client(
        vendor_id=vendor.id,
        created_by=sample_admin.id,
        name="Invalid Rate Client",
        display_name="Invalid Rate Client",
    )
    consultant = Consultant(
        first_name="Invalid",
        last_name="Rate",
        email="invalid.rate@example.com",
        visa_status="H1B",
        recruiter_id=sample_admin.id,
    )

    db_session.add_all([client_record, consultant])
    await db_session.commit()

    await db_session.refresh(vendor)
    await db_session.refresh(client_record)
    await db_session.refresh(consultant)

    response = await client.post(
        "/api/v1/submissions",
        json={
            "consultant_public_id": str(consultant.public_id),
            "vendor_public_id": str(vendor.public_id),
            "client_public_id": str(client_record.public_id),
            "client_name_snapshot": client_record.name,
            "vendor_name_snapshot": vendor.name,
            "job_title_snapshot": "Invalid Rate Developer",
            "job_title": "Invalid Rate Developer",
            "employment_type": "C2C",
            "rate": "0",
            "currency": "USD",
        },
        headers=admin_headers,
    )

    assert response.status_code == 422