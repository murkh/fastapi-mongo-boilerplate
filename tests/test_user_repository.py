import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.app.models.user import UserCreate
from src.app.repositories.user import UserRepository


class TestUserRepositoryPasswordHashing:
    """Test user repository password hashing functionality."""

    @pytest.fixture
    def user_repository(self):
        """Create a user repository instance with mocked database."""
        with patch("src.app.repositories.base.get_database") as mock_db:
            # Mock the database to return a mock collection
            mock_collection = AsyncMock()
            mock_db.return_value = {"users": mock_collection}

            repo = UserRepository()
            return repo

    @pytest.fixture
    def sample_user_data(self):
        """Create sample user data for testing."""
        return {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "testpassword123",
        }

    @pytest.mark.asyncio
    async def test_create_user_hashes_password(self, user_repository, sample_user_data):
        """Test that creating a user hashes the password."""
        user_create = UserCreate(**sample_user_data)

        # Mock the collection.insert_one method
        mock_result = Mock()
        mock_result.inserted_id = "507f1f77bcf86cd799439011"  # Valid ObjectId
        user_repository.collection.insert_one.return_value = mock_result

        # Create the user
        user = await user_repository.create_user(user_create)

        # Verify that insert_one was called with hashed password
        call_args = user_repository.collection.insert_one.call_args[0][0]
        assert "hashed_password" in call_args
        assert call_args["hashed_password"].startswith("$2b$")
        assert "password" not in call_args  # Original password should be removed

        # Verify that the user has a hashed_password field
        assert hasattr(user, "hashed_password")
        assert user.hashed_password is not None
        assert user.hashed_password.startswith("$2b$")

    @pytest.mark.asyncio
    async def test_verify_user_password_correct(self, user_repository):
        """Test that password verification works with correct password."""
        # Create a real hash for testing
        from src.app.utils.password import hash_password

        test_password = "testpassword123"
        real_hash = hash_password(test_password)

        # Mock the collection.find_one method to return user with real hash
        user_repository.collection.find_one.return_value = {
            "email": "test@example.com",
            "hashed_password": real_hash,
        }

        # Test that the method calls find_one with correct query
        result = await user_repository.verify_user_password(
            "test@example.com", test_password
        )
        user_repository.collection.find_one.assert_called_with(
            {"email": "test@example.com"}
        )
        assert result is True

        # Test with wrong password
        result = await user_repository.verify_user_password(
            "test@example.com", "wrongpassword"
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_user_password_user_not_found(self, user_repository):
        """Test that password verification returns False for non-existent user."""
        # Mock the collection.find_one method to return None
        user_repository.collection.find_one.return_value = None

        result = await user_repository.verify_user_password(
            "nonexistent@example.com", "anypassword"
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_user_password_no_hash_field(self, user_repository):
        """Test that password verification returns False when user has no hash field."""
        # Mock the collection.find_one method to return user without hash
        user_repository.collection.find_one.return_value = {
            "email": "test@example.com",
            "username": "testuser",
            # No hashed_password field
        }

        result = await user_repository.verify_user_password(
            "test@example.com", "anypassword"
        )
        assert result is False
