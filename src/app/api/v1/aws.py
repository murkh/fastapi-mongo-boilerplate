from fastapi import APIRouter, Depends

from ...schema.responses import DirectoryListResponse, DirectoryTreeResponse
from ...services import get_aws_storage_service
from ...services.aws_service import AWSStorageService
from ...core.exceptions import BadRequestException


router = APIRouter(prefix="/aws", tags=["AWS S3"])


@router.get("/list", response_model=DirectoryListResponse)
def list_s3(prefix: str = "", service: AWSStorageService = Depends(get_aws_storage_service)):
    entries = service.list_directory(prefix)
    return {"entries": entries}


@router.get("/download")
def download_s3(path: str = "", service: AWSStorageService = Depends(get_aws_storage_service)):
    file_content = service.download_file(path)
    return {"file": file_content}


@router.get("/tree", response_model=DirectoryTreeResponse)
def tree_s3(prefix: str = "", max_depth: int = 5, service: AWSStorageService = Depends(get_aws_storage_service)):
    tree = service.list_directory_tree(prefix, max_depth=max_depth)
    return {"tree": tree}
