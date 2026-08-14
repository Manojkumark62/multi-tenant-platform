from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class InventoryBase(BaseModel):
    tenant_id: int
    product_id: int
    quantity: int = Field(default=0, ge=0)

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=0)

class InventoryResponse(InventoryBase):
    id: int
    reserved_quantity: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)