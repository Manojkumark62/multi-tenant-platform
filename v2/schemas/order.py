from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)

class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)
    currency: str = Field(default="USD", min_length=3, max_length=3)

class OrderUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=1, max_length=30)

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    status: str
    total_amount: Decimal
    currency: str
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)