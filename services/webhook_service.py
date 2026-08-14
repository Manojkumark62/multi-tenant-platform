from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.webhook import Webhook
from models.webhook_retry import WebhookRetry
from v1.schemas.webhook import WebhookCreate, WebhookUpdate
from utils.datetime import utc_now_naive

def create_webhook(db: Session, tenant_id: int, webhook_data: WebhookCreate) -> Webhook:
    existing_webhook = db.query(Webhook).filter(Webhook.tenant_id == tenant_id, Webhook.url == webhook_data.url).first()
    if existing_webhook:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Webhook with this URL already exists")

    webhook = Webhook(
        tenant_id=tenant_id,
        name=webhook_data.name,
        url=webhook_data.url,
        event_type=webhook_data.event_type,
        secret=webhook_data.secret,
        is_active=webhook_data.is_active,
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return webhook

def get_webhook(db: Session, tenant_id: int, webhook_id: int) -> Webhook:
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id, Webhook.tenant_id == tenant_id).first()
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    return webhook

def list_webhooks(db: Session, tenant_id: int, offset: int = 0, limit: int = 20) -> list[Webhook]:
    return db.query(Webhook).filter(Webhook.tenant_id == tenant_id).order_by(Webhook.id.desc()).offset(offset).limit(limit).all()

def update_webhook(db: Session, tenant_id: int, webhook_id: int, webhook_data: WebhookUpdate) -> Webhook:
    webhook = get_webhook(db, tenant_id, webhook_id)
    update_data = webhook_data.model_dump(exclude_unset=True)

    if "url" in update_data and update_data["url"] != webhook.url:
        existing_webhook = db.query(Webhook).filter(Webhook.tenant_id == tenant_id, Webhook.url == update_data["url"], Webhook.id != webhook_id).first()
        if existing_webhook:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Webhook with this URL already exists")

    for field, value in update_data.items():
        setattr(webhook, field, value)

    db.commit()
    db.refresh(webhook)
    return webhook

def deactivate_webhook(db: Session, tenant_id: int, webhook_id: int) -> Webhook:
    webhook = get_webhook(db, tenant_id, webhook_id)
    webhook.is_active = False
    db.commit()
    db.refresh(webhook)
    return webhook

def create_webhook_retry(db: Session, webhook_id: int, event_id: str, payload: dict, error_message: str | None = None) -> WebhookRetry:
    retry = WebhookRetry(webhook_id=webhook_id, event_id=event_id, payload=payload, error_message=error_message, attempt_count=0, status="pending", next_retry_at=utc_now_naive())
    db.add(retry)
    db.commit()
    db.refresh(retry)
    return retry

def mark_retry_success(db: Session, retry_id: int) -> WebhookRetry:
    retry = db.query(WebhookRetry).filter(WebhookRetry.id == retry_id).first()
    if not retry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook retry not found")

    retry.status = "success"
    retry.completed_at = utc_now_naive()
    db.commit()
    db.refresh(retry)
    return retry