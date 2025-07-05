from fastapi import APIRouter, Depends

from src.app.core.exceptions import InternalServerException

router = APIRouter(prefix="/local", tags=["LOCAL Storage"])


@router.get("/list")
def list_s3(path: str = ""):
    try:
        return {"Hello": "World"}
    except Exception as e:
        raise InternalServerException(detail=str(e))


@router.get("/download")
def list_s3(path: str = ""):
    try:
        return {"Hello": "World"}
    except Exception as e:
        raise InternalServerException(detail=str(e))
