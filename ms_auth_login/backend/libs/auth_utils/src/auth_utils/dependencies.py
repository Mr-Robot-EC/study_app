# File: backend/libs/auth_utils/src/auth_utils/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .models.user import CurrentUser
from .jwt import decode_jwt

# Token security scheme
security = HTTPBearer()

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        service_name: str = None  # The service using this utility
) -> CurrentUser:
    """
    Dependency to get the current user from a JWT token

    Args:
        credentials: The HTTP Bearer token
        service_name: Optional service name to validate against audience

    Returns:
        CurrentUser: The current authenticated user
    """
    token = credentials.credentials

    # Decode and validate the token
    payload = decode_jwt(token, service_name)

    # Extract user information
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User identifier missing"
        )

    return CurrentUser(
        id=user_id,
        email=payload.get("email", ""),
        name=payload.get("name"),
        roles=payload.get("roles", []),
        permissions=payload.get("permissions", []),
        metadata=payload.get("metadata", {})
    )