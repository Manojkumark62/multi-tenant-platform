from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SessionResponse(BaseModel):
    id: int
    user_id: int
    ip_address: str | None
    user_agent: str | None
    expires_at: datetime
    created_at: datetime
    revoked_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class SessionRevoke(BaseModel):
    session_id: int