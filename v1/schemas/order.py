from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

class OrderItemCreate(BaseModel):
    product_id: int
    product_version_id: int | None = None
    quantity: int = Field(ge=1)

class OrderBase(BaseModel):
    tenant_id: int | None = None
    user_id: int | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)

class OrderCreate(BaseModel):
    items: list[OrderItemCreate] | None = None
    product_id: int | None = None
    product_version_id: int | None = None
    quantity: int | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)

    @model_validator(mode="before")
    @classmethod
    def normalize_order_payload(cls, values: Any):
        if not isinstance(values, dict):
            return values

        if values.get("items") is not None:
            return values

        product_id = values.get("product_id")
        quantity = values.get("quantity")
        if product_id is not None and quantity is not None:
            values["items"] = [{
                "product_id": product_id,
                "product_version_id": values.get("product_version_id"),
                "quantity": quantity,
            }]

        return values

    @property
    def normalized_items(self):
        return self.items or []

class OrderUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=1, max_length=30)

class OrderResponse(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    status: str
    total_amount: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)