from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class OtpVerificationCreate(BaseModel):
    user_id: int | None = None
    destination: str = Field(min_length=1, max_length=255)
    purpose: str = Field(min_length=1, max_length=50)

class OtpVerificationVerify(BaseModel):
    destination: str = Field(min_length=1, max_length=255)
    purpose: str = Field(min_length=1, max_length=50)
    otp: str = Field(min_length=4, max_length=10)

class OtpVerificationResponse(BaseModel):
    id: int
    user_id: int | None
    destination: str
    purpose: str
    attempts: int
    expires_at: datetime
    verified_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)