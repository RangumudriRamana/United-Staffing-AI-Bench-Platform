import pytest

from app.requirements.enums import RequirementStatus
from tests.factories.vendors import VendorFactory, ClientFactory


async def create_vendor_and_client(db_session, created_by):
    vendor = VendorFactory.build(created_by=created_by)
    db_session.add(vendor)
    await db_session.flush()

    requirement_client = ClientFactory.build(
        vendor_id=vendor.id,
        created_by=created_by,
    )
    db_session.add(requirement_client)
    await db_session.flush()

    return vendor, requirement_client


async def create_requirement(
    http_client,
    requirement_client,
    vendor,
    admin_headers,
):
    response = await http_client.post(
        "/api/v1/requirements",
        headers=admin_headers,
        json={
            "vendor_id": vendor.id,
            "client_id": requirement_client.id,
            "job_title": "Senior Java Developer",
            "employment_type": "C2C",
            "work_model": "HYBRID",
            "priority": "MEDIUM",
            "experience_min": 3,
            "positions": 1,
        },
    )

    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_requirement_transition_draft_to_open(
    client,
    db_session,
    sample_admin,
    admin_headers,
):
    vendor, requirement_client = await create_vendor_and_client(
        db_session,
        sample_admin.id,
    )

    requirement = await create_requirement(
        client,
        requirement_client,
        vendor,
        admin_headers,
    )

    response = await client.post(
        f"/api/v1/requirements/{requirement['public_id']}/transition",
        headers=admin_headers,
        json={
            "target_status": "OPEN",
            "reason": "Requirement approved for sourcing.",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == RequirementStatus.OPEN.value


@pytest.mark.asyncio
async def test_requirement_invalid_transition_returns_400(
    client,
    db_session,
    sample_admin,
    admin_headers,
):
    vendor, requirement_client = await create_vendor_and_client(
        db_session,
        sample_admin.id,
    )

    requirement = await create_requirement(
        client,
        requirement_client,
        vendor,
        admin_headers,
    )

    response = await client.post(
        f"/api/v1/requirements/{requirement['public_id']}/transition",
        headers=admin_headers,
        json={
            "target_status": "FILLED",
            "reason": "Invalid transition test.",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_requirement_transition_unknown_requirement_returns_404(
    client,
    admin_headers,
):
    from uuid import uuid4

    response = await client.post(
        f"/api/v1/requirements/{uuid4()}/transition",
        headers=admin_headers,
        json={
            "target_status": "OPEN",
            "reason": "Unknown requirement test.",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_requirement_same_status_transition_is_noop(
    client,
    db_session,
    sample_admin,
    admin_headers,
):
    vendor, requirement_client = await create_vendor_and_client(
        db_session,
        sample_admin.id,
    )

    requirement = await create_requirement(
        client,
        requirement_client,
        vendor,
        admin_headers,
    )

    response = await client.post(
        f"/api/v1/requirements/{requirement['public_id']}/transition",
        headers=admin_headers,
        json={
            "target_status": "DRAFT",
            "reason": "Same status test.",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == RequirementStatus.DRAFT.value