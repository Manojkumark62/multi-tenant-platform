from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class TenantUserBase(BaseModel):
    tenant_id: int
    user_id: int
    role: str = Field(default="member", min_length=1, max_length=50)

class TenantUserCreate(TenantUserBase):
    pass

class TenantUserUpdate(BaseModel):
    role: str | None = Field(default=None, min_length=1, max_length=50)

class TenantUserResponse(TenantUserBase):
    id: int
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)