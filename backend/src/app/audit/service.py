from uuid import UUID
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.audit.models import AuditRecord
from app.audit.schemas import AuditRecordCreatePayload
from app.core.middleware import correlation_id_ctx

class AuditService:
    """Orchestrates append-only compliance entries updates, correlation searches, and history maps."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_next_entity_version(
        self,
        entity_type: str,
        entity_public_id: str,
    ) -> int:
        """Returns the next audit version for a specific entity."""

        stmt = (
            select(func.max(AuditRecord.entity_version))
            .where(
                func.upper(AuditRecord.entity_type) == entity_type.upper().strip(),
                AuditRecord.entity_public_id == str(entity_public_id),
            )
        )

        res = await self.db.execute(stmt)
        current_version = res.scalar_one_or_none()

        return (current_version or 0) + 1

    async def write_audit_entry(self, payload: AuditRecordCreatePayload) -> AuditRecord:
        """Appends an un-alterable checkpoint row line onto the global system log matrix."""
        new_record = AuditRecord(
            actor_user_id=payload.actor_user_id,
            action_type=payload.action_type,
            source_context=payload.source_context.upper().strip(),
            correlation_id=payload.correlation_id or correlation_id_ctx.get() or None,
            entity_type=payload.entity_type.upper().strip(),
            entity_public_id=str(payload.entity_public_id),
            entity_version=payload.entity_version,
            before_snapshot_json=payload.before_snapshot_json,
            after_snapshot_json=payload.after_snapshot_json,
            metadata_json=payload.metadata_json
        )
        self.db.add(new_record)
        await self.db.flush()
        return new_record

    async def fetch_entity_version_history(self, entity_type: str, entity_public_id: str) -> list[AuditRecord]:
        """Queries log tracks to compile structural chronological changes for a target identity."""
        stmt = (
            select(AuditRecord)
            .where(
                func.upper(AuditRecord.entity_type) == entity_type.upper().strip(),
                AuditRecord.entity_public_id == str(entity_public_id)
            )
            .order_by(desc(AuditRecord.occurred_at))
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def resolve_correlation_chain(self, correlation_id: str) -> list[AuditRecord]:
        """Assembles end-to-end transactional execution maps matching common correlation logs."""
        stmt = (
            select(AuditRecord)
            .where(AuditRecord.correlation_id == correlation_id)
            .order_by(AuditRecord.occurred_at.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())