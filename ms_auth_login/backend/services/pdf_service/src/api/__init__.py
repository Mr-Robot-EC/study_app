# File: backend/services/pdf_service/src/api/__init__.py
from .document import router as document_router
from .admin import router as admin_router

__all__ = ["document_router", "admin_router"]