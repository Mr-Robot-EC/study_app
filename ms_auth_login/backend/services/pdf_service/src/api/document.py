# File: backend/services/pdf_service/src/api/document.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4

from auth_utils import get_current_user, CurrentUser, validate_ownership
from ..db.session import get_db
from ..db.models import Document, DocumentAudit
from ..schemas import DocumentCreate, DocumentUpdate, Document as DocumentSchema, DocumentAudit as DocumentAuditSchema

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)


@router.post("", response_model=DocumentSchema)
async def create_document(
        document: DocumentCreate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
):
    # Create document with current user ID from JWT
    db_document = Document(
        id=uuid4(),
        title=document.title,
        content=document.content,
        user_id=UUID(current_user.id)  # User ID from JWT
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Create audit record
    audit = DocumentAudit(
        id=uuid4(),
        document_id=db_document.id,
        action="created",
        user_id=UUID(current_user.id)
    )
    db.add(audit)
    db.commit()

    return db_document


@router.get("", response_model=List[DocumentSchema])
async def read_documents(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
):
    # Only return documents owned by the current user unless admin
    if "admin" in current_user.roles:
        documents = db.query(Document).offset(skip).limit(limit).all()
    else:
        documents = db.query(Document).filter(
            Document.user_id == UUID(current_user.id)
        ).offset(skip).limit(limit).all()

    return documents


@router.get("/{document_id}", response_model=DocumentSchema)
async def read_document(
        document_id: UUID,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate document ownership
    await validate_ownership(document.user_id, current_user)

    # Create view audit record
    audit = DocumentAudit(
        id=uuid4(),
        document_id=document.id,
        action="viewed",
        user_id=UUID(current_user.id)
    )
    db.add(audit)
    db.commit()

    return document


@router.put("/{document_id}", response_model=DocumentSchema)
async def update_document(
        document_id: UUID,
        document_update: DocumentUpdate,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
):
    db_document = db.query(Document).filter(Document.id == document_id).first()

    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate document ownership
    await validate_ownership(db_document.user_id, current_user)

    # Update document
    for field, value in document_update.dict(exclude_unset=True).items():
        setattr(db_document, field, value)

    db.commit()
    db.refresh(db_document)

    # Create update audit record
    audit = DocumentAudit(
        id=uuid4(),
        document_id=db_document.id,
        action="updated",
        user_id=UUID(current_user.id),
        details=f"Updated fields: {', '.join(document_update.dict(exclude_unset=True).keys())}"
    )
    db.add(audit)
    db.commit()

    return db_document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
        document_id: UUID,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate document ownership
    await validate_ownership(document.user_id, current_user)

    # Create delete audit record before deletion
    audit = DocumentAudit(
        id=uuid4(),
        document_id=document.id,
        action="deleted",
        user_id=UUID(current_user.id)
    )
    db.add(audit)

    # Delete document
    db.delete(document)
    db.commit()

    return None


@router.get("/{document_id}/audit", response_model=List[DocumentAuditSchema])
async def get_document_audit_trail(
        document_id: UUID,
        db: Session = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate document ownership
    await validate_ownership(document.user_id, current_user)

    # Get audit trail
    audit_trail = db.query(DocumentAudit).filter(
        DocumentAudit.document_id == document_id
    ).order_by(DocumentAudit.created_at.desc()).all()

    return audit_trail

# File: backend/services/pdf_service/src/api/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from auth_utils import CurrentUser, require_roles
from ..db.session import get_db
from ..db.models import Document
from ..schemas import Document as DocumentSchema

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/documents", response_model=List[DocumentSchema])
async def admin_read_all_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(["admin"]))  # Only admins can access
):
    documents = db.query(Document).offset(skip).limit(limit).all()
    return documents