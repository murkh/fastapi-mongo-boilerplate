import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.app.repositories.user import UserRepository
from src.app.services.user import UserService


@pytest.fixture
def mock_database():
    """Mock database connection."""
    with patch("src.app.repositories.base.get_database") as mock_get_db:
        mock_db = MagicMock()
        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        yield mock_db, mock_collection


@pytest.fixture
def user_repository(mock_database):
    """User repository with mocked database."""
    mock_db, mock_collection = mock_database
    repo = UserRepository()
    repo.collection = mock_collection
    return repo


@pytest.fixture
def user_service(user_repository):
    """User service with mocked repository."""
    service = UserService()
    service.repository = user_repository
    return service


class TestUserRepositoryAggregation:
    """Test aggregation pipeline methods in UserRepository."""

    @pytest.mark.asyncio
    async def test_get_user_statistics(self, user_repository):
        """Test user statistics aggregation."""
        # Mock the aggregation result
        mock_result = {
            "total_users": [{"count": 100}],
            "active_users": [{"count": 85}],
            "superusers": [{"count": 5}],
            "users_by_month": [
                {"_id": {"year": 2024, "month": 1}, "count": 20},
                {"_id": {"year": 2024, "month": 2}, "count": 25},
            ],
            "average_username_length": [{"avg_length": 8.5}],
        }

        with patch.object(
            user_repository, "aggregate_single", return_value=mock_result
        ):
            result = await user_repository.get_user_statistics()

            assert result["total_users"] == 100
            assert result["active_users"] == 85
            assert result["superusers"] == 5
            assert len(result["users_by_month"]) == 2
            assert result["average_username_length"] == 8.5

    @pytest.mark.asyncio
    async def test_get_user_statistics_empty(self, user_repository):
        """Test user statistics when no data exists."""
        with patch.object(user_repository, "aggregate_single", return_value=None):
            result = await user_repository.get_user_statistics()

            assert result["total_users"] == 0
            assert result["active_users"] == 0
            assert result["superusers"] == 0
            assert result["users_by_month"] == []
            assert result["average_username_length"] == 0

    @pytest.mark.asyncio
    async def test_get_users_by_activity_status(self, user_repository):
        """Test users grouped by activity status."""
        mock_result = [
            {
                "status": "active",
                "count": 85,
                "users": [
                    {"id": "1", "username": "user1", "email": "user1@example.com"}
                ],
            },
            {
                "status": "inactive",
                "count": 15,
                "users": [
                    {"id": "2", "username": "user2", "email": "user2@example.com"}
                ],
            },
        ]

        with patch.object(user_repository, "aggregate", return_value=mock_result):
            result = await user_repository.get_users_by_activity_status(limit=5)

            assert len(result) == 2
            assert result[0]["status"] == "active"
            assert result[0]["count"] == 85
            assert result[1]["status"] == "inactive"
            assert result[1]["count"] == 15

    @pytest.mark.asyncio
    async def test_get_recent_users_with_details(self, user_repository):
        """Test recent users with computed fields."""
        mock_result = [
            {
                "_id": "1",
                "username": "user1",
                "email": "user1@example.com",
                "days_since_created": 5,
                "has_full_name": True,
                "email_domain": "@example.com",
            }
        ]

        with patch.object(user_repository, "aggregate", return_value=mock_result):
            result = await user_repository.get_recent_users_with_details(days=30)

            assert len(result) == 1
            assert result[0]["username"] == "user1"
            assert result[0]["days_since_created"] == 5
            assert result[0]["has_full_name"] is True
            assert result[0]["email_domain"] == "@example.com"

    @pytest.mark.asyncio
    async def test_get_user_growth_trend(self, user_repository):
        """Test user growth trend aggregation."""
        mock_result = [
            {
                "year": 2024,
                "month": 1,
                "new_users": 20,
                "active_users": 18,
                "superusers": 2,
                "month_name": "January",
            },
            {
                "year": 2024,
                "month": 2,
                "new_users": 25,
                "active_users": 22,
                "superusers": 3,
                "month_name": "February",
            },
        ]

        with patch.object(user_repository, "aggregate", return_value=mock_result):
            result = await user_repository.get_user_growth_trend(months=12)

            assert len(result) == 2
            assert result[0]["year"] == 2024
            assert result[0]["month"] == 1
            assert result[0]["new_users"] == 20
            assert result[0]["month_name"] == "January"

    @pytest.mark.asyncio
    async def test_search_users_advanced(self, user_repository):
        """Test advanced user search with aggregation."""
        mock_result = {
            "data": [
                {
                    "_id": "1",
                    "username": "user1",
                    "email": "user1@example.com",
                    "is_active": True,
                }
            ],
            "total": [{"count": 1}],
            "facets": [{"_id": True, "count": 1}],
        }

        with patch.object(
            user_repository, "aggregate_single", return_value=mock_result
        ):
            result = await user_repository.search_users_advanced(
                search_term="user1", limit=20, skip=0
            )

            assert len(result["data"]) == 1
            assert result["total"] == 1
            assert len(result["facets"]) == 1
            assert result["pagination"]["has_more"] is False

    @pytest.mark.asyncio
    async def test_search_users_advanced_empty(self, user_repository):
        """Test advanced user search with no results."""
        with patch.object(user_repository, "aggregate_single", return_value=None):
            result = await user_repository.search_users_advanced(
                search_term="nonexistent", limit=20, skip=0
            )

            assert result["data"] == []
            assert result["total"] == 0
            assert result["facets"] == []
            assert result["pagination"]["has_more"] is False


