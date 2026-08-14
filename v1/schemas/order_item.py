from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0, decimal_places=2)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=1)

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)