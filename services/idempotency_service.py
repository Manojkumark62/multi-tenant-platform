from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.idempotency_key import IdempotencyKey
from utils.idempotency import generate_request_hash

def create_idempotency_key(db: Session, user_id: int, key: str, payload: dict) -> IdempotencyKey:
    request_hash = generate_request_hash(payload)
    existing_key = db.query(IdempotencyKey).filter(IdempotencyKey.key == key, IdempotencyKey.user_id == user_id).first()

    if existing_key:
        if existing_key.request_hash != request_hash:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Idempotency key was already used with a different request")
        return existing_key

    idempotency_key = IdempotencyKey(key=key, user_id=user_id, request_hash=request_hash, status="processing")
    db.add(idempotency_key)
    db.commit()
    db.refresh(idempotency_key)
    return idempotency_key

def get_idempotency_key(db: Session, user_id: int, key: str) -> IdempotencyKey | None:
    return db.query(IdempotencyKey).filter(IdempotencyKey.key == key, IdempotencyKey.user_id == user_id).first()

def mark_completed(db: Session, idempotency_id: int, response_data: dict, status_code: int = 200) -> IdempotencyKey:
    idempotency_key = db.query(IdempotencyKey).filter(IdempotencyKey.id == idempotency_id).first()

    if not idempotency_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idempotency key not found")

    idempotency_key.status = "completed"
    idempotency_key.response_data = response_data
    idempotency_key.response_status = status_code
    db.commit()
    db.refresh(idempotency_key)
    return idempotency_key

def mark_failed(db: Session, idempotency_id: int, response_data: dict, status_code: int = 500) -> IdempotencyKey:
    idempotency_key = db.query(IdempotencyKey).filter(IdempotencyKey.id == idempotency_id).first()

    if not idempotency_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idempotency key not found")

    idempotency_key.status = "failed"
    idempotency_key.response_data = response_data
    idempotency_key.response_status = status_code
    db.commit()
    db.refresh(idempotency_key)
    return idempotency_key

def get_stored_response(idempotency_key: IdempotencyKey) -> tuple[dict, int] | None:
    if idempotency_key.status != "completed" or idempotency_key.response_data is None:
        return None
    return idempotency_key.response_data, idempotency_key.response_status or 200