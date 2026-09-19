from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.submissions.enums import (
    SubmissionStatus,
    EmploymentType,
    InterviewType,
    InterviewStatus,
    OfferStatus,
    PlacementStatus,
)


# ============================================================
# Submission
# ============================================================

class SubmissionCreateRequest(BaseModel):
    consultant_public_id: UUID
    vendor_public_id: UUID
    vendor_contact_public_id: UUID | None = None
    client_public_id: UUID
    requirement_public_id: UUID | None = None

    client_name_snapshot: str = Field(..., max_length=150)
    vendor_name_snapshot: str = Field(..., max_length=150)
    job_title_snapshot: str = Field(..., max_length=150)

    job_id: str | None = Field(None, max_length=100)

    job_title: str = Field(..., max_length=150)
    job_location: str | None = Field(None, max_length=150)

    employment_type: EmploymentType = EmploymentType.C2C

    rate: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)

    expected_start_date: date | None = None

    submission_notes: str | None = Field(
        default=None,
        max_length=2000,
    )


class SubmissionUpdateRequest(BaseModel):
    vendor_contact_id: int | None = None
    requirement_id: int | None = None

    job_id: str | None = None
    job_title: str | None = None
    job_location: str | None = None

    employment_type: EmploymentType | None = None

    rate: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, max_length=3)

    expected_start_date: date | None = None

    submission_notes: str | None = Field(
        default=None,
        max_length=2000,
    )


class SubmissionTransitionRequest(BaseModel):
    target_status: SubmissionStatus

    reason: str | None = Field(
        default=None,
        max_length=255,
    )

    notes: str | None = Field(
        default=None,
        max_length=500,
    )


class SubmissionResponse(BaseModel):
    public_id: UUID

    consultant_id: int
    submitted_by: int

    vendor_id: int
    vendor_contact_id: int | None

    client_id: int
    requirement_id: int | None

    client_name_snapshot: str
    vendor_name_snapshot: str
    job_title_snapshot: str

    job_id: str | None

    job_title: str
    job_location: str | None

    employment_type: EmploymentType

    rate: Decimal
    currency: str

    submission_status: SubmissionStatus

    submitted_at: datetime
    expected_start_date: date | None

    submission_notes: str | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Interview
# ============================================================

class InterviewCreateRequest(BaseModel):
    round_number: int = Field(default=1, ge=1)

    interview_type: InterviewType

    scheduled_at: datetime

    timezone: str = Field(
        default="UTC",
        max_length=50,
    )

    interviewer: str | None = Field(
        default=None,
        max_length=100,
    )


class InterviewResponse(BaseModel):
    public_id: UUID
    round_number: int
    interview_type: InterviewType
    status: InterviewStatus
    scheduled_at: datetime
    timezone: str
    interviewer: str | None
    feedback: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Offer
# ============================================================

class OfferCreateRequest(BaseModel):
    offered_rate: Decimal = Field(..., gt=0)

    currency: str = Field(
        default="USD",
        max_length=3,
    )

    start_date: date

    expiration_date: date | None = None

    notes: str | None = Field(
        default=None,
        max_length=500,
    )


class OfferResponse(BaseModel):
    public_id: UUID
    offered_rate: Decimal
    currency: str
    start_date: date
    expiration_date: date | None
    offer_status: OfferStatus
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Placement
# ============================================================

class PlacementCreateRequest(BaseModel):
    started_on: date

    ended_on: date | None = None

    billing_rate: Decimal = Field(..., gt=0)

    pay_rate: Decimal = Field(..., gt=0)


class PlacementResponse(BaseModel):
    public_id: UUID
    started_on: date
    ended_on: date | None
    billing_rate: Decimal
    pay_rate: Decimal
    placement_status: PlacementStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SubmissionHistoryResponse(BaseModel):
    id: int
    submission_id: int
    changed_by: int
    status: SubmissionStatus
    effective_from: datetime
    effective_until: datetime | None
    reason: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientFeedbackResponse(BaseModel):
    id: int
    submission_id: int
    author: str
    rating: int
    feedback: str
    received_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConsultantSummaryResponse(BaseModel):
    public_id: UUID
    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class VendorSummaryResponse(BaseModel):
    public_id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class VendorContactSummaryResponse(BaseModel):
    public_id: UUID
    name: str
    title: str | None
    email: str
    phone: str | None

    model_config = ConfigDict(from_attributes=True)


class ClientSummaryResponse(BaseModel):
    public_id: UUID
    name: str
    display_name: str | None

    model_config = ConfigDict(from_attributes=True)


class SubmissionDetailResponse(SubmissionResponse):
    consultant: ConsultantSummaryResponse | None = None
    vendor: VendorSummaryResponse | None = None
    vendor_contact: VendorContactSummaryResponse | None = None
    client: ClientSummaryResponse | None = None

    history: list[SubmissionHistoryResponse] = []
    interviews: list[InterviewResponse] = []
    feedback: list[ClientFeedbackResponse] = []
    offers: list[OfferResponse] = []
    placements: list[PlacementResponse] = []


# ============================================================
# Search / List
# ============================================================

class SubmissionSearchFilters(BaseModel):
    consultant_id: int | None = None
    vendor_id: int | None = None
    client_id: int | None = None
    requirement_id: int | None = None
    submission_status: SubmissionStatus | None = None
    employment_type: EmploymentType | None = None
    job_title: str | None = None
    page: int = 1
    page_size: int = 25


class SubmissionListResponse(BaseModel):
    items: list[SubmissionResponse]
    total: int
    page: int
    page_size: int