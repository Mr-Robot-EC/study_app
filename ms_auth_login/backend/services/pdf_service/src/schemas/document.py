# File: backend/services/pdf_service/src/schemas/document.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1)
    content: str

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class Document(DocumentBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True