from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class InventoryReservationBase(BaseModel):
    quantity: int = Field(..., gt=0)
    status: str = Field(default="reserved", max_length=50)
    expires_at: datetime | None = None

class InventoryReservationCreate(InventoryReservationBase):
    inventory_id: int
    order_id: int

class InventoryReservationUpdate(BaseModel):
    quantity: int | None = Field(None, gt=0)
    status: str | None = Field(None, max_length=50)
    expires_at: datetime | None = None

class InventoryReservationResponse(InventoryReservationBase):
    id: int
    inventory_id: int
    order_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)