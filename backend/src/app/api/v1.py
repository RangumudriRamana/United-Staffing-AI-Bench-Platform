from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.consultants.router import router as consultants_router

v1_router = APIRouter()

# Authentication routes will cleanly mount at /api/v1/auth
v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# The feature router already owns the /consultants prefix.
v1_router.include_router(consultants_router)
