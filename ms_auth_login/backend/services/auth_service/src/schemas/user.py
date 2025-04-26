# File: backend/services/auth_service/src/schemas/user.py
from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: EmailStr
    full_name: str = Field(..., min_length=1)


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for user updates"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Full name cannot be empty")
        return v


class RolesUpdate(BaseModel):
    """Schema for updating user roles"""
    roles: List[str]


class UserInDB(UserBase):
    """Schema for user in database"""
    id: UUID
    roles: List[str] = ["user"]
    permissions: List[str] = []
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    google_id: Optional[str] = None
    user_metadata: Optional[Dict] = {}  # Changed from 'metadata' to 'user_metadata'


    class Config:
        from_attributes = True


class User(UserInDB):
    """Full user schema returned to clients"""
    # This inherits everything from UserInDB
    pass