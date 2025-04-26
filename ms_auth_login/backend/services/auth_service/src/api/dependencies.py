# File: backend/services/auth_service/src/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import PyJWTError
from uuid import UUID

from ..core.config import settings
from ..db.session import get_db
from ..db.models import User

# OAuth2 password bearer token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Get user ID from token
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception

        # Check if token is a refresh token
        if payload.get("token_type") == "refresh":
            raise credentials_exception

    except PyJWTError:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
):
    """Check if current user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return current_user


async def get_current_admin(
        current_user: User = Depends(get_current_active_user)
):
    """Check if current user is admin"""
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return current_user
