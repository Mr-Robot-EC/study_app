from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from ..session import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID, primary_key=True, default=uuid4)
    title = Column(String)
    content = Column(Text)
    user_id = Column(UUID, index=True)  # Reference to user ID from auth service
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)