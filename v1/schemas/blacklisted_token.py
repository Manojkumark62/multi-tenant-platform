from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class BlacklistedTokenCreate(BaseModel):
    user_id: int
    token_jti: str = Field(min_length=1, max_length=255)
    expires_at: datetime

class BlacklistedTokenResponse(BaseModel):
    id: int
    user_id: int
    token_jti: str
    expires_at: datetime
    blacklisted_at: datetime

    model_config = ConfigDict(from_attributes=True)