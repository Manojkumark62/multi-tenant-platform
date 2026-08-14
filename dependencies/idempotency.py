from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.user import get_current_user
from models.idempotency_key import IdempotencyKey
from models.user import User
from utils.idempotency import generate_request_hash, validate_idempotency_key

def get_idempotency_key(idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")) -> str:
    if not idempotency_key or not validate_idempotency_key(idempotency_key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Valid Idempotency-Key header is required")
    return idempotency_key

def check_idempotency_key(idempotency_key: str = Depends(get_idempotency_key), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> IdempotencyKey | None:
    existing_key = db.query(IdempotencyKey).filter(IdempotencyKey.key == idempotency_key, IdempotencyKey.user_id == current_user.id).first()
    return existing_key

def create_request_hash(payload: dict) -> str:
    return generate_request_hash(payload)