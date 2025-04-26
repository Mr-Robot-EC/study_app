# File: backend/services/auth_service/src/api/webhooks.py
import json
import hashlib
import hmac
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
import httpx

from ..schemas import WebhookCreate, WebhookResponse
from ..db.session import get_db
from ..db.models import Webhook, User
from .dependencies import get_current_admin

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("", response_model=WebhookResponse)
async def create_webhook(
        webhook: WebhookCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin)
):
    """Create a new webhook (admin only)"""
    db_webhook = Webhook(
        url=str(webhook.url),
        event_type=webhook.event_type,
        secret=webhook.secret,
        created_by=current_user.id,
        config=webhook.config or {}
    )

    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)

    return db_webhook


@router.get("", response_model=List[WebhookResponse])
async def read_webhooks(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin)
):
    """Get all webhooks (admin only)"""
    webhooks = db.query(Webhook).all()
    return webhooks


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def read_webhook(
        webhook_id: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin)
):
    """Get webhook by ID (admin only)"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    return webhook


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
        webhook_id: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin)
):
    """Delete webhook (admin only)"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )

    db.delete(webhook)
    db.commit()

    return None


async def trigger_webhook(
        db: Session,
        event_type: str,
        user_id: UUID,
        data: Optional[dict] = None,
        background_tasks: Optional[BackgroundTasks] = None
):
    """Trigger webhooks for given event type"""
    # Get webhooks for this event type
    webhooks = db.query(Webhook).filter(
        Webhook.event_type == event_type,
        Webhook.is_active == True
    ).all()

    if not webhooks:
        return

    # Get user data
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return

    # Prepare payload
    payload = {
        "event": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "roles": user.roles
        }
    }

    # Add custom data if provided
    if data:
        payload["data"] = data

    # Function to send webhook
    async def send_webhook(webhook: Webhook, payload: dict):
        try:
            # Prepare payload
            json_payload = json.dumps(payload)

            # Create signature for security
            signature = hmac.new(
                webhook.secret.encode(),
                json_payload.encode(),
                hashlib.sha256
            ).hexdigest()

            # Send webhook
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": event_type
                    },
                    timeout=5.0
                )

            # Update webhook stats
            webhook.last_triggered = datetime.utcnow()
            webhook.trigger_count += 1
            db.commit()

            return response.status_code

        except Exception as e:
            print(f"Error sending webhook to {webhook.url}: {str(e)}")
            return None

    # If background tasks provided, use them
    if background_tasks:
        for webhook in webhooks:
            background_tasks.add_task(send_webhook, webhook, payload)
    else:
        # Otherwise, send synchronously (less recommended)
        for webhook in webhooks:
            await send_webhook(webhook, payload)