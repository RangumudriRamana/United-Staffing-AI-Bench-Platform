from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from typing import Any
from pydantic import BaseModel, Field
from app.requirements.enums import RequirementStatus, WorkModel, RequirementPriority
from app.submissions.enums import EmploymentType, DocumentType

class CreateRequirementRequest(BaseModel):
    """Payload validating new inbound corporate position specifications."""
    vendor_id: int
    client_id: int
    job_title: str = Field(..., max_length=150)
    job_code: str | None = Field(None, max_length=50)
    employment_type: EmploymentType = EmploymentType.C2C
    work_model: WorkModel = WorkModel.HYBRID
    location: str | None = Field(None, max_length=150)
    description: str | None = None
    notes: str | None = Field(None, max_length=1000)
    
    rate_min: Decimal | None = Field(None, gt=0)
    rate_max: Decimal | None = Field(None, gt=0)
    currency: str = Field("USD", max_length=3)
    priority: RequirementPriority = RequirementPriority.MEDIUM
    experience_min: int = Field(0, ge=0)
    experience_max: int | None = Field(None, ge=0)
    positions: int = Field(1, gt=0)
    target_start_date: date | None = None

class RequirementTransitionRequest(BaseModel):
    """Payload governing formal state machine updates."""
    target_status: RequirementStatus
    reason: str | None = Field(None, max_length=255)
    notes: str | None = Field(None, max_length=500)

class RequirementTechnologyRequest(BaseModel):
    """Payload managing technical skill constraint assignments."""
    technology_id: int
    minimum_years: int = Field(1, ge=0)
    mandatory: bool = True
    notes: str | None = Field(None, max_length=255)

class RequirementDocumentRequest(BaseModel):
    """Payload managing compliance document requirements."""
    document_type: DocumentType
    mandatory: bool = True
    notes: str | None = Field(None, max_length=255)

class OwnerReassignmentRequest(BaseModel):
    """Payload handling administrative recruiter assignment changes."""
    new_owner_id: int

# --- Response Serialization DTOs ---

class RequirementTechnologyResponse(BaseModel):
    technology_id: int
    minimum_years: int
    mandatory: bool
    notes: str | None

    class Config:
        from_attributes = True

class RequirementResponse(BaseModel):
    """Unified serialization model detailing full aggregate trees for screens."""
    public_id: UUID
    vendor_id: int
    client_id: int
    owner_recruiter_id: int
    job_title: str
    job_code: str | None
    employment_type: EmploymentType
    work_model: WorkModel
    location: str | None
    rate_min: Decimal | None
    rate_max: Decimal | None
    currency: str
    priority: RequirementPriority
    status: RequirementStatus
    positions: int
    received_date: datetime
    target_start_date: date | None
    description: str | None
    notes: str | None
    
    # Eagerly loaded child tables
    technologies: list[RequirementTechnologyResponse] = []
    history: list[Any] = []

    class Config:
        from_attributes = True