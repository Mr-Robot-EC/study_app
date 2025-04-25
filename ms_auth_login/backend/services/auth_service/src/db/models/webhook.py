import uuid
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID


from ms_auth_login.backend.services.auth_service.src.db.session import Base

class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    url = Column(String)
    event_type = Column(String)  # e.g., "user.created", "user.login", etc.
    secret = Column(String)
    created_by = Column(UUID, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)