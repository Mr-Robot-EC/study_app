import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

# Import the auth utilities with the correct path for your new structure
from backend.libs.auth_utils.src.permissions import require_roles, require_permissions


class TestPermissionUtils:
    async def test_require_roles_success(self, mock_env_vars):
        # Create a checker function
        checker = require_roles(["user"])

        # Create a mock user
        mock_user = MagicMock()
        mock_user.roles = ["user", "premium"]

        # Call the function
        result = await checker(mock_user)

        # Should return the user
        assert result == mock_user

    async def test_require_roles_failure(self, mock_env_vars):
        # Create a checker function
        checker = require_roles(["admin"])

        # Create a mock user without admin role
        mock_user = MagicMock()
        mock_user.roles = ["user"]

        # Call the function, should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await checker(mock_user)

        assert exc_info.value.status_code == 403

    async def test_require_permissions_success(self, mock_env_vars):
        # Create a checker function
        checker = require_permissions(["read:docs"])

        # Create a mock user
        mock_user = MagicMock()
        mock_user.permissions = ["read:docs", "write:docs"]

        # Call the function
        result = await checker(mock_user)

        # Should return the user
        assert result == mock_user

    async def test_require_permissions_failure(self, mock_env_vars):
        # Create a checker function
        checker = require_permissions(["admin:system"])

        # Create a mock user without admin permission
        mock_user = MagicMock()
        mock_user.permissions = ["read:docs"]

        # Call the function, should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await checker(mock_user)

        assert exc_info.value.status_code == 403