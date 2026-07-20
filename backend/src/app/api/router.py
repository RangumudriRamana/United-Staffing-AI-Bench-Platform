from fastapi import APIRouter

from app.api.v1 import v1_router
from app.health.router import router as health_router

api_router = APIRouter(prefix="/api/v1")

# Keep your existing health check route active
api_router.include_router(health_router)

# Include the centralized business feature aggregator
api_router.include_router(v1_router)