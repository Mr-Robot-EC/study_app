# File: backend/services/auth_service/src/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Union, List
from uuid import uuid4
from passlib.context import CryptContext
import jwt

from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storage"""
    return pwd_context.hash(password)


def create_jwt_token(
        data: Dict,
        expires_delta: Optional[timedelta] = None,
        audiences: Union[str, List[str]] = None
) -> str:
    """
    Create a JWT token with standard claims

    Args:
        data: Payload data to include in the token
        expires_delta: Optional expiration time delta
        audiences: Service(s) the token is intended for

    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()

    # Set standard claims
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid4()),
        "iss": "auth-service"
    })

    # Add audience if provided
    if audiences:
        to_encode["aud"] = audiences

    # Encode the JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt