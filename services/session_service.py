from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.session import Session as UserSession
from models.user import User
from utils.datetime import utc_now_naive

def create_session(db: Session, user_id: int, token_hash: str, expires_at) -> UserSession:
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or inactive")

    session = UserSession(user_id=user_id, refresh_token=token_hash, expires_at=expires_at)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_session(db: Session, session_id: int, user_id: int | None = None) -> UserSession:
    query = db.query(UserSession).filter(UserSession.id == session_id)
    if user_id is not None:
        query = query.filter(UserSession.user_id == user_id)

    session = query.first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session

def get_active_session(db: Session, token_hash: str) -> UserSession:
    session = db.query(UserSession).filter(UserSession.refresh_token == token_hash, UserSession.revoked_at.is_(None)).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or revoked")

    if session.expires_at <= utc_now_naive():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session has expired")

    return session

def revoke_session(db: Session, session_id: int, user_id: int) -> UserSession:
    session = get_session(db, session_id, user_id)

    if session.revoked_at is not None:
        return session

    session.revoked_at = utc_now_naive()
    db.commit()
    db.refresh(session)
    return session

def revoke_all_user_sessions(db: Session, user_id: int) -> int:
    sessions = db.query(UserSession).filter(UserSession.user_id == user_id, UserSession.revoked_at.is_(None)).all()

    revoked_count = 0
    current_time = utc_now_naive()

    for session in sessions:
        session.revoked_at = current_time
        revoked_count += 1

    db.commit()
    return revoked_count

def list_user_sessions(db: Session, user_id: int, include_revoked: bool = False, offset: int = 0, limit: int = 20) -> list[UserSession]:
    query = db.query(UserSession).filter(UserSession.user_id == user_id)

    if not include_revoked:
        query = query.filter(UserSession.revoked_at.is_(None))

    return query.order_by(UserSession.created_at.desc()).offset(offset).limit(limit).all()