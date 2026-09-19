from pydantic import BaseModel, Field
from uuid import UUID

class MatchPolicyWeights(BaseModel):
    """Configurable weights controlling domain logic matching equations."""
    technology_weight: float = Field(0.50, ge=0.0, le=1.0)
    experience_weight: float = Field(0.30, ge=0.0, le=1.0)
    readiness_weight: float = Field(0.20, ge=0.0, le=1.0)

class ComponentScores(BaseModel):
    """Granular score distribution properties ensuring total algorithmic transparency."""
    overall_score: int = Field(..., ge=0, le=100)
    technology_score: int = Field(..., ge=0, le=100)
    experience_score: int = Field(..., ge=0, le=100)
    readiness_score: int = Field(..., ge=0, le=100)

class MatchExplanation(BaseModel):
    """Structured text reasons detailing exactly why a candidate matched or fell short."""
    positives: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

class RankedConsultantResponse(BaseModel):
    """Outbound transport serialization schema representing a curated candidate target."""
    consultant_public_id: UUID
    first_name: str
    last_name: str
    current_title: str | None
    scores: ComponentScores
    explanation: MatchExplanation

    class Config:
        from_attributes = True
