import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB
from sqlalchemy.orm import relationship

from ..session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    roles = Column(ARRAY(String), default=["user"])
    permissions = Column(ARRAY(String), default=["read:own"])
    google_id = Column(String, nullable=True, unique=True)
    user_metadata = Column(JSONB, default={})  # Changed from 'metadata' to 'user_metadata'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="created_by_user", foreign_keys="Webhook.created_by")