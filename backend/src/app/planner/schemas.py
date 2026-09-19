from datetime import date, datetime
from pydantic import BaseModel


class PlannerSummary(BaseModel):
    planner_date: date
    open_tasks: int
    urgent_tasks: int
    high_priority_tasks: int
    marketing_follow_ups: int
    submission_follow_ups: int
    vendor_outreach: int


class PlannerTaskItem(BaseModel):
    public_id: str
    title: str
    task_type: str
    priority: str
    status: str
    due_at: datetime


class PlannerResponse(BaseModel):
    summary: PlannerSummary
    tasks: list[PlannerTaskItem]