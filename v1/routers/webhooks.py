from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.webhook import WebhookCreate, WebhookResponse, WebhookUpdate
from services import webhook_service

router = APIRouter(prefix="/webhooks", tags=["V1 - Webhooks"])

@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(data: WebhookCreate, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return webhook_service.create_webhook(db, current_tenant.id, data)

@router.get("/{webhook_id}", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
def get_webhook(webhook_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return webhook_service.get_webhook(db, current_tenant.id, webhook_id)

@router.get("/", response_model=list[WebhookResponse], status_code=status.HTTP_200_OK)
def list_webhooks(page: int = 1, page_size: int = 20, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    return webhook_service.list_webhooks(db, current_tenant.id, offset, page_size)

@router.patch("/{webhook_id}", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
def update_webhook(webhook_id: int, data: WebhookUpdate, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return webhook_service.update_webhook(db, current_tenant.id, webhook_id, data)

@router.delete("/{webhook_id}", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
def deactivate_webhook(webhook_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return webhook_service.deactivate_webhook(db, current_tenant.id, webhook_id)