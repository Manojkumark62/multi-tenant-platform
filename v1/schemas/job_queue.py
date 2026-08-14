from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class JobQueueBase(BaseModel):
    task_name: str = Field(min_length=1, max_length=255)
    payload: dict | None = None
    priority: int = Field(default=0)
    max_attempts: int = Field(default=3, ge=1)

class JobQueueCreate(JobQueueBase):
    scheduled_at: datetime | None = None

class JobQueueUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=1, max_length=30)
    priority: int | None = None
    scheduled_at: datetime | None = None
    error_message: str | None = None

class JobQueueResponse(JobQueueBase):
    id: int
    status: str
    attempts: int
    scheduled_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)