from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies.tenant import get_current_tenant
from dependencies.user import get_current_user
from models.tenant import Tenant
from models.user import User
from v1.schemas.audit_log import AuditLogResponse
from services import audit_service

router = APIRouter(prefix="/audit-logs", tags=["V1 - Audit Logs"])

@router.get("/{audit_id}", response_model=AuditLogResponse, status_code=status.HTTP_200_OK)
def get_audit_log(audit_id: int, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return audit_service.get_audit_log(db, current_tenant.id, audit_id)

@router.get("/", response_model=list[AuditLogResponse], status_code=status.HTTP_200_OK)
def list_audit_logs(page: int = 1, page_size: int = 20, user_id: int | None = None, entity_type: str | None = None, entity_id: int | None = None, current_tenant: Tenant = Depends(get_current_tenant), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    return audit_service.list_audit_logs(db, current_tenant.id, user_id, entity_type, entity_id, offset, page_size)