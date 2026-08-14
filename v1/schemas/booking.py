from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator

class BookingBase(BaseModel):
    booking_reference: str | None = Field(default=None, min_length=1, max_length=100)
    resource_id: str | None = Field(default=None, min_length=1, max_length=100)
    start_time: datetime
    end_time: datetime | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_booking_time(self):
        if self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=1, max_length=30)
    start_time: datetime | None = None
    end_time: datetime | None = None
    notes: str | None = None

class BookingResponse(BookingBase):
    id: int
    tenant_id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)