from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.user import get_current_user
from models.user import User
from v1.schemas.session import SessionResponse
from services import session_service
from utils.token import hash_token

router = APIRouter(prefix="/sessions", tags=["V1 - Sessions"])

@router.get("/", response_model=list[SessionResponse], status_code=status.HTTP_200_OK)
def list_sessions(page: int = 1, page_size: int = 20, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    return session_service.list_user_sessions(db, current_user.id, False, offset, page_size)

@router.get("/{session_id}", response_model=SessionResponse, status_code=status.HTTP_200_OK)
def get_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return session_service.get_session(db, session_id, current_user.id)

@router.post("/revoke/{session_id}", response_model=SessionResponse, status_code=status.HTTP_200_OK)
def revoke_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return session_service.revoke_session(db, session_id, current_user.id)

@router.post("/revoke-all", status_code=status.HTTP_200_OK)
def revoke_all_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    revoked_count = session_service.revoke_all_user_sessions(db, current_user.id)
    return {"message": "All sessions revoked", "revoked_count": revoked_count}

@router.post("/validate", response_model=SessionResponse, status_code=status.HTTP_200_OK)
def validate_session(token: str, db: Session = Depends(get_db)):
    token_hash = hash_token(token)
    return session_service.get_active_session(db, token_hash)