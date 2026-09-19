import pytest

from app.marketing.enums import (
    MarketingActivityType,
    MarketingChannel,
    MarketingOutcome,
)
from app.models.user import User
from app.vendors.models import Vendor, VendorContact, Client
from app.consultants.models import Consultant


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_marketing_activity_with_follow_up(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    vendor = Vendor(
        name="Marketing Test Vendor",
        created_by=sample_admin.id,
    )
    db_session.add(vendor)
    await db_session.flush()

    contact = VendorContact(
        vendor_id=vendor.id,
        name="Marketing Recruiter",
        email="marketing.recruiter@testvendor.com",
    )
    db_session.add(contact)

    consultant = Consultant(
        first_name="Marketing",
        last_name="Test",
        email="marketing.test@example.com",
        visa_status="H1B",
        recruiter_id=sample_admin.id,
    )
    db_session.add(consultant)

    await db_session.commit()
    await db_session.refresh(vendor)
    await db_session.refresh(contact)
    await db_session.refresh(consultant)

    response = await client.post(
        "/api/v1/marketing/activities",
        json={
            "consultant_public_id": str(consultant.public_id),
            "vendor_public_id": str(vendor.public_id),
            "vendor_contact_public_id": str(contact.public_id),
            "activity_type": MarketingActivityType.PROFILE_MARKETING.value,
            "channel": MarketingChannel.EMAIL.value,
            "outcome": MarketingOutcome.SENT.value,
            "subject": "Consultant profile marketed",
            "notes": "Profile sent to vendor recruiter.",
            "follow_up_required": True,
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["consultant_public_id"] == str(consultant.public_id)
    assert data["vendor_public_id"] == str(vendor.public_id)
    assert data["vendor_contact_public_id"] == str(contact.public_id)

    assert data["activity_type"] == "PROFILE_MARKETING"
    assert data["channel"] == "EMAIL"
    assert data["outcome"] == "SENT"
    assert data["follow_up_required"] is True

@pytest.mark.api
@pytest.mark.asyncio
async def test_list_marketing_activities_for_consultant(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    vendor = Vendor(
        name="Marketing List Vendor",
        created_by=sample_admin.id,
    )
    db_session.add(vendor)
    await db_session.flush()

    contact = VendorContact(
        vendor_id=vendor.id,
        name="List Recruiter",
        email="list.recruiter@testvendor.com",
    )
    db_session.add(contact)

    consultant = Consultant(
        first_name="List",
        last_name="Test",
        email="list.test@example.com",
        visa_status="H1B",
        recruiter_id=sample_admin.id,
    )
    db_session.add(consultant)

    await db_session.commit()
    await db_session.refresh(vendor)
    await db_session.refresh(contact)
    await db_session.refresh(consultant)

    create_response = await client.post(
        "/api/v1/marketing/activities",
        json={
            "consultant_public_id": str(consultant.public_id),
            "vendor_public_id": str(vendor.public_id),
            "vendor_contact_public_id": str(contact.public_id),
            "activity_type": MarketingActivityType.PROFILE_MARKETING.value,
            "channel": MarketingChannel.EMAIL.value,
            "outcome": MarketingOutcome.SENT.value,
            "subject": "List test marketing",
            "notes": "Testing activity history.",
            "follow_up_required": False,
        },
        headers=admin_headers,
    )

    assert create_response.status_code == 201

    list_response = await client.get(
        f"/api/v1/marketing/activities/consultant/{consultant.public_id}",
        headers=admin_headers,
    )

    assert list_response.status_code == 200

    data = list_response.json()

    assert len(data) == 1
    assert data[0]["consultant_public_id"] == str(consultant.public_id)
    assert data[0]["vendor_public_id"] == str(vendor.public_id)
    assert data[0]["vendor_contact_public_id"] == str(contact.public_id)
    assert data[0]["activity_type"] == "PROFILE_MARKETING"
    assert data[0]["channel"] == "EMAIL"
    assert data[0]["outcome"] == "SENT"

@pytest.mark.api
@pytest.mark.asyncio
async def test_get_marketing_activity_by_public_id(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    vendor = Vendor(
        name="Marketing Get Vendor",
        created_by=sample_admin.id,
    )
    db_session.add(vendor)
    await db_session.flush()

    contact = VendorContact(
        vendor_id=vendor.id,
        name="Get Recruiter",
        email="get.recruiter@testvendor.com",
    )
    db_session.add(contact)

    consultant = Consultant(
        first_name="Get",
        last_name="Test",
        email="get.test@example.com",
        visa_status="H1B",
        recruiter_id=sample_admin.id,
    )
    db_session.add(consultant)

    await db_session.commit()
    await db_session.refresh(vendor)
    await db_session.refresh(contact)
    await db_session.refresh(consultant)

    create_response = await client.post(
        "/api/v1/marketing/activities",
        json={
            "consultant_public_id": str(consultant.public_id),
            "vendor_public_id": str(vendor.public_id),
            "vendor_contact_public_id": str(contact.public_id),
            "activity_type": MarketingActivityType.PROFILE_MARKETING.value,
            "channel": MarketingChannel.EMAIL.value,
            "outcome": MarketingOutcome.SENT.value,
            "subject": "Get test marketing",
            "notes": "Testing single activity retrieval.",
            "follow_up_required": False,
        },
        headers=admin_headers,
    )

    assert create_response.status_code == 201

    created = create_response.json()
    activity_public_id = created["public_id"]

    get_response = await client.get(
        f"/api/v1/marketing/activities/{activity_public_id}",
        headers=admin_headers,
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["public_id"] == activity_public_id
    assert data["consultant_public_id"] == str(consultant.public_id)
    assert data["vendor_public_id"] == str(vendor.public_id)
    assert data["vendor_contact_public_id"] == str(contact.public_id)
    assert data["activity_type"] == "PROFILE_MARKETING"
    assert data["channel"] == "EMAIL"
    assert data["outcome"] == "SENT"
    assert data["subject"] == "Get test marketing"
    assert data["follow_up_required"] is False

@pytest.mark.api
@pytest.mark.asyncio
async def test_create_marketing_activity_rejects_contact_from_different_vendor(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    vendor_a = Vendor(
        name="Vendor A",
        created_by=sample_admin.id,
    )
    vendor_b = Vendor(
        name="Vendor B",
        created_by=sample_admin.id,
    )
    db_session.add_all([vendor_a, vendor_b])
    await db_session.flush()

    contact_a = VendorContact(
        vendor_id=vendor_a.id,
        name="Vendor A Recruiter",
        email="recruiter@vendora.com",
    )
    db_session.add(contact_a)

    consultant = Consultant(
        first_name="Integrity",
        last_name="Test",
        email="integrity.test@example.com",
        visa_status="H1B",
        recruiter_id=sample_admin.id,
    )
    db_session.add(consultant)

    await db_session.commit()
    await db_session.refresh(vendor_b)
    await db_session.refresh(contact_a)
    await db_session.refresh(consultant)

    response = await client.post(
        "/api/v1/marketing/activities",
        json={
            "consultant_public_id": str(consultant.public_id),
            "vendor_public_id": str(vendor_b.public_id),
            "vendor_contact_public_id": str(contact_a.public_id),
            "activity_type": MarketingActivityType.PROFILE_MARKETING.value,
            "channel": MarketingChannel.EMAIL.value,
            "outcome": MarketingOutcome.SENT.value,
            "subject": "Invalid vendor contact test",
            "notes": "Contact belongs to another vendor.",
            "follow_up_required": False,
        },
        headers=admin_headers,
    )

    assert response.status_code == 400

@pytest.mark.api
@pytest.mark.asyncio
async def test_create_marketing_activity_rejects_client_from_different_vendor(
    client,
    sample_admin: User,
    admin_headers,
    db_session,
):
    vendor_a = Vendor(
        name="Client Vendor A",
        created_by=sample_admin.id,
    )
    vendor_b = Vendor(
        name="Client Vendor B",
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
    db_session.add(client_a)

    consultant = Consultant(
        first_name="Client",
        last_name="Integrity",
        email="client.integrity@example.com",
        visa_status="H1B",
        recruiter_id=sample_admin.id,
    )
    db_session.add(consultant)

    await db_session.commit()
    await db_session.refresh(vendor_b)
    await db_session.refresh(client_a)
    await db_session.refresh(consultant)

    response = await client.post(
        "/api/v1/marketing/activities",
        json={
            "consultant_public_id": str(consultant.public_id),
            "vendor_public_id": str(vendor_b.public_id),
            "client_public_id": str(client_a.public_id),
            "activity_type": MarketingActivityType.CLIENT_OUTREACH.value,
            "channel": MarketingChannel.EMAIL.value,
            "outcome": MarketingOutcome.SENT.value,
            "subject": "Invalid client vendor test",
            "notes": "Client belongs to another vendor.",
            "follow_up_required": False,
        },
        headers=admin_headers,
    )

    assert response.status_code == 400