"""
Application Entry Point

Responsibilities:
- Initialize FastAPI
- Configure CORS
- Register global exception handlers
- Register routers
- Expose health endpoints
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.auth.bootstrap import ensure_initial_admin
from app.database.session import SessionLocal
from app.ai_matching.router import router as ai_matching_router

from app.auth.router import router as auth_router
from app.consultants.router import router as consultants_router
from app.requirements.router import router as requirements_router
from app.submissions.router import router as submissions_router
from app.health.router import router as health_router
from app.vendors.router import router as vendors_router
from app.marketing.router import router as marketing_router
from app.tasks.router import router as tasks_router
from app.planner.router import router as planner_router
from app.notifications.router import router as notifications_router
from app.audit.router import router as audit_router
from app.reporting.router import router as reporting_router
from app.core.middleware import TelemetryPerimeterMiddleware

from app.analytics.executive.router import router as executive_analytics_router
from app.analytics.dashboard.router import router as recruiter_dashboard_router
from app.analytics.vendor_dashboard.router import router as vendor_analytics_router


from app.core.exceptions import AppException
from app.core.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)


# -------------------------------------------------------------------------
# Lifespan
# -------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup / Shutdown events.

    Startup Tasks:
    - Ensure initial admin exists
    - Future:
        - Verify database connectivity
        - Warm caches
        - Register background workers
    """
    print("Starting United Staffing AI Platform...")

    async with SessionLocal() as db:
        await ensure_initial_admin(db)

    yield

    print("Shutting down United Staffing AI Platform...")


# -------------------------------------------------------------------------
# FastAPI Application
# -------------------------------------------------------------------------

app = FastAPI(
    title="United Staffing AI Bench Platform",
    description="Enterprise FastAPI backend for Consultant, Requirement and Submission Management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# -------------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite React
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Correlation-ID",
    ],
)

app.add_middleware(TelemetryPerimeterMiddleware)

# -------------------------------------------------------------------------
# Global Exception Handlers
# -------------------------------------------------------------------------

app.add_exception_handler(AppException, app_exception_handler)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)


# -------------------------------------------------------------------------
# API Routers
# -------------------------------------------------------------------------

API_PREFIX = "/api/v1"

app.include_router(
    vendors_router,
    prefix=API_PREFIX,
)

app.include_router(
    health_router,
    prefix=API_PREFIX,
)

app.include_router(
    auth_router,
    prefix=API_PREFIX,
)

app.include_router(
    consultants_router,
    prefix=API_PREFIX,
)

app.include_router(
    requirements_router,
    prefix=API_PREFIX,
)

app.include_router(
    submissions_router,
    prefix=API_PREFIX,
)

app.include_router(
    marketing_router,
    prefix=API_PREFIX,
)
app.include_router(
    tasks_router,
    prefix=API_PREFIX,
)
app.include_router(
    planner_router,
    prefix=API_PREFIX,
)
app.include_router(
    notifications_router,
    prefix=API_PREFIX,
)
app.include_router(
    audit_router,
    prefix=API_PREFIX,
)
app.include_router(
    reporting_router,
    prefix=API_PREFIX,
)

app.include_router(
    ai_matching_router,
    prefix="/api/v1/ai",
    tags=["AI Matching"],
)

app.include_router(
    executive_analytics_router,
    prefix=API_PREFIX,
)

app.include_router(
    recruiter_dashboard_router,
    prefix=API_PREFIX,
)

app.include_router(
    vendor_analytics_router,
    prefix=API_PREFIX,
)

# -------------------------------------------------------------------------
# Root Endpoint
# -------------------------------------------------------------------------

@app.get("/", tags=["Root"])
async def root():
    return {
        "application": "United Staffing AI Bench Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }