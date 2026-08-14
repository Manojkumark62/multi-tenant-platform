from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from services import auth_service
from v1.schemas.auth import RegisterRequest, LoginRequest, VerifyOTP, RefreshTokenRequest, LogoutRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["V2 - Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register_user(db, request)

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login_user(db, request)

@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(request: VerifyOTP, db: Session = Depends(get_db)):
    return auth_service.verify_otp(db, request)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(db, request.refresh_token)

@router.post("/logout")
def logout(request: LogoutRequest, db: Session = Depends(get_db)):
    return auth_service.logout_user(db, request.refresh_token)