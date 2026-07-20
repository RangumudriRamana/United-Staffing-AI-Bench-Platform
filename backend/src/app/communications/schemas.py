from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.communications.enums import CommunicationType, CommunicationDirection

class InternalNoteRequest(BaseModel):
    """Payload parameter model creating simple localized user annotations."""
    related_entity_type: str = Field(..., max_length=50)
    related_entity_id: int
    subject: str = Field(..., max_length=255)
    body_preview: str

class CommunicationResponse(BaseModel):
    """Outbound serialization DTO serving full data logs back to feed panels."""
    public_id: UUID
    sender_user_id: int | None
    communication_type: CommunicationType
    direction: CommunicationDirection
    subject: str
    body_preview: str | None
    related_entity_type: str
    related_entity_id: int
    occurred_at: datetime

    class Config:
        from_attributes = True