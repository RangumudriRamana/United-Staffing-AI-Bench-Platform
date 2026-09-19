from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.enums import TaskPriority, TaskStatus, TaskType
from app.tasks.models import Task


class PlannerService:
    """Builds the authenticated user's operational Daily Planner."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_plan(
        self,
        user_id: int,
        planner_date: date,
    ):
        stmt = (
            select(Task)
            .where(
                Task.owner_id == user_id,
                Task.status.in_(
                    [
                        TaskStatus.OPEN,
                        TaskStatus.IN_PROGRESS,
                    ]
                ),
                Task.due_at >= planner_date,
                Task.due_at < planner_date.fromordinal(
                    planner_date.toordinal() + 1
                ),
            )
            .order_by(Task.due_at.asc())
        )

        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())

        open_tasks = len(tasks)

        urgent_tasks = sum(
            1 for task in tasks
            if task.priority == TaskPriority.URGENT
        )

        high_priority_tasks = sum(
            1 for task in tasks
            if task.priority == TaskPriority.HIGH
        )

        marketing_follow_ups = sum(
            1 for task in tasks
            if task.task_type
            in {
                TaskType.FOLLOW_UP_CONSULTANT,
                TaskType.MARKETING_REFRESH,
            }
        )

        submission_follow_ups = sum(
            1 for task in tasks
            if task.task_type
            in {
                TaskType.SUBMIT_PROFILE,
                TaskType.REQUEST_FEEDBACK,
                TaskType.INTERVIEW_FOLLOW_UP,
                TaskType.INTERVIEW_PREPARATION,
                TaskType.OFFER_REVIEW,
                TaskType.PLACEMENT_CONFIRMATION,
            }
        )

        vendor_outreach = sum(
            1 for task in tasks
            if task.task_type
            in {
                TaskType.FOLLOW_UP_VENDOR,
                TaskType.FOLLOW_UP_CLIENT,
            }
        )

        return {
            "summary": {
                "planner_date": planner_date,
                "open_tasks": open_tasks,
                "urgent_tasks": urgent_tasks,
                "high_priority_tasks": high_priority_tasks,
                "marketing_follow_ups": marketing_follow_ups,
                "submission_follow_ups": submission_follow_ups,
                "vendor_outreach": vendor_outreach,
            },
            "tasks": [
                {
                    "public_id": str(task.public_id),
                    "title": task.title,
                    "task_type": task.task_type.value,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "due_at": task.due_at,
                }
                for task in tasks
            ],
        }