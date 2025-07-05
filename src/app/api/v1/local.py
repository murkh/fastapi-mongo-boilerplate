from fastapi import APIRouter, Depends, HTTPException

from ...core.exceptions import BadRequestException, InternalServerException
from ...services import get_local_storage_service
from ...services.local_storage import LocalStorageService


router = APIRouter(prefix="/local", tags=["LOCAL Storage"])


@router.get("/list")
def list_local(path: str = "", service: LocalStorageService = Depends(get_local_storage_service)):
    try:
        return service.list_directory(path)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise InternalServerException(detail=str(e))



@router.get("/download")
def download_local(path: str = "", service: LocalStorageService = Depends(get_local_storage_service)):
    try:
        if not path:
            raise BadRequestException(
                detail="Incorrect Path or Path not provided")
        return service.download_file(path)
    except BadRequestException as e:
        raise e
    except Exception as e:
        raise InternalServerException(detail=str(e))


# New endpoint for nested tree
@router.get("/tree")
def tree_local(path: str = "", max_depth: int = 5, service: LocalStorageService = Depends(get_local_storage_service)):
    try:
        return service.list_directory_tree(path, max_depth=max_depth)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise InternalServerException(detail=str(e))
