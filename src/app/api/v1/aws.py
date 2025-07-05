from fastapi import APIRouter

from src.app.core.exceptions import InternalServerException


router = APIRouter(prefix="/aws", tags=["AWS S3"])


@router.get("/list")
def list_s3(prefix: str = ""):
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
