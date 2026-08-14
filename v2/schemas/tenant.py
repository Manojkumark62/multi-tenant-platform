from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class TenantBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    slug: str = Field(min_length=1, max_length=100)

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    slug: str | None = Field(default=None, min_length=1, max_length=100)

class TenantResponse(TenantBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)