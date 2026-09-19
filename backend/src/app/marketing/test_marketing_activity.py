import pytest

from app.marketing.enums import (
    MarketingActivityType,
    MarketingChannel,
    MarketingOutcome,
)
from app.models.user import User
from app.vendors.models import Vendor, VendorContact
from app.consultants.models import Consultant


@pytest.mark.api
@pytest.mark.asyncio
async def test_create_marketing_activity_with_follow_up(
    client,
    sample_admin: User,
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
        headers={
            "Authorization": f"Bearer {sample_admin.access_token}",
        },
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