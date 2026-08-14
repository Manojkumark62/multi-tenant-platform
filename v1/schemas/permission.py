from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class PermissionBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None

class PermissionResponse(PermissionBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)