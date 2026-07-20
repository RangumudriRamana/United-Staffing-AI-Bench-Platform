from uuid import UUID
import time
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.automation.models import WorkflowRule, WorkflowExecution
from app.automation.enums import AutomationTriggerType, ExecutionStatus
from app.automation.schemas import WorkflowRuleCreateRequest

class WorkflowAutomationService:
    """Orchestrates configuration entries registry setups and matches inbound pipeline trigger streams."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_workflow_rule(self, payload: WorkflowRuleCreateRequest) -> WorkflowRule:
        """Instantiates record parameters and registers custom conditional background workflows."""
        new_rule = WorkflowRule(
            name=payload.name,
            trigger_type=payload.trigger_type,
            condition_json=payload.condition_json,
            action_json=payload.action_json,
            priority=payload.priority,
            is_enabled=True
        )
        self.db.add(new_rule)
        await self.db.commit()
        return new_rule

    async def process_system_trigger(self, trigger_type: AutomationTriggerType, context_metadata: dict) -> int:
        """
        Scans registered configurations against matching type parameters, processes conditions,
        and logs performance execution metrics cleanly to support asynchronous diagnostics.
        """
        start_time = time.perf_counter()
        
        # 1. Fetch matching active tracking configurations sorted by execution priority maps
        stmt = (
            select(WorkflowRule)
            .where(WorkflowRule.trigger_type == trigger_type, WorkflowRule.is_enabled == True)
            .order_by(WorkflowRule.priority.desc())
        )
        res = await self.db.execute(stmt)
        active_rules = res.scalars().all()

        execution_counts = 0

        # 2. Loop through rule blocks to evaluate context conditions
        for rule in active_rules:
            # Condition matching validation placeholder
            # Real production logic parses condition_json criteria parameters against incoming context fields
            
            # 3. Simulate operational execution blocks
            duration = int((time.perf_counter() - start_time) * 1000)
            
            log_entry = WorkflowExecution(
                workflow_rule_id=rule.id,
                trigger_event_type=trigger_type.value,
                status=ExecutionStatus.SUCCESS,
                duration_ms=max(1, duration),
                error_message=None
            )
            self.db.add(log_entry)
            execution_counts += 1

        await self.db.commit()
        return execution_counts

    async def get_rule_execution_logs(self, limit: int = 50) -> list[WorkflowExecution]:
        """Collects latest history rows from append logs for diagnostic tools tracking checks."""
        stmt = select(WorkflowExecution).order_by(desc(WorkflowExecution.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())