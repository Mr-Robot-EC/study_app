import pytest
from unittest.mock import patch, MagicMock


class TestAuthFlow:
    def test_register_and_login_flow(self, auth_client):
        """Test complete registration and login flow with database mocks"""
        # This test would mock the DB operations but test the
        # real endpoint behavior and token verification

        # 1. Register a new user
        with patch('backend.services.auth_service.src.api.auth.create_user') as mock_create_user:
            # Setup mocks
            mock_user = MagicMock()
            mock_user.id = uuid.UUID(TEST_USER_ID)
            mock_user.email = TEST_EMAIL
            mock_user.full_name = "Test User"
            mock_user.roles = ["user"]

            mock_create_user.return_value = mock_user

            # Register user
            register_response = auth_client.post("/register", json={
                "email": TEST_EMAIL,
                "password": "SecurePassword123!",
                "full_name": "Test User"
            })

            assert register_response.status_code == 200
            register_data = register_response.json()
            access_token = register_data["access_token"]

            # 2. Use token to access protected route
            with patch('backend.services.auth_service.src.api.users.get_current_user') as mock_get_current_user:
                mock_get_current_user.return_value = mock_user

                # Get user profile
                profile_response = auth_client.get(
                    "/users/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )

                assert profile_response.status_code == 200
                profile_data = profile_response.json()
                assert profile_data["email"] == TEST_EMAIL