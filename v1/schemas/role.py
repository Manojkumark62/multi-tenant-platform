from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class RoleBase(BaseModel):
    tenant_id: int | None = None
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None

class RoleResponse(RoleBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)