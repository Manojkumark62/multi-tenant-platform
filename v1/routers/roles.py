from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.permissions import require_permission
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from services import role_service

router = APIRouter(prefix="/roles", tags=["V1 - Roles"])

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(data: RoleCreate, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db), current_user: User = Depends(require_permission("role:create"))):
    return role_service.create_role(db, current_tenant.id, data)

@router.get("/{role_id}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
def get_role(role_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return role_service.get_role(db, role_id, current_tenant.id)

@router.get("/", response_model=list[RoleResponse], status_code=status.HTTP_200_OK)
def list_roles(page: int = 1, page_size: int = 20, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    offset = (page - 1) * page_size
    return role_service.list_roles(db, current_tenant.id, offset, page_size)

@router.patch("/{role_id}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
def update_role(role_id: int, data: RoleUpdate, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db), current_user: User = Depends(require_permission("role:update"))):
    return role_service.update_role(db, role_id, data, current_tenant.id)

@router.delete("/{role_id}", response_model=RoleResponse, status_code=status.HTTP_200_OK)
def deactivate_role(role_id: int, current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db), current_user: User = Depends(require_permission("role:delete"))):
    return role_service.deactivate_role(db, role_id, current_tenant.id)