# File: backend/services/pdf_service/src/schemas/audit.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class DocumentAudit(BaseModel):
    id: UUID
    document_id: UUID
    action: str
    user_id: UUID
    created_at: datetime
    details: Optional[str] = None

    class Config:
        from_attributes = True