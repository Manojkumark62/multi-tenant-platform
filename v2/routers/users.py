from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.user import get_current_user
from models.user import User
from v2.schemas.user import UserResponse
from services import user_service

router = APIRouter(prefix="/users", tags=["V2 - Users"])

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user_details(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.get_user(db, user_id)

@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def list_users(page: int = 1, page_size: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    offset = (page - 1) * page_size
    return user_service.list_users(db, offset, page_size)