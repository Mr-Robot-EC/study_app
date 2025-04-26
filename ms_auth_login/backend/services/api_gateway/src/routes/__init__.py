# File: backend/services/api_gateway/src/routes/__init__.py
from .health import router as health_router
from .info import router as info_router

__all__ = ["health_router", "info_router"]