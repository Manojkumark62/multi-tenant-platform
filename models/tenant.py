from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant_users = relationship("TenantUser", back_populates="tenant", cascade="all, delete-orphan", overlaps="users")
    users = relationship("User", secondary="tenant_users", back_populates="tenants", overlaps="tenant_users")
    products = relationship("Product", back_populates="tenant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="tenant", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="tenant", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="tenant", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="tenant", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="tenant", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="tenant", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="tenant", cascade="all, delete-orphan")
    idempotency_keys = relationship("IdempotencyKey", back_populates="tenant", cascade="all, delete-orphan")
    otp_verifications = relationship("OTPVerification", back_populates="tenant", cascade="all, delete-orphan")
    scheduled_jobs = relationship("ScheduledJob", back_populates="tenant", cascade="all, delete-orphan")
    external_integrations = relationship("ExternalIntegration", back_populates="tenant", cascade="all, delete-orphan")
    job_queue = relationship("JobQueue", back_populates="tenant", cascade="all, delete-orphan")