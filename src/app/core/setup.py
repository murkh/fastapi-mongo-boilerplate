from typing import Any

from fastapi import APIRouter, FastAPI

from .config import (
    AppSettings,
    EnvironmentSettings,
)
from .error_handler import setup_exception_handlers


def create_application(
    router: APIRouter,
    settings: (
        AppSettings
        | EnvironmentSettings
    ),

    **kwargs: Any,
) -> FastAPI:

    if isinstance(settings, AppSettings):
        to_update = {
            "title": settings.APP_NAME,
            "description": settings.APP_DESCRIPTION,
        }
        kwargs.update(to_update)

    application = FastAPI(**kwargs)

    # Setup global exception handlers
    setup_exception_handlers(application)

    application.include_router(router)

    return application
