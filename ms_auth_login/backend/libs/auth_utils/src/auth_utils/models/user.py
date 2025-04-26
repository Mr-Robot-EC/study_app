# File: backend/libs/auth_utils/src/auth_utils/models/user.py
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: str  # Using string instead of UUID for easier handling in JWT
    email: str
    name: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    metadata: Optional[Dict] = None

    @property
    def uuid(self) -> UUID:
        """Convert string ID to UUID when needed"""
        return UUID(self.id)