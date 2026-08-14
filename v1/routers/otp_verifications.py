from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.user import get_current_user
from models.idempotency_key import IdempotencyKey
from models.user import User
from v1.schemas.idempotency_key import IdempotencyKeyResponse
from services import idempotency_service

router = APIRouter(prefix="/idempotency-keys", tags=["V1 - Idempotency"])

@router.get("/{key}", response_model=IdempotencyKeyResponse, status_code=status.HTTP_200_OK)
def get_idempotency_key(key: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    idempotency_key = idempotency_service.get_idempotency_key(db, current_user.id, key)
    if not idempotency_key:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idempotency key not found")
    return idempotency_key

@router.post("/check", response_model=IdempotencyKeyResponse, status_code=status.HTTP_200_OK)
def check_idempotency_key(payload: dict, idempotency_key: str = Header(..., alias="Idempotency-Key"), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return idempotency_service.create_idempotency_key(db, current_user.id, idempotency_key, payload)