import json
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ExternalIntegrationBase(BaseModel):
    provider: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=150)
    integration_type: str = Field(min_length=1, max_length=100)
    credentials: dict | None = None
    configuration: dict | None = None

    @field_validator("credentials", "configuration", mode="before")
    @classmethod
    def parse_json_dict(cls, value):
        if value is None or isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return value
        return value

class ExternalIntegrationCreate(ExternalIntegrationBase):
    pass

class ExternalIntegrationUpdate(BaseModel):
    provider: str | None = Field(default=None, min_length=1, max_length=100)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    integration_type: str | None = Field(default=None, min_length=1, max_length=100)
    credentials: dict | None = None
    configuration: dict | None = None
    is_active: bool | None = None

class ExternalIntegrationResponse(ExternalIntegrationBase):
    id: int
    tenant_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)