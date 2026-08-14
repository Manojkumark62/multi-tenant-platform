from fastapi import APIRouter, Body, Depends, Form, Header, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from database import get_db
from services import auth_service
from v1.schemas.auth import RegisterRequest, LoginRequest, VerifyOTP, RefreshTokenRequest, LogoutRequest, TokenResponse
from v1.schemas.auth import RequestOTP, OTPResponse

router = APIRouter(prefix="/auth", tags=["V1 - Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register_user(db, request)

@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    return auth_service.login_user(db, LoginRequest(email=username, password=password))

@router.post("/send-otp", response_model=OTPResponse)
def send_otp(request: RequestOTP, db: Session = Depends(get_db)):
    try:
        return auth_service.request_otp(db, request.email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(request: VerifyOTP, db: Session = Depends(get_db)):
    return auth_service.verify_otp(db, request)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: str | dict | None = Body(default=None),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    token_value = None

    if isinstance(request, dict):
        token_value = request.get("refresh_token")
    elif isinstance(request, str):
        token_value = request

    if not token_value and authorization:
        auth_header = authorization.strip()
        if auth_header.lower().startswith("bearer "):
            token_value = auth_header.split(" ", 1)[1]

    if not token_value:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Refresh token is required")

    return auth_service.refresh_access_token(db, token_value)

@router.post("/logout")
def logout(request: LogoutRequest, db: Session = Depends(get_db)):
    return auth_service.logout_user(db, request.refresh_token)