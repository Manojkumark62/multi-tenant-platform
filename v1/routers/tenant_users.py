from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.tenant_user import TenantUserResponse
from models.tenant_user import TenantUser
from services import tenant_service

router = APIRouter(prefix="/tenant-users", tags=["V1 - Tenant Users"])

@router.post("/{tenant_id}/users/{user_id}", response_model=TenantUserResponse, status_code=status.HTTP_201_CREATED)
def add_user_to_tenant(tenant_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return tenant_service.add_user_to_tenant(db, tenant_id, user_id)

@router.get("/current", response_model=list[TenantUserResponse], status_code=status.HTTP_200_OK)
def list_current_tenant_users(current_tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    return db.query(TenantUser).filter(TenantUser.tenant_id == current_tenant.id).all()