from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.audit.enums import AuditActionType

class AuditRecordCreatePayload(BaseModel):
    """Payload block emitted by internal platform audit publishers."""
    actor_user_id: int | None = None
    action_type: AuditActionType
    source_context: str = Field(..., max_length=100)
    correlation_id: str | None = Field(None, max_length=50)
    entity_type: str = Field(..., max_length=50)
    entity_public_id: str = Field(..., max_length=50)
    entity_version: int = 1
    before_snapshot_json: dict | None = None
    after_snapshot_json: dict | None = None
    metadata_json: dict | None = None

class AuditRecordResponse(BaseModel):
    """Outbound tracking DTO serving verified history lines back to governance screens."""
    public_id: UUID
    occurred_at: datetime
    actor_user_id: int | None
    action_type: AuditActionType
    source_context: str
    correlation_id: str | None
    entity_type: str
    entity_public_id: str
    entity_version: int
    before_snapshot_json: dict | None
    after_snapshot_json: dict | None
    metadata_json: dict | None

    class Config:
        from_attributes = True