from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.automation.enums import AutomationTriggerType, ExecutionStatus

class WorkflowRuleCreateRequest(BaseModel):
    name: str = Field(..., max_length=150)
    trigger_type: AutomationTriggerType
    condition_json: dict | None = None
    action_json: dict = Field(..., description="Array of execution action blocks.")
    priority: int = 1

class WorkflowRuleResponse(BaseModel):
    public_id: UUID
    name: str
    trigger_type: AutomationTriggerType
    is_enabled: bool
    priority: int
    condition_json: dict | None
    action_json: dict
    created_at: datetime

    class Config:
        from_attributes = True

class WorkflowExecutionResponse(BaseModel):
    id: int
    trigger_event_type: str
    status: ExecutionStatus
    duration_ms: int
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True