from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...core.database import get_database

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "FastAPI MongoDB Boilerplate"
    }


@router.get("/db")
async def database_health_check(
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Dict[str, str]:
    """Database health check endpoint."""
    try:
        # Ping the database
        await db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        } 