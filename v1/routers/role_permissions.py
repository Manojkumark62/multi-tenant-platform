from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.permissions import require_permission
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.role_permission import RolePermissionResponse
from services import role_service

router = APIRouter(prefix="/role-permissions", tags=["V1 - Role Permissions"])

@router.post("/{role_id}/permissions/{permission_id}", response_model=RolePermissionResponse, status_code=status.HTTP_201_CREATED)
def assign_permission(role_id: int, permission_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db), current_user: User = Depends(require_permission("role:permission:assign"))):
    return role_service.assign_permission(db, role_id, permission_id, current_tenant.id)

@router.delete("/{role_id}/permissions/{permission_id}", status_code=status.HTTP_200_OK)
def remove_permission(role_id: int, permission_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db), current_user: User = Depends(require_permission("role:permission:remove"))):
    role_service.remove_permission(db, role_id, permission_id, current_tenant.id)
    return {
        "message": "Permission removed from role",
        "role_id": role_id,
        "permission_id": permission_id,
    }