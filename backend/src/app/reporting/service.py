from uuid import UUID
import time
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.enums import AuditActionType
from app.audit.schemas import AuditRecordCreatePayload
from app.audit.service import AuditService

from app.core.exceptions import AppException
from app.reporting.models import ReportDefinition, ReportExecution
from app.reporting.enums import ReportExecutionStatus
from app.reporting.schemas import ReportDefinitionCreateRequest


class ReportingService:
    """Orchestrates persistent report template metadata, execution logging tracking, and exporter selection."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)

    async def create_report_definition(self, payload: ReportDefinitionCreateRequest, user_id: int) -> ReportDefinition:
        """Registers a reusable structural reporting template profile configuration."""
        new_def = ReportDefinition(
            name=payload.name,
            report_type=payload.report_type,
            output_format=payload.output_format,
            parameters_json=payload.parameters_json,
            schedule=payload.schedule,
            created_by=user_id,
            is_enabled=True
        )
        self.db.add(new_def)
        await self.db.commit()
        return new_def

    async def trigger_on_demand_execution(self, public_id: UUID, executioner_user_id: int) -> ReportExecution:
        """
        Executes report data generation streams asynchronously, mapping parameters
        and capturing diagnostic performance records to prevent system degradation.
        """
        start_time = time.perf_counter()

        # 1. Locate the master template blueprint mapping profiles
        stmt = select(ReportDefinition).where(ReportDefinition.public_id == public_id)
        res = await self.db.execute(stmt)
        definition = res.scalars().first()
        if not definition:
            raise AppException(status_code=404, message="Target report template layout configuration not found.")

        # 2. Stage the execution row log tracking entry
        execution_log = ReportExecution(
            report_definition_id=definition.id,
            generated_by=executioner_user_id,
            status=ReportExecutionStatus.RUNNING
        )
        self.db.add(execution_log)
        await self.db.flush()

        try:
            # --- Pluggable Exporter Interface Abstraction Simulation ---
            # Real production logic leverages a ReportDataProvider strategy mapping read tables 
            # to transform array fields directly depending on chosen output_format parameters.
            
            # 3. Simulate secure file manifest generation paths
            simulated_storage_path = f"/var/storage/exports/{definition.report_type.value.lower()}_{execution_log.id}.csv"
            
            duration = int((time.perf_counter() - start_time) * 1000)
            
            # 4. Finalize processing statuses atomically
            execution_log.status = ReportExecutionStatus.SUCCESS
            execution_log.file_location = simulated_storage_path
            execution_log.duration_ms = max(1, duration)

            await self.audit_service.write_audit_entry(
                AuditRecordCreatePayload(
                    actor_user_id=executioner_user_id,
                    action_type=AuditActionType.EXPORT,
                    source_context="REPORTING_SERVICE",
                    entity_type="REPORT_DEFINITION",
                    entity_public_id=str(definition.public_id),
                    entity_version=await self.audit_service.get_next_entity_version(
                        entity_type="REPORT_DEFINITION",
                        entity_public_id=str(definition.public_id),
                    ),
                    before_snapshot_json=None,
                    after_snapshot_json={
                        "report_definition_public_id": str(definition.public_id),
                        "report_type": definition.report_type.value,
                        "output_format": definition.output_format.value,
                    },
                    metadata_json={
                        "operation": "run_report_export",
                        "execution_id": execution_log.id,
                        "file_location": simulated_storage_path,
                        "duration_ms": execution_log.duration_ms,
                    },
                )
            )

            await self.db.commit()
            return execution_log
            
        except Exception as error:
            await self.db.rollback()
            execution_log.status = ReportExecutionStatus.FAILED
            execution_log.error_message = str(error)[:499]
            await self.db.commit()
            raise error

    async def fetch_execution_history_logs(self, limit: int = 50) -> list[ReportExecution]:
        """Collects historical generation tracks to feed system overview monitoring layers."""
        stmt = select(ReportExecution).order_by(desc(ReportExecution.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())