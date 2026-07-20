from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.tasks.enums import TaskType, TaskStatus, TaskPriority

class TaskCreatePayload(BaseModel):
    """Payload parameter container processed by automation rules engines."""
    owner_id: int
    task_type: TaskType
    priority: TaskPriority = TaskPriority.NORMAL
    title: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=1000)
    related_entity_type: str | None = Field(None, max_length=50)
    related_entity_id: int | None = None
    due_at: datetime

class TaskResponse(BaseModel):
    """Outbound tracking DTO returning data straight to workspace widgets."""
    public_id: UUID
    owner_id: int
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    title: str
    description: str | None
    related_entity_type: str | None
    related_entity_id: int | None
    due_at: datetime
    completed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True