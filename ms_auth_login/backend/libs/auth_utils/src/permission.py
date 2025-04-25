from typing import List
from fastapi import Depends, HTTPException, status

from .models import CurrentUser
from .dependencies import get_current_user


def require_roles(required_roles: List[str]):
    """
    Dependency to check if user has any of the required roles

    Args:
        required_roles: List of roles, any of which grants access

    Returns:
        Dependency function that yields the current user if authorized
    """

    async def role_checker(current_user: CurrentUser = Depends(get_current_user)):
        for role in required_roles:
            if role in current_user.roles:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have required roles: {', '.join(required_roles)}"
        )

    return role_checker


def require_permissions(required_permissions: List[str]):
    """
    Dependency to check if user has any of the required permissions

    Args:
        required_permissions: List of permissions, any of which grants access

    Returns:
        Dependency function that yields the current user if authorized
    """

    async def permission_checker(current_user: CurrentUser = Depends(get_current_user)):
        user_permissions = current_user.permissions

        for permission in required_permissions:
            if permission in user_permissions:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have required permissions: {', '.join(required_permissions)}"
        )

    return permission_checker


async def validate_ownership(resource_user_id: UUID, current_user: CurrentUser):
    """
    Validate that the current user owns the resource or is an admin

    Args:
        resource_user_id: The user ID associated with the resource
        current_user: The current authenticated user

    Returns:
        bool: True if the user has access

    Raises:
        HTTPException: If the user doesn't have access
    """
    # Admins can access any resource
    if "admin" in current_user.roles:
        return True

    # Users can only access their own resources
    if resource_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    return True