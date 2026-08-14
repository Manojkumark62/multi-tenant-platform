from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from database import Base


class InventoryReservation(Base):
    __tablename__ = "inventory_reservations"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="reserved")
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)

    inventory = relationship("Inventory", back_populates="reservations")
    order = relationship("Order", back_populates="inventory_reservations")

    @property
    def user_id(self):
        return self.order.user_id if self.order else None

    @user_id.setter
    def user_id(self, value):
        return None

    @property
    def updated_at(self):
        return self.created_at

    @updated_at.setter
    def updated_at(self, value):
        return None

    @property
    def released_at(self):
        return None

    @released_at.setter
    def released_at(self, value):
        return None