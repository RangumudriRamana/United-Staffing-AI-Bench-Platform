from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.integrations.enums import IntegrationType, IntegrationStatus

class IntegrationConnectionCreateRequest(BaseModel):
    provider_name: str = Field(..., max_length=100)
    integration_type: IntegrationType
    configuration_json: dict | None = None
    credentials_reference: str | None = Field(None, max_length=255)

class IntegrationConnectionResponse(BaseModel):
    public_id: UUID
    provider_name: str
    integration_type: IntegrationType
    status: IntegrationStatus
    is_enabled: bool
    last_sync_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True

class IntegrationHealthResponse(BaseModel):
    """Outbound status model confirming health distributions for structural overview pages."""
    provider_name: str
    status: IntegrationStatus
    is_operational: bool
    latency_ms: int