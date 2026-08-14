from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies.user import get_current_user
from database import get_db
from models.tenant import Tenant
from models.tenant_user import TenantUser
from models.user import User

def get_current_tenant(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Tenant:
    tenant_user = db.query(TenantUser).filter(TenantUser.user_id == current_user.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not associated with a tenant")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_user.tenant_id, Tenant.is_active.is_(True)).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not found or inactive")

    return tenant