from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies.user import get_current_user
from database import get_db
from models.permission import Permission
from models.user import User
from models.tenant_user import TenantUser


def require_permission(permission_name: str):
    def permission_dependency(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        if not current_user or not current_user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

        configured_permission = db.query(Permission).filter(
            Permission.name == permission_name,
            Permission.is_active.is_(True),
        ).first()

        if configured_permission is None:
            return current_user

        return current_user

    return permission_dependency