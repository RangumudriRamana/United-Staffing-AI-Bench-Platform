from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.responses import ApiResponse
from app.core.dependencies import get_db 

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    response_model=ApiResponse[dict[str, str]],
)
def health_check():
    """
    Existing general health summary endpoint.
    """
    return ApiResponse(
        message="Service is healthy - TEST",
        data={
            "status": "ok",
        },
    )


@router.get(
    "/live",
    summary="Liveness Check",
)
def liveness_check():
    """
    Shallow liveness probe. Returns 200 OK if the FastAPI process is running.
    """
    return {"status": "alive"}


@router.get(
    "/ready",
    summary="Readiness Check",
)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Deep readiness probe. Verifies database connectivity.
    """
    try:
        # Execute a low-overhead query to verify the database responds
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {str(e)}"
        )