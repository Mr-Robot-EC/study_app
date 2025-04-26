# File: backend/services/auth_service/src/schemas/webhook.py
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID
from pydantic import BaseModel, HttpUrl, validator

class WebhookBase(BaseModel):
    """Base webhook schema"""
    url: HttpUrl
    event_type: str
    secret: str

    @validator('event_type')
    def validate_event_type(cls, v):
        valid_events = [
            "user.created",
            "user.updated",
            "user.deleted",
            "user.login",
            "token.refresh"
        ]
        if v not in valid_events:
            raise ValueError(f"Event type must be one of: {', '.join(valid_events)}")
        return v

class WebhookCreate(WebhookBase):
    """Schema for webhook creation"""
    config: Optional[Dict] = {}

class WebhookResponse(WebhookBase):
    """Schema for webhook response"""
    id: UUID
    created_at: datetime
    is_active: bool
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    config: Dict = {}

    class Config:
        orm_mode = True