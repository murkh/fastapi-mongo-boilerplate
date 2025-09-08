from enum import Enum
from os import getenv
from pydantic_settings import BaseSettings
from pydantic import field_validator


class AppSettings(BaseSettings):
    APP_NAME: str = getenv("APP_NAME", default="FastAPI MongoDB Boilerplate")
    APP_DESCRIPTION: str | None = getenv(
        "APP_DESCRIPTION",
        default="FastAPI boilerplate with Motor (MongoDB async driver)",
    )
    APP_VERSION: str | None = getenv("APP_VERSION", default="0.1.0")


class DatabaseSettings(BaseSettings):
    MONGODB_URL: str = getenv("MONGODB_URL", default="mongodb://localhost:27017")
    MONGODB_DATABASE: str = getenv("MONGODB_DATABASE", default="fastapi_boilerplate")
    MONGODB_MAX_POOL_SIZE: int = int(getenv("MONGODB_MAX_POOL_SIZE", default="10"))
    MONGODB_MIN_POOL_SIZE: int = int(getenv("MONGODB_MIN_POOL_SIZE", default="1"))


class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = EnvironmentOption.LOCAL
    DEBUG: bool = getenv("DEBUG", default="true").lower() == "true"

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def parse_environment(cls, v: str | EnvironmentOption) -> EnvironmentOption:
        if isinstance(v, EnvironmentOption):
            return v
        # Fallback to env var if direct value provided
        value = v or getenv("ENVIRONMENT", default=EnvironmentOption.LOCAL.value)
        try:
            return EnvironmentOption(str(value).lower())
        except Exception:
            return EnvironmentOption.LOCAL


class Settings(AppSettings, DatabaseSettings, EnvironmentSettings):
    pass


settings = Settings()
