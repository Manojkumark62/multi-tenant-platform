from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ApprovalBase(BaseModel):
    tenant_id: int
    requested_by: int
    resource_type: str = Field(min_length=1, max_length=100)
    resource_id: str = Field(min_length=1, max_length=100)
    level: int = Field(default=1, ge=1)
    comments: str | None = None

class ApprovalCreate(ApprovalBase):
    pass

class ApprovalUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=1, max_length=30)
    approved_by: int | None = None
    comments: str | None = None

class ApprovalResponse(ApprovalBase):
    id: int
    approved_by: int | None
    status: str
    created_at: datetime
    updated_at: datetime
    approved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
