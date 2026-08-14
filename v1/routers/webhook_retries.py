from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from models.webhook_retry import WebhookRetry
from v1.schemas.webhook_retry import WebhookRetryResponse
from services import webhook_service

router = APIRouter(prefix="/webhook-retries", tags=["V1 - Webhook Retries"])

@router.get("/{retry_id}", response_model=WebhookRetryResponse, status_code=status.HTTP_200_OK)
def get_webhook_retry(retry_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    retry = db.query(WebhookRetry).join(WebhookRetry.webhook).filter(WebhookRetry.id == retry_id, WebhookRetry.webhook.has(tenant_id=current_tenant.id)).first()
    if not retry:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook retry not found")
    return retry

@router.post("/{retry_id}/success", response_model=WebhookRetryResponse, status_code=status.HTTP_200_OK)
def mark_retry_success(retry_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return webhook_service.mark_retry_success(db, retry_id)