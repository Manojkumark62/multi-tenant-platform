from pydantic import BaseModel, ConfigDict

class RolePermissionBase(BaseModel):
    role_id: int
    permission_id: int

class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermissionResponse(RolePermissionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)