from uuid import UUID

from datetime import datetime
from pydantic import BaseModel


class MatchRequest(BaseModel):
    consultant_id: UUID
    requirement_id: UUID


class MatchResponse(BaseModel):
    consultant_id: UUID
    requirement_id: UUID

    match_score: float

    recommendation: str

    matching_skills: list[str]
    missing_skills: list[str]

    experience_score: float
    visa_score: float
    location_score: float

    strengths: list[str]
    weaknesses: list[str]

    consultant_experience: float | None = None
    required_experience: float | None = None

    consultant_visa: str | None = None
    required_visa: str | None = None

    consultant_location: str | None = None
    required_location: str | None = None

    recommendation_reason: str

    next_actions: list[str]

class MatchHistoryItem(BaseModel):
    consultant_id: UUID
    consultant_name: str

    requirement_id: UUID
    requirement_name: str

    match_score: float
    recommendation: str
    matched_at: datetime


class MatchHistoryResponse(BaseModel):
    history: list[MatchHistoryItem]

class BatchMatchRequest(BaseModel):
    requirement_id: UUID


class BatchMatchItem(BaseModel):
    consultant_id: UUID
    consultant_name: str
    score: float
    recommendation: str


class BatchMatchResponse(BaseModel):
    matches: list[BatchMatchItem]