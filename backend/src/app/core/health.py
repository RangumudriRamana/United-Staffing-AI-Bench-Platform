from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database.base import get_db_session
import logging

router = APIRouter(prefix="/health", tags=["System Health Diagnostics"])
logger = logging.getLogger("app.telemetry")

@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_probe() -> dict:
    """Simplistic liveness probe verifying that the application process loop is functional."""
    return {"status": "ALIVE", "timestamp": text("now()")}

@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_probe(
    db: AsyncSession = Depends(get_db_session),
    response: Response = Response()
) -> dict:
    """
    Comprehensive multi-dependency readiness evaluation node checking
    persistence connection pools and operational parameters safely.
    """
    diagnostics = {
        "status": "READY",
        "dependencies": {
            "database": "UNKNOWN"
        }
    }
    
    try:
        # Verify persistence engine loop capability without table content dependency
        await db.execute(text("SELECT 1"))
        diagnostics["dependencies"]["database"] = "HEALTHY"
        return diagnostics
    except Exception as failure:
        logger.critical(f"Readiness Probe Check Fail Sequence Triggered: {str(failure)}")
        diagnostics["status"] = "UNREADY"
        diagnostics["dependencies"]["database"] = "CRITICAL_DISCONNECTED"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return diagnostics
