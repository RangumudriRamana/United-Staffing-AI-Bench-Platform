from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.core.exceptions import AppException
from app.integrations.models import IntegrationConnection
from app.integrations.enums import IntegrationStatus
from app.integrations.schemas import IntegrationConnectionCreateRequest, IntegrationHealthResponse

class IntegrationHubService:
    """Orchestrates third-party connectivity profiles, connection testing simulations, and synchronization records."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_connection_profile(self, payload: IntegrationConnectionCreateRequest) -> IntegrationConnection:
        """Instantiates connection definitions and registers a fresh provider node configuration."""
        new_conn = IntegrationConnection(
            provider_name=payload.provider_name.upper().strip(),
            integration_type=payload.integration_type,
            configuration_json=payload.configuration_json,
            credentials_reference=payload.credentials_reference,
            status=IntegrationStatus.CONNECTED,
            is_enabled=True
        )
        self.db.add(new_conn)
        await self.db.commit()
        return new_conn

    async def execute_connectivity_check(self, public_id: UUID) -> IntegrationHealthResponse:
        """
        Simulates remote provider API ping checks, measuring latency metrics
        without exposing active security secrets or token strings.
        """
        stmt = select(IntegrationConnection).where(IntegrationConnection.public_id == public_id)
        res = await self.db.execute(stmt)
        connection = res.scalars().first()

        if not connection:
            raise AppException(status_code=404, message="Target integration connection node layout not found.")

        # --- Pluggable Adapter Interface Abstraction Simulation ---
        # Real production logic references the provider capability mapping graph
        # and dispatches an authentic connection verification request via HTTP client tools.
        
        connection.last_sync_at = datetime.now(timezone.utc)
        await self.db.commit()

        return IntegrationHealthResponse(
            provider_name=connection.provider_name,
            status=connection.status,
            is_operational=connection.status == IntegrationStatus.CONNECTED,
            latency_ms=45  # Baseline simulated API round-trip velocity
        )

    async def fetch_active_connections_list(self) -> list[IntegrationConnection]:
        """Queries database rows to supply overview grids matching management monitors."""
        stmt = select(IntegrationConnection).where(IntegrationConnection.is_enabled == True)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())