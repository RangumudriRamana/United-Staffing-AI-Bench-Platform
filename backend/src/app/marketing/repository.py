from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.marketing.models import MarketingActivity


class MarketingActivityRepository:
    """
    Persistence operations for MarketingActivity records.

    The repository intentionally deals with internal database IDs.
    Public-ID resolution belongs in the service layer.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        consultant_id: int,
        vendor_id: int,
        vendor_contact_id: int | None,
        client_id: int | None,
        performed_by: int,
        activity_type,
        channel,
        outcome,
        subject: str | None,
        notes: str | None,
        follow_up_required: bool,
        occurred_at,
    ) -> MarketingActivity:
        activity = MarketingActivity(
            consultant_id=consultant_id,
            vendor_id=vendor_id,
            vendor_contact_id=vendor_contact_id,
            client_id=client_id,
            performed_by=performed_by,
            activity_type=activity_type,
            channel=channel,
            outcome=outcome,
            subject=subject,
            notes=notes,
            follow_up_required=follow_up_required,
            occurred_at=occurred_at,
        )

        self.db.add(activity)
        await self.db.flush()

        return activity

    async def get_by_public_id(self, public_id: UUID):
        stmt = (
            select(MarketingActivity)
            .where(MarketingActivity.public_id == public_id)
            .options(
                selectinload(MarketingActivity.consultant),
                selectinload(MarketingActivity.vendor),
                selectinload(MarketingActivity.vendor_contact),
                selectinload(MarketingActivity.client),
            )
        )

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_consultant(self, consultant_id: int):
        stmt = (
            select(MarketingActivity)
            .where(MarketingActivity.consultant_id == consultant_id)
            .options(
                selectinload(MarketingActivity.consultant),
                selectinload(MarketingActivity.vendor),
                selectinload(MarketingActivity.vendor_contact),
                selectinload(MarketingActivity.client),
            )
            .order_by(MarketingActivity.occurred_at.desc())
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())