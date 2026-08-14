from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.user import User
from v1.schemas.user import UserCreate, UserUpdate
from utils.hashing import hash_password

def create_user(db: Session, user_data: UserCreate) -> User:
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    full_name = (user_data.full_name or "").strip()
    parts = full_name.split(maxsplit=1)
    first_name = parts[0] if parts else None
    last_name = parts[1] if len(parts) > 1 else None

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        first_name=first_name,
        last_name=last_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def list_users(db: Session, offset: int = 0, limit: int = 20) -> list[User]:
    return db.query(User).order_by(User.id.desc()).offset(offset).limit(limit).all()

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    user = get_user(db, user_id)

    update_data = user_data.model_dump(exclude_unset=True)
    if "email" in update_data and update_data["email"] != user.email:
        existing_user = db.query(User).filter(User.email == update_data["email"], User.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already in use")

    if "full_name" in update_data:
        user.full_name = update_data["full_name"]
        update_data.pop("full_name")

    if "phone" in update_data:
        update_data.pop("phone")

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

def deactivate_user(db: Session, user_id: int) -> User:
    user = get_user(db, user_id)
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user