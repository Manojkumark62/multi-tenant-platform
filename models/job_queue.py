from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base

class JobQueue(Base):
    __tablename__ = "job_queue"

    id = Column(Integer, primary_key=True, index=True)
    scheduled_job_id = Column(Integer, ForeignKey("scheduled_jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(String(100), nullable=False, index=True)
    payload = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=5)
    available_at = Column(DateTime, nullable=True, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="job_queue")
    scheduled_job = relationship("ScheduledJob", back_populates="job_queue_items")