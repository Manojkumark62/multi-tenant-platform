from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Numeric
from sqlalchemy.orm import relationship
from database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="orders")
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    inventory_reservations = relationship("InventoryReservation", back_populates="order", cascade="all, delete-orphan")

    @property
    def currency(self):
        return "USD"

    @currency.setter
    def currency(self, value):
        return None

    @property
    def items(self):
        return list(self.order_items or [])

    @items.setter
    def items(self, value):
        return None

    @property
    def updated_at(self):
        return self.created_at

    @updated_at.setter
    def updated_at(self, value):
        return None