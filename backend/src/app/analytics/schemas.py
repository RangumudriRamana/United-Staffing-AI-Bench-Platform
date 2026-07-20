from pydantic import BaseModel, Field

class RecruiterKPIMetrics(BaseModel):
    """Unified data metric matrix tracking recruiter performance output signals."""
    recruiter_id: int
    active_consultants: int = 0
    total_submissions: int = 0
    interviews_scheduled: int = 0
    placements_secured: int = 0
    placement_conversion_rate: float = Field(0.0, description="Percentage calculation of placements per submission")

class ExecutiveBenchHealth(BaseModel):
    """Business summary data mapping total operational capacity constraints."""
    total_consultants: int = 0
    available_now: int = 0
    currently_on_project: int = 0
    active_placements_revenue: int = 0