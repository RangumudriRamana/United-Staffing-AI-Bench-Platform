from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.marketing.enums import (
    MarketingActivityType,
    MarketingChannel,
    MarketingOutcome,
)


class MarketingActivityCreateRequest(BaseModel):
    consultant_public_id: UUID
    vendor_public_id: UUID
    vendor_contact_public_id: UUID | None = None
    client_public_id: UUID | None = None

    activity_type: MarketingActivityType
    channel: MarketingChannel
    outcome: MarketingOutcome

    subject: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    follow_up_required: bool = False
    occurred_at: datetime | None = None


class MarketingActivityResponse(BaseModel):
    public_id: UUID

    consultant_public_id: UUID
    vendor_public_id: UUID
    vendor_contact_public_id: UUID | None
    client_public_id: UUID | None

    performed_by: int

    activity_type: MarketingActivityType
    channel: MarketingChannel
    outcome: MarketingOutcome

    subject: str | None
    notes: str | None
    follow_up_required: bool
    occurred_at: datetime

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)