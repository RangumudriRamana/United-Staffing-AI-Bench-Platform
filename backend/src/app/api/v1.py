from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.consultants.router import router as consultants_router
from app.requirements.router import router as requirements_router
from app.submissions.router import router as submissions_router
from app.ai_matching.router import router as ai_matching_router
from app.planner.router import router as planner_router
from app.reporting.router import router as reporting_router

v1_router = APIRouter()

v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
v1_router.include_router(consultants_router)
v1_router.include_router(requirements_router)
v1_router.include_router(submissions_router)
v1_router.include_router(ai_matching_router)
v1_router.include_router(planner_router)
v1_router.include_router(reporting_router)
