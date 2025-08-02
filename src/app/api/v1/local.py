from fastapi import APIRouter, Depends

from ...schema.responses import DirectoryListResponse, DirectoryTreeResponse
from ...services import get_local_storage_service
from ...services.local_storage import LocalStorageService


router = APIRouter(prefix="/local", tags=["LOCAL Storage"])


@router.get("/list", response_model=DirectoryListResponse)
def list_local(path: str = "", service: LocalStorageService = Depends(get_local_storage_service)):
    entries = service.list_directory(path)
    return {"entries": entries}


@router.get("/download")
def download_local(path: str = "", service: LocalStorageService = Depends(get_local_storage_service)):
    file_content = service.download_file(path)
    return {"file": file_content}


# New endpoint for nested tree
@router.get("/tree", response_model=DirectoryTreeResponse)
def tree_local(path: str = "", max_depth: int = 5, service: LocalStorageService = Depends(get_local_storage_service)):
    tree = service.list_directory_tree(path, max_depth=max_depth)
    return {"tree": tree}
