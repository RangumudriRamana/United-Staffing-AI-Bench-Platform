from fastapi import APIRouter

# from app.api.v1 import v1_router
from app.health.router import router as health_router
from app.marketing.router import router as marketing_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(marketing_router)

# api_router.include_router(v1_router)