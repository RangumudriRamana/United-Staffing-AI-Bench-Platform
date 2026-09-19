import pytest

from app.requirements.enums import RequirementStatus
from tests.factories.vendors import VendorFactory, ClientFactory


async def create_vendor_and_client(db_session, created_by):
    vendor = VendorFactory.build(created_by=created_by)
    db_session.add(vendor)
    await db_session.flush()

    client = ClientFactory.build(
    vendor_id=vendor.id,
    created_by=created_by,
)
    db_session.add(client)
    await db_session.flush()

    return vendor, client


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_requirement_success(
    client,
    admin_headers,
    db_session,
    sample_admin,
):
    vendor, requirement_client = await create_vendor_and_client(
    db_session,
    sample_admin.id,
)

    payload = {
        "vendor_id": vendor.id,
        "client_id": requirement_client.id,
        "job_title": "Senior Java Developer",
        "job_code": "REQ-TEST-001",
        "employment_type": "C2C",
        "work_model": "HYBRID",
        "location": "Dallas, TX",
        "description": "Senior Java development requirement.",
        "notes": "Test requirement",
        "rate_min": "70",
        "rate_max": "90",
        "currency": "USD",
        "priority": "MEDIUM",
        "experience_min": 5,
        "experience_max": 8,
        "positions": 2,
    }

    response = await client.post(
        "/api/v1/requirements",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["job_title"] == "Senior Java Developer"
    assert data["job_code"] == "REQ-TEST-001"
    assert data["status"] == RequirementStatus.DRAFT.value


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_requirement_duplicate_job_code(
    client,
    admin_headers,
    db_session,
    sample_admin,
):
    vendor, requirement_client = await create_vendor_and_client(
    db_session,
    sample_admin.id,
)

    payload = {
        "vendor_id": vendor.id,
        "client_id": requirement_client.id,
        "job_title": "Java Developer",
        "job_code": "REQ-DUPLICATE-001",
        "employment_type": "C2C",
        "work_model": "REMOTE",
        "rate_min": "60",
        "rate_max": "80",
        "currency": "USD",
        "priority": "MEDIUM",
        "experience_min": 3,
        "positions": 1,
    }

    first = await client.post(
        "/api/v1/requirements",
        json=payload,
        headers=admin_headers,
    )

    assert first.status_code == 201

    second = await client.post(
        "/api/v1/requirements",
        json=payload,
        headers=admin_headers,
    )

    assert second.status_code == 409
    assert "already exists" in second.json()["message"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_requirement_invalid_billing_range(
    client,
    admin_headers,
    db_session,
    sample_admin,
):
    vendor, requirement_client = await create_vendor_and_client(
    db_session,
    sample_admin.id,
)

    payload = {
        "vendor_id": vendor.id,
        "client_id": requirement_client.id,
        "job_title": "DevOps Engineer",
        "job_code": "REQ-RANGE-001",
        "employment_type": "C2C",
        "work_model": "REMOTE",
        "rate_min": "100",
        "rate_max": "80",
        "currency": "USD",
        "priority": "HIGH",
        "experience_min": 4,
        "positions": 1,
    }

    response = await client.post(
        "/api/v1/requirements",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 400
    assert "Minimum billing range" in response.json()["message"]