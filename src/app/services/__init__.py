from .aws_service import AWSStorageService
from .local_storage import LocalStorageService
from ..core.config import settings


def get_local_storage_service() -> LocalStorageService:
    return LocalStorageService()


def get_aws_storage_service() -> AWSStorageService:
    bucket_name = settings.AWS_S3_BUCKET_NAME
    return AWSStorageService(bucket_name=bucket_name)
