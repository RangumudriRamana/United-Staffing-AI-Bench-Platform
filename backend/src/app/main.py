import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.logging import configure_logging
from app.core.middleware import TelemetryPerimeterMiddleware

configure_logging()

settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    lifespan=lifespan,
)

# 2. Add CORS Middleware (Supports local dev & single-server hosting)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Telemetry Guard registered once
app.add_middleware(TelemetryPerimeterMiddleware)

register_exception_handlers(app)

# 4. Mount primary application context routes FIRST
app.include_router(api_router)


# 5. Serve React Frontend Static Files & SPA Fallback LAST
frontend_dist = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../frontend/dist")
)

if os.path.exists(frontend_dist):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(frontend_dist, "assets")),
        name="static-assets",
    )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        target_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(target_path) and os.path.isfile(target_path):
            return FileResponse(target_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "message": settings.project_name,
            "environment": settings.environment,
        }