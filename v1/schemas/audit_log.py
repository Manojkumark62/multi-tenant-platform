from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class AuditLogBase(BaseModel):
    action: str = Field(..., min_length=1, max_length=100)
    entity_type: str | None = Field(None, max_length=100)
    entity_id: int | None = None
    description: str | None = None
    ip_address: str | None = Field(None, max_length=45)
    user_agent: str | None = Field(None, max_length=500)

class AuditLogCreate(AuditLogBase):
    tenant_id: int
    user_id: int | None = None

class AuditLogResponse(AuditLogBase):
    id: int
    tenant_id: int
    user_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)