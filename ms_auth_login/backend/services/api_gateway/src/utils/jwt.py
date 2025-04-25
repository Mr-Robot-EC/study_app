import jwt
from fastapi import HTTPException, status
import logging

from ..config.settings import JWT_SECRET_KEY, JWT_ALGORITHM

logger = logging.getLogger("api_gateway")


async def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token

    Args:
        token: The JWT token to verify

    Returns:
        dict: The decoded token payload

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.PyJWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )