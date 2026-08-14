from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_reference = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="bookings")
    user = relationship("User", back_populates="bookings")

    @property
    def resource_id(self):
        return self.booking_reference

    @resource_id.setter
    def resource_id(self, value):
        self.booking_reference = value

    @property
    def tenant_id_value(self):
        return self.tenant_id

    @tenant_id_value.setter
    def tenant_id_value(self, value):
        self.tenant_id = value