from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.consultants.models import Consultant
from app.marketing.models import MarketingActivity
from app.marketing.repository import MarketingActivityRepository
from app.marketing.schemas import MarketingActivityCreateRequest
from app.tasks.enums import TaskPriority, TaskStatus, TaskType
from app.tasks.models import Task
from app.vendors.models import Client, Vendor, VendorContact


class MarketingActivityService:
    """
    Application service for recording consultant marketing activity.

    MarketingActivity represents what actually happened.
    Task represents follow-up work that must happen next.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = MarketingActivityRepository(db)

    async def _get_consultant_or_raise(
        self,
        public_id: UUID,
    ) -> Consultant:
        stmt = select(Consultant).where(
            Consultant.public_id == public_id,
            Consultant.deleted_at.is_(None),
        )

        result = await self.db.execute(stmt)
        consultant = result.scalars().first()

        if consultant is None:
            raise AppException(
                status_code=404,
                message="Consultant record not found.",
            )

        return consultant

    async def _get_vendor_or_raise(
        self,
        public_id: UUID,
    ) -> Vendor:
        stmt = select(Vendor).where(
            Vendor.public_id == public_id,
        )

        result = await self.db.execute(stmt)
        vendor = result.scalars().first()

        if vendor is None:
            raise AppException(
                status_code=404,
                message="Vendor record not found.",
            )

        return vendor

    async def _get_vendor_contact_or_raise(
        self,
        public_id: UUID,
    ) -> VendorContact:
        stmt = select(VendorContact).where(
            VendorContact.public_id == public_id,
        )

        result = await self.db.execute(stmt)
        contact = result.scalars().first()

        if contact is None:
            raise AppException(
                status_code=404,
                message="Vendor contact record not found.",
            )

        return contact

    async def _get_client_or_raise(
        self,
        public_id: UUID,
    ) -> Client:
        stmt = select(Client).where(
            Client.public_id == public_id,
        )

        result = await self.db.execute(stmt)
        client = result.scalars().first()

        if client is None:
            raise AppException(
                status_code=404,
                message="Client record not found.",
            )

        return client

    @staticmethod
    def _resolve_follow_up_task_type(
        activity_type,
        vendor_contact_id: int | None,
        client_id: int | None,
    ) -> TaskType:
        """
        Determines the appropriate follow-up task category.

        Client follow-ups take precedence when a client is explicitly
        targeted. Otherwise a vendor follow-up is created.
        """

        if client_id is not None:
            return TaskType.FOLLOW_UP_CLIENT

        if vendor_contact_id is not None:
            return TaskType.FOLLOW_UP_VENDOR

        return TaskType.FOLLOW_UP_CONSULTANT

    async def create_activity(
        self,
        payload: MarketingActivityCreateRequest,
        current_user_id: int,
    ) -> MarketingActivity:
        """
        Records a marketing activity and optionally creates
        its corresponding follow-up task.
        """

        consultant = await self._get_consultant_or_raise(
            payload.consultant_public_id,
        )

        vendor = await self._get_vendor_or_raise(
            payload.vendor_public_id,
        )

        vendor_contact = None

        if payload.vendor_contact_public_id is not None:
            vendor_contact = await self._get_vendor_contact_or_raise(
                payload.vendor_contact_public_id,
            )

            if vendor_contact.vendor_id != vendor.id:
                raise AppException(
                    status_code=400,
                    message="Vendor contact does not belong to the selected vendor.",
                )

        client = None

        if payload.client_public_id is not None:
            client = await self._get_client_or_raise(
                payload.client_public_id,
            )

            if client.vendor_id != vendor.id:
                raise AppException(
                    status_code=400,
                    message="Client does not belong to the selected vendor.",
                )

        occurred_at = payload.occurred_at or datetime.utcnow()

        if occurred_at.tzinfo is not None:
            occurred_at = occurred_at.astimezone(timezone.utc).replace(tzinfo=None)

        try:
            activity = await self.repository.create(
                consultant_id=consultant.id,
                vendor_id=vendor.id,
                vendor_contact_id=(
                    vendor_contact.id
                    if vendor_contact
                    else None
                ),
                client_id=(
                    client.id
                    if client
                    else None
                ),
                performed_by=current_user_id,
                activity_type=payload.activity_type,
                channel=payload.channel,
                outcome=payload.outcome,
                subject=payload.subject,
                notes=payload.notes,
                follow_up_required=payload.follow_up_required,
                occurred_at=occurred_at,
            )

            if vendor_contact is not None:
                vendor_contact.last_contacted = occurred_at

            if payload.follow_up_required:
                task_type = self._resolve_follow_up_task_type(
                    activity_type=payload.activity_type,
                    vendor_contact_id=(
                        vendor_contact.id
                        if vendor_contact
                        else None
                    ),
                    client_id=(
                        client.id
                        if client
                        else None
                    ),
                )

                follow_up_task = Task(
                    owner_id=current_user_id,
                    task_type=task_type,
                    priority=TaskPriority.NORMAL,
                    status=TaskStatus.OPEN,
                    title=(
                        f"Follow up on marketing activity "
                        f"for {consultant.first_name} "
                        f"{consultant.last_name}"
                    ),
                    description=payload.notes,
                    related_entity_type="CONSULTANT",
                    related_entity_id=consultant.id,
                    due_at=occurred_at,
                )

                self.db.add(follow_up_task)

            await self.db.commit()

            activity = await self.repository.get_by_public_id(
                activity.public_id,
            )

            if activity is None:
                raise AppException(
                    status_code=500,
                    message="Marketing activity was created but could not be reloaded.",
                )

            return activity

        except AppException:
            await self.db.rollback()
            raise

        except Exception:
            await self.db.rollback()
            raise

    async def get_activity(
        self,
        public_id: UUID,
    ) -> MarketingActivity:
        activity = await self.repository.get_by_public_id(
            public_id,
        )

        if activity is None:
            raise AppException(
                status_code=404,
                message="Marketing activity record not found.",
            )

        return activity

    async def list_consultant_activities(
        self,
        consultant_public_id: UUID,
    ) -> list[MarketingActivity]:
        consultant = await self._get_consultant_or_raise(
            consultant_public_id,
        )

        return await self.repository.list_by_consultant(
            consultant.id,
        )