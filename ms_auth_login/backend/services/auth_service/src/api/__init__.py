# File: backend/services/auth_service/src/api/__init__.py
from .auth import router as auth_router
from .users import router as users_router
from .webhooks import router as webhooks_router

__all__ = ["auth_router", "users_router", "webhooks_router"]