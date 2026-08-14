from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.user import User
from models.session import Session as UserSession
from models.blacklisted_token import BlacklistedToken
from models.otp_verification import OTPVerification
from models.tenant import Tenant
from models.tenant_user import TenantUser
from utils.jwt_handle import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, create_refresh_token, decode_token
from utils.hashing import hash_password, verify_password
from utils.otp import verify_otp as verify_otp_code
from utils.token import generate_jti, generate_token, hash_token
from utils.datetime import add_days, utc_now_naive
from datetime import datetime, timezone, timedelta
import secrets

def register_user(db: Session, request) -> dict:
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    full_name = (request.full_name or "").strip()
    name_parts = full_name.split(maxsplit=1)
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )
    db.add(user)
    db.flush()

    if request.tenant_id is not None:
        tenant = db.query(Tenant).filter(Tenant.id == request.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
        db.add(TenantUser(tenant_id=tenant.id, user_id=user.id))

    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully", "user_id": user.id, "email": user.email}


def login_user(db: Session, request) -> dict:
    return login(db, request.email, request.password)


def verify_otp(db: Session, request) -> dict:
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    otp_record = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.user_id == user.id,
            OTPVerification.is_verified.is_(False),
            OTPVerification.expires_at > utc_now_naive(),
        )
        .order_by(OTPVerification.created_at.desc())
        .first()
    )

    if not otp_record or request.otp != otp_record.otp_code:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP")

    otp_record.is_verified = True
    otp_record.verified_at = utc_now_naive()

    access_jti = generate_jti()
    refresh_jti = generate_jti()
    access_token = create_access_token({"sub": str(user.id), "jti": access_jti})
    refresh_token = create_refresh_token({"sub": str(user.id), "jti": refresh_jti})

    session = UserSession(user_id=user.id, refresh_token=hash_token(refresh_token), expires_at=add_days(7))
    db.add(session)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


def logout_user(db: Session, refresh_token: str) -> dict:
    logout(db, refresh_token)
    return {"message": "Logged out successfully"}


def login(db: Session, email: str, password: str) -> dict:
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_jti = generate_jti()
    refresh_jti = generate_jti()
    access_token = create_access_token({"sub": str(user.id), "jti": access_jti})
    refresh_token = create_refresh_token({"sub": str(user.id), "jti": refresh_jti})

    session = UserSession(user_id=user.id, refresh_token=hash_token(refresh_token), expires_at=add_days(7))
    db.add(session)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60}


def request_otp(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise ValueError("User with this email does not exist")

    if getattr(user, "is_email_verified", False):
        raise ValueError("Email is already verified")

    otp = f"{secrets.randbelow(1000000):06d}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    db.query(OTPVerification).filter(
        OTPVerification.user_id == user.id,
        OTPVerification.is_verified.is_(False),
        OTPVerification.expires_at > datetime.now(timezone.utc),
    ).delete(synchronize_session=False)

    tenant_id = None
    if hasattr(user, "tenant_users"):
        tenant_link = db.query(TenantUser).filter(TenantUser.user_id == user.id).order_by(TenantUser.id.desc()).first()
        if tenant_link is not None:
            tenant_id = tenant_link.tenant_id
    if tenant_id is None:
        tenant_id = 1

    otp_record = OTPVerification(
        tenant_id=tenant_id,
        user_id=user.id,
        otp_code=otp,
        purpose="email_verification",
        attempts=0,
        is_verified=False,
        expires_at=expires_at,
    )

    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)

    print(f"OTP for {email}: {otp}")  # Development only: replace this with email sending later.

    return {"message": "OTP sent successfully", "email": email}

def refresh_access_token(db: Session, refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token") from exc

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_hash = hash_token(refresh_token)
    session = db.query(UserSession).filter(UserSession.refresh_token == token_hash, UserSession.user_id == int(user_id), UserSession.revoked_at.is_(None)).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or revoked")

    user = db.query(User).filter(User.id == int(user_id), User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    access_jti = generate_jti()
    refresh_jti = generate_jti()
    access_token = create_access_token({"sub": str(user.id), "jti": access_jti})
    new_refresh_token = create_refresh_token({"sub": str(user.id), "jti": refresh_jti})

    session.refresh_token = hash_token(new_refresh_token)
    session.expires_at = add_days(7)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

def logout(db: Session, refresh_token: str) -> None:
    token_hash = hash_token(refresh_token)
    session = db.query(UserSession).filter(UserSession.refresh_token == token_hash, UserSession.revoked_at.is_(None)).first()
    if session:
        session.revoked_at = utc_now_naive()
        db.commit()

def blacklist_token(db: Session, token: str) -> None:
    payload = decode_token(token)
    jti = payload.get("jti")
    user_id = payload.get("sub")
    expires_at = payload.get("exp")

    if not jti or not user_id or not expires_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    from datetime import datetime, timezone
    expiry = datetime.fromtimestamp(expires_at, tz=timezone.utc).replace(tzinfo=None)
    existing_token = db.query(BlacklistedToken).filter(BlacklistedToken.token_jti == jti).first()

    if not existing_token:
        db.add(BlacklistedToken(user_id=int(user_id), token_jti=jti, expires_at=expiry))
        db.commit()