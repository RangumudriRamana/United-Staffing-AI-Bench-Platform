from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from typing import Any
from pydantic import BaseModel, Field
from app.submissions.enums import SubmissionStatus, EmploymentType, InterviewType, InterviewStatus, OfferStatus, PlacementStatus

class SubmissionCreateRequest(BaseModel):
    """Payload validating new inbound opportunity submission tracking records."""
    consultant_id: int
    client_name: str = Field(..., max_length=150)
    job_title: str = Field(..., max_length=150)
    job_location: str | None = Field(None, max_length=150)
    employment_type: EmploymentType = EmploymentType.C2C
    rate: Decimal = Field(..., gt=0)
    currency: str = Field("USD", max_length=3)
    expected_start_date: date | None = None

class SubmissionTransitionRequest(BaseModel):
    """Payload governing formal state machine transition steps."""
    target_status: SubmissionStatus
    reason: str | None = Field(None, max_length=255)
    notes: str | None = Field(None, max_length=500)

class InterviewCreateRequest(BaseModel):
    """Payload structuring upcoming technical or client interview loops."""
    interview_type: InterviewType
    scheduled_at: datetime
    timezone: str = "UTC"
    interviewer: str | None = Field(None, max_length=100)

class OfferCreateRequest(BaseModel):
    """Payload managing formal contract offer rate proposals."""
    offered_rate: Decimal = Field(..., gt=0)
    start_date: datetime
    notes: str | None = Field(None, max_length=500)

class PlacementCreateRequest(BaseModel):
    """Payload locking down active project financial splits."""
    consultant_public_id: UUID
    billing_rate: Decimal = Field(..., gt=0)
    pay_rate: Decimal = Field(..., gt=0)

# --- Serialization / Response Wrappers ---

class SubmissionResponse(BaseModel):
    """Thin transport outbound wrapper matching platform response schemas."""
    public_id: UUID
    consultant_id: int
    client_name: str
    job_title: str
    employment_type: EmploymentType
    rate: Decimal
    currency: str
    submission_status: SubmissionStatus
    submitted_at: datetime
    
    # Nested arrays automatically filled by eager loading detailed strategies
    history: list[Any] = []
    interviews: list[Any] = []
    offers: list[Any] = []
    placements: list[Any] = []

    class Config:
        from_attributes = True