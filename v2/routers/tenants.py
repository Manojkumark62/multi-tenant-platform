from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v2.schemas.tenant import TenantResponse
from services import tenant_service

router = APIRouter(prefix="/tenants", tags=["V2 - Tenants"])

@router.get("/current", response_model=TenantResponse, status_code=status.HTTP_200_OK)
def get_current_tenant_details(current_tenant: Tenant = Depends(get_current_tenant)):
    return current_tenant

@router.get("/{tenant_id}", response_model=TenantResponse, status_code=status.HTTP_200_OK)
def get_tenant(tenant_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return tenant_service.get_tenant(db, tenant_id)

@router.get("/", response_model=list[TenantResponse], status_code=status.HTTP_200_OK)
def list_tenants(page: int = 1, page_size: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    offset = (page - 1) * page_size
    return tenant_service.list_tenants(db, offset, page_size)