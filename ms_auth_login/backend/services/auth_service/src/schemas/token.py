# File: backend/services/auth_service/src/schemas/token.py
from typing import List, Optional, Union
from pydantic import BaseModel, validator

class TokenPayload(BaseModel):
    """Schema for token payload"""
    sub: str
    exp: int
    iat: int
    jti: str
    iss: str
    email: Optional[str] = None
    name: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    aud: Optional[Union[str, List[str]]] = None
    token_type: Optional[str] = None  # For refresh tokens

class Token(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int  # Seconds until token expires

class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str

class LogoutRequest(BaseModel):
    """Schema for logout request"""
    refresh_token: Optional[str] = None

    @validator('refresh_token')
    def validate_refresh_token(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Refresh token cannot be empty if provided")
        return v