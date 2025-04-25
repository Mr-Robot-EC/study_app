from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class WebhookBase(BaseModel):
    url: str
    event_type: str
    secret: str

class WebhookCreate(WebhookBase):
    pass

class WebhookResponse(WebhookBase):
    id: UUID
    created_at: datetime
    is_active: bool

    class Config:
        orm_mode = True