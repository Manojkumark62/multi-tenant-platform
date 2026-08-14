from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.permission import Permission
from models.tenant_user import TenantUser
from models.user import User
from v1.schemas.permission import PermissionCreate, PermissionUpdate


def create_permission(db: Session, permission_data: PermissionCreate) -> Permission:
    existing_permission = db.query(Permission).filter(Permission.name == permission_data.name).first()
    if existing_permission:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Permission with this name already exists")

    permission = Permission(name=permission_data.name, description=permission_data.description, is_active=True)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def get_permission(db: Session, permission_id: int) -> Permission:
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return permission


def get_permission_by_name(db: Session, name: str) -> Permission | None:
    return db.query(Permission).filter(Permission.name == name).first()


def list_permissions(db: Session, offset: int = 0, limit: int = 20) -> list[Permission]:
    return db.query(Permission).filter(Permission.is_active.is_(True)).order_by(Permission.id.asc()).offset(offset).limit(limit).all()


def update_permission(db: Session, permission_id: int, permission_data: PermissionUpdate) -> Permission:
    permission = get_permission(db, permission_id)
    update_data = permission_data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != permission.name:
        existing_permission = db.query(Permission).filter(Permission.name == update_data["name"], Permission.id != permission_id).first()
        if existing_permission:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Permission with this name already exists")

    for field, value in update_data.items():
        setattr(permission, field, value)

    db.commit()
    db.refresh(permission)
    return permission


def deactivate_permission(db: Session, permission_id: int) -> Permission:
    permission = get_permission(db, permission_id)
    permission.is_active = False
    db.commit()
    db.refresh(permission)
    return permission


def user_has_permission(db: Session, user_id: int, permission_name: str, tenant_id: int | None = None) -> bool:
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        return False

    if tenant_id is not None:
        user_in_tenant = db.query(TenantUser.id).filter(
            TenantUser.user_id == user_id,
            TenantUser.tenant_id == tenant_id,
            TenantUser.is_active.is_(True),
        ).first()
        if not user_in_tenant:
            return False

    permission = db.query(Permission.id).filter(
        Permission.name == permission_name,
        Permission.is_active.is_(True),
    ).first()

    return permission is not None