import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from backend.libs.auth_utils.src.dependencies import get_current_user
from backend.libs.auth_utils.src.jwt import decode_jwt


class TestJwtUtils:
    async def test_get_current_user(self, valid_access_token, mock_env_vars):
        # Create a mock request with Authorization header
        mock_credentials = MagicMock()
        mock_credentials.credentials = valid_access_token

        # Call the function
        user = await get_current_user(mock_credentials, "pdf-service")

        # Assert user properties
        assert str(user.id) == TEST_USER_ID
        assert user.email == TEST_EMAIL
        assert "user" in user.roles

    async def test_decode_jwt_with_valid_token(self, valid_access_token, mock_env_vars):
        # Call the function
        payload = await decode_jwt(valid_access_token)

        # Assert payload properties
        assert payload["sub"] == TEST_USER_ID
        assert payload["email"] == TEST_EMAIL

    async def test_decode_jwt_with_expired_token(self, expired_access_token, mock_env_vars):
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await decode_jwt(expired_access_token)

        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()