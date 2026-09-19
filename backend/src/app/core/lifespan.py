from app.database.session import engine
from app.database.base import Base

# Import every model so SQLAlchemy registers them
from app.models import *
from app.consultants.models import *
from app.requirements.models import *
from app.submissions.models import *
from app.vendors.models import *
from app.analytics.models import *
from app.audit.models import *
from app.automation.models import *
from app.communications.models import *
from app.integrations.models import *
from app.notifications.models import *
from app.reporting.models import *
from app.tasks.models import *
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting United Staffing AI Bench Platform")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized")

    yield

    logger.info("Stopping United Staffing AI Bench Platform")