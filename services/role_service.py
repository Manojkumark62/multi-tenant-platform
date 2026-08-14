from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.role import Role
from models.role_permission import RolePermission
from models.permission import Permission
from v1.schemas.role import RoleCreate, RoleUpdate

def create_role(db: Session, tenant_id: int | None, role_data: RoleCreate) -> Role:
    existing_role = db.query(Role).filter(Role.tenant_id == tenant_id, Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role with this name already exists")

    role = Role(tenant_id=tenant_id, name=role_data.name, description=role_data.description, is_active=True)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

def get_role(db: Session, role_id: int, tenant_id: int | None = None) -> Role:
    query = db.query(Role).filter(Role.id == role_id)

    if tenant_id is not None:
        query = query.filter(Role.tenant_id == tenant_id)

    role = query.first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role

def list_roles(db: Session, tenant_id: int | None = None, offset: int = 0, limit: int = 20) -> list[Role]:
    query = db.query(Role)

    if tenant_id is not None:
        query = query.filter(Role.tenant_id == tenant_id)

    return query.order_by(Role.id.desc()).offset(offset).limit(limit).all()

def update_role(db: Session, role_id: int, role_data: RoleUpdate, tenant_id: int | None = None) -> Role:
    role = get_role(db, role_id, tenant_id)
    update_data = role_data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != role.name:
        existing_role = db.query(Role).filter(Role.tenant_id == role.tenant_id, Role.name == update_data["name"], Role.id != role_id).first()
        if existing_role:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role with this name already exists")

    for field, value in update_data.items():
        setattr(role, field, value)

    db.commit()
    db.refresh(role)
    return role

def deactivate_role(db: Session, role_id: int, tenant_id: int | None = None) -> Role:
    role = get_role(db, role_id, tenant_id)
    role.is_active = False
    db.commit()
    db.refresh(role)
    return role

def assign_permission(db: Session, role_id: int, permission_id: int, tenant_id: int | None = None) -> RolePermission:
    role = get_role(db, role_id, tenant_id)

    if not role.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role is inactive")

    permission = db.query(Permission).filter(Permission.id == permission_id, Permission.is_active.is_(True)).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    existing_assignment = db.query(RolePermission).filter(RolePermission.role_id == role_id, RolePermission.permission_id == permission_id).first()
    if existing_assignment:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Permission is already assigned to this role")

    role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
    db.add(role_permission)
    db.commit()
    db.refresh(role_permission)
    return role_permission

def remove_permission(db: Session, role_id: int, permission_id: int, tenant_id: int | None = None) -> None:
    role = get_role(db, role_id, tenant_id)
    role_permission = db.query(RolePermission).filter(RolePermission.role_id == role.id, RolePermission.permission_id == permission_id).first()

    if not role_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role permission not found")

    db.delete(role_permission)
    db.commit()