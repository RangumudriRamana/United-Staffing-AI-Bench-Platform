from datetime import datetime
from pydantic import BaseModel, Field
from app.analytics.schemas import RecruiterKPIMetrics

class FollowUpItem(BaseModel):
    """Represents a time-sensitive actionable task entry pushed to the recruiter."""
    task_type: str = Field(..., description="e.g., 'OFFER_EXPIRATION', 'STALLED_SUBMISSION'")
    description: str
    severity: str = Field("MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")
    target_public_id: str | None = None

class DashboardTimelineEvent(BaseModel):
    """Lightweight projection item mapping recent actions from the event stream ledger."""
    event_type: str
    summary: str
    occurred_at: datetime
    actor_id: int | None

class RecruiterDashboardResponse(BaseModel):
    """Curated aggregate collection model transmitting all workspace widgets simultaneously."""
    summary: RecruiterKPIMetrics
    followups: list[FollowUpItem] = Field(default_factory=list)
    timeline: list[DashboardTimelineEvent] = Field(default_factory=list)

    class Config:
        from_attributes = True