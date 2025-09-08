from src.app.utils.password import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing and verification functionality."""

    def test_hash_password(self):
        """Test that password hashing works correctly."""
        password = "testpassword123"
        hashed = hash_password(password)

        # Check that the hash is different from the original password
        assert hashed != password
        # Check that the hash is a string
        assert isinstance(hashed, str)
        # Check that the hash starts with $2b$ (bcrypt identifier)
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        """Test that password verification works with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)

        # Verify the password should return True
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that password verification fails with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword123"
        hashed = hash_password(password)

        # Verify the wrong password should return False
        assert verify_password(wrong_password, hashed) is False

    def test_hash_password_bytes_input(self):
        """Test that password hashing works with bytes input."""
        password_bytes = b"testpassword123"
        hashed = hash_password(password_bytes)

        # Verify the password should work
        assert verify_password(password_bytes, hashed) is True

    def test_verify_password_bytes_hash(self):
        """Test that password verification works with bytes hash."""
        password = "testpassword123"
        hashed = hash_password(password)
        hashed_bytes = hashed.encode("utf-8")

        # Verify the password should work with bytes hash
        assert verify_password(password, hashed_bytes) is True

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"

        hash1 = hash_password(password1)
        hash2 = hash_password(password2)

        # Hashes should be different
        assert hash1 != hash2

    def test_same_password_different_salts(self):
        """Test that the same password produces different hashes due to salt."""
        password = "testpassword123"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to different salts
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
