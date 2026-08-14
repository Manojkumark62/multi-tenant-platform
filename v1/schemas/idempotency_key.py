from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class IdempotencyKeyCreate(BaseModel):
    key: str = Field(min_length=1, max_length=255)
    endpoint: str = Field(min_length=1, max_length=255)
    request_hash: str = Field(min_length=1, max_length=255)
    expires_at: datetime

class IdempotencyKeyResponse(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    key: str
    endpoint: str
    request_hash: str
    response_status: int | None
    response_body: dict | None
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)