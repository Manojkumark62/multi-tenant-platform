from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.audit_log import AuditLog
from v1.schemas.audit_log import AuditLogCreate

def create_audit_log(db: Session, audit_data: AuditLogCreate) -> AuditLog:
    audit_log = AuditLog(user_id=audit_data.user_id, tenant_id=audit_data.tenant_id, action=audit_data.action, entity_type=audit_data.entity_type, entity_id=audit_data.entity_id, old_values=audit_data.old_values, new_values=audit_data.new_values, ip_address=audit_data.ip_address, user_agent=audit_data.user_agent)
    db.add(audit_log)
    db.flush()
    return audit_log

def get_audit_log(db: Session, tenant_id: int, audit_id: int) -> AuditLog:
    audit_log = db.query(AuditLog).filter(AuditLog.id == audit_id, AuditLog.tenant_id == tenant_id).first()
    if not audit_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")
    return audit_log

def list_audit_logs(db: Session, tenant_id: int, user_id: int | None = None, entity_type: str | None = None, entity_id: int | None = None, offset: int = 0, limit: int = 20) -> list[AuditLog]:
    query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)

    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)

    if entity_type is not None:
        query = query.filter(AuditLog.entity_type == entity_type)

    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)

    return query.order_by(AuditLog.id.desc()).offset(offset).limit(limit).all()