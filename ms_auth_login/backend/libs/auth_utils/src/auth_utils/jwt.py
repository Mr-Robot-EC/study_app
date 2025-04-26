# File: backend/libs/auth_utils/src/auth_utils/jwt.py
from datetime import datetime
import jwt
from fastapi import HTTPException, status

from .config import JWT_SECRET_KEY, JWT_ALGORITHM

def decode_jwt(token: str, service_name: str = None):
    """
    Decode and validate a JWT token

    Args:
        token: The JWT token to decode
        service_name: Optional service name to validate against audience

    Returns:
        dict: The decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        # Check token expiration
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has no expiration"
            )

        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )

        # Check audience if service_name is provided
        if service_name:
            aud = payload.get("aud", [])
            if isinstance(aud, str):
                aud = [aud]

            if service_name not in aud:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token not valid for {service_name}"
                )

        return payload

    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}"
        )