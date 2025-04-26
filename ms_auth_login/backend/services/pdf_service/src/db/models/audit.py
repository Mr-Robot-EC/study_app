# File: backend/services/pdf_service/src/db/models/audit.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from ..session import Base

class DocumentAudit(Base):
    __tablename__ = "document_audits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    action = Column(String)  # e.g., "created", "updated", "viewed"
    user_id = Column(UUID(as_uuid=True))  # User who performed the action
    created_at = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)  # Additional details about the action