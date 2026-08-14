from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.user import get_current_user
from models.user import User
from v1.schemas.user import UserCreate, UserResponse, UserUpdate
from services import user_service

router = APIRouter(prefix="/users", tags=["V1 - Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, data)

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user_details(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.get_user(db, user_id)

@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.update_user(db, user_id, data)

@router.delete("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def deactivate_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.deactivate_user(db, user_id)