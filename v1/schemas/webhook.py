from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class WebhookBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    url: str = Field(min_length=1, max_length=1000)
    secret: str | None = Field(default=None, max_length=255)
    event_type: str = Field(min_length=1, max_length=100)
    is_active: bool = True

class WebhookCreate(WebhookBase):
    pass

class WebhookUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    url: str | None = Field(default=None, min_length=1, max_length=1000)
    secret: str | None = Field(default=None, max_length=255)
    event_type: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None

class WebhookResponse(WebhookBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)