from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.communications.models import Communication
from app.communications.enums import CommunicationType, CommunicationDirection
from app.communications.schemas import InternalNoteRequest
from app.communications.timeline import TimelineComposer

class CommunicationService:
    """Orchestrates persistent messaging inputs, internal annotations updates, and timeline mapping pipelines."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_internal_note(self, payload: InternalNoteRequest, author_user_id: int) -> Communication:
        """Appends a permanent team annotation to the shared entity timeline registry."""
        new_note = Communication(
            sender_user_id=author_user_id,
            communication_type=CommunicationType.INTERNAL_NOTE,
            direction=CommunicationDirection.INTERNAL,
            subject=payload.subject,
            body_preview=payload.body_preview,
            related_entity_type=payload.related_entity_type.upper().strip(),
            related_entity_id=payload.related_entity_id,
            occurred_at=datetime.now(timezone.utc)
        )
        self.db.add(new_note)
        await self.db.commit()
        return new_note

    async def fetch_entity_unified_timeline(self, entity_type: str, entity_id: int) -> list[dict]:
        """Queries localized data subsets and delegates formatting down to the composer components."""
        stmt = (
            select(Communication)
            .where(
                Communication.related_entity_type == entity_type.upper().strip(),
                Communication.related_entity_id == entity_id
            )
            .order_by(desc(Communication.occurred_at))
        )
        res = await self.db.execute(stmt)
        records = res.scalars().all()

        return TimelineComposer.merge_and_sort_activities(list(records))