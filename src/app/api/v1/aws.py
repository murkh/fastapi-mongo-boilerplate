
from fastapi import APIRouter, Depends, HTTPException

from ...services import get_aws_storage_service
from ...services.aws_service import AWSStorageService
from ...core.exceptions import InternalServerException


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


@router.get("/tree")
def tree_s3(prefix: str = "", max_depth: int = 5, service: AWSStorageService = Depends(get_aws_storage_service)):
    try:
        return service.list_directory_tree(prefix, max_depth=max_depth)
    except Exception as e:
        raise InternalServerException(detail=str(e))
