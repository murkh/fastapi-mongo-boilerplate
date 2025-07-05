from fastapi import APIRouter
from .aws import router as aws_router
from .local import router as local_router


router = APIRouter(prefix="/v1")
router.include_router(aws_router)
router.include_router(local_router)
