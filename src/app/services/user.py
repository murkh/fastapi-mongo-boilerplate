from typing import List, Optional, Dict, Any

from ..models.user import User, UserCreate, UserUpdate
from ..repositories.user import UserRepository


class UserService:
    """User service for business logic operations."""

    def __init__(self) -> None:
        self.repository: UserRepository = UserRepository()

    async def create_user(self, user_in: UserCreate) -> User:
        """Create a new user with validation."""
        # Check if email is already taken
        if await self.repository.is_email_taken(user_in.email):
            raise ValueError("Email already registered")

        # Check if username is already taken
        if await self.repository.is_username_taken(user_in.username):
            raise ValueError("Username already taken")

        return await self.repository.create_user(user_in)

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await self.repository.get(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.repository.get_by_email(email)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await self.repository.get_by_username(username)

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users with pagination."""
        return await self.repository.get_multi(skip=skip, limit=limit)

    async def update_user(self, user_id: str, user_in: UserUpdate) -> Optional[User]:
        """Update user with validation."""
        # Check if user exists
        existing_user = await self.repository.get(user_id)
        if not existing_user:
            return None

        # Check if new email is already taken by another user
        if user_in.email and user_in.email != existing_user.email:
            if await self.repository.is_email_taken(user_in.email):
                raise ValueError("Email already registered")

        # Check if new username is already taken by another user
        if user_in.username and user_in.username != existing_user.username:
            if await self.repository.is_username_taken(user_in.username):
                raise ValueError("Username already taken")

        return await self.repository.update(id=user_id, obj_in=user_in)

    async def delete_user(self, user_id: str) -> bool:
        """Delete user."""
        return await self.repository.delete(id=user_id)

    async def get_users_count(self) -> int:
        """Get total number of users."""
        return await self.repository.count()

    async def user_exists(self, user_id: str) -> bool:
        """Check if user exists."""
        return await self.repository.exists(user_id)

    # Aggregation Pipeline Methods

    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        return await self.repository.get_user_statistics()

    async def get_users_by_activity_status(
        self, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get users grouped by activity status."""
        return await self.repository.get_users_by_activity_status(limit)

    async def get_recent_users_with_details(
        self, days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get recent users with computed fields."""
        return await self.repository.get_recent_users_with_details(days)

    async def get_user_growth_trend(self, months: int = 12) -> List[Dict[str, Any]]:
        """Get user growth trend over time."""
        return await self.repository.get_user_growth_trend(months)

    async def search_users_advanced(
        self,
        search_term: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_order: int = -1,
        limit: int = 20,
        skip: int = 0,
    ) -> Dict[str, Any]:
        """Advanced user search with aggregation pipeline."""
        return await self.repository.search_users_advanced(
            search_term=search_term,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            skip=skip,
        )
