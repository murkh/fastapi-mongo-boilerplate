from fastapi import APIRouter, Depends, HTTPException

from src.app.core.exceptions import BadRequestException, InternalServerException
from src.app.services import get_local_storage_service
from src.app.services.local_storage import LocalStorageService

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
