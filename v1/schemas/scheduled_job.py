from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ScheduledJobBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    job_type: str = Field(..., min_length=1, max_length=100)
    cron_expression: str | None = Field(None, max_length=100)
    payload: str | None = None
    is_active: bool = True

class ScheduledJobCreate(ScheduledJobBase):
    tenant_id: int

class ScheduledJobUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    job_type: str | None = Field(None, min_length=1, max_length=100)
    cron_expression: str | None = Field(None, max_length=100)
    payload: str | None = None
    is_active: bool | None = None

class ScheduledJobResponse(ScheduledJobBase):
    id: int
    tenant_id: int
    last_run_at: datetime | None
    next_run_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class JobQueueResponse(BaseModel):
    id: int
    scheduled_job_id: int | None
    tenant_id: int
    job_type: str
    payload: str | None
    status: str
    attempts: int
    max_attempts: int
    available_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)