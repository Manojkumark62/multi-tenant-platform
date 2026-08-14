from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class InventoryUpdate(BaseModel):
    quantity: int = Field(ge=0)

class InventoryResponse(BaseModel):
    id: int
    tenant_id: int
    product_id: int
    quantity: int
    reserved_quantity: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)