from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class AccountFunnelStage(BaseModel):
    """Tracks a single checkpoint in the commercial workflow pipeline."""
    stage_name: str
    count: int = 0
    conversion_rate: float = Field(0.0, description="Percentage change from the preceding stage phase.")

class RelationshipHealthDTO(BaseModel):
    """Quantifies account engagement quality alongside structural indicators."""
    health_score: int = Field(..., ge=0, le=100)
    status_label: str  # e.g., "STRATEGIC", "STAGNANT", "AT_RISK"
    contributing_factors: list[str] = Field(default_factory=list)

class AccountResponseTimeMetrics(BaseModel):
    """Averages execution velocity signals across operational milestones."""
    avg_days_req_to_submission: float = 0.0
    avg_days_submission_to_interview: float = 0.0
    avg_days_interview_to_feedback: float = 0.0

class VendorAnalyticsSummaryResponse(BaseModel):
    """ Curated organizational data matrix detailing customer health metrics. """
    vendor_public_id: UUID
    vendor_name: str
    funnel: list[AccountFunnelStage] = Field(default_factory=list)
    health: RelationshipHealthDTO
    velocity: AccountResponseTimeMetrics

    class Config:
        from_attributes = True