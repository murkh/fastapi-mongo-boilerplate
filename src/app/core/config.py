from enum import Enum
from os import getenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    APP_NAME: str = getenv("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: str | None = getenv("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = getenv("APP_VERSION", default=None)


class CloudServiceProviderSettings(BaseSettings):
    PROVIDER_NAME: str


class AWSServiceProviderSettings(CloudServiceProviderSettings):
    PROVIDER_NAME: str = "aws"
    AWS_ACCESS_KEY_ID: str | None = getenv("AWS_ACCESS_KEY_ID", default=None)
    AWS_SECRET_ACCESS_KEY: SecretStr = SecretStr(
        getenv("AWS_SECRET_ACCESS_KEY", default=""))
    AWS_REGION: str | None = getenv("AWS_REGION", default=None)


class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = getenv(
        "ENVIRONMENT", default=EnvironmentOption.LOCAL.value)


class Settings(
    AppSettings,
    AWSServiceProviderSettings,
    EnvironmentSettings
):
    pass


settings = Settings()
