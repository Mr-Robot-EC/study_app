from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from backend.libs.auth_utils import CurrentUser, require_roles
from ..db.session import get_db
from ..db.models import Document
from ..schemas import Document as DocumentSchema

router = APIRouter(
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