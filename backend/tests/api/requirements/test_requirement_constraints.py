import pytest
from sqlalchemy import select

from app.consultants.enums import DocumentType
from app.consultants.models import Technology, TechnologyCategory
from app.requirements.models import Requirement
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


async def create_technologies(db_session):
    category = TechnologyCategory(
        name="Backend Engineering",
        display_name="Backend Engineering",
        slug="backend-engineering",
        is_active=True,
    )
    db_session.add(category)
    await db_session.flush()

    java = Technology(
        name="Java",
        display_name="Java",
        slug="java",
        category_id=category.id,
        is_active=True,
    )

    python = Technology(
        name="Python",
        display_name="Python",
        slug="python",
        category_id=category.id,
        is_active=True,
    )

    db_session.add_all([java, python])
    await db_session.flush()

    return java, python


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
            "job_title": "Senior Java Developer",
            "job_code": "REQ-CONSTRAINT-TEST",
            "employment_type": "C2C",
            "work_model": "HYBRID",
            "location": "Dallas, TX",
            "description": "Constraint test requirement.",
            "rate_min": 70,
            "rate_max": 90,
            "currency": "USD",
            "priority": "MEDIUM",
            "experience_min": 5,
            "experience_max": 8,
            "positions": 1,
        },
        headers=admin_headers,
    )

    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.api
@pytest.mark.asyncio
async def test_assign_requirement_technology_success(
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

    requirement_row = await db_session.scalar(
        select(Requirement).where(
            Requirement.public_id == requirement["public_id"]
        )
    )
    assert requirement_row is not None

    java, _ = await create_technologies(db_session)

    response = await client.post(
        f"/api/v1/requirements/{requirement['public_id']}/technologies",
        json={
            "technology_id": java.id,
            "minimum_years": 5,
            "mandatory": True,
            "notes": "Core Java experience required.",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201, response.text

    body = response.json()
    assert body["requirement_id"] == requirement_row.id
    assert body["technology_id"] == java.id
    assert body["minimum_years"] == 5
    assert body["mandatory"] is True


@pytest.mark.api
@pytest.mark.asyncio
async def test_assign_requirement_duplicate_technology_returns_400(
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

    java, _ = await create_technologies(db_session)

    payload = {
        "technology_id": java.id,
        "minimum_years": 5,
        "mandatory": True,
    }

    first_response = await client.post(
        f"/api/v1/requirements/{requirement['public_id']}/technologies",
        json=payload,
        headers=admin_headers,
    )

    assert first_response.status_code == 201, first_response.text

    duplicate_response = await client.post(
        f"/api/v1/requirements/{requirement['public_id']}/technologies",
        json=payload,
        headers=admin_headers,
    )

    assert duplicate_response.status_code == 400
    assert (
        duplicate_response.json()["message"]
        == "Target technical parameter already mapped to requirement details."
    )


@pytest.mark.api
@pytest.mark.asyncio
async def test_assign_requirement_negative_experience_returns_400(
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
        f"/api/v1/requirements/{requirement['public_id']}/technologies",
        json={
            "technology_id": 999999,
            "minimum_years": -1,
            "mandatory": False,
        },
        headers=admin_headers,
    )

    assert response.status_code in (400, 422)


@pytest.mark.api
@pytest.mark.asyncio
async def test_assign_requirement_technology_unknown_requirement_returns_404(
    client,
    admin_headers,
):
    from uuid import uuid4

    response = await client.post(
        f"/api/v1/requirements/{uuid4()}/technologies",
        json={
            "technology_id": 999999,
            "minimum_years": 3,
            "mandatory": True,
        },
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Requirement record not found."


@pytest.mark.api
@pytest.mark.asyncio
async def test_assign_requirement_document_success(
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

    requirement_row = await db_session.scalar(
        select(Requirement).where(
            Requirement.public_id == requirement["public_id"]
        )
    )
    assert requirement_row is not None

    response = await client.post(
        f"/api/v1/requirements/{requirement['public_id']}/documents",
        json={
            "document_type": DocumentType.RESUME.value,
            "mandatory": True,
            "notes": "Current resume required.",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201, response.text

    body = response.json()
    assert body["requirement_id"] == requirement_row.id
    assert body["document_type"] == DocumentType.RESUME.value
    assert body["mandatory"] is True


@pytest.mark.api
@pytest.mark.asyncio
async def test_assign_requirement_duplicate_document_returns_400(
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

    payload = {
        "document_type": DocumentType.RESUME.value,
        "mandatory": True,
    }

    first_response = await client.post(
        f"/api/v1/requirements/{requirement['public_id']}/documents",
        json=payload,
        headers=admin_headers,
    )

    assert first_response.status_code == 201, first_response.text

    duplicate_response = await client.post(
        f"/api/v1/requirements/{requirement['public_id']}/documents",
        json=payload,
        headers=admin_headers,
    )

    assert duplicate_response.status_code == 400
    assert (
        duplicate_response.json()["message"]
        == "Target compliance document profile already linked."
    )


@pytest.mark.api
@pytest.mark.asyncio
async def test_assign_requirement_document_unknown_requirement_returns_404(
    client,
    admin_headers,
):
    from uuid import uuid4

    response = await client.post(
        f"/api/v1/requirements/{uuid4()}/documents",
        json={
            "document_type": DocumentType.RESUME.value,
            "mandatory": True,
        },
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Requirement record not found."