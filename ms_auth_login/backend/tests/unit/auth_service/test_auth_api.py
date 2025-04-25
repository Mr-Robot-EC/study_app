import uuid
from unittest.mock import patch, MagicMock
import pytest

# Test constants
TEST_USER_ID = str(uuid.uuid4())
TEST_EMAIL = "test@example.com"


class TestAuthAPI:
    def test_register_user(self, auth_client):
        # Mocked DB response
        with patch('backend.services.auth_service.src.api.auth.create_user') as mock_create_user:
            mock_user = MagicMock()
            mock_user.id = uuid.UUID(TEST_USER_ID)
            mock_user.email = TEST_EMAIL
            mock_user.full_name = "Test User"
            mock_user.roles = ["user"]

            mock_create_user.return_value = mock_user

            response = auth_client.post("/register", json={
                "email": TEST_EMAIL,
                "password": "SecurePassword123!",
                "full_name": "Test User"
            })

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["user"]["email"] == TEST_EMAIL

    def test_login_user(self, auth_client):
        # Mocked user authentication
        with patch('backend.services.auth_service.src.api.auth.authenticate_user') as mock_auth:
            mock_user = MagicMock()
            mock_user.id = uuid.UUID(TEST_USER_ID)
            mock_user.email = TEST_EMAIL
            mock_user.full_name = "Test User"
            mock_user.roles = ["user"]
            mock_user.last_login = None

            mock_auth.return_value = mock_user

            # Create form data
            response = auth_client.post(
                "/token",
                data={
                    "username": TEST_EMAIL,
                    "password": "SecurePassword123!"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data