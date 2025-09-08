from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import APIRouter, FastAPI

from .config import (
    AppSettings,
    EnvironmentSettings,
)
from .database import connect_to_mongo, close_mongo_connection
from .error_handler import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager."""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


def create_application(
    router: APIRouter,
    settings: (AppSettings | EnvironmentSettings),
    **kwargs: Any,
) -> FastAPI:
    if isinstance(settings, AppSettings):
        to_update = {
            "title": settings.APP_NAME,
            "description": settings.APP_DESCRIPTION,
        }
        kwargs.update(to_update)

    application = FastAPI(lifespan=lifespan, **kwargs)

    # Setup global exception handlers
    setup_exception_handlers(application)

    application.include_router(router)

    return application