class TestUserServiceAggregation:
    """Test aggregation pipeline methods in UserService."""

    @pytest.mark.asyncio
    async def test_get_user_statistics_service(self, user_service):
        """Test user statistics through service layer."""
        mock_stats = {
            "total_users": 100,
            "active_users": 85,
            "superusers": 5,
            "users_by_month": [],
            "average_username_length": 8.5,
        }

        with patch.object(
            user_service.repository, "get_user_statistics", return_value=mock_stats
        ):
            result = await user_service.get_user_statistics()

            assert result["total_users"] == 100
            assert result["active_users"] == 85
            assert result["superusers"] == 5

    @pytest.mark.asyncio
    async def test_search_users_advanced_service(self, user_service):
        """Test advanced search through service layer."""
        mock_search_result = {
            "data": [{"username": "user1"}],
            "total": 1,
            "facets": [],
            "pagination": {"has_more": False},
        }

        with patch.object(
            user_service.repository,
            "search_users_advanced",
            return_value=mock_search_result,
        ):
            result = await user_service.search_users_advanced(
                search_term="user1", filters={"is_active": True}, limit=20, skip=0
            )

            assert len(result["data"]) == 1
            assert result["total"] == 1


class TestBaseRepositoryAggregation:
    """Test base repository aggregation methods."""

    @pytest.mark.asyncio
    async def test_aggregate_method(self, mock_database):
        """Test basic aggregation method."""
        from src.app.repositories.base import BaseRepository
        from src.app.models.user import User

        mock_db, mock_collection = mock_database
        repo = BaseRepository(User, "users")
        repo.collection = mock_collection

        # Mock the aggregate method directly
        async def mock_aggregate(pipeline, allowDiskUse=False):
            return [{"_id": "1", "username": "user1"}]

        with patch.object(repo, "aggregate", side_effect=mock_aggregate):
            pipeline = [{"$match": {"is_active": True}}]
            result = await repo.aggregate(pipeline)

            assert len(result) == 1
            assert result[0]["username"] == "user1"

    @pytest.mark.asyncio
    async def test_aggregate_with_model(self, mock_database):
        """Test aggregation with model instantiation."""
        from src.app.repositories.base import BaseRepository
        from src.app.models.user import User

        mock_db, mock_collection = mock_database
        repo = BaseRepository(User, "users")
        repo.collection = mock_collection

        # Mock the aggregate method directly
        async def mock_aggregate(pipeline, allowDiskUse=False):
            return [
                {
                    "_id": "507f1f77bcf86cd799439011",
                    "username": "user1",
                    "email": "user1@example.com",
                }
            ]

        with patch.object(repo, "aggregate", side_effect=mock_aggregate):
            pipeline = [{"$match": {"is_active": True}}]
            result = await repo.aggregate_with_model(pipeline)

            assert len(result) == 1
            assert isinstance(result[0], User)
            assert result[0].username == "user1"

    @pytest.mark.asyncio
    async def test_aggregate_count(self, mock_database):
        """Test aggregation count method."""
        from src.app.repositories.base import BaseRepository
        from src.app.models.user import User

        mock_db, mock_collection = mock_database
        repo = BaseRepository(User, "users")
        repo.collection = mock_collection

        # Mock the aggregate method directly
        async def mock_aggregate(pipeline, allowDiskUse=False):
            return [{"total": 5}]

        with patch.object(repo, "aggregate", side_effect=mock_aggregate):
            pipeline = [{"$match": {"is_active": True}}]
            result = await repo.aggregate_count(pipeline)

            assert result == 5
