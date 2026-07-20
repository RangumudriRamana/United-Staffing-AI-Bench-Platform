from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.reporting.enums import ReportCategory, ExportFormat, ReportExecutionStatus

class ReportDefinitionCreateRequest(BaseModel):
    name: str = Field(..., max_length=150)
    report_type: ReportCategory
    output_format: ExportFormat = ExportFormat.CSV
    parameters_json: dict | None = None
    schedule: str | None = Field(None, max_length=100)

class ReportDefinitionResponse(BaseModel):
    public_id: UUID
    name: str
    report_type: ReportCategory
    output_format: ExportFormat
    parameters_json: dict | None
    schedule: str | None
    is_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ReportExecutionResponse(BaseModel):
    id: int
    status: ReportExecutionStatus
    file_location: str | None
    duration_ms: int
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True