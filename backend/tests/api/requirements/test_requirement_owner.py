import pytest

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


async def create_requirement(
    http_client,
    requirement_client,
    vendor,
    admin_headers,
):
    response = await http_client.post(
        "/api/v1/requirements",
        json={
            "vendor_id": vendor.id,
            "client_id": requirement_client.id,
            "job_title": "Owner Test Requirement",
            "employment_type": "C2C",
            "work_model": "HYBRID",
            "priority": "MEDIUM",
            "experience_min": 3,
            "positions": 1,
        },
        headers=admin_headers,
    )

    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.api
@pytest.mark.asyncio
async def test_requirement_owner_reassignment_success(
    client,
    db_session,
    sample_admin,
    admin_headers,
    sample_user,
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
        f"/api/v1/requirements/{requirement['public_id']}/owner",
        json={
            "new_owner_id": sample_user.id,
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()
    assert body["owner_recruiter_id"] == sample_user.id


@pytest.mark.api
@pytest.mark.asyncio
async def test_requirement_owner_reassignment_unknown_requirement_returns_404(
    client,
    admin_headers,
    sample_user,
):
    from uuid import uuid4

    response = await client.post(
        f"/api/v1/requirements/{uuid4()}/owner",
        json={
            "new_owner_id": sample_user.id,
        },
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Requirement record not found."


@pytest.mark.api
@pytest.mark.asyncio
async def test_requirement_owner_reassignment_recruiter_forbidden(
    client,
    db_session,
    sample_admin,
    admin_headers,
    user_headers,
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
        f"/api/v1/requirements/{requirement['public_id']}/owner",
        json={
            "new_owner_id": sample_admin.id,
        },
        headers=user_headers,
    )

    assert response.status_code == 403
