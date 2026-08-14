from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class WebhookRetryBase(BaseModel):
    webhook_id: int
    attempt_number: int = Field(ge=1)
    scheduled_at: datetime

class WebhookRetryCreate(WebhookRetryBase):
    pass

class WebhookRetryUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=1, max_length=30)
    error_message: str | None = None
    attempted_at: datetime | None = None

class WebhookRetryResponse(WebhookRetryBase):
    id: int
    status: str
    error_message: str | None
    attempted_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)