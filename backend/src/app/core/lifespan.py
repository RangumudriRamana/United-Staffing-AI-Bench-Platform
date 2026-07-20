from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting United Staffing AI Bench Platform")

    yield

    logger.info("Stopping United Staffing AI Bench Platform")