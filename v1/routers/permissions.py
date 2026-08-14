from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.permissions import require_permission
from dependencies.user import get_current_user
from models.user import User
from v1.schemas.permission import PermissionCreate, PermissionResponse, PermissionUpdate
from services import permission_service

router = APIRouter(prefix="/permissions", tags=["V1 - Permissions"])

@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(data: PermissionCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("permission:create"))):
    return permission_service.create_permission(db, data)

@router.get("/{permission_id}", response_model=PermissionResponse, status_code=status.HTTP_200_OK)
def get_permission(permission_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return permission_service.get_permission(db, permission_id)

@router.get("/", response_model=list[PermissionResponse], status_code=status.HTTP_200_OK)
def list_permissions(page: int = 1, page_size: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    offset = (page - 1) * page_size
    return permission_service.list_permissions(db, offset, page_size)

@router.patch("/{permission_id}", response_model=PermissionResponse, status_code=status.HTTP_200_OK)
def update_permission(permission_id: int, data: PermissionUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("permission:update"))):
    return permission_service.update_permission(db, permission_id, data)

@router.delete("/{permission_id}", response_model=PermissionResponse, status_code=status.HTTP_200_OK)
def deactivate_permission(permission_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permission("permission:delete"))):
    return permission_service.deactivate_permission(db, permission_id)