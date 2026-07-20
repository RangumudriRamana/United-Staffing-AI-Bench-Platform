from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.communications.models import Communication
from app.communications.schemas import CommunicationResponse

class TimelineComposer:
    """Read-optimized composition component that gathers distinct streams into a unified chronology."""
    
    @staticmethod
    def merge_and_sort_activities(communications: list[Communication]) -> list[dict]:
        """Combines system events and raw records into standardized chronological payloads."""
        feed = []
        for c in communications:
            feed.append({
                "source": "COMMUNICATION",
                "public_id": str(c.public_id),
                "type": c.communication_type.value,
                "direction": c.direction.value,
                "title": c.subject,
                "content": c.body_preview,
                "timestamp": c.occurred_at.isoformat()
            })
            
        # Execute global descending chronological sorting sequence
        feed.sort(key=lambda x: x["timestamp"], reverse=True)
        return feed