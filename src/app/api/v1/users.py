from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import EmailStr

from ...models.user import User, UserCreate, UserUpdate
from ...services.user import UserService

router = APIRouter()


def get_user_service() -> UserService:
    """Dependency to get user service."""
    return UserService()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, user_service: UserService = Depends(get_user_service)
) -> User:
    """Create a new user."""
    try:
        user = await user_service.create_user(user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
) -> List[User]:
    """Get all users with pagination."""
    users = await user_service.get_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str, user_service: UserService = Depends(get_user_service)
) -> User:
    """Get user by ID."""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/by-email/{email}", response_model=User)
async def get_user_by_email(
    email: EmailStr, user_service: UserService = Depends(get_user_service)
) -> User:
    """Get user by email."""
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/by-username/{username}", response_model=User)
async def get_user_by_username(
    username: str, user_service: UserService = Depends(get_user_service)
) -> User:
    """Get user by username."""
    user = await user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Update user."""
    try:
        user = await user_service.update_user(user_id, user_in)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str, user_service: UserService = Depends(get_user_service)
) -> None:
    """Delete user."""
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.get("/count/total")
async def get_users_count(
    user_service: UserService = Depends(get_user_service),
) -> dict[str, int]:
    """Get total number of users."""
    count = await user_service.get_users_count()
    return {"total_users": count}


# Aggregation Pipeline Endpoints


@router.get("/analytics/statistics")
async def get_user_statistics(
    user_service: UserService = Depends(get_user_service),
) -> dict[str, Any]:
    """Get comprehensive user statistics using aggregation pipeline."""
    return await user_service.get_user_statistics()


@router.get("/analytics/activity-status")
async def get_users_by_activity_status(
    limit: int = Query(10, ge=1, le=100, description="Maximum users per status"),
    user_service: UserService = Depends(get_user_service),
) -> List[dict[str, Any]]:
    """Get users grouped by activity status."""
    return await user_service.get_users_by_activity_status(limit)


@router.get("/analytics/recent-users")
async def get_recent_users_with_details(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    user_service: UserService = Depends(get_user_service),
) -> List[dict[str, Any]]:
    """Get recent users with computed fields."""
    return await user_service.get_recent_users_with_details(days)


@router.get("/analytics/growth-trend")
async def get_user_growth_trend(
    months: int = Query(12, ge=1, le=60, description="Number of months to analyze"),
    user_service: UserService = Depends(get_user_service),
) -> List[dict[str, Any]]:
    """Get user growth trend over time."""
    return await user_service.get_user_growth_trend(months)


@router.get("/search/advanced")
async def search_users_advanced(
    search_term: str = Query(
        ..., description="Search term for username, email, or full name"
    ),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_superuser: Optional[bool] = Query(
        None, description="Filter by superuser status"
    ),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: int = Query(
        -1, ge=-1, le=1, description="Sort order: -1 for descending, 1 for ascending"
    ),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    user_service: UserService = Depends(get_user_service),
) -> dict[str, Any]:
    """Advanced user search with aggregation pipeline."""
    # Build filters
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    if is_superuser is not None:
        filters["is_superuser"] = is_superuser

    return await user_service.search_users_advanced(
        search_term=search_term,
        filters=filters if filters else None,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        skip=skip,
    )
