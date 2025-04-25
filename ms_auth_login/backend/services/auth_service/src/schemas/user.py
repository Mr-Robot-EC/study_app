from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

from ms_auth_login.backend.services.auth_service.src.schemas.token import Token

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class RolesUpdate(BaseModel):
    roles: List[str]

class User(UserBase):
    id: UUID
    roles: List[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    google_id: Optional[str] = None

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: User