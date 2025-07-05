
from fastapi import APIRouter, Depends, HTTPException

from src.app.core.exceptions import InternalServerException
from src.app.services import get_aws_storage_service, AWSStorageService


router = APIRouter(prefix="/aws", tags=["AWS S3"])


@router.get("/list")
def list_s3(prefix: str = "", service: AWSStorageService = Depends(get_aws_storage_service)):
    try:
        return service.list_directory(prefix)
    except Exception as e:
        raise InternalServerException(detail=str(e))


@router.get("/download")
def download_s3(path: str = "", service: AWSStorageService = Depends(get_aws_storage_service)):
    try:
        file_content = service.download_file(path)
        return {"file": file_content}
    except Exception as e:
        raise InternalServerException(detail=str(e))
