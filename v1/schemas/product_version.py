from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ProductVersionBase(BaseModel):
    version: str = Field(..., min_length=1, max_length=50)
    price: Decimal = Field(..., ge=0)
    description: str | None = None
    is_active: bool = True

class ProductVersionCreate(ProductVersionBase):
    product_id: int

class ProductVersionUpdate(BaseModel):
    version: str | None = Field(None, min_length=1, max_length=50)
    price: Decimal | None = Field(None, ge=0)
    description: str | None = None
    is_active: bool | None = None

class ProductVersionResponse(ProductVersionBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)