# File: backend/services/auth_service/src/api/users.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from ..schemas import User, UserUpdate, RolesUpdate
from ..db.session import get_db
from ..db.models import User as UserModel
from .dependencies import get_current_user, get_current_active_user, get_current_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def read_users_me(
        current_user: UserModel = Depends(get_current_active_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=User)
async def update_user_me(
        user_update: UserUpdate,
        current_user: UserModel = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Update current user profile"""
    # Update user fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    # Trigger webhook for user.updated event
    from .webhooks import trigger_webhook
    await trigger_webhook(db, "user.updated", current_user.id)

    return current_user


@router.get("", response_model=List[User])
async def read_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_admin)
):
    """Get all users (admin only)"""
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=User)
async def read_user(
        user_id: UUID,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_admin)
):
    """Get user by ID (admin only)"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}/roles", response_model=User)
async def update_user_roles(
        user_id: UUID,
        roles_update: RolesUpdate,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_admin)
):
    """Update user roles (admin only)"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update roles
    user.roles = roles_update.roles
    db.commit()
    db.refresh(user)

    # Trigger webhook for user.updated event
    from .webhooks import trigger_webhook
    await trigger_webhook(db, "user.updated", user.id)

    return user


@router.put("/{user_id}/activate", response_model=User)
async def activate_user(
        user_id: UUID,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_admin)
):
    """Activate a user (admin only)"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    db.commit()
    db.refresh(user)

    # Trigger webhook for user.updated event
    from .webhooks import trigger_webhook
    await trigger_webhook(db, "user.updated", user.id)

    return user


@router.put("/{user_id}/deactivate", response_model=User)
async def deactivate_user(
        user_id: UUID,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_admin)
):
    """Deactivate a user (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    db.commit()
    db.refresh(user)

    # Trigger webhook for user.updated event
    from .webhooks import trigger_webhook
    await trigger_webhook(db, "user.updated", user.id)

    return user