import re
from typing import Literal
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from app.consultants.enums import VisaStatus, MarketingStatus, RateType


class ConsultantBase(BaseModel):
    """Internal core contract containing fields shared across creation and responses."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    current_title: str | None = Field(None, max_length=150)
    total_experience_years: int = Field(default=0, ge=0)
    current_location: str | None = Field(None, max_length=150)
    preferred_location: str | None = Field(None, max_length=150)
    relocation_available: bool = Field(default=False)
    remote_preference: str = Field(default="Hybrid", max_length=50)
    visa_status: VisaStatus
    visa_expiration: date | None = Field(None)
    work_authorized: bool = Field(default=True)
    availability_date: date | None = Field(None)
    marketing_status: MarketingStatus = Field(default=MarketingStatus.NEW)
    rate_type: RateType = Field(default=RateType.HOURLY)
    expected_rate: Decimal | None = Field(None, ge=0)

    # --- Data Invariant Normalizations ---
    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Enforces uniform lowercasing and trims loose padding whitespace."""
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, v: str | None) -> str | None:
        """Strips out structural formatting artifacts to leave numeric sequences."""
        if v and isinstance(v, str):
            return re.sub(r"\D", "", v)
        return v


class ConsultantCreateRequest(ConsultantBase):
    """Validates structural fields required to initialize a new bench profile record."""
    pass


class UpdateConsultantRequest(BaseModel):
    """Enables clean HTTP PATCH semantics by exposing every record attribute as optional."""
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    current_title: str | None = Field(None, max_length=150)
    total_experience_years: int | None = Field(None, ge=0)
    current_location: str | None = Field(None, max_length=150)
    preferred_location: str | None = Field(None, max_length=150)
    relocation_available: bool | None = None
    remote_preference: str | None = Field(None, max_length=50)
    visa_status: VisaStatus | None = None
    visa_expiration: date | None = None
    work_authorized: bool | None = None
    availability_date: date | None = None
    marketing_status: MarketingStatus | None = None
    rate_type: RateType | None = None
    expected_rate: Decimal | None = Field(None, ge=0)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, v: str | None) -> str | None:
        if v and isinstance(v, str):
            return re.sub(r"\D", "", v)
        return v


class ConsultantResponse(ConsultantBase):
    """Explicit response model preventing leaks of auto-incrementing surrogate primary keys."""
    public_id: UUID
    created_at: datetime
    updated_at: datetime

    # Binds directly to modern Pydantic v2 configuration parameters
    model_config = ConfigDict(from_attributes=True)


class ConsultantFilterParams(BaseModel):
    """Data filter mappings consumed directly by repository query orchestrators."""
    visa_status: VisaStatus | None = None
    marketing_status: MarketingStatus | None = None
    recruiter_id: int | None = None
    current_location: str | None = None
    remote_preference: str | None = None
    availability_date: date | None = None
    minimum_experience: int | None = Field(None, ge=0)
    maximum_rate: Decimal | None = Field(None, ge=0)
    search: str | None = None

class AdvancedSearchCriteria(BaseModel):
    """Unified request model capturing cross-entity search filters and technology array matches."""
    technologies: list[str] = Field(default_factory=list)
    match_mode: Literal["ANY", "ALL"] = "ANY"
    min_tech_experience: int | None = Field(None, ge=0)
    
    # Core domain filters
    visa_status: list[VisaStatus] = Field(default_factory=list)
    marketing_status: list[MarketingStatus] = Field(default_factory=list)
    current_location: str | None = Field(None, max_length=150)
    remote_preference: str | None = Field(None, max_length=50)
    
    # Text-box query search across multiple fields
    search: str | None = None

class ConsultantStatusTransitionRequest(BaseModel):
    """Payload schema governing formal business state machine adjustments."""
    target_status: MarketingStatus
    reason: str | None = Field(None, max_length=255, description="Contextual reason for the state transition.")
    notes: str | None = Field(None, max_length=500, description="Supplementary operational feedback notes.")