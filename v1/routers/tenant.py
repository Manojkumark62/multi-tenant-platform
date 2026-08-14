from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from services import tenant_service

router = APIRouter(prefix="/tenants", tags=["V1 - Tenants"])

@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(data: TenantCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return tenant_service.create_tenant(db, data)

@router.get("/current", response_model=TenantResponse, status_code=status.HTTP_200_OK)
def get_current_tenant_details(current_tenant: Tenant = Depends(get_current_tenant)):
    return current_tenant

@router.get("/{tenant_id}", response_model=TenantResponse, status_code=status.HTTP_200_OK)
def get_tenant(tenant_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return tenant_service.get_tenant(db, tenant_id)

@router.patch("/{tenant_id}", response_model=TenantResponse, status_code=status.HTTP_200_OK)
def update_tenant(tenant_id: int, data: TenantUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return tenant_service.update_tenant(db, tenant_id, data)

@router.delete("/{tenant_id}", response_model=TenantResponse, status_code=status.HTTP_200_OK)
def deactivate_tenant(tenant_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return tenant_service.deactivate_tenant(db, tenant_id)