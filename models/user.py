from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def full_name(self):
        parts = [part for part in (self.first_name, self.last_name) if part]
        return " ".join(parts)

    @full_name.setter
    def full_name(self, value):
        name = (value or "").strip()
        if not name:
            self.first_name = None
            self.last_name = None
            return

        parts = name.split(maxsplit=1)
        self.first_name = parts[0]
        self.last_name = parts[1] if len(parts) > 1 else None

    @property
    def phone(self):
        return None

    @phone.setter
    def phone(self, value):
        return

    tenant_users = relationship("TenantUser", back_populates="user", cascade="all, delete-orphan", overlaps="tenants")
    tenants = relationship("Tenant", secondary="tenant_users", back_populates="users", overlaps="tenant_users")
    orders = relationship("Order", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    requested_approvals = relationship("Approval", foreign_keys="Approval.requested_by", back_populates="requester")
    approved_approvals = relationship("Approval", foreign_keys="Approval.approved_by", back_populates="approver")
    otp_verifications = relationship("OTPVerification", back_populates="user", cascade="all, delete-orphan")