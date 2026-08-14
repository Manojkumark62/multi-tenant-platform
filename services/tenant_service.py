from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.tenant import Tenant
from models.tenant_user import TenantUser
from v1.schemas.tenant import TenantCreate, TenantUpdate

def create_tenant(db: Session, tenant_data: TenantCreate) -> Tenant:
    existing_tenant = db.query(Tenant).filter(Tenant.slug == tenant_data.slug).first()
    if existing_tenant:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tenant with this slug already exists")

    tenant = Tenant(name=tenant_data.name, slug=tenant_data.slug)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

def get_tenant(db: Session, tenant_id: int) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant

def get_tenant_by_slug(db: Session, slug: str) -> Tenant | None:
    return db.query(Tenant).filter(Tenant.slug == slug).first()

def list_tenants(db: Session, offset: int = 0, limit: int = 20) -> list[Tenant]:
    return db.query(Tenant).order_by(Tenant.id.desc()).offset(offset).limit(limit).all()

def update_tenant(db: Session, tenant_id: int, tenant_data: TenantUpdate) -> Tenant:
    tenant = get_tenant(db, tenant_id)
    update_data = tenant_data.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != tenant.slug:
        existing_tenant = db.query(Tenant).filter(Tenant.slug == update_data["slug"], Tenant.id != tenant_id).first()
        if existing_tenant:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tenant slug is already in use")

    for field, value in update_data.items():
        setattr(tenant, field, value)

    db.commit()
    db.refresh(tenant)
    return tenant

def deactivate_tenant(db: Session, tenant_id: int) -> Tenant:
    tenant = get_tenant(db, tenant_id)
    tenant.is_active = False
    db.commit()
    db.refresh(tenant)
    return tenant

def add_user_to_tenant(db: Session, tenant_id: int, user_id: int) -> TenantUser:
    tenant = get_tenant(db, tenant_id)
    if not tenant.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant is inactive")

    existing_membership = db.query(TenantUser).filter(TenantUser.tenant_id == tenant_id, TenantUser.user_id == user_id).first()
    if existing_membership:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member of this tenant")

    tenant_user = TenantUser(tenant_id=tenant_id, user_id=user_id)
    db.add(tenant_user)
    db.commit()
    db.refresh(tenant_user)
    return tenant_user