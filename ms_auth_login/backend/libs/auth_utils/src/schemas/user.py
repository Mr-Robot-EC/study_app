from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel

class CurrentUser(BaseModel):
    id: UUID
    email: str
    name: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    metadata: Optional[Dict] = None