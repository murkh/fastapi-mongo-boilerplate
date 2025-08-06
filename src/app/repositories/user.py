from typing import Optional, List, Dict, Any

from ..models.user import User, UserCreate, UserUpdate
from ..utils.password import hash_password, verify_password
from .base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User repository with user-specific operations and aggregations."""

    def __init__(self):
        super().__init__(User, "users")

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_data = await self.collection.find_one({"email": email})
        if user_data:
            return User(**user_data)
        return None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        user_data = await self.collection.find_one({"username": username})
        if user_data:
            return User(**user_data)
        return None

    async def create_user(self, user_in: UserCreate) -> User:
        """Create a new user with password hashing."""
        user_data = user_in.model_dump()
        password = user_data.pop("password")
        
        # Hash the password before storing
        hashed_password = hash_password(password)
        user_data["hashed_password"] = hashed_password

        result = await self.collection.insert_one(user_data)
        user_data["_id"] = result.inserted_id

        return User(**user_data)

    async def is_email_taken(self, email: str) -> bool:
        """Check if email is already taken."""
        result = await self.collection.count_documents({"email": email})
        return result > 0

    async def is_username_taken(self, username: str) -> bool:
        """Check if username is already taken."""
        result = await self.collection.count_documents({"username": username})
        return result > 0

    async def verify_user_password(self, email: str, password: str) -> bool:
        """Verify a user's password."""
        user_data = await self.collection.find_one({"email": email})
        if not user_data or "hashed_password" not in user_data:
            return False
        
        return verify_password(password, user_data["hashed_password"])

    async def get_user_with_password(self, email: str) -> Optional[dict]:
        """Get user data including hashed password for authentication."""
        user_data = await self.collection.find_one({"email": email})
        return user_data

    # Aggregation Pipeline Methods

    async def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive user statistics using aggregation pipeline.
        
        Returns:
            Dictionary with user statistics including:
            - total_users: Total number of users
            - active_users: Number of active users
            - superusers: Number of superusers
            - users_by_month: Users created by month
            - average_username_length: Average username length
        """
        pipeline = [
            {
                "$facet": {
                    "total_users": [{"$count": "count"}],
                    "active_users": [
                        {"$match": {"is_active": True}},
                        {"$count": "count"}
                    ],
                    "superusers": [
                        {"$match": {"is_superuser": True}},
                        {"$count": "count"}
                    ],
                    "users_by_month": [
                        {
                            "$group": {
                                "_id": {
                                    "year": {"$year": "$created_at"},
                                    "month": {"$month": "$created_at"}
                                },
                                "count": {"$sum": 1}
                            }
                        },
                        {"$sort": {"_id.year": 1, "_id.month": 1}}
                    ],
                    "average_username_length": [
                        {
                            "$group": {
                                "_id": None,
                                "avg_length": {"$avg": {"$strLenCP": "$username"}}
                            }
                        }
                    ]
                }
            }
        ]
        
        result = await self.aggregate_single(pipeline)
        if not result:
            return {
                "total_users": 0,
                "active_users": 0,
                "superusers": 0,
                "users_by_month": [],
                "average_username_length": 0
            }
        
        return {
            "total_users": result["total_users"][0]["count"] if result["total_users"] else 0,
            "active_users": result["active_users"][0]["count"] if result["active_users"] else 0,
            "superusers": result["superusers"][0]["count"] if result["superusers"] else 0,
            "users_by_month": result["users_by_month"],
            "average_username_length": round(
                result["average_username_length"][0]["avg_length"], 2
            ) if result["average_username_length"] else 0
        }

    async def get_users_by_activity_status(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get users grouped by activity status with counts.
        
        Args:
            limit: Maximum number of results per group
            
        Returns:
            List of users grouped by activity status
        """
        pipeline = [
            {
                "$group": {
                    "_id": "$is_active",
                    "users": {
                        "$push": {
                            "id": "$_id",
                            "username": "$username",
                            "email": "$email",
                            "full_name": "$full_name",
                            "created_at": "$created_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "status": {
                        "$cond": {
                            "if": "$_id",
                            "then": "active",
                            "else": "inactive"
                        }
                    },
                    "count": 1,
                    "users": {"$slice": ["$users", limit]}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        return await self.aggregate(pipeline)

    async def get_recent_users_with_details(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get recent users with additional computed fields.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recent users with computed fields
        """
        from datetime import datetime, timedelta, timezone
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": cutoff_date}
                }
            },
            {
                "$addFields": {
                    "days_since_created": {
                        "$floor": {
                            "$divide": [
                                {"$subtract": [datetime.now(timezone.utc), "$created_at"]},
                                1000 * 60 * 60 * 24  # milliseconds in a day
                            ]
                        }
                    },
                    "has_full_name": {"$ne": ["$full_name", None]},
                    "email_domain": {
                        "$substr": ["$email", {"$indexOfBytes": ["$email", "@"]}, -1]
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "username": 1,
                    "email": 1,
                    "full_name": 1,
                    "is_active": 1,
                    "is_superuser": 1,
                    "created_at": 1,
                    "days_since_created": 1,
                    "has_full_name": 1,
                    "email_domain": 1
                }
            },
            {"$sort": {"created_at": -1}}
        ]
        
        return await self.aggregate(pipeline)

    async def get_user_growth_trend(self, months: int = 12) -> List[Dict[str, Any]]:
        """
        Get user growth trend over the specified number of months.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            List of monthly user growth data
        """
        from datetime import datetime, timedelta, timezone
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=months * 30)
        
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"}
                    },
                    "new_users": {"$sum": 1},
                    "active_users": {
                        "$sum": {"$cond": ["$is_active", 1, 0]}
                    },
                    "superusers": {
                        "$sum": {"$cond": ["$is_superuser", 1, 0]}
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "year": "$_id.year",
                    "month": "$_id.month",
                    "new_users": 1,
                    "active_users": 1,
                    "superusers": 1,
                    "month_name": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$_id.month", 1]}, "then": "January"},
                                {"case": {"$eq": ["$_id.month", 2]}, "then": "February"},
                                {"case": {"$eq": ["$_id.month", 3]}, "then": "March"},
                                {"case": {"$eq": ["$_id.month", 4]}, "then": "April"},
                                {"case": {"$eq": ["$_id.month", 5]}, "then": "May"},
                                {"case": {"$eq": ["$_id.month", 6]}, "then": "June"},
                                {"case": {"$eq": ["$_id.month", 7]}, "then": "July"},
                                {"case": {"$eq": ["$_id.month", 8]}, "then": "August"},
                                {"case": {"$eq": ["$_id.month", 9]}, "then": "September"},
                                {"case": {"$eq": ["$_id.month", 10]}, "then": "October"},
                                {"case": {"$eq": ["$_id.month", 11]}, "then": "November"},
                                {"case": {"$eq": ["$_id.month", 12]}, "then": "December"}
                            ],
                            "default": "Unknown"
                        }
                    }
                }
            },
            {"$sort": {"year": 1, "month": 1}}
        ]
        
        return await self.aggregate(pipeline)

    async def search_users_advanced(
        self, 
        search_term: str, 
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_order: int = -1,
        limit: int = 20,
        skip: int = 0
    ) -> Dict[str, Any]:
        """
        Advanced user search with aggregation pipeline.
        
        Args:
            search_term: Text to search in username, email, and full_name
            filters: Additional filters to apply
            sort_by: Field to sort by
            sort_order: 1 for ascending, -1 for descending
            limit: Maximum number of results
            skip: Number of results to skip
            
        Returns:
            Dictionary with search results and metadata
        """
        # Build match stage
        match_stage = {
            "$or": [
                {"username": {"$regex": search_term, "$options": "i"}},
                {"email": {"$regex": search_term, "$options": "i"}},
                {"full_name": {"$regex": search_term, "$options": "i"}}
            ]
        }
        
        # Add additional filters
        if filters:
            match_stage.update(filters)
        
        pipeline = [
            {"$match": match_stage},
            {
                "$facet": {
                    "data": [
                        {"$sort": {sort_by: sort_order}},
                        {"$skip": skip},
                        {"$limit": limit},
                        {
                            "$project": {
                                "_id": 1,
                                "username": 1,
                                "email": 1,
                                "full_name": 1,
                                "is_active": 1,
                                "is_superuser": 1,
                                "created_at": 1,
                                "updated_at": 1
                            }
                        }
                    ],
                    "total": [{"$count": "count"}],
                    "facets": [
                        {
                            "$group": {
                                "_id": "$is_active",
                                "count": {"$sum": 1}
                            }
                        }
                    ]
                }
            }
        ]
        
        result = await self.aggregate_single(pipeline)
        if not result:
            return {
                "data": [],
                "total": 0,
                "facets": [],
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "has_more": False
                }
            }
        
        total = result["total"][0]["count"] if result["total"] else 0
        
        return {
            "data": result["data"],
            "total": total,
            "facets": result["facets"],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total
            }
        }
