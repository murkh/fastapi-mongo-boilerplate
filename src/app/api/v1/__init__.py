from fastapi import APIRouter

from .health import router as health_router
from .users import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(users_router, prefix="/users", tags=["users"])
