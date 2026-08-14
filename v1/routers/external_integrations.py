from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.external_integration import ExternalIntegrationCreate, ExternalIntegrationResponse, ExternalIntegrationUpdate
from services import integration_service

router = APIRouter(prefix="/external-integrations", tags=["V1 - External Integrations"])

@router.post("/", response_model=ExternalIntegrationResponse, status_code=status.HTTP_201_CREATED)
def create_integration(data: ExternalIntegrationCreate, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return integration_service.create_integration(db, current_tenant.id, data)

@router.get("/{integration_id}", response_model=ExternalIntegrationResponse, status_code=status.HTTP_200_OK)
def get_integration(integration_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return integration_service.get_integration(db, current_tenant.id, integration_id)

@router.get("/", response_model=list[ExternalIntegrationResponse], status_code=status.HTTP_200_OK)
def list_integrations(page: int = 1, page_size: int = 20, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    return integration_service.list_integrations(db, current_tenant.id, offset, page_size)

@router.patch("/{integration_id}", response_model=ExternalIntegrationResponse, status_code=status.HTTP_200_OK)
def update_integration(integration_id: int, data: ExternalIntegrationUpdate, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return integration_service.update_integration(db, current_tenant.id, integration_id, data)

@router.delete("/{integration_id}", response_model=ExternalIntegrationResponse, status_code=status.HTTP_200_OK)
def deactivate_integration(integration_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return integration_service.deactivate_integration(db, current_tenant.id, integration_id)

@router.post("/{integration_id}/test", status_code=status.HTTP_200_OK)
def test_integration(integration_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return integration_service.test_integration(db, current_tenant.id, integration_id)