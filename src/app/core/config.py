from enum import Enum
from os import getenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    APP_NAME: str = getenv("APP_NAME", default="File Explorer API")
    APP_DESCRIPTION: str | None = getenv(
        "APP_DESCRIPTION", default="Basic App to explorer the contents of a storage provider")
    APP_VERSION: str | None = getenv("APP_VERSION", default=None)


class CloudServiceProviderSettings(BaseSettings):
    PROVIDER_NAME: str


class AWSServiceProviderSettings(CloudServiceProviderSettings):
    PROVIDER_NAME: str = "aws"
    AWS_ACCESS_KEY_ID: str | None = getenv("AWS_ACCESS_KEY_ID", default=None)
    AWS_SECRET_ACCESS_KEY: SecretStr = SecretStr(
        getenv("AWS_SECRET_ACCESS_KEY", default=""))
    AWS_REGION: str | None = getenv("AWS_REGION", default=None)
    AWS_S3_BUCKET_NAME: str | None = getenv("AWS_S3_BUCKET_NAME")


class LocalStorageProviderSettings(CloudServiceProviderSettings):
    PROVIDER_NAME: str = "local"
    LOCAL_STORAGE_PATH: str = getenv("LOCAL_STORAGE_PATH", default="./storage")


class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = getenv(
        "ENVIRONMENT", default=EnvironmentOption.LOCAL.value)


class Settings(
    AppSettings,
    LocalStorageProviderSettings,
    AWSServiceProviderSettings,
    EnvironmentSettings
):
    pass


settings = Settings()
