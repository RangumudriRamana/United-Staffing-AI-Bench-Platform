from fastapi import APIRouter

from app.auth.router import router as auth_router

# As your developer hooks up future contexts, they will import them here:
# from app.consultants.router import router as consultants_router
# from app.vendors.router import router as vendors_router
# from app.requirements.router import router as requirements_router

v1_router = APIRouter()

# Authentication routes mount cleanly at /api/v1/auth
v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Future feature routers register right below:
# v1_router.include_router(consultants_router, prefix="/consultants", tags=["Consultants"])
# v1_router.include_router(vendors_router, prefix="/vendors", tags=["Vendors"])