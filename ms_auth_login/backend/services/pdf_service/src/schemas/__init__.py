# File: backend/services/pdf_service/src/schemas/__init__.py
from .document import DocumentBase, DocumentCreate, DocumentUpdate, Document
from .audit import DocumentAudit

__all__ = ["DocumentBase", "DocumentCreate", "DocumentUpdate", "Document", "DocumentAudit"]