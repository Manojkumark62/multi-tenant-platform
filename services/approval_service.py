from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.approval import Approval
from models.user import User
from v1.schemas.approval import ApprovalCreate, ApprovalUpdate
from utils.datetime import utc_now_naive

def create_approval(db: Session, tenant_id: int, requested_by: int, approval_data: ApprovalCreate) -> Approval:
    requester = db.query(User).filter(User.id == requested_by, User.is_active.is_(True)).first()
    if not requester:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requesting user not found")

    approval = Approval(tenant_id=tenant_id, requested_by=requested_by, entity_type=approval_data.entity_type, entity_id=approval_data.entity_id, reason=approval_data.reason, status="pending")
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval

def get_approval(db: Session, tenant_id: int, approval_id: int) -> Approval:
    approval = db.query(Approval).filter(Approval.id == approval_id, Approval.tenant_id == tenant_id).first()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    return approval

def list_approvals(db: Session, tenant_id: int, status_filter: str | None = None, entity_type: str | None = None, entity_id: int | None = None, offset: int = 0, limit: int = 20) -> list[Approval]:
    query = db.query(Approval).filter(Approval.tenant_id == tenant_id)

    if status_filter is not None:
        query = query.filter(Approval.status == status_filter)

    if entity_type is not None:
        query = query.filter(Approval.entity_type == entity_type)

    if entity_id is not None:
        query = query.filter(Approval.entity_id == entity_id)

    return query.order_by(Approval.id.desc()).offset(offset).limit(limit).all()

def approve_request(db: Session, tenant_id: int, approval_id: int, approved_by: int, approval_data: ApprovalUpdate | None = None) -> Approval:
    approval = get_approval(db, tenant_id, approval_id)

    if approval.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval is not pending")

    approver = db.query(User).filter(User.id == approved_by, User.is_active.is_(True)).first()
    if not approver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approving user not found")

    if approval.requested_by == approved_by:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requester cannot approve their own request")

    approval.status = "approved"
    approval.approved_by = approved_by
    approval.approved_at = utc_now_naive()

    if approval_data:
        update_data = approval_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field not in {"status", "approved_by", "approved_at"}:
                setattr(approval, field, value)

    db.commit()
    db.refresh(approval)
    return approval

def reject_request(db: Session, tenant_id: int, approval_id: int, rejected_by: int, reason: str | None = None) -> Approval:
    approval = get_approval(db, tenant_id, approval_id)

    if approval.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval is not pending")

    rejector = db.query(User).filter(User.id == rejected_by, User.is_active.is_(True)).first()
    if not rejector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rejecting user not found")

    if approval.requested_by == rejected_by:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requester cannot reject their own request")

    approval.status = "rejected"
    approval.approved_by = rejected_by
    approval.approved_at = utc_now_naive()

    if reason:
        approval.reason = reason

    db.commit()
    db.refresh(approval)
    return approval