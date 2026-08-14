from datetime import datetime
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.booking import Booking
from models.tenant import Tenant
from models.user import User
from v1.schemas.booking import BookingCreate, BookingUpdate
from utils.datetime import utc_now_naive

def create_booking(db: Session, tenant_id: int, user_id: int, booking_data: BookingCreate) -> Booking:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.is_active.is_(True)).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if booking_data.start_time.replace(tzinfo=None) <= utc_now_naive():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking start time must be in the future")

    if booking_data.end_time is not None and booking_data.start_time >= booking_data.end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_time must be later than start_time")

    overlapping_booking = db.query(Booking).filter(
        Booking.tenant_id == tenant_id,
        Booking.status.in_(["pending", "confirmed"]),
        Booking.start_time < booking_data.end_time,
        Booking.end_time > booking_data.start_time,
    ).first()
    if overlapping_booking:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking period overlaps with an existing booking")

    booking_reference = booking_data.booking_reference or f"BK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    booking = Booking(
        tenant_id=tenant_id,
        user_id=user_id,
        booking_reference=booking_reference,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time,
        notes=booking_data.notes,
        status="pending",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def get_booking(db: Session, tenant_id: int, booking_id: int) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.tenant_id == tenant_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking

def list_bookings(db: Session, tenant_id: int, user_id: int | None = None, offset: int = 0, limit: int = 20) -> list[Booking]:
    query = db.query(Booking).filter(Booking.tenant_id == tenant_id)
    if user_id is not None:
        query = query.filter(Booking.user_id == user_id)
    return query.order_by(Booking.start_time.asc()).offset(offset).limit(limit).all()

def update_booking(db: Session, tenant_id: int, booking_id: int, booking_data: BookingUpdate) -> Booking:
    booking = get_booking(db, tenant_id, booking_id)
    update_data = booking_data.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] == "confirmed":
        overlapping_booking = db.query(Booking).filter(
            Booking.id != booking.id,
            Booking.tenant_id == tenant_id,
            Booking.status == "confirmed",
            Booking.start_time < booking.end_time,
            Booking.end_time > booking.start_time,
        ).first()
        if overlapping_booking:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking period overlaps with an existing confirmed booking")

    for field, value in update_data.items():
        setattr(booking, field, value)

    db.commit()
    db.refresh(booking)
    return booking

def cancel_booking(db: Session, tenant_id: int, booking_id: int) -> Booking:
    booking = get_booking(db, tenant_id, booking_id)

    if booking.status in {"cancelled", "completed"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking cannot be cancelled")

    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking