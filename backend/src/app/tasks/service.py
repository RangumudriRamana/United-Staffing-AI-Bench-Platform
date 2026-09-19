from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.tasks.models import Task
from app.tasks.enums import TaskStatus
from app.tasks.schemas import TaskCreatePayload

class TaskService:
    """Orchestrates actionable work queues, owner routing modifications, and task status closures."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_operational_task(self, payload: TaskCreatePayload) -> Task:
        """Instantiates record definitions and pushes a fresh task entry onto user schedules."""
        new_task = Task(
            owner_id=payload.owner_id,
            task_type=payload.task_type,
            priority=payload.priority,
            title=payload.title,
            description=payload.description,
            related_entity_type=payload.related_entity_type,
            related_entity_id=payload.related_entity_id,
            due_at=payload.due_at,
            status=TaskStatus.OPEN
        )
        self.db.add(new_task)
        await self.db.commit()
        return new_task

    async def complete_target_task(self, public_id: UUID, current_user_id: int) -> Task:
        """Locates active work items and marks them finished under security boundaries."""
        stmt = select(Task).where(Task.public_id == public_id)
        res = await self.db.execute(stmt)
        task = res.scalars().first()

        if not task:
            raise AppException(status_code=404, message="Target action item record not found.")
        if task.owner_id != current_user_id:
            raise AppException(status_code=403, message="Unauthorized interaction context boundary.")
        if task.status == TaskStatus.COMPLETED:
            return task

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.db.commit()
        return task

    async def fetch_user_active_queue(self, user_id: int) -> list[Task]:
        """Queries localized data windows to supply the recruiter workspace widgets."""
        stmt = (
            select(Task)
            .where(
                Task.owner_id == user_id,
                Task.status.in_([TaskStatus.OPEN, TaskStatus.IN_PROGRESS])
            )
            .order_by(Task.due_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())