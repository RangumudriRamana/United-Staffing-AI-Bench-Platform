from pydantic import BaseModel, Field
from typing import List, Any
from datetime import datetime

class ExecutiveSummaryDTO(BaseModel):
    """Firm-wide aggregate KPIs providing quick high-level visibility indicators."""
    total_consultants: int
    available_consultants: int
    active_requirements: int
    active_submissions: int
    placements_this_month: int

class BenchHealthDTO(BaseModel):
    """Tracks talent utilization breakdowns and highlights un-marketed bench volume."""
    available: int
    marketing_active: int
    placed: int
    idle_greater_30_days: int

class RecruiterPerformanceSummaryDTO(BaseModel):
    """Aggregated tracking row detailing sourcing productivity metrics."""
    recruiter_name: str
    submissions_count: int
    placements_count: int
    conversion_rate: float

class ForecastIndicatorsDTO(BaseModel):
    """Leading operational signals derived systematically from historic pipelines."""
    expected_placements_this_month: int
    pipeline_growth_velocity: str  # e.g., "ACCELERATING", "STABLE", "DECLINING"

class ExecutiveDashboardResponse(BaseModel):
    """The master serialization read model container serving leadership screens."""
    summary: ExecutiveSummaryDTO
    bench_health: BenchHealthDTO
    recruiter_performance: List[RecruiterPerformanceSummaryDTO] = Field(default_factory=list)
    forecast: ForecastIndicatorsDTO

    class Config:
        from_attributes = True